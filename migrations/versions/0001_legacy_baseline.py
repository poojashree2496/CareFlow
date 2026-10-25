"""legacy baseline: the schema of the original single-file prototype

Revision ID: 0001
Revises:
Create Date: 2026-10-24

This revision recreates the ten tables of the original prototype exactly as it created them.
It is idempotent: a table that already exists (an existing prototype database, or one created
by the old app's ``db.create_all()``) is left untouched, so existing data is preserved.
Existing databases without an ``alembic_version`` table can simply run ``flask db upgrade``.
"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _missing(name):
    return not sa.inspect(op.get_bind()).has_table(name)


def upgrade():
    if _missing("patient"):
        op.create_table(
            "patient",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("patient_code", sa.String(20), nullable=False),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("dob", sa.String(10)), sa.Column("gender", sa.String(30)), sa.Column("phone", sa.String(30)), sa.Column("email", sa.String(120)),
            sa.Column("blood_group", sa.String(5)), sa.Column("allergies", sa.Text()), sa.Column("emergency_contact", sa.String(120)),
            sa.Column("medical_history", sa.Text()), sa.Column("created_at", sa.DateTime()),
            sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("patient_code", name="uq_patient_patient_code"),
        )
    if _missing("doctor"):
        op.create_table(
            "doctor",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("specialty", sa.String(100), nullable=False),
            sa.Column("department", sa.String(100)), sa.Column("phone", sa.String(30)), sa.Column("available", sa.Boolean()),
            sa.PrimaryKeyConstraint("id"),
        )
    if _missing("appointment"):
        op.create_table(
            "appointment",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("doctor_id", sa.Integer(), nullable=False),
            sa.Column("appointment_date", sa.String(10), nullable=False), sa.Column("appointment_time", sa.String(5), nullable=False),
            sa.Column("reason", sa.String(300)), sa.Column("status", sa.String(30)),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.ForeignKeyConstraint(["doctor_id"], ["doctor.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("admission"):
        op.create_table(
            "admission",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("ward", sa.String(80), nullable=False),
            sa.Column("bed", sa.String(30)), sa.Column("admitted_on", sa.String(10), nullable=False), sa.Column("discharged_on", sa.String(10)),
            sa.Column("status", sa.String(30)), sa.Column("notes", sa.Text()),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("lab_report"):
        op.create_table(
            "lab_report",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("test_name", sa.String(120), nullable=False),
            sa.Column("sample_date", sa.String(10), nullable=False), sa.Column("result", sa.Text()), sa.Column("status", sa.String(30)), sa.Column("ordered_by", sa.String(120)),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("medicine"):
        op.create_table(
            "medicine",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("category", sa.String(80)),
            sa.Column("stock", sa.Integer()), sa.Column("reorder_level", sa.Integer()), sa.Column("unit_price", sa.Float()), sa.Column("expiry_date", sa.String(10)),
            sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name", name="uq_medicine_name"),
        )
    if _missing("prescription"):
        op.create_table(
            "prescription",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("doctor_name", sa.String(120)),
            sa.Column("medicine", sa.String(120), nullable=False), sa.Column("dosage", sa.String(120)), sa.Column("instructions", sa.Text()), sa.Column("created_at", sa.DateTime()),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("bill"):
        op.create_table(
            "bill",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("description", sa.String(200), nullable=False),
            sa.Column("consultation", sa.Float()), sa.Column("laboratory", sa.Float()), sa.Column("pharmacy", sa.Float()), sa.Column("room", sa.Float()),
            sa.Column("insurance_provider", sa.String(120)), sa.Column("insurance_status", sa.String(40)), sa.Column("paid", sa.Boolean()), sa.Column("created_at", sa.DateTime()),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("radiology_record"):
        op.create_table(
            "radiology_record",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("patient_id", sa.Integer(), nullable=False), sa.Column("modality", sa.String(50), nullable=False),
            sa.Column("study_date", sa.String(10), nullable=False), sa.Column("findings", sa.Text()), sa.Column("report_status", sa.String(30)),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"]), sa.PrimaryKeyConstraint("id"),
        )
    if _missing("audit_log"):
        op.create_table(
            "audit_log",
            sa.Column("id", sa.Integer(), nullable=False), sa.Column("action", sa.String(120), nullable=False), sa.Column("details", sa.Text()), sa.Column("created_at", sa.DateTime()),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    # Never drops patient data. Downgrading below the CareFlow schema is intentionally unsupported.
    raise RuntimeError("Refusing to drop the original hospital tables. Restore from a backup if you need to go back.")
