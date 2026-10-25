"""Alembic migrations: fresh install, upgrade of the original prototype's database, and data safety."""
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import upgrade

from careflow import create_app
from careflow.extensions import db

LEGACY_SQL = (Path(__file__).parent / "legacy_schema.sql").read_text()


def app_for(path):
    return create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{path}", "SECRET_KEY": "t" * 48, "RATE_LIMIT_ENABLED": False})


def run_upgrade(app):
    with app.app_context():
        upgrade(directory=str(Path(app.root_path).parent / "migrations"))


@pytest.fixture()
def tmpdb():
    d = tempfile.mkdtemp(prefix="cf_mig_")
    yield os.path.join(d, "migration_test.sqlite3")
    shutil.rmtree(d, ignore_errors=True)


def make_legacy(path, admissions=(), appointments=()):
    c = sqlite3.connect(path)
    c.executescript(LEGACY_SQL)
    c.execute("insert into patient(id,patient_code,name,dob,created_at) values (1,'P-260101-AAAA','Legacy One','1980-01-02','2026-01-01 08:00:00.000000')")
    c.execute("insert into patient(id,patient_code,name,created_at) values (2,'P-260101-BBBB','Legacy Two',NULL)")
    c.execute("insert into doctor(id,name,specialty) values (1,'Dr Old','General')")
    c.execute("insert into medicine(id,name,stock) values (1,'Aspirin',5)")
    c.execute("insert into lab_report(patient_id,test_name,sample_date,result,status) values (1,'CBC','2026-01-02','Hb 12','Completed')")
    c.execute("insert into radiology_record(patient_id,modality,study_date,findings,report_status) values (1,'X-ray','2026-01-03','clear','Final')")
    c.execute("insert into prescription(patient_id,medicine,created_at) values (1,'Paracetamol','2026-01-04 09:00:00.000000')")
    c.execute("insert into audit_log(action,details,created_at) values ('Patient registered','x','2026-01-01 08:00:00.000000')")
    for a in admissions:
        c.execute("insert into admission(patient_id,ward,bed,admitted_on,discharged_on,status) values (?,?,?,?,?,?)", a)
    for a in appointments:
        c.execute("insert into appointment(patient_id,doctor_id,appointment_date,appointment_time,status) values (?,?,?,?,?)", a)
    c.commit()
    c.close()


def test_fresh_install_schema_matches_models(tmpdb):
    app = app_for(tmpdb)
    run_upgrade(app)
    with app.app_context():
        with db.engine.connect() as conn:
            diff = compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), db.metadata)
        assert diff == []
        assert sa.inspect(db.engine).has_table("alembic_version")


def test_legacy_database_upgrades_without_losing_data(tmpdb):
    make_legacy(tmpdb, admissions=[(1, "Ward A", "A1", "2026-01-05", "", "Admitted"), (2, "Ward B", "B2", "2026-01-01", "2026-01-04", "Discharged")])
    before = sqlite3.connect(tmpdb).execute("select count(*) from patient").fetchone()[0]
    run_upgrade(app_for(tmpdb))
    c = sqlite3.connect(tmpdb)
    assert c.execute("select count(*) from patient").fetchone()[0] == before == 2
    assert c.execute("select name, data_origin, consent_data_sharing from patient where id=1").fetchone() == ("Legacy One", "imported", 0)
    assert c.execute("select created_at is not null from patient where id=2").fetchone()[0] == 1       # NULL created_at repaired
    assert c.execute("select discharge_status from admission where patient_id=2").fetchone()[0] == "Completed"
    assert c.execute("select discharge_status from admission where patient_id=1").fetchone()[0] == "None"
    assert c.execute("select admitted_at from admission where patient_id=1").fetchone()[0].startswith("2026-01-05")
    assert c.execute("select order_status from radiology_record").fetchone()[0] == "Final"
    assert c.execute("select status, dispensed_quantity from prescription").fetchone() == ("Ordered", 0)
    assert c.execute("select status from lab_report").fetchone()[0] == "Completed"                     # legacy vocabulary kept
    assert c.execute("select category from audit_log").fetchone()[0] == "system"


