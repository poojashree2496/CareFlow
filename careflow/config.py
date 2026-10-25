"""Configuration loading, database selection and safe diagnostics.

Design rules (see SUPABASE_SETUP.md):
  * ``.env`` is loaded from the application directory, never from the CWD.
  * An explicit PostgreSQL request is never silently replaced by SQLite.
  * Passwords, tokens and full connection URIs are never printed or logged.
"""
from __future__ import annotations

import os
import re
import secrets
import socket
import ssl
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit

BASE_DIR = Path(__file__).resolve().parent.parent
INSECURE_DEFAULT_SECRETS = {
    "",
    "change-this-demo-secret-before-deployment",
    "replace-with-a-long-random-secret",
    "changeme",
    "secret",
}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
_HOST_RE = re.compile(r"^(?=.{1,253}$)([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$")


class ConfigError(RuntimeError):
    """Raised for configuration problems. Messages never contain secrets."""


def load_env(env_file: str | os.PathLike | None = None) -> bool:
    """Load ``.env`` from the application directory (not the CWD)."""
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover
        return False
    path = Path(env_file) if env_file else BASE_DIR / ".env"
    if path.is_file():
        return bool(load_dotenv(path, override=False))
    return False


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc


# --------------------------------------------------------------------------- #
# Database URL handling
# --------------------------------------------------------------------------- #
def redact_url(url: str) -> str:
    """Return the URL with the password removed. Safe for logs/diagnostics."""
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
        if parts.port:
            host += f":{parts.port}"
        user = unquote(parts.username) if parts.username else ""
        netloc = f"{user}:***@{host}" if user else host
        return urlunsplit((parts.scheme, netloc, parts.path, "", ""))
    except Exception:
        return "<unparseable database url>"


@dataclass
class DatabaseSettings:
    uri: str
    backend: str  # 'sqlite' | 'postgresql'
    host: str = ""
    port: int | None = None
    database: str = ""
    username_hint: str = ""
    sslmode: str = ""
    kind: str = ""  # 'local', 'supabase-direct', 'supabase-session-pooler', 'supabase-transaction-pooler', 'postgresql'
    warnings: list[str] = field(default_factory=list)
    engine_options: dict = field(default_factory=dict)

    def describe(self) -> dict:
        """Safe, secret-free description for health/diagnostic output."""
        return {
            "backend": self.backend,
            "kind": self.kind,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "sslmode": self.sslmode,
            "warnings": list(self.warnings),
        }


def _looks_like_placeholder(value: str) -> bool:
    v = value.strip()
    return (
        not v
        or any(ch in v for ch in "[]<>{}")
        or v.lower() in {"host", "hostname", "your-host", "pooler-host", "project-ref", "password", "your-password"}
        or "..." in v
        or v.lower().startswith("your")
    )


