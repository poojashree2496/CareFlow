"""Database configuration, safe diagnostics and health checks. No network access is required."""
import socket

import pytest

from careflow import config as cfg
from careflow.config import ConfigError, diagnose_connectivity, parse_postgres_url, redact_url, resolve_database

GOOD = "postgresql://postgres.abcdefghij:S3cret-pw@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"


def test_url_is_normalised_for_psycopg3_and_tls_is_required():
    s = parse_postgres_url(GOOD)
    assert s.uri.startswith("postgresql+psycopg://") and "sslmode=require" in s.uri
    assert (s.kind, s.port, s.database) == ("supabase-session-pooler", 5432, "postgres")
    assert parse_postgres_url(GOOD.replace("postgresql://", "postgres://")).backend == "postgresql"


def test_transaction_pooler_disables_prepared_statements_and_warns():
    s = parse_postgres_url(GOOD.replace(":5432", ":6543"))
    assert s.kind == "supabase-transaction-pooler"
    assert s.engine_options["connect_args"]["prepare_threshold"] is None
    assert any("migrations" in w for w in s.warnings)


@pytest.mark.parametrize("url,fragment", [
    ("postgresql://postgres:pw@[YOUR-HOST]:5432/postgres", "placeholder"),
    ("postgresql://postgres:pw@host:5432/postgres", "placeholder"),
    ("postgresql://postgres:[YOUR-PASSWORD]@db.abcdefgh.supabase.co:5432/postgres", "placeholder"),
    ("postgresql://postgres@db.abcdefgh.supabase.co:5432/postgres", "password"),
    ("postgresql://postgres:p@ss@db.abcdefgh.supabase.co:5432/postgres", "URL-encode"),
    ("postgresql://postgres:pw@db.abcdefgh.supabase.co:5432", "database name"),
    ("postgresql+psycopg2://postgres:pw@db.abcdefgh.supabase.co/postgres", "psycopg v3"),
    ("mysql://u:p@h.example/db", "must start with postgresql"),
])
def test_bad_urls_are_rejected_with_actionable_messages(url, fragment):
    with pytest.raises(ConfigError, match=fragment):
        parse_postgres_url(url)


def test_pooler_username_hint_and_direct_ipv6_hint():
    s = parse_postgres_url("postgresql://postgres:pw12345678@aws-0-eu-west-1.pooler.supabase.com:5432/postgres")
    assert any("postgres.<project-ref>" in w for w in s.warnings)
    d = parse_postgres_url("postgresql://postgres:pw12345678@db.abcdefghij.supabase.co:5432/postgres")
    assert d.kind == "supabase-direct" and any("IPv6" in w for w in d.warnings)


def test_redact_and_describe_never_expose_the_password():
    s = parse_postgres_url(GOOD)
    assert "S3cret-pw" not in redact_url(GOOD)
    assert "S3cret-pw" not in str(s.describe())


def test_no_silent_sqlite_fallback_when_postgres_is_requested():
    with pytest.raises(ConfigError, match="Refusing to fall back"):
        resolve_database({"DB_BACKEND": "postgres"})
    with pytest.raises(ConfigError, match="required"):
        resolve_database({}, env_name="production")
    with pytest.raises(ConfigError, match="conflicts"):
        resolve_database({"DATABASE_URL": "sqlite:///x.db"}, env_name="production")
    with pytest.raises(ConfigError, match="DB_BACKEND"):
        resolve_database({"DB_BACKEND": "mongo"})
    assert resolve_database({}).backend == "sqlite"                       # explicit development default
    assert resolve_database({"DATABASE_URL": GOOD}).backend == "postgresql"


def test_a_broken_postgres_url_raises_instead_of_using_sqlite():
    with pytest.raises(ConfigError):
        resolve_database({"DATABASE_URL": "postgresql://postgres:pw@[YOUR-HOST]/postgres"})


def test_dns_failure_is_reported_as_dns_and_stops(monkeypatch):
    def boom(*a, **k):
        raise socket.gaierror(-2, "Name or service not known")
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    steps = diagnose_connectivity(parse_postgres_url(GOOD))
    stages = [s["stage"] for s in steps]
    assert "dns" in stages and stages[-1] == "dns" and steps[-1]["ok"] is False
    assert "do not guess" in steps[-1]["detail"]
    assert "S3cret-pw" not in str(steps)


def test_dns_ok_but_tcp_blocked_is_classified_as_network_not_password(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.9", 5432))])

    def refuse(*a, **k):
        raise TimeoutError("timed out")
    monkeypatch.setattr(socket, "create_connection", refuse)
    steps = diagnose_connectivity(parse_postgres_url(GOOD), timeout=0.1)
    assert [s["ok"] for s in steps if s["stage"] == "dns"] == [True]
    assert all(s["ok"] is False for s in steps if s["stage"] == "tcp")
    hint = " ".join(s["detail"] for s in steps if s["stage"] == "hint")
    assert "network/firewall" in hint and "Do not change the password" in hint
    assert not any(s["stage"] in ("tls+auth", "schema") for s in steps)      # never reaches auth, so it never claims a credentials problem


def test_other_port_reachable_suggests_switching_pooler_mode(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.9", 5432))])

    class Ok:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def conn(addr, timeout=None):
        if addr[1] == 6543:
            return Ok()
        raise OSError("blocked")
    monkeypatch.setattr(socket, "create_connection", conn)
    steps = diagnose_connectivity(parse_postgres_url(GOOD), timeout=0.1)
    assert any("switch the port" in s["detail"] for s in steps if s["stage"] == "hint")


def test_sqlite_diagnosis_says_local_only():
    steps = diagnose_connectivity(cfg.sqlite_settings("x.db"))
    assert "local development only" in steps[0]["detail"]


def test_production_refuses_weak_secret_and_demo_mode(monkeypatch):
    monkeypatch.setattr(cfg, "load_env", lambda *a, **k: False)
    monkeypatch.setenv("CAREFLOW_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", GOOD)
    monkeypatch.setenv("SECRET_KEY", "changeme")
    monkeypatch.delenv("TESTING", raising=False)
    with pytest.raises(ConfigError):
        cfg.build_config({})


def test_health_reports_503_when_database_is_down(app, monkeypatch):
    c = app.test_client()
    assert c.get("/health").status_code == 200
    from careflow.extensions import db

    def broken(*a, **k):
        raise RuntimeError("connection refused")
    monkeypatch.setattr(db.session, "execute", broken)
    r = c.get("/health")
    assert r.status_code == 503 and r.json["database"] == "unavailable"
    assert "refused" not in r.get_data(as_text=True)                          # no internals leaked
    assert c.get("/health/live").status_code == 200                           # liveness does not depend on the DB
