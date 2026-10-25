"""Test fixtures. Tests NEVER read .env and NEVER touch a configured database.

Database: set TEST_DATABASE_URL to a *local* PostgreSQL database whose name contains "test"
(recommended - the same engine as production). Without it, a throw-away SQLite file is used.
"""
import os
import tempfile

import pytest
from sqlalchemy import text

os.environ["DEMO_PASSWORD"] = "CareFlow-Test-Pass-2026!"
for k in list(os.environ):  # make sure the developer's real settings can never leak into tests
    if k.startswith(("AI_", "SUPABASE_")) or k in ("DATABASE_URL", "SECRET_KEY"):
        os.environ.pop(k)

from careflow import create_app, seed  # noqa: E402
from careflow.extensions import db  # noqa: E402
from careflow.security import limiter  # noqa: E402

DEMO_PW = os.environ["DEMO_PASSWORD"]
DOMAIN = seed.DOMAIN


def _uri():
    url = os.environ.get("TEST_DATABASE_URL")
    if url:
        return url
    return "sqlite:///" + os.path.join(tempfile.gettempdir(), "careflow_pytest.sqlite3")


def make_app(**over):
    cfg = {"TESTING": True, "SQLALCHEMY_DATABASE_URI": _uri(), "SECRET_KEY": "t" * 48, "DEMO_MODE": True, "RATE_LIMIT_ENABLED": False,
           "UPLOAD_DIR": os.path.join(tempfile.gettempdir(), "careflow_pytest_uploads"), "OCR_ENABLED": False}
    cfg.update(over)
    return create_app(cfg)


def _drop_all():
    """SQLite enforces FKs while dropping; app_user <-> patient is circular, so suspend enforcement for the drop."""
    if db.engine.dialect.name == "sqlite":
        with db.engine.connect() as c:
            c.exec_driver_sql("PRAGMA foreign_keys=OFF")
            db.metadata.drop_all(c)
            c.commit()
    else:
        db.drop_all()


@pytest.fixture(scope="session")
def _schema_app():
    app = make_app()
    with app.app_context():
        _drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        _drop_all()


def reset_db():
    db.session.remove()
    tables = [t.name for t in db.metadata.sorted_tables]
    if db.engine.dialect.name == "postgresql":
        db.session.execute(text("TRUNCATE " + ", ".join(f'"{t}"' for t in tables) + " RESTART IDENTITY CASCADE"))
    else:
        # app_user <-> patient reference each other, so no delete order satisfies every FK: suspend them while clearing
        db.session.execute(text("PRAGMA foreign_keys=OFF"))
        for t in reversed(db.metadata.sorted_tables):
            db.session.execute(t.delete())
        db.session.commit()
        db.session.execute(text("PRAGMA foreign_keys=ON"))
    db.session.commit()


@pytest.fixture()
def app(_schema_app):
    with _schema_app.app_context():
        reset_db()
        limiter.reset()
        seed.run()
        _schema_app.config.update(DEMO_MODE=True, RATE_LIMIT_ENABLED=False, AI_PROVIDER="", AI_MODEL="", AI_API_KEY="", AI_BASE_URL="", AI_ALLOW_EXTERNAL_PHI=False)
        yield _schema_app
        db.session.remove()


class Api:
    def __init__(self, app):
        self.c = app.test_client()
        self.csrf = ""
        self.refresh()

    def refresh(self):
        self.csrf = self.c.get("/api/auth/csrf").json["csrf"]

    def _h(self):
        return {"X-CSRF-Token": self.csrf}

    def login(self, who, password=None):
        r = self.c.post("/api/auth/login", json={"email": who if "@" in who else f"{who}@{DOMAIN}", "password": password or DEMO_PW}, headers=self._h())
        if r.status_code == 200:
            self.csrf = r.json["csrf"]
        return r

    def get(self, url, **kw):
        return self.c.get(url, **kw)

    def post(self, url, json=None, **kw):
        if "data" in kw:   # multipart upload
            return self.c.post(url, headers=self._h(), **kw)
        return self.c.post(url, json=json if json is not None else {}, headers=self._h(), **kw)

    def put(self, url, json=None, **kw):
        return self.c.put(url, json=json or {}, headers=self._h(), **kw)

    def patch(self, url, json=None, **kw):
        return self.c.patch(url, json=json or {}, headers=self._h(), **kw)

    def delete(self, url, **kw):
        return self.c.delete(url, headers=self._h(), **kw)


@pytest.fixture()
def as_user(app):
    def make(who):
        a = Api(app)
        r = a.login(who)
        assert r.status_code == 200, r.get_json()
        return a
    return make


@pytest.fixture()
def anon(app):
    return Api(app)


@pytest.fixture()
def ids(app):
    """Primary keys of the seeded demo world, looked up by role/name."""
    from careflow.models import AppUser, Patient, Bed
    from sqlalchemy import select
    u = {x.email.split("@")[0]: x.id for x in db.session.execute(select(AppUser)).scalars()}
    p = {x.name.split(" (")[0]: x.id for x in db.session.execute(select(Patient)).scalars()}
    return type("Ids", (), {"user": u, "patient": p})