def parse_postgres_url(raw: str) -> DatabaseSettings:
    """Validate a PostgreSQL URL and normalise it for psycopg v3."""
    url = raw.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql+psycopg2://") or url.startswith("postgresql+asyncpg://") or url.startswith("postgresql+pg8000://"):
        raise ConfigError("Unsupported PostgreSQL driver in DATABASE_URL. This project uses psycopg v3: use 'postgresql://...' (it is converted automatically).")
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    if not url.startswith("postgresql+psycopg://"):
        raise ConfigError("DATABASE_URL must start with postgresql:// (or postgres://) for PostgreSQL.")

    # Detect the classic "unescaped @ in the password" mistake before parsing.
    after_scheme = url.split("://", 1)[1]
    authority = after_scheme.split("/", 1)[0]
    if authority.count("@") > 1:
        raise ConfigError("DATABASE_URL has more than one '@' in its authority section. URL-encode special characters in the password (for example '@' becomes '%40').")
    if re.search(r"\[(YOUR|PASSWORD|HOST|PROJECT|REGION)[^\]]*\]|<[^>]+>|\{[^}]+\}", authority, re.I):
        raise ConfigError("DATABASE_URL still contains a dashboard placeholder such as [YOUR-PASSWORD] or [YOUR-HOST]. Replace it with the real value "
                          "(URL-encode special characters in the password) and do not keep the square brackets.")
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
    except ValueError as exc:
        raise ConfigError("DATABASE_URL could not be parsed (check for stray square brackets or unencoded characters in the host or password).") from exc
    try:
        port = parts.port
    except ValueError as exc:
        raise ConfigError("DATABASE_URL has an invalid port.") from exc
    if _looks_like_placeholder(host):
        raise ConfigError("DATABASE_URL still contains a placeholder host. Copy the exact host from Supabase Dashboard > Connect; never invent a hostname.")
    if not (_HOST_RE.match(host) or host in LOCAL_HOSTS or ":" in host):
        raise ConfigError("DATABASE_URL host is not a valid hostname.")
    if port is not None and not (1 <= port <= 65535):
        raise ConfigError("DATABASE_URL port is out of range.")
    port = port or 5432
    database = parts.path.lstrip("/") or ""
    if not database:
        raise ConfigError("DATABASE_URL has no database name (normally '/postgres').")
    if not parts.username:
        raise ConfigError("DATABASE_URL has no username.")
    if parts.password is None or _looks_like_placeholder(unquote(parts.password)):
        raise ConfigError("DATABASE_URL has no password (or still has the placeholder). Set it locally in .env only.")

    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    warnings: list[str] = []
    is_local = host in LOCAL_HOSTS
    if "sslmode" not in query and not is_local:
        query["sslmode"] = "require"
    sslmode = query.get("sslmode", "")
    if sslmode in {"disable", "allow", "prefer"} and not is_local:
        warnings.append(f"sslmode={sslmode} does not guarantee TLS for a remote database.")

    username = unquote(parts.username)
    kind = "local" if is_local else "postgresql"
    if host.endswith(".pooler.supabase.com"):
        kind = "supabase-transaction-pooler" if port == 6543 else "supabase-session-pooler"
        if "." not in username:
            warnings.append("Supabase pooler usernames look like 'postgres.<project-ref>'; plain 'postgres' usually fails with 'Tenant or user not found'.")
    elif re.match(r"^db\.[a-z0-9]+\.supabase\.co$", host):
        kind = "supabase-direct"
        warnings.append("Supabase direct connections (db.<ref>.supabase.co) are IPv6-only on many plans; on IPv4-only networks use the Session Pooler URI from the dashboard.")
    elif host.endswith(".supabase.co") or host.endswith(".supabase.com"):
        kind = "supabase"

    connect_args: dict = {"connect_timeout": env_int("DB_CONNECT_TIMEOUT", 8), "application_name": "careflow"}
    if port == 6543:
        # PgBouncer transaction mode cannot reuse server-side prepared statements.
        connect_args["prepare_threshold"] = None
        warnings.append("Port 6543 is the transaction pooler: fine for the web app, but run migrations through the session pooler (5432) or direct connection.")

    netloc = parts.netloc
    new_url = urlunsplit((parts.scheme, netloc, parts.path, urlencode(query), ""))
    engine_options = {
        "pool_pre_ping": True,
        "pool_recycle": env_int("DB_POOL_RECYCLE", 270),
        "pool_size": env_int("DB_POOL_SIZE", 5),
        "max_overflow": env_int("DB_MAX_OVERFLOW", 5),
        "pool_timeout": env_int("DB_POOL_TIMEOUT", 10),
        "connect_args": connect_args,
    }
    return DatabaseSettings(
        uri=new_url, backend="postgresql", host=host, port=port, database=database,
        username_hint=username.split(".")[0] + ("…" if "." in username else ""),
        sslmode=sslmode, kind=kind, warnings=warnings, engine_options=engine_options,
    )


def sqlite_settings(path: str | os.PathLike) -> DatabaseSettings:
    p = str(path)
    uri = p if p.startswith("sqlite:") else "sqlite:///" + str(Path(p).resolve()).replace("\\", "/")
    return DatabaseSettings(
        uri=uri, backend="sqlite", host="", database=Path(p.replace("sqlite:///", "")).name, kind="local",
        engine_options={"connect_args": {"timeout": 15, "check_same_thread": False}},
    )


