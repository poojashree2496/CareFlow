"""WSGI entry point.  Run:  flask --app app run   |   gunicorn app:app
CareFlow 2.x replaces the single-file prototype (kept for reference in legacy/app_v1.py)."""
import os

# Local demo convenience: with the default local SQLite database in a development environment, demonstration mode
# (demo accounts listed on the sign-in page) is on unless you configure otherwise. Anything that sets DATABASE_URL
# or CAREFLOW_ENV=production (real use) is never affected, and values you set yourself always win.
if not os.environ.get("DATABASE_URL") and os.environ.get("CAREFLOW_ENV", "development") == "development":
    os.environ.setdefault("DEMO_MODE", "1")
    os.environ.setdefault("DEMO_PASSWORD", "CareFlow-Demo-2026!")

from careflow import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["CAREFLOW_ENV"] == "development")
