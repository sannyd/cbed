# 2026-10-12 — Real-time user activity tracker middleware.
#
# Captures user_id, email, client_ip, and current endpoint on every
# authenticated request. Storage:
#
#   Primary: Django cache (Redis in production, LocMem in local) with
#            a 15-minute TTL. Key shape `user_active_{user.id}` stores
#            a small dict with the full record. A second key
#            `active_ips:{ip}` lets us look up by IP without scanning.
#
#   Secondary: Postgres `users_user.last_active` + `last_login_ip` +
#              `last_login_user_agent`, debounced to once per 5 minutes
#              per user (via a per-user throttle cache key). This is the
#              cold-cache fallback for `manage.py get_realtime_users`.
#
# Hermes CLI consumer: `python manage.py get_realtime_users [--ip IP]`

from __future__ import annotations

import logging
from typing import Optional

from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("cbed.activity_tracker")

# Cache TTL for the user_active record (spec: 15 minutes).
USER_ACTIVE_TTL_SECONDS = 15 * 60

# Throttle window for Postgres writes (spec: 5 minutes).
DB_WRITE_THROTTLE_SECONDS = 5 * 60

# Path prefixes to skip — admin, static, health checks, swagger.
# Tracking these adds cache entries without giving us any signal.
SKIP_PATH_PREFIXES = (
    "/static/",
    "/media/",
    "/admin/jsi18n/",
    "/favicon.ico",
    "/healthz",
    "/readyz",
    "/swagger",
    "/redoc",
)


def get_client_ip(request) -> str:
    """Extract the real client IP from a Django request.

    Preference order:
        1. HTTP_X_FORWARDED_FOR (first hop, comma-separated chain)
        2. HTTP_X_REAL_IP       (set by nginx / Cloudflare)
        3. REMOTE_ADDR          (direct connection)
    Returns empty string if no IP is present.
    """
    xff = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    real_ip = (request.META.get("HTTP_X_REAL_IP") or "").strip()
    if real_ip:
        return real_ip
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _is_skippable(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in SKIP_PATH_PREFIXES)


def _user_active_cache_key(user_id: int) -> str:
    return f"user_active_{user_id}"


def _ip_lookup_cache_key(ip: str) -> str:
    return f"active_ips:{ip}"


def _db_throttle_cache_key(user_id: int) -> str:
    return f"user_active_db_throttle_{user_id}"


class ActivityTrackerMiddleware(MiddlewareMixin):
    """Capture user_id + IP + endpoint on every authenticated request.

    Hooked into MIDDLEWARE AFTER django.contrib.auth.middleware.AuthenticationMiddleware
    so `request.user` is populated. Anonymous requests are skipped (no
    user_id to key on).
    """

    def process_request(self, request):
        # Cheap pre-checks before we touch the cache layer.
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return None
        path = request.path or ""
        if _is_skippable(path):
            return None

        client_ip = get_client_ip(request)
        if not client_ip:
            # No IP, nothing useful to record.
            return None

        now = timezone.now()
        ts_iso = now.isoformat()
        user_id = user.id

        record = {
            "user_id": user_id,
            "email": user.email or "",
            "name": user.name or user.get_username() or "",
            "ip": client_ip,
            "endpoint": path,
            "method": request.method or "",
            "ts": ts_iso,
            "ts_unix": int(now.timestamp()),
        }

        # PRIMARY: cache write. Best-effort — if cache is down, log and
        # continue. Production cache has IGNORE_EXCEPTIONS=True so this
        # should never raise, but be defensive.
        try:
            cache.set(_user_active_cache_key(user_id), record, USER_ACTIVE_TTL_SECONDS)
            # IP -> user_id reverse lookup, also 15-minute TTL.
            ip_key = _ip_lookup_cache_key(client_ip)
            existing_user_ids = cache.get(ip_key) or set()
            if isinstance(existing_user_ids, set):
                existing_user_ids.add(user_id)
            else:
                # Defensive: if a non-set value is in the cache (e.g. another
                # process wrote a list), coerce it.
                existing_user_ids = set(existing_user_ids) | {user_id}
            cache.set(ip_key, existing_user_ids, USER_ACTIVE_TTL_SECONDS)
        except Exception as exc:  # pragma: no cover — defensive
            logger.warning("activity_tracker: cache write failed: %s", exc)

        # SECONDARY: DB write, debounced to once per 5 minutes per user.
        # We don't have request.user.pk guaranteed here in process_request
        # for all auth backends, but for Django's default it is set.
        try:
            throttle_key = _db_throttle_cache_key(user_id)
            if cache.get(throttle_key):
                return None
            # Mark the throttle BEFORE the write so a slow DB doesn't
            # cause another concurrent request to also try to write.
            cache.set(throttle_key, ts_iso, DB_WRITE_THROTTLE_SECONDS)
            self._write_db(user, client_ip, now, request)
        except Exception as exc:  # pragma: no cover — defensive
            logger.warning("activity_tracker: db throttle / write failed: %s", exc)

        return None

    def _write_db(self, user, client_ip: str, now, request) -> None:
        """Best-effort Postgres update of last_active + last_login_ip.

        Only writes fields that exist on the User model. The IP-capture
        migration 0028 added `last_login_ip`, `last_login_user_agent`,
        and `last_active` — if it hasn't been applied yet, this method
        silently no-ops for those fields.
        """
        update_fields = []
        if hasattr(user, "last_active"):
            user.last_active = now
            update_fields.append("last_active")
        if hasattr(user, "last_login_ip"):
            if getattr(user, "last_login_ip", None) != client_ip:
                user.last_login_ip = client_ip
                update_fields.append("last_login_ip")
        if hasattr(user, "last_login_user_agent"):
            ua = (request.META.get("HTTP_USER_AGENT") or "")[:512]
            if getattr(user, "last_login_user_agent", "") != ua:
                user.last_login_user_agent = ua
                update_fields.append("last_login_user_agent")
        if not update_fields:
            return
        # use update_fields so we don't accidentally clobber concurrent
        # writes to other fields (e.g. last_login itself).
        user.save(update_fields=update_fields)
