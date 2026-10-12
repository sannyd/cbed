# 2026-10-12 — `python manage.py get_realtime_users [--ip IP]`
#
# Reports users active in the last 30 minutes. Primary path: the
# `user_active_{user_id}` cache entries written by
# cbed.middleware.activity_tracker.ActivityTrackerMiddleware.
# Fallback: Postgres `users_user.last_active` / `last_login_ip` for the
# case where the cache is cold but the user has DB activity in the
# last 30 minutes.
#
# Output: a fixed-width table on stdout, also machine-parseable via
# `--json` for downstream Hermes automation.
#
# Examples:
#   python manage.py get_realtime_users
#   python manage.py get_realtime_users --ip 209.30.146.74
#   python manage.py get_realtime_users --since-min 60 --json
#   python manage.py get_realtime_users --source cache   # cache only, no DB
#   python manage.py get_realtime_users --source db      # DB only, no cache

from __future__ import annotations

import json
from datetime import timedelta

from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from cbed.middleware.activity_tracker import (
    _ip_lookup_cache_key,
    _user_active_cache_key,
)


# Default lookback window. Spec says "last 30 minutes".
DEFAULT_SINCE_MINUTES = 30

# Path: just print rows. Truncation width matches the spec columns.
COL_USER_ID = 8
COL_NAME = 24
COL_EMAIL = 32
COL_IP = 18
COL_ENDPOINT = 32
COL_TS = 22