def resolve_database(environ=None, env_name: str = "development") -> DatabaseSettings:
    """Select the database. Never falls back from an explicit PostgreSQL request."""
    environ = os.environ if environ is None else environ
    raw = (environ.get("DATABASE_URL") or "").strip()
    backend_pref = (environ.get("DB_BACKEND") or "").strip().lower()
    if backend_pref not in {"", "sqlite", "postgres", "postgresql"}:
        raise ConfigError("DB_BACKEND must be 'sqlite' or 'postgres'.")
    wants_pg = backend_pref in {"postgres", "postgresql"}

    if not raw:
        if wants_pg:
            raise ConfigError("DB_BACKEND=postgres but DATABASE_URL is empty. Refusing to fall back to SQLite.")
        if env_name == "production":
            raise ConfigError("DATABASE_URL (PostgreSQL) is required when CAREFLOW_ENV=production.")
        return sqlite_settings(environ.get("SQLITE_PATH") or BASE_DIR / "hospital.db")

    if raw.startswith("sqlite"):
        if wants_pg or env_name == "production":
            raise ConfigError("A SQLite DATABASE_URL conflicts with PostgreSQL/production mode.")
        return sqlite_settings(raw)
    return parse_postgres_url(raw)


# --------------------------------------------------------------------------- #
# Application configuration
# --------------------------------------------------------------------------- #
def build_config(overrides: dict | None = None) -> dict:
    """Assemble the Flask config from the environment (plus explicit overrides)."""
    overrides = dict(overrides or {})
    testing = bool(overrides.get("TESTING"))
    if not testing:
        load_env()
    env_name = (overrides.get("CAREFLOW_ENV") or os.environ.get("CAREFLOW_ENV") or ("testing" if testing else "development")).lower()
    if env_name not in {"development", "testing", "production"}:
        raise ConfigError("CAREFLOW_ENV must be development, testing or production.")
    production = env_name == "production"

    if testing and "SQLALCHEMY_DATABASE_URI" in overrides:
        uri = overrides.pop("SQLALCHEMY_DATABASE_URI")
        engine_options = overrides.pop("SQLALCHEMY_ENGINE_OPTIONS", None)
        _assert_safe_test_database(uri)
        db_settings = sqlite_settings(uri) if uri.startswith("sqlite") else parse_postgres_url(uri)
        db_settings.uri = uri if uri.startswith("sqlite") else db_settings.uri
        if engine_options is not None:
            db_settings.engine_options = engine_options
    else:
        db_settings = resolve_database(env_name=env_name)

    secret = overrides.pop("SECRET_KEY", None) or os.environ.get("SECRET_KEY", "")
    if secret in INSECURE_DEFAULT_SECRETS:
        if production:
            raise ConfigError("SECRET_KEY must be set to a long random value when CAREFLOW_ENV=production.")
        secret = secrets.token_hex(32)  # per-process; sessions reset on restart
    if production and len(secret) < 32:
        raise ConfigError("SECRET_KEY must be at least 32 characters in production.")

    demo = env_bool("DEMO_MODE", False) if "DEMO_MODE" not in overrides else bool(overrides.pop("DEMO_MODE"))
    if production and demo:
        demo = False  # demonstration conveniences are never active in production

    cfg = {
        "CAREFLOW_ENV": env_name,
        "SECRET_KEY": secret,
        "DEMO_MODE": demo,
        "SQLALCHEMY_DATABASE_URI": db_settings.uri,
        "SQLALCHEMY_ENGINE_OPTIONS": db_settings.engine_options,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "DATABASE_SETTINGS": db_settings,
        # Sessions / cookies
        "SESSION_COOKIE_NAME": "careflow_session",
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": production or env_bool("SESSION_COOKIE_SECURE", False),
        "SESSION_IDLE_MINUTES": env_int("SESSION_IDLE_MINUTES", 30),
        "SESSION_ABSOLUTE_HOURS": env_int("SESSION_ABSOLUTE_HOURS", 12),
        "MAX_CONTENT_LENGTH": env_int("MAX_UPLOAD_MB", 15) * 1024 * 1024,
        # Login protection
        "LOGIN_MAX_FAILURES": env_int("LOGIN_MAX_FAILURES", 5),
        "LOGIN_LOCK_MINUTES": env_int("LOGIN_LOCK_MINUTES", 15),
        "RATE_LIMIT_ENABLED": env_bool("RATE_LIMIT_ENABLED", True),
        "API_RATE_PER_MINUTE": env_int("API_RATE_PER_MINUTE", 600),
        "LOGIN_RATE_PER_MINUTE": env_int("LOGIN_RATE_PER_MINUTE", 10),
        # Clinical operations (configurable, not clinical guidance)
        "CRITICAL_ACK_MINUTES": env_int("CRITICAL_ACK_MINUTES", 30),
        "ALERT_ESCALATE_MINUTES": env_int("ALERT_ESCALATE_MINUTES", 15),
        "OBS_EXPECTED_INTERVAL_MIN": env_int("OBS_EXPECTED_INTERVAL_MIN", 240),
        "APPOINTMENT_DAY_START": os.environ.get("APPOINTMENT_DAY_START", "08:00"),
        "APPOINTMENT_DAY_END": os.environ.get("APPOINTMENT_DAY_END", "20:00"),
        # Documents
        "STORAGE_BACKEND": (os.environ.get("STORAGE_BACKEND") or "local").lower(),
        "UPLOAD_DIR": os.environ.get("UPLOAD_DIR") or str(BASE_DIR / "instance" / "private_uploads"),
        "UPLOAD_MAX_PDF_PAGES": env_int("UPLOAD_MAX_PDF_PAGES", 60),
        "SUPABASE_URL": os.environ.get("SUPABASE_URL", "").rstrip("/"),
        "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""),  # server-side only
        "SUPABASE_BUCKET": os.environ.get("SUPABASE_BUCKET", "patient-documents"),
        "SIGNED_URL_SECONDS": env_int("SIGNED_URL_SECONDS", 60),
        "OCR_ENABLED": env_bool("OCR_ENABLED", True),
        "OCR_LANGUAGES": os.environ.get("OCR_LANGUAGES", "eng"),
        "TESSERACT_CMD": os.environ.get("TESSERACT_CMD", ""),
        # AI provider (keys stay on the server)
        "AI_PROVIDER": (os.environ.get("AI_PROVIDER") or "").lower(),
        "AI_MODEL": os.environ.get("AI_MODEL", ""),
        "AI_API_KEY": os.environ.get("AI_API_KEY", ""),
        "AI_BASE_URL": os.environ.get("AI_BASE_URL", ""),
        "AI_TIMEOUT_SECONDS": env_int("AI_TIMEOUT_SECONDS", 45),
        "AI_MAX_OUTPUT_TOKENS": env_int("AI_MAX_OUTPUT_TOKENS", 900),
        "AI_MAX_EVIDENCE_CHARS": env_int("AI_MAX_EVIDENCE_CHARS", 14000),
        "AI_ALLOW_EXTERNAL_PHI": env_bool("AI_ALLOW_EXTERNAL_PHI", False),
        "AI_VISION_ENABLED": env_bool("AI_VISION_ENABLED", False),
        "AI_RETENTION_DAYS": env_int("AI_RETENTION_DAYS", 30),
        "AI_RATE_PER_MINUTE": env_int("AI_RATE_PER_MINUTE", 20),
        # Monitoring
        "SIMULATOR_ENABLED": env_bool("SIMULATOR_ENABLED", demo),
    }
    cfg.update(overrides)
    return cfg