def test_upgraded_legacy_data_is_usable_through_the_app(tmpdb):
    make_legacy(tmpdb, admissions=[(1, "Ward A", "A1", "2026-01-05", "", "Admitted")])
    app = app_for(tmpdb)
    run_upgrade(app)
    from conftest import Api, DEMO_PW
    from careflow import seed
    with app.app_context():
        from careflow.services import monitoring
        monitoring.ensure_reference_data()
        from careflow.models import AppUser
        from careflow.security import hash_password
        db.session.add(AppUser(email="a@example.org", name="Admin Person", role="hospital_admin", password_hash=hash_password("Long-Admin-Pass-2026"), must_change_password=False))
        db.session.commit()
    app.config["DEMO_MODE"] = False
    a = Api(app)
    assert a.login("a@example.org", "Long-Admin-Pass-2026").status_code == 200
    items = a.get("/api/patients").json["items"]
    assert {p["name"] for p in items} == {"Legacy One", "Legacy Two"}
    board = a.get("/api/bedboard").json
    assert [w["admission_id"] for w in board["awaiting_bed"]] == [1]        # legacy admission without a bed record is surfaced, not lost
    # legacy 'Completed' lab is still readable and is treated as released by the workflow rules
    with app.app_context():
        from careflow.models import LabReport
        from careflow.services.orders import lab_transition
        lr = db.session.get(LabReport, 1)
        assert lr.status == "Completed"
        with pytest.raises(Exception, match="cannot move from Released"):
            lab_transition(lr, "Ordered")


def test_patient_portal_migration_on_legacy_database(tmpdb):
    """0003 is additive: existing rows survive, the patient role becomes valid, and the new tables/columns exist."""
    make_legacy(tmpdb)
    run_upgrade(app_for(tmpdb))
    c = sqlite3.connect(tmpdb)
    cols = {r[1] for r in c.execute("pragma table_info(app_user)")}
    assert "patient_id" in cols
    assert c.execute("select count(*) from patient_deliverable").fetchone()[0] == 2   # released legacy lab + radiology report are tracked
    assert c.execute("select count(*) from lab_report").fetchone()[0] == 1
    assert "patient_visible" in {r[1] for r in c.execute("pragma table_info(medical_document)")}


def test_upgrade_refuses_when_existing_data_violates_new_rules(tmpdb, capsys):
    make_legacy(tmpdb, admissions=[(1, "Ward A", "A1", "2026-01-05", "", "Admitted"), (1, "Ward B", "B1", "2026-01-06", "", "Admitted")])
    with pytest.raises(SystemExit):
        run_upgrade(app_for(tmpdb))
    assert "more than one active admission" in capsys.readouterr().err
    c = sqlite3.connect(tmpdb)
    assert c.execute("select count(*) from patient").fetchone()[0] == 2                              # nothing was altered or deleted
    assert c.execute("select count(*) from admission").fetchone()[0] == 2
    assert "data_origin" not in [r[1] for r in c.execute("pragma table_info(patient)")]


def test_duplicate_live_appointments_block_upgrade(tmpdb, capsys):
    make_legacy(tmpdb, appointments=[(1, 1, "2026-02-01", "10:00", "Scheduled"), (2, 1, "2026-02-01", "10:00", "Scheduled")])
    with pytest.raises(SystemExit):
        run_upgrade(app_for(tmpdb))
    assert "booked more than once" in capsys.readouterr().err


def test_downgrade_is_refused(tmpdb, capsys):
    from flask_migrate import downgrade
    app = app_for(tmpdb)
    run_upgrade(app)
    with app.app_context():
        with pytest.raises(SystemExit):
            downgrade(directory=str(Path(app.root_path).parent / "migrations"), revision="0001")
    assert "not supported" in capsys.readouterr().err


@pytest.mark.skipif(not os.environ.get("TEST_MIGRATION_DATABASE_URL"), reason="set TEST_MIGRATION_DATABASE_URL to an empty local PostgreSQL test database")
def test_postgres_fresh_upgrade_matches_models():
    url = os.environ["TEST_MIGRATION_DATABASE_URL"]
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": url, "SECRET_KEY": "t" * 48})
    with app.app_context():
        db.session.execute(sa.text("DROP SCHEMA public CASCADE")); db.session.execute(sa.text("CREATE SCHEMA public")); db.session.commit()
    run_upgrade(app)
    with app.app_context():
        with db.engine.connect() as conn:
            assert compare_metadata(MigrationContext.configure(conn, opts={"compare_type": True}), db.metadata) == []
        # the partial unique indexes that prevent double-booking / double-admission exist in PostgreSQL
        idx = {r[0] for r in db.session.execute(sa.text("select indexname from pg_indexes where schemaname='public'"))}
        assert {"uq_admission_active_patient", "uq_appointment_doctor_slot_active", "uq_alert_open_patient_rule"} <= idx
