"""Session handling, CSRF, rate limiting, login protection and security headers."""
from __future__ import annotations

import hmac
import re
import secrets
import threading
import time
import uuid
from collections import defaultdict, deque
from datetime import timedelta

from flask import g, jsonify, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from .audit import audit
from .extensions import db
from .models import AppUser, utcnow
from .utils import ApiError

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
# Endpoints authenticated by a device API key rather than a browser session.
CSRF_EXEMPT_PREFIXES = ("/api/integrations/",)
PUBLIC_PATHS = {"/health", "/health/live", "/login", "/api/auth/login", "/api/auth/csrf", "/api/auth/demo-accounts"}
COMMON_PASSWORDS = {"password", "password1", "123456789", "1234567890", "qwertyuiop", "letmein123", "welcome123", "admin12345", "careflow123"}
COMMON_WORDS = {"password", "passw0rd", "qwerty", "qwertyuiop", "letmein", "welcome", "administrator", "admin", "careflow", "hospital", "iloveyou", "changeme", "abcdefgh", "trustno"}
_DUMMY_HASH = generate_password_hash("careflow-dummy-password-for-timing")


# --------------------------------------------------------------------------- #
# Passwords
# --------------------------------------------------------------------------- #
def hash_password(password: str) -> str:
    return generate_password_hash(password, method="scrypt")


def validate_password_strength(password: str, *, email: str = "", name: str = ""):
    if len(password or "") < 12:
        raise ApiError("Password must be at least 12 characters")
    if len(password) > 200:
        raise ApiError("Password is too long")
    low = password.lower()
    letters = re.sub(r"[^a-z]", "", low)
    if low in COMMON_PASSWORDS or letters in COMMON_WORDS or len(set(low)) < 5:
        raise ApiError("Password is too easy to guess")
    local = (email or "").split("@")[0].lower()
    if local and len(local) >= 4 and local in low:
        raise ApiError("Password must not contain your e-mail name")
    if name and len(name) >= 4 and name.lower().replace(" ", "") in low.replace(" ", ""):
        raise ApiError("Password must not contain your name")


# --------------------------------------------------------------------------- #
# Rate limiting (per process; use a shared store such as Redis for multi-instance deployments)
# --------------------------------------------------------------------------- #
class RateLimiter:
    def __init__(self):
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window: float = 60.0) -> bool:
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            if len(self._hits) > 20000:  # bound memory
                for k in list(self._hits)[:5000]:
                    if not self._hits[k]:
                        del self._hits[k]
            return True

    def reset(self):
        with self._lock:
            self._hits.clear()


limiter = RateLimiter()


# --------------------------------------------------------------------------- #
# CSRF
# --------------------------------------------------------------------------- #
def csrf_token() -> str:
    tok = session.get("csrf")
    if not tok:
        tok = secrets.token_urlsafe(32)
        session["csrf"] = tok
    return tok


def _check_csrf():
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token") or ""
    expected = session.get("csrf", "")
    if not expected or not sent or not hmac.compare_digest(sent, expected):
        raise ApiError("Missing or invalid CSRF token. Reload the page and try again.", 403)


# --------------------------------------------------------------------------- #
# Request lifecycle
# --------------------------------------------------------------------------- #
def load_user_from_session(app):
    uid = session.get("uid")
    if not uid:
        return None
    now = time.time()
    idle = app.config["SESSION_IDLE_MINUTES"] * 60
    absolute = app.config["SESSION_ABSOLUTE_HOURS"] * 3600
    if now - session.get("last_seen", 0) > idle or now - session.get("login_at", 0) > absolute:
        session.clear()
        return None
    user = db.session.get(AppUser, uid)
    if user is None or not user.is_active or user.session_epoch != session.get("epoch"):
        session.clear()
        return None
    if user.is_demo and not app.config["DEMO_MODE"]:
        session.clear()
        return None
    session["last_seen"] = now
    return user


# A patient login is limited to its own portal, the assistant (which re-checks scope) and account basics: enforced for every request.
PATIENT_API_PREFIXES = ("/api/auth/", "/api/portal/", "/api/ai/", "/api/workspaces")