def _assert_safe_test_database(uri: str) -> None:
    """Tests call drop_all(); refuse anything that does not look disposable."""
    low = uri.lower()
    if low.startswith("sqlite"):
        if low.endswith("hospital.db") or "/hospital.db" in low:
            raise ConfigError("Refusing to run tests against hospital.db.")
        return
    name = urlsplit(uri.replace("postgresql+psycopg", "postgresql", 1)).path.lstrip("/").lower()
    host = (urlsplit(uri.replace("postgresql+psycopg", "postgresql", 1)).hostname or "").lower()
    if "test" not in name or host not in LOCAL_HOSTS:
        raise ConfigError("Test database must be a local PostgreSQL database whose name contains 'test'.")


# --------------------------------------------------------------------------- #
# Connectivity diagnostics (used by `flask db-doctor`)
# --------------------------------------------------------------------------- #
def diagnose_connectivity(settings: DatabaseSettings, ports_to_probe=(5432, 6543), timeout: float = 6.0) -> list[dict]:
    """Staged connectivity test that separates DNS, TCP, TLS, auth and schema problems.

    Returns a list of ``{"stage", "ok", "detail"}`` dicts. No secrets are included.
    """
    steps: list[dict] = []

    def add(stage, ok, detail):
        steps.append({"stage": stage, "ok": ok, "detail": detail})

    if settings.backend == "sqlite":
        add("config", True, f"SQLite file database '{settings.database}' (local development only).")
        return steps

    add("config", True, f"{settings.kind} host={settings.host} port={settings.port} db={settings.database} sslmode={settings.sslmode}")
    for w in settings.warnings:
        add("hint", True, w)

    # DNS
    try:
        infos = socket.getaddrinfo(settings.host, settings.port, proto=socket.IPPROTO_TCP)
        families = sorted({("IPv6" if i[0] == socket.AF_INET6 else "IPv4") for i in infos})
        add("dns", True, f"Resolved to {len(infos)} address(es) [{', '.join(families)}].")
        if families == ["IPv6"]:
            add("hint", True, "Host resolves to IPv6 only. IPv4-only networks cannot reach it; use the Supabase Session Pooler URI.")
    except socket.gaierror as exc:
        add("dns", False, f"DNS resolution failed ({exc.strerror or exc}). Check the exact hostname in Supabase Dashboard > Connect; do not guess it.")
        return steps

    # TCP on the configured port and on the common pooler ports
    probe = [settings.port] + [p for p in ports_to_probe if p != settings.port]
    reachable = {}
    for port in probe:
        t0 = time.monotonic()
        try:
            with socket.create_connection((settings.host, port), timeout=timeout):
                reachable[port] = True
                add("tcp", True, f"TCP {settings.host}:{port} reachable in {int((time.monotonic() - t0) * 1000)} ms.")
        except OSError as exc:
            reachable[port] = False
            add("tcp", False, f"TCP {settings.host}:{port} NOT reachable ({exc.__class__.__name__}: {getattr(exc, 'strerror', None) or exc}).")
    if not reachable.get(settings.port):
        if any(v for p, v in reachable.items() if p != settings.port):
            add("hint", True, "The configured port is blocked but another pooler port is reachable: switch the port in the dashboard URI (5432 session mode / 6543 transaction mode).")
        else:
            add("hint", True,
                "DNS works but no PostgreSQL port is reachable. This points to a network/firewall restriction (campus, hostel or corporate Wi-Fi often block outbound 5432/6543), "
                "not a password problem. Try another network or a mobile hotspot, or run the app on a server host whose egress allows PostgreSQL. "
                "Do not change the password in response to this error.")
        return steps

    # TLS + authentication through the real driver
    try:
        import psycopg
        dsn = settings.uri.replace("postgresql+psycopg://", "postgresql://", 1)
        t0 = time.monotonic()
        with psycopg.connect(dsn, connect_timeout=int(timeout), application_name="careflow-doctor") as conn:
            add("tls+auth", True, f"Authenticated in {int((time.monotonic() - t0) * 1000)} ms (sslmode={settings.sslmode or 'default'}).")
            cur = conn.execute("select current_database(), current_user")
            dbn, usr = cur.fetchone()
            add("session", True, f"database={dbn} role={usr.split('.')[0]}")
            tables = [r[0] for r in conn.execute("select table_name from information_schema.tables where table_schema='public' order by 1").fetchall()]
            if not tables:
                add("schema", False, "Connected, but the public schema is empty. Run: flask --app app db upgrade")
            else:
                add("schema", True, f"{len(tables)} public tables present: {', '.join(tables[:12])}{' …' if len(tables) > 12 else ''}")
                add("migrations", "alembic_version" in tables, "alembic_version present." if "alembic_version" in tables else "alembic_version missing: run `flask --app app db upgrade`.")
    except Exception as exc:  # classify without leaking the DSN
        msg = str(exc).split("\n")[0]
        msg = re.sub(r"(password|user)=[^\s]+", r"\1=***", msg, flags=re.I)
        low = msg.lower()
        if "tenant or user not found" in low:
            hint = "Pooler rejected the username: use 'postgres.<project-ref>' exactly as shown in the dashboard."
        elif "password authentication failed" in low or "authentication failed" in low:
            hint = "Server reachable but credentials rejected: reset the database password in Supabase and update .env locally."
        elif "ssl" in low or "tls" in low or "certificate" in low:
            hint = "TLS negotiation problem: keep sslmode=require (or verify-full with the Supabase CA certificate)."
        elif "timeout" in low or "timed out" in low:
            hint = "Connection attempt timed out after TCP succeeded: check pooler mode/port pairing."
        elif "permission denied" in low:
            hint = "The database role lacks privileges on the target schema."
        else:
            hint = "See message."
        add("tls+auth", False, f"{exc.__class__.__name__}: {msg[:220]} -- {hint}")
    return steps
