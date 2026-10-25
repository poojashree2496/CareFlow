"""Operational commands: flask --app app <command>."""
from __future__ import annotations

import getpass
import os
import sys

import click
from flask import current_app
from sqlalchemy import select, text


def register_cli(app):
    @app.cli.command("db-doctor")
    @click.option("--timeout", default=6.0, show_default=True)
    def db_doctor(timeout):
        """Staged database diagnostics: config, DNS, TCP, TLS/auth, schema. Never prints credentials."""
        from .config import diagnose_connectivity
        steps = diagnose_connectivity(current_app.config["DATABASE_SETTINGS"], timeout=timeout)
        for st in steps:
            click.echo(f"[{'OK ' if st['ok'] else 'FAIL'}] {st['stage']:<10} {st['detail']}")
        sys.exit(0 if all(s["ok"] for s in steps) else 1)

    @app.cli.command("check-config")
    def check_config():
        """Show the effective (non-secret) configuration."""
        c = current_app.config
        ds = c["DATABASE_SETTINGS"]
        for k, v in (("environment", c["CAREFLOW_ENV"]), ("database", f"{ds.backend} ({ds.kind}) host={ds.host or '-'} db={ds.database}"), ("demo_mode", c["DEMO_MODE"]),
                     ("storage", c.get("STORAGE_BACKEND")), ("ai_provider", c["AI_PROVIDER"] or "(not configured)"), ("ai_external_phi_allowed", c["AI_ALLOW_EXTERNAL_PHI"]),
                     ("rate_limiting", c["RATE_LIMIT_ENABLED"]), ("secure_cookies", bool(c.get("SESSION_COOKIE_SECURE")))):
            click.echo(f"{k:<24} {v}")
        for w in ds.warnings:
            click.echo(f"warning: {w}")

    @app.cli.command("init-reference-data")
    def init_reference():
        """Load observation types (idempotent)."""
        from .services import monitoring
        monitoring.ensure_reference_data()
        from .extensions import db
        db.session.commit()
        click.echo("Reference data ready.")

    @app.cli.command("seed-demo")
    @click.option("--force", is_flag=True, help="Allow seeding when the database already contains patients.")
    def seed_demo(force):
        """Load fictional demonstration data (requires DEMO_MODE=1 and a non-production environment)."""
        from . import seed
        from .extensions import db
        from .models import Patient
        if current_app.config["CAREFLOW_ENV"] == "production":
            raise click.ClickException("Refusing to load demonstration data in production.")
        if not current_app.config["DEMO_MODE"]:
            raise click.ClickException("Set DEMO_MODE=1 to load demonstration data.")
        if seed.seeded():
            raise click.ClickException("Demonstration data is already present.")
        if db.session.execute(select(Patient.id).limit(1)).first() and not force:
            raise click.ClickException("The database already has patients. Use --force only if you accept mixing demo data with them.")
        click.echo("Seeded: " + str(seed.run()))
        click.echo(f"Demo accounts use e-mails like doctor1@{seed.DOMAIN}. The shared demo password is shown on the sign-in page in demo mode only.")

    @app.cli.command("add-sample-patients")
    def add_sample_patients():
        """Add a large set of extra sample patients (incl. Pooja Shree), staff, wards and records. Safe to run twice."""
        from . import seed, seed_more
        if current_app.config["CAREFLOW_ENV"] == "production":
            raise click.ClickException("Refusing to load sample data in production.")
        if not seed.seeded():
            raise click.ClickException("Run `python -m flask --app app seed-demo` first.")
        if seed_more.already_added():
            click.echo("Sample patients are already present; nothing to do.")
            return
        res = seed_more.run()
        click.echo(f"Added {res['patients']} patients.")
        for email, name in res["portal_logins"]:
            click.echo(f"  Patient login: {email}  ({name})")
        click.echo("Other new logins: doctor3..doctor7, nurse2..nurse4 (same domain). Password is the shared sign-in password.")

    @app.cli.command("add-bulk-patients")
    @click.option("--count", default=150, show_default=True, type=click.IntRange(1, 2000), help="How many new patients to create.")
    def add_bulk_patients(count):
        """Add many varied sample patients with matching records. Run it again to add more."""
        from . import seed, seed_bulk
        if current_app.config["CAREFLOW_ENV"] == "production":
            raise click.ClickException("Refusing to load sample data in production.")
        if not seed.seeded():
            raise click.ClickException("Run `python -m flask --app app seed-demo` first.")
        res = seed_bulk.run(count)
        click.echo("Added: " + ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in res.items()))

    @app.cli.command("add-sample-staff")
    @click.option("--patient-logins", default=30, show_default=True, type=click.IntRange(0, 500), help="How many patients get a portal login.")
    def add_sample_staff(patient_logins):
        """Add more sample accounts for every role (admins, doctors, nurses, lab, pharmacy, radiology, billing, patients)."""
        from . import seed, seed_staff
        if current_app.config["CAREFLOW_ENV"] == "production":
            raise click.ClickException("Refusing to load sample data in production.")
        if not seed.seeded():
            raise click.ClickException("Run `python -m flask --app app seed-demo` first.")
        res = seed_staff.run(patient_logins)
        click.echo(f"Added {len(res['accounts'])} accounts:")
        for role, email, name in res["accounts"]:
            click.echo(f"  {role:15} {email:45} {name}")

    @app.cli.command("reset-demo-passwords")
    def reset_demo_passwords():
        """Set every demonstration account's password to the current DEMO_PASSWORD (demo mode only)."""
        from . import seed
        from .extensions import db
        from .models import AppUser
        from .security import hash_password
        if current_app.config["CAREFLOW_ENV"] == "production" or not current_app.config["DEMO_MODE"]:
            raise click.ClickException("Only available with DEMO_MODE=1 outside production.")
        h = hash_password(seed.demo_password())
        n = 0
        for u in db.session.execute(select(AppUser).where(AppUser.is_demo.is_(True))).scalars():
            u.password_hash, u.must_change_password, u.failed_logins, u.locked_until = h, False, 0, None
            n += 1
        db.session.commit()
        click.echo(f"Reset {n} demo account(s) to the current DEMO_PASSWORD.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True)
    @click.option("--role", type=click.Choice(["super_admin", "hospital_admin"]), default="super_admin", show_default=True)
    def create_admin(email, name, role):
        """Create an administrator. The password is read from CAREFLOW_ADMIN_PASSWORD or prompted (never echoed)."""
        from .extensions import db
        from .models import AppUser, utcnow
        from .security import hash_password, validate_password_strength
        email = email.strip().lower()
        pw = os.environ.get("CAREFLOW_ADMIN_PASSWORD") or getpass.getpass("Password (min 12 chars): ")
        validate_password_strength(pw, email=email, name=name)
        if db.session.execute(select(AppUser.id).where(AppUser.email == email)).first():
            raise click.ClickException("An account with this e-mail already exists.")
        db.session.add(AppUser(email=email, name=name, role=role, password_hash=hash_password(pw), must_change_password=False, password_changed_at=utcnow()))
        from .audit import audit
        audit("user.created", category="admin", details=f"role={role} via cli")
        db.session.commit()
        click.echo(f"Created {role} account for {email}.")

    @app.cli.command("monitor-sweep")
    def monitor_sweep():
        """Run missing-data alerts and escalations (schedule this with cron / Task Scheduler)."""
        from .services import monitoring
        click.echo(monitoring.run_sweeps(force=True))

    @app.cli.command("purge-ai")
    def purge_ai():
        """Delete AI conversations older than AI_RETENTION_DAYS."""
        from datetime import timedelta
        from .extensions import db
        from .models import AiConversation, utcnow
        cutoff = utcnow() - timedelta(days=current_app.config["AI_RETENTION_DAYS"])
        old = db.session.execute(select(AiConversation).where(AiConversation.updated_at < cutoff)).scalars().all()
        for c in old:
            db.session.delete(c)
        db.session.commit()
        click.echo(f"Removed {len(old)} conversation(s).")

    @app.cli.command("db-status")
    def db_status():
        """Compare the database revision with the migration scripts."""
        from . import schema_status
        click.echo(schema_status(current_app))