def init_security(app):
    @app.before_request
    def _before():
        g.request_id = str(uuid.uuid4())
        g.user = None
        path = request.path
        if path.startswith("/static/"):
            return None
        try:
            g.user = load_user_from_session(app)
            if app.config["RATE_LIMIT_ENABLED"] and path.startswith("/api/"):
                ident = f"u{g.user.id}" if g.user else f"ip{request.remote_addr}"
                if not limiter.hit(f"api:{ident}", app.config["API_RATE_PER_MINUTE"]):
                    raise ApiError("Too many requests. Please slow down.", 429)
            if request.method not in SAFE_METHODS and path.startswith("/api/") and not path.startswith(CSRF_EXEMPT_PREFIXES):
                _check_csrf()
            if path.startswith("/api/") and g.user is None and path not in PUBLIC_PATHS and not path.startswith(CSRF_EXEMPT_PREFIXES):
                raise ApiError("Authentication required", 401)
            if g.user is not None and g.user.role == "patient" and path.startswith("/api/") and not path.startswith(PATIENT_API_PREFIXES):
                from .audit import audit
                audit("access.denied", category="security", outcome="denied", details=f"patient account blocked from {request.method} {path[:80]}", commit=True)
                raise ApiError("Patient accounts can only view their own record and use the assistant", 403)
            if g.user is not None and g.user.must_change_password and path.startswith("/api/") and path not in {"/api/auth/password", "/api/auth/me", "/api/auth/logout", "/api/auth/csrf"}:
                raise ApiError("You must change your password before continuing", 403, must_change_password=True)
        except ApiError as e:
            return _json_error(e)
        return None

    @app.after_request
    def _after(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        resp.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'",
        )
        if request.path.startswith("/api/") or request.path in ("/", "/login"):
            resp.headers["Cache-Control"] = "no-store"
            resp.headers["Pragma"] = "no-cache"
        if app.config.get("CAREFLOW_ENV") == "production":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        rid = getattr(g, "request_id", None)
        if rid:
            resp.headers["X-Request-ID"] = rid
        return resp

    @app.errorhandler(ApiError)
    def _api_error(e):
        return _json_error(e)

    @app.errorhandler(404)
    def _nf(e):
        if request.path.startswith("/api/"):
            return jsonify(ok=False, error="Not found"), 404
        return e

    @app.errorhandler(405)
    def _mna(e):
        return jsonify(ok=False, error="Method not allowed"), 405

    @app.errorhandler(413)
    def _too_large(e):
        return jsonify(ok=False, error="Upload is larger than the permitted size"), 413

    @app.errorhandler(Exception)
    def _unhandled(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            if request.path.startswith("/api/"):
                return jsonify(ok=False, error=e.description or e.name), e.code
            return e
        db.session.rollback()
        app.logger.exception("Unhandled error (request %s)", getattr(g, "request_id", "-"))
        if request.path.startswith("/api/") or request.is_json:
            return jsonify(ok=False, error="Unexpected server error", request_id=getattr(g, "request_id", "")), 500
        return "Unexpected server error", 500


def _json_error(e: ApiError):
    db.session.rollback()
    body = {"ok": False, "error": e.message}
    body.update(e.extra)
    resp = jsonify(body)
    resp.status_code = e.status
    return resp


# --------------------------------------------------------------------------- #
# Login / logout
# --------------------------------------------------------------------------- #
def attempt_login(app, email: str, password: str) -> AppUser:
    email = (email or "").strip().lower()
    ip = request.remote_addr or "-"
    if app.config["RATE_LIMIT_ENABLED"]:
        if not limiter.hit(f"login:ip:{ip}", app.config["LOGIN_RATE_PER_MINUTE"]) or not limiter.hit(f"login:em:{email}", app.config["LOGIN_RATE_PER_MINUTE"]):
            audit("auth.rate_limited", category="security", outcome="denied", details=f"ip={ip}", commit=True)
            raise ApiError("Too many sign-in attempts. Try again in a minute.", 429)
    user = db.session.execute(db.select(AppUser).where(AppUser.email == email)).scalar_one_or_none()
    generic = ApiError("Incorrect e-mail or password", 401)
    if user is None:
        check_password_hash(_DUMMY_HASH, password or "")
        audit("auth.login_failed", category="security", outcome="denied", details="unknown account", commit=True)
        raise generic
    now = utcnow()
    if user.locked_until and user.locked_until > now:
        check_password_hash(_DUMMY_HASH, password or "")
        audit("auth.login_blocked_locked", category="security", outcome="denied", user=user, commit=True)
        raise ApiError("Account temporarily locked after repeated failures. Try again later.", 423)
    if not check_password_hash(user.password_hash, password or ""):
        user.failed_logins = (user.failed_logins or 0) + 1
        if user.failed_logins >= app.config["LOGIN_MAX_FAILURES"]:
            user.locked_until = now + timedelta(minutes=app.config["LOGIN_LOCK_MINUTES"])
            user.failed_logins = 0
            audit("auth.account_locked", category="security", outcome="denied", user=user)
        audit("auth.login_failed", category="security", outcome="denied", user=user, commit=True)
        raise generic
    if not user.is_active:
        audit("auth.login_suspended", category="security", outcome="denied", user=user, commit=True)
        raise ApiError("This account is suspended. Contact an administrator.", 403)
    if user.is_demo and not app.config["DEMO_MODE"]:
        audit("auth.login_demo_disabled", category="security", outcome="denied", user=user, commit=True)
        raise generic
    user.failed_logins = 0
    user.locked_until = None
    user.last_login_at = now
    audit("auth.login", category="security", user=user)
    db.session.commit()
    csrf = session.get("csrf")
    session.clear()  # defend against session fixation
    session["uid"] = user.id
    session["epoch"] = user.session_epoch
    session["login_at"] = time.time()
    session["last_seen"] = time.time()
    session["csrf"] = csrf or secrets.token_urlsafe(32)
    session.permanent = False
    return user


def logout():
    if getattr(g, "user", None):
        audit("auth.logout", category="security", commit=True)
    session.clear()
