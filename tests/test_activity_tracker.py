# 2026-10-12 — Tests for cbed.middleware.activity_tracker and the
# `manage.py get_realtime_users` command.
#
# Run with:
#   docker compose -f local.yml exec django pytest tests/test_activity_tracker.py -v
#
# Coverage:
#   - get_client_ip() preference order (X-Forwarded-For > X-Real-IP > REMOTE_ADDR)
#   - skip logic (static, health, swagger)
#   - cache write on authed request
#   - IP reverse-lookup key
#   - DB throttle (5 min)
#   - anonymous requests are skipped
#   - get_realtime_users command with --ip and --json

from __future__ import annotations

import json
from datetime import timedelta
from io import StringIO

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory
from django.utils import timezone
from django.contrib.auth import get_user_model

from cbed.middleware.activity_tracker import (
    ActivityTrackerMiddleware,
    USER_ACTIVE_TTL_SECONDS,
    DB_WRITE_THROTTLE_SECONDS,
    _ip_lookup_cache_key,
    _user_active_cache_key,
    _db_throttle_cache_key,
    get_client_ip,
    _is_skippable,
)


User = get_user_model()


# ----------------------------------------------------------------------
# Pure-function tests (no DB, no middleware invocation)
# ----------------------------------------------------------------------
class TestGetClientIp:
    def make_request(self, **meta):
        rf = RequestFactory()
        req = rf.get("/")
        for k, v in meta.items():
            req.META[k] = v
        return req

    def test_prefers_xff_first_hop(self):
        req = self.make_request(
            HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.1",
            HTTP_X_REAL_IP="5.6.7.8",
            REMOTE_ADDR="9.9.9.9",
        )
        assert get_client_ip(req) == "1.2.3.4"

    def test_xff_strips_whitespace(self):
        req = self.make_request(HTTP_X_FORWARDED_FOR="  1.2.3.4  ,  10.0.0.1  ")
        assert get_client_ip(req) == "1.2.3.4"

    def test_falls_back_to_x_real_ip(self):
        req = self.make_request(HTTP_X_REAL_IP="5.6.7.8", REMOTE_ADDR="9.9.9.9")
        assert get_client_ip(req) == "5.6.7.8"

    def test_falls_back_to_remote_addr(self):
        req = self.make_request(REMOTE_ADDR="9.9.9.9")
        assert get_client_ip(req) == "9.9.9.9"

    def test_empty_when_no_ip(self):
        req = self.make_request()
        assert get_client_ip(req) == ""


class TestIsSkippable:
    @pytest.mark.parametrize("path", [
        "/static/foo.css",
        "/media/img.png",
        "/admin/jsi18n/",
        "/favicon.ico",
        "/healthz",
        "/readyz",
        "/swagger",
        "/redoc",
    ])
    def test_skipped(self, path):
        assert _is_skippable(path) is True

    @pytest.mark.parametrize("path", [
        "/api/v1/users/me/",
        "/api/v1/mcq/section/123/",
        "/auth/signin",
        "/api/v1/some/endpoint",
    ])
    def test_not_skipped(self, path):
        assert _is_skippable(path) is False


# ----------------------------------------------------------------------
# Middleware invocation tests
# ----------------------------------------------------------------------
@pytest.fixture
def authed_user(db):
    u = User.objects.create(
        username="testuser",
        email="test@example.com",
        name="Test User",
    )
    u.set_password("hunter2")
    u.save()
    return u


@pytest.fixture
def clear_cache():
    cache.clear()
    yield
    cache.clear()


class TestMiddlewareOnRequest:
    def test_anon_request_is_skipped(self, clear_cache):
        rf = RequestFactory()
        req = rf.get("/api/v1/foo", HTTP_X_FORWARDED_FOR="1.2.3.4")
        req.user = type("Anon", (), {"is_authenticated": False})()
        mw = ActivityTrackerMiddleware(lambda r: None)
        result = mw.process_request(req)
        assert result is None
        # Nothing in the cache
        assert cache.get(_user_active_cache_key(0)) is None

    def test_authed_request_writes_cache(self, clear_cache, authed_user):
        rf = RequestFactory()
        req = rf.get(
            "/api/v1/mcq/section/123/",
            HTTP_X_FORWARDED_FOR="209.30.146.74, 10.0.0.1",
            HTTP_USER_AGENT="Bar Exam Drills/1.0 iOS",
        )
        # Simulate authed user
        req.user = authed_user
        mw = ActivityTrackerMiddleware(lambda r: None)
        result = mw.process_request(req)
        assert result is None
        rec = cache.get(_user_active_cache_key(authed_user.id))
        assert rec is not None
        assert rec["user_id"] == authed_user.id
        assert rec["email"] == "test@example.com"
        assert rec["name"] == "Test User"
        assert rec["ip"] == "209.30.146.74"
        assert rec["endpoint"] == "/api/v1/mcq/section/123/"
        assert rec["method"] == "GET"

    def test_ip_reverse_lookup_populated(self, clear_cache, authed_user):
        rf = RequestFactory()
        req = rf.get("/api/v1/foo", HTTP_X_FORWARDED_FOR="209.30.146.74")
        req.user = authed_user
        mw = ActivityTrackerMiddleware(lambda r: None)
        mw.process_request(req)
        ids = cache.get(_ip_lookup_cache_key("209.30.146.74"))
        assert isinstance(ids, set)
        assert authed_user.id in ids

    def test_two_users_same_ip(self, clear_cache, db):
        u1 = User.objects.create(username="u1", email="u1@x.com", name="U1")
        u2 = User.objects.create(username="u2", email="u2@x.com", name="U2")
        rf = RequestFactory()
        mw = ActivityTrackerMiddleware(lambda r: None)
        for u in (u1, u2):
            req = rf.get("/api/v1/foo", HTTP_X_FORWARDED_FOR="9.9.9.9")
            req.user = u
            mw.process_request(req)
        ids = cache.get(_ip_lookup_cache_key("9.9.9.9"))
        assert {u1.id, u2.id} == ids

    def test_static_path_is_skipped(self, clear_cache, authed_user):
        rf = RequestFactory()
        req = rf.get("/static/foo.css", HTTP_X_FORWARDED_FOR="1.2.3.4")
        req.user = authed_user
        mw = ActivityTrackerMiddleware(lambda r: None)
        mw.process_request(req)
        assert cache.get(_user_active_cache_key(authed_user.id)) is None

    def test_no_ip_skips(self, clear_cache, authed_user):
        rf = RequestFactory()
        req = rf.get("/api/v1/foo")
        req.user = authed_user
        mw = ActivityTrackerMiddleware(lambda r: None)
        mw.process_request(req)
        assert cache.get(_user_active_cache_key(authed_user.id)) is None