class Command(BaseCommand):
    help = (
        "Report users active in the last N minutes. "
        "Reads primarily from the activity_tracker cache; falls back to "
        "Postgres users_user.last_active when the cache is cold. "
        "Use --ip to filter to a specific client IP."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--ip",
            default=None,
            help="Filter to a specific client IP (matches both cache and DB).",
        )
        parser.add_argument(
            "--since-min",
            type=int,
            default=DEFAULT_SINCE_MINUTES,
            help=(
                f"Lookback window in minutes (default {DEFAULT_SINCE_MINUTES}). "
                "Cache records older than this are dropped even if the TTL "
                "hasn't expired."
            ),
        )
        parser.add_argument(
            "--source",
            choices=("auto", "cache", "db"),
            default="auto",
            help=(
                "Where to read from. 'auto' (default) uses cache first and "
                "merges in DB rows for the same lookback window. 'cache' "
                "skips the DB query. 'db' skips the cache scan (useful if "
                "the cache is down or you want long-window DB records)."
            ),
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit JSON instead of a fixed-width table (for automation).",
        )

    def handle(self, *args, **options):
        since_min = options["since_min"]
        ip_filter = (options["ip"] or "").strip() or None
        source = options["source"]
        as_json = options["json"]

        if since_min <= 0:
            raise CommandError("--since-min must be > 0")

        now = timezone.now()
        cutoff_unix = int((now - timedelta(minutes=since_min)).timestamp())

        rows = []

        # -- Cache pass --
        if source in ("auto", "cache"):
            cache_rows = self._collect_from_cache(ip_filter, cutoff_unix)
            rows.extend(cache_rows)

        # -- DB pass --
        if source in ("auto", "db"):
            db_rows = self._collect_from_db(ip_filter, cutoff_unix, now)
            # Dedupe by user_id — cache row wins if both exist.
            seen = {r["user_id"] for r in rows}
            for r in db_rows:
                if r["user_id"] not in seen:
                    rows.append(r)

        # Final sort: most recent first.
        rows.sort(key=lambda r: r.get("ts_unix", 0), reverse=True)

        if as_json:
            self.stdout.write(json.dumps(rows, indent=2, default=str))
            return

        self._print_table(rows)

    # ------------------------------------------------------------------
    # Cache collection
    # ------------------------------------------------------------------
    def _collect_from_cache(self, ip_filter, cutoff_unix):
        """Return list of active-user dicts from the cache.

        If --ip is given, we use the `active_ips:{ip}` reverse-lookup
        set to get the user_ids that have hit that IP in the last 15
        minutes. Otherwise we have no global index of user_active keys,
        so we fall back to scanning the IP keys via a small trick:
        we can't enumerate Redis keys without SCAN, but we can iterate
        a small set of "candidate" user_ids from the most recent DB
        last_active. For now, if --ip is None, we return an empty
        list and let the DB pass fill in. (Future: maintain a
        `active_user_ids` set updated by the middleware.)
        """
        if not ip_filter:
            # No global index, let the DB pass handle it.
            return []
        user_ids = cache.get(_ip_lookup_cache_key(ip_filter)) or set()
        if not isinstance(user_ids, set):
            try:
                user_ids = set(user_ids)
            except TypeError:
                return []
        rows = []
        for uid in user_ids:
            rec = cache.get(_user_active_cache_key(uid))
            if not rec:
                continue
            if rec.get("ts_unix", 0) < cutoff_unix:
                continue
            if ip_filter and rec.get("ip") != ip_filter:
                continue
            rows.append(self._format_record(rec))
        return rows

    # ------------------------------------------------------------------
    # DB collection
    # ------------------------------------------------------------------
    def _collect_from_db(self, ip_filter, cutoff_unix, now):
        """Return list of active-user dicts from Postgres.

        Queries users_user for rows with last_active >= cutoff (or
        last_login_ip matching ip_filter, with a coarser time window
        if needed). Fields are read defensively — if migration 0028
        hasn't been applied, the relevant fields don't exist and we
        no-op with a warning.
        """
        from cbed.users.models import User  # local import for management-command idiom

        cutoff_dt = now - timedelta(seconds=(now.timestamp() - cutoff_unix))
        qs = User.objects.all()

        # Filter to the lookback window. If `last_active` doesn't exist
        # on the model, fall back to `last_login`.
        has_last_active = any(f.name == "last_active" for f in User._meta.get_fields())
        has_last_login_ip = any(f.name == "last_login_ip" for f in User._meta.get_fields())
        if ip_filter and not has_last_login_ip:
            self.stderr.write(
                "WARNING: --ip filter requires the last_login_ip column "
                "(migration 0028). Cache-only results returned instead."
            )
            return []

        if has_last_active:
            qs = qs.filter(last_active__gte=cutoff_dt)
        else:
            qs = qs.filter(last_login__gte=cutoff_dt)

        if ip_filter and has_last_login_ip:
            qs = qs.filter(last_login_ip=ip_filter)

        rows = []
        for u in qs.only(
            "id", "email", "name", "username", "last_login",
            "last_active", "last_login_ip", "last_login_user_agent",
        )[:500]:  # safety cap
            ip = getattr(u, "last_login_ip", None) or ""
            if ip_filter and ip != ip_filter:
                continue
            ts = getattr(u, "last_active", None) or u.last_login
            if ts is None:
                continue
            row = {
                "user_id": u.id,
                "email": u.email or "",
                "name": u.name or u.get_username() or "",
                "ip": ip,
                "endpoint": "",  # DB doesn't carry endpoint
                "method": "",
                "ts": ts.isoformat(),
                "ts_unix": int(ts.timestamp()),
                "source": "db",
            }
            rows.append(row)
        return rows

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    @staticmethod
    def _format_record(rec):
        return {
            "user_id": rec.get("user_id"),
            "email": rec.get("email", ""),
            "name": rec.get("name", ""),
            "ip": rec.get("ip", ""),
            "endpoint": rec.get("endpoint", ""),
            "method": rec.get("method", ""),
            "ts": rec.get("ts", ""),
            "ts_unix": rec.get("ts_unix", 0),
            "source": "cache",
        }

    def _print_table(self, rows):
        if not rows:
            self.stdout.write("(no active users in the lookback window)")
            return
        # Header
        header = (
            f"{'USER_ID':<{COL_USER_ID}} "
            f"{'NAME':<{COL_NAME}} "
            f"{'EMAIL':<{COL_EMAIL}} "
            f"{'IP':<{COL_IP}} "
            f"{'ENDPOINT':<{COL_ENDPOINT}} "
            f"{'TIMESTAMP':<{COL_TS}}"
        )
        self.stdout.write(header)
        self.stdout.write("-" * len(header))
        for r in rows:
            line = (
                f"{str(r['user_id']):<{COL_USER_ID}} "
                f"{(r['name'] or '')[:COL_NAME]:<{COL_NAME}} "
                f"{(r['email'] or '')[:COL_EMAIL]:<{COL_EMAIL}} "
                f"{(r['ip'] or '')[:COL_IP]:<{COL_IP}} "
                f"{(r['endpoint'] or '')[:COL_ENDPOINT]:<{COL_ENDPOINT}} "
                f"{(r['ts'] or '')[:COL_TS]:<{COL_TS}}"
            )
            self.stdout.write(line)
        self.stdout.write("")
        self.stdout.write(f"Total: {len(rows)} active user(s)")
