"""patient portal: patient logins, shareable documents and hand-over tracking

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-25 12:00:00

Adds (all additive, no data is removed):
  * app_user.patient_id + the 'patient' role (a patient login is linked to exactly one patient record)
  * medical_document.patient_visible (files shared into the patient's own portal; default hidden)
  * patient_deliverable (digital / physical hand-over tracking), back-filled for results already released
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
OLD_ROLES = "role IN ('super_admin','hospital_admin','doctor','nurse','lab_staff','pharmacist','radiology_staff','billing_staff')"
NEW_ROLES = "role IN ('super_admin','hospital_admin','doctor','nurse','lab_staff','pharmacist','radiology_staff','billing_staff','patient')"


def _has_column(table, col):
    return col in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # ---- app_user: patient link and widened role check --------------------------------------------------
    if not _has_column("app_user", "patient_id"):
        with op.batch_alter_table("app_user", naming_convention=NAMING) as batch:
            batch.add_column(sa.Column("patient_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(op.f("fk_app_user_patient_id_patient"), "patient", ["patient_id"], ["id"])
            batch.create_unique_constraint(op.f("uq_app_user_patient_id"), ["patient_id"])
    checks = {c.get("name") for c in insp.get_check_constraints("app_user")}
    if bind.dialect.name == "postgresql":
        if "ck_app_user_role_valid" in checks:
            op.drop_constraint(op.f("ck_app_user_role_valid"), "app_user", type_="check")
        op.create_check_constraint(op.f("ck_app_user_role_valid"), "app_user", sa.text(NEW_ROLES))
        if "ck_app_user_patient_link_matches_role" not in checks:
            op.create_check_constraint(op.f("ck_app_user_patient_link_matches_role"), "app_user", sa.text("(role = 'patient') = (patient_id IS NOT NULL)"))
    else:   # SQLite rebuilds the table; the naming convention prefixes the short names
        with op.batch_alter_table("app_user", naming_convention=NAMING) as batch:
            if "ck_app_user_role_valid" in checks:
                batch.drop_constraint("role_valid", type_="check")
            batch.create_check_constraint("role_valid", sa.text(NEW_ROLES))
            if "ck_app_user_patient_link_matches_role" not in checks:
                batch.create_check_constraint("patient_link_matches_role", sa.text("(role = 'patient') = (patient_id IS NOT NULL)"))

    # ---- documents shareable with the patient ----------------------------------------------------------
    if not _has_column("medical_document", "patient_visible"):
        with op.batch_alter_table("medical_document") as batch:
            batch.add_column(sa.Column("patient_visible", sa.Boolean(), nullable=False, server_default=sa.false()))

    # ---- hand-over tracking ------------------------------------------------------------------------------
    if not insp.has_table("patient_deliverable"):
        op.create_table(
            "patient_deliverable",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("patient_id", sa.Integer(), nullable=False),
            sa.Column("kind", sa.String(length=40), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("ref_type", sa.String(length=20), nullable=True),
            sa.Column("ref_id", sa.Integer(), nullable=True),
            sa.Column("document_id", sa.Integer(), nullable=True),
            sa.Column("digital_available", sa.Boolean(), nullable=False),
            sa.Column("physical_status", sa.String(length=24), nullable=False),
            sa.Column("physical_note", sa.String(length=300), nullable=True),
            sa.Column("received_by_name", sa.String(length=120), nullable=True),
            sa.Column("handed_over_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("handed_over_by_id", sa.Integer(), nullable=True),
            sa.Column("created_by_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.CheckConstraint("physical_status IN ('Not requested','Requested','Ready for collection','Handed over')", name=op.f("ck_patient_deliverable_physical_status_valid")),
            sa.ForeignKeyConstraint(["created_by_id"], ["app_user.id"], name=op.f("fk_patient_deliverable_created_by_id_app_user")),
            sa.ForeignKeyConstraint(["document_id"], ["medical_document.id"], name=op.f("fk_patient_deliverable_document_id_medical_document")),
            sa.ForeignKeyConstraint(["handed_over_by_id"], ["app_user.id"], name=op.f("fk_patient_deliverable_handed_over_by_id_app_user")),
            sa.ForeignKeyConstraint(["patient_id"], ["patient.id"], name=op.f("fk_patient_deliverable_patient_id_patient")),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_patient_deliverable")),
            sa.UniqueConstraint("patient_id", "ref_type", "ref_id", "kind", name="uq_deliverable_ref"),
        )
        op.create_index(op.f("ix_patient_deliverable_patient_id"), "patient_deliverable", ["patient_id"], unique=False)
        _backfill(bind)


def _backfill(bind):
    """Track results that were already released before this upgrade, so patients see them in the portal immediately."""
    now = sa.func.now()
    t = sa.table("patient_deliverable", sa.column("patient_id"), sa.column("kind"), sa.column("title"), sa.column("ref_type"), sa.column("ref_id"),
                 sa.column("digital_available"), sa.column("physical_status"), sa.column("physical_note"), sa.column("received_by_name"), sa.column("created_at"))
    def ins(rows):
        if rows:
            op.bulk_insert(t, rows)
    stamp = sa.text("CURRENT_TIMESTAMP")
    import datetime as dt
    n = dt.datetime.now(dt.timezone.utc)
    base = dict(digital_available=True, physical_status="Not requested", physical_note="", received_by_name="", created_at=n)
    insp = sa.inspect(bind)
    if insp.has_table("lab_report"):
        ins([dict(base, patient_id=r.patient_id, kind="Laboratory report", title=f"{r.test_name} ({r.sample_date})"[:200], ref_type="lab", ref_id=r.id)
             for r in bind.execute(sa.text("SELECT id, patient_id, test_name, sample_date FROM lab_report WHERE status IN ('Released','Completed')"))])
    if insp.has_table("radiology_record"):
        ins([dict(base, patient_id=r.patient_id, kind="Radiology report", title=f"{r.modality} ({r.study_date})"[:200], ref_type="radiology", ref_id=r.id)
             for r in bind.execute(sa.text("SELECT id, patient_id, modality, study_date FROM radiology_record WHERE order_status = 'Final' OR (order_status IS NULL AND report_status = 'Final')"))])
    if insp.has_table("bill"):
        ins([dict(base, patient_id=r.patient_id, kind="Invoice / receipt", title=(r.description or "Bill")[:200], ref_type="bill", ref_id=r.id)
             for r in bind.execute(sa.text("SELECT id, patient_id, description FROM bill WHERE status IS NULL OR status != 'Void'"))])


def downgrade():
    raise RuntimeError("Downgrading below the patient-portal schema would destroy data and is not supported. Restore from a backup instead.")