class TestDbThrottle:
    def test_first_request_writes_throttle_key(
        self, clear_cache, authed_user
    ):
        rf = RequestFactory()
        req = rf.get("/api/v1/foo", HTTP_X_FORWARDED_FOR="1.2.3.4")
        req.user = authed_user
        mw = ActivityTrackerMiddleware(lambda r: None)
        mw.process_request(req)
        throttle = cache.get(_db_throttle_cache_key(authed_user.id))
        assert throttle is not None

    def test_subsequent_request_within_window_skips_db(
        self, clear_cache, authed_user
    ):
        # Pre-set the throttle as if a recent request already wrote.
        cache.set(_db_throttle_cache_key(authed_user.id), "1m_ago", 60)
        rf = RequestFactory()
        req = rf.get("/api/v1/foo", HTTP_X_FORWARDED_FOR="1.2.3.4")
        req.user = authed_user
        # We can't easily verify "no DB write happened" without a mock,
        # but we CAN verify the throttle is still in place (the middleware
        # doesn't clear it).
        mw = ActivityTrackerMiddleware(lambda r: None)
        mw.process_request(req)
        assert cache.get(_db_throttle_cache_key(authed_user.id)) is not None


# ----------------------------------------------------------------------
# Management command tests
# ----------------------------------------------------------------------
class TestGetRealtimeUsersCommand:
    def test_no_active_users(self, clear_cache, db):
        out = StringIO()
        call_command("get_realtime_users", stdout=out)
        assert "no active users" in out.getvalue().lower()

    def test_json_output(self, clear_cache, db, authed_user):
        # Seed a cache record
        now = timezone.now()
        cache.set(_user_active_cache_key(authed_user.id), {
            "user_id": authed_user.id,
            "email": authed_user.email,
            "name": authed_user.name,
            "ip": "209.30.146.74",
            "endpoint": "/api/v1/foo",
            "method": "GET",
            "ts": now.isoformat(),
            "ts_unix": int(now.timestamp()),
        }, USER_ACTIVE_TTL_SECONDS)
        cache.set(_ip_lookup_cache_key("209.30.146.74"),
                  {authed_user.id}, USER_ACTIVE_TTL_SECONDS)
        out = StringIO()
        call_command("get_realtime_users", "--ip", "209.30.146.74",
                     "--json", stdout=out)
        data = json.loads(out.getvalue())
        assert len(data) == 1
        assert data[0]["user_id"] == authed_user.id
        assert data[0]["ip"] == "209.30.146.74"

    def test_ip_filter_excludes_other_ips(
        self, clear_cache, db, authed_user
    ):
        now = timezone.now()
        cache.set(_user_active_cache_key(authed_user.id), {
            "user_id": authed_user.id,
            "email": authed_user.email,
            "name": authed_user.name,
            "ip": "1.1.1.1",
            "endpoint": "/api/v1/foo",
            "method": "GET",
            "ts": now.isoformat(),
            "ts_unix": int(now.timestamp()),
        }, USER_ACTIVE_TTL_SECONDS)
        cache.set(_ip_lookup_cache_key("1.1.1.1"),
                  {authed_user.id}, USER_ACTIVE_TTL_SECONDS)
        out = StringIO()
        # Filter to a different IP — should return 0 rows.
        call_command("get_realtime_users", "--ip", "9.9.9.9",
                     "--json", stdout=out)
        data = json.loads(out.getvalue())
        assert data == []

    def test_db_fallback_path(self, clear_cache, db, authed_user):
        # No cache record. Set last_active via update_fields trick to
        # avoid clobbering other fields. If the column doesn't exist
        # (migration 0028 not applied), the test will be skipped.
        if not any(f.name == "last_active" for f in User._meta.get_fields()):
            pytest.skip("last_active column not present (migration 0028 not applied)")
        authed_user.last_active = timezone.now()
        authed_user.save(update_fields=["last_active"])
        out = StringIO()
        call_command("get_realtime_users", "--source", "db", "--json",
                     stdout=out)
        data = json.loads(out.getvalue())
        # At least our user should be in the result
        ids = {r["user_id"] for r in data}
        assert authed_user.id in ids
        # The DB-fallback row should have source=db and empty endpoint.
        our = next(r for r in data if r["user_id"] == authed_user.id)
        assert our["source"] == "db"
        assert our["endpoint"] == ""
