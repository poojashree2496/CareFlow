"""CareFlow - connected hospital information platform (Flask application factory)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request
from sqlalchemy import event, text
from sqlalchemy.engine import Engine

from .config import BASE_DIR, ConfigError, build_config
from .extensions import db, migrate

__version__ = "2.0.0"


@event.listens_for(Engine, "connect")
def _sqlite_pragmas(dbapi_conn, _record):  # pragma: no cover - trivial
    if dbapi_conn.__class__.__module__.startswith("sqlite3"):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA busy_timeout=15000")
        try:
            cur.execute("PRAGMA journal_mode=WAL")
        except Exception:
            pass
        cur.close()


def create_app(config_overrides: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(BASE_DIR / "static"), template_folder=str(BASE_DIR / "templates"))
    app.config.update(build_config(config_overrides))
    app.config["JSON_SORT_KEYS"] = False
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    # SQLAlchemy echo would print SQL with bound parameters (PHI); keep it off.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    db.init_app(app)
    migrate.init_app(app, db, directory=str(BASE_DIR / "migrations"), compare_type=True, render_as_batch=True)

    from . import models  # noqa: F401  (register tables)
    from .security import init_security
    init_security(app)

    from .api import register_blueprints
    register_blueprints(app)

    from .cli import register_cli
    register_cli(app)

    _register_pages(app)
    _announce(app)
    return app


def _announce(app: Flask):
    s = app.config["DATABASE_SETTINGS"]
    app.logger.info("CareFlow %s env=%s db=%s(%s) demo=%s", __version__, app.config["CAREFLOW_ENV"], s.backend, s.kind, app.config["DEMO_MODE"])
    for w in s.warnings:
        app.logger.warning("database: %s", w)


def schema_status(app: Flask) -> dict:
    """Compare the database's alembic revision with the migration scripts."""
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        cfg = Config()
        cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
        head = ScriptDirectory.from_config(cfg).get_current_head()
        row = db.session.execute(text("select version_num from alembic_version")).first()
        current = row[0] if row else None
        return {"current": current, "head": head, "state": "current" if current == head else "behind"}
    except Exception:
        db.session.rollback()
        return {"current": None, "head": None, "state": "unknown"}


def _register_pages(app: Flask):
    from flask import g

    from .security import csrf_token

    @app.route("/health/live")
    def health_live():
        return jsonify(status="ok", application="CareFlow", version=__version__)

    @app.route("/health")
    def health():
        s = app.config["DATABASE_SETTINGS"]
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok", application="CareFlow", version=__version__, database="connected", backend=s.backend), 200
        except Exception as exc:
            db.session.rollback()
            app.logger.error("Database health check failed: %s", exc.__class__.__name__)
            return jsonify(status="error", application="CareFlow", database="unavailable", backend=s.backend), 503

    @app.route("/login")
    def login_page():
        if getattr(g, "user", None):
            return redirect("/")
        return render_template("login.html", csrf=csrf_token(), demo=app.config["DEMO_MODE"], env=app.config["CAREFLOW_ENV"])

    @app.route("/")
    def index():
        if getattr(g, "user", None) is None:
            return redirect("/login")
        return render_template("index.html", csrf=csrf_token(), demo=app.config["DEMO_MODE"], env=app.config["CAREFLOW_ENV"])
