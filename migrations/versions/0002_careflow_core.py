"""careflow core

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24 21:05:01.679783

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


LEGACY_TS = ("patient", "prescription", "bill", "audit_log")


def _preflight_legacy_data():
    """Abort (before changing anything) if legacy rows would violate the new integrity rules."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    problems = []
    if insp.has_table("appointment"):
        n = bind.execute(sa.text(
            "SELECT COUNT(*) FROM (SELECT doctor_id, appointment_date, appointment_time FROM appointment "
            "WHERE status IN ('Scheduled','Checked-in') GROUP BY 1,2,3 HAVING COUNT(*) > 1) d")).scalar()
        if n:
            problems.append(f"{n} doctor time slot(s) are booked more than once among live appointments")
    if insp.has_table("admission"):
        n = bind.execute(sa.text("SELECT COUNT(*) FROM (SELECT patient_id FROM admission WHERE status = 'Admitted' GROUP BY 1 HAVING COUNT(*) > 1) d")).scalar()
        if n:
            problems.append(f"{n} patient(s) have more than one active admission")
    if insp.has_table("medicine"):
        n = bind.execute(sa.text("SELECT COUNT(*) FROM medicine WHERE stock < 0")).scalar()
        if n:
            problems.append(f"{n} medicine(s) have negative stock")
    if problems:
        raise RuntimeError(
            "CareFlow upgrade stopped before changing the database because existing data conflicts with new integrity rules: "
            + "; ".join(problems) + ". Correct these records in the old application (or directly) and run the upgrade again.")


def _fill_missing_created_at():
    bind = op.get_bind()
    for name in LEGACY_TS:
        bind.execute(sa.text(f"UPDATE {name} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))


def _t(name, *cols):
    return sa.table(name, *[sa.column(c) for c in cols])


def _backfill_legacy_rows():
    """Give pre-existing rows sensible values for the new columns (they were NULL because the old app had none)."""
    bind = op.get_bind()

    def fill(table, **vals):
        t = _t(table, *vals.keys())
        for col, val in vals.items():
            bind.execute(sa.update(t).where(t.c[col].is_(None)).values({col: val}))

    fill("patient", data_origin="imported", consent_data_sharing=False, identity_verified=False)
    bind.execute(sa.text("UPDATE patient SET updated_at = created_at WHERE updated_at IS NULL"))
    fill("appointment", duration_min=15, visit_type="Consultation", reschedule_count=0)
    fill("admission", discharge_status="None", reason="")
    bind.execute(sa.text("UPDATE admission SET discharge_status = 'Completed' WHERE status = 'Discharged' AND discharge_status = 'None'"))
    # admission / discharge instants from the legacy date strings (midnight UTC)
    adm = sa.table("admission", sa.column("id"), sa.column("admitted_on"), sa.column("discharged_on"),
                   sa.column("admitted_at", sa.DateTime(timezone=True)), sa.column("discharged_at", sa.DateTime(timezone=True)))
    from datetime import datetime, timezone
    for rid, a_on, d_on in bind.execute(sa.select(adm.c.id, adm.c.admitted_on, adm.c.discharged_on)).fetchall():
        vals = {}
        for key, raw in (("admitted_at", a_on), ("discharged_at", d_on)):
            try:
                vals[key] = datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc) if raw else None
            except (TypeError, ValueError):
                vals[key] = None
        bind.execute(sa.update(adm).where(adm.c.id == rid).values(**vals))
    fill("bill", other_charges=0.0, status="Issued")
    fill("doctor", registration_no="")
    fill("lab_report", priority="Routine", amendment_count=0)
    fill("medicine", is_active=True, generic_name="", strength="", form="", batch_no="")
    fill("prescription", status="Ordered", is_prn=False, dispensed_quantity=0, route="", frequency="", allergy_override_reason="", cancelled_reason="")
    bind.execute(sa.text("UPDATE radiology_record SET order_status = CASE WHEN report_status IN ('Final','Completed') THEN 'Final' ELSE 'Ordered' END WHERE order_status IS NULL"))
    fill("radiology_record", priority="Routine", urgent_finding=False, amendment_count=0, impression="", recommendations="", study_description="", indication="")
    fill("audit_log", category="system", outcome="success", user_role="", entity_type="", ip="", request_id="")


def _add_legacy_table_constraints():
    bind = op.get_bind()
    uq_names = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
    if bind.dialect.name == "postgresql":
        # tables created by the old app's db.create_all() carry PostgreSQL's default constraint names
        insp = sa.inspect(bind)
        for table, col, new in (("patient", "patient_code", "uq_patient_patient_code"), ("medicine", "name", "uq_medicine_name")):
            for uc in insp.get_unique_constraints(table):
                if uc["column_names"] == [col] and uc["name"] and uc["name"] != new:
                    op.execute(sa.text(f'ALTER TABLE {table} RENAME CONSTRAINT "{uc["name"]}" TO "{new}"'))
    else:
        with op.batch_alter_table("patient", schema=None, recreate="always", naming_convention=uq_names):
            pass
    with op.batch_alter_table("medicine", schema=None, naming_convention=uq_names) as batch_op:
        batch_op.create_check_constraint(op.f("ck_medicine_stock_nonneg"), "stock >= 0")


def upgrade():
    _preflight_legacy_data()
    _fill_missing_created_at()
    op.create_table('department',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_department')),
    sa.UniqueConstraint('name', name=op.f('uq_department_name'))
    )
    op.create_table('observation_type',
    sa.Column('code', sa.String(length=30), nullable=False),
    sa.Column('label', sa.String(length=80), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=False),
    sa.Column('plausible_min', sa.Float(), nullable=True),
    sa.Column('plausible_max', sa.Float(), nullable=True),
    sa.Column('decimals', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_observation_type'))
    )
    op.create_table('ward',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('specialty', sa.String(length=100), nullable=True),
    sa.Column('floor', sa.String(length=20), nullable=True),
    sa.Column('daily_rate', sa.Float(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], name=op.f('fk_ward_department_id_department')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ward')),
    sa.UniqueConstraint('name', name=op.f('uq_ward_name'))
    )
    op.create_table('app_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=300), nullable=False),
    sa.Column('role', sa.String(length=30), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('ward_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_demo', sa.Boolean(), nullable=False),
    sa.Column('must_change_password', sa.Boolean(), nullable=False),
    sa.Column('failed_logins', sa.Integer(), nullable=False),
    sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('password_changed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('session_epoch', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.CheckConstraint("role IN ('super_admin','hospital_admin','doctor','nurse','lab_staff','pharmacist','radiology_staff','billing_staff')", name=op.f('ck_app_user_role_valid')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_app_user_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], name=op.f('fk_app_user_doctor_id_doctor')),
    sa.ForeignKeyConstraint(['ward_id'], ['ward.id'], name=op.f('fk_app_user_ward_id_ward')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_app_user')),
    sa.UniqueConstraint('doctor_id', name=op.f('uq_app_user_doctor_id')),
    sa.UniqueConstraint('email', name=op.f('uq_app_user_email'))
    )
    with op.batch_alter_table('app_user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_app_user_role'), ['role'], unique=False)

    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ward_id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['ward_id'], ['ward.id'], name=op.f('fk_room_ward_id_ward')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_room')),
    sa.UniqueConstraint('ward_id', 'label', name='uq_room_ward_label')
    )
    with op.batch_alter_table('room', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_room_ward_id'), ['ward_id'], unique=False)

    op.create_table('alert_rule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=True),
    sa.Column('rule_kind', sa.String(length=12), nullable=False),
    sa.Column('type_code', sa.String(length=30), nullable=True),
    sa.Column('operator', sa.String(length=3), nullable=True),
    sa.Column('threshold', sa.Float(), nullable=True),
    sa.Column('severity', sa.String(length=10), nullable=False),
    sa.Column('window_minutes', sa.Integer(), nullable=True),
    sa.Column('cooldown_minutes', sa.Integer(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('review_status', sa.String(length=12), nullable=False),
    sa.Column('reviewed_by', sa.String(length=120), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint("rule_kind IN ('threshold','missing')", name=op.f('ck_alert_rule_kind_valid')),
    sa.CheckConstraint("severity IN ('Info','Warning','Critical')", name=op.f('ck_alert_rule_severity_valid')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_alert_rule_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['type_code'], ['observation_type.code'], name=op.f('fk_alert_rule_type_code_observation_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_alert_rule'))
    )
    op.create_table('bed',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('ward_id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=30), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('status_note', sa.String(length=200), nullable=True),
    sa.Column('status_changed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.CheckConstraint("status IN ('Available','Occupied','Cleaning','Reserved','Maintenance')", name=op.f('ck_bed_status_valid')),
    sa.ForeignKeyConstraint(['room_id'], ['room.id'], name=op.f('fk_bed_room_id_room')),
    sa.ForeignKeyConstraint(['ward_id'], ['ward.id'], name=op.f('fk_bed_ward_id_ward')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bed')),
    sa.UniqueConstraint('code', name=op.f('uq_bed_code')),
    sa.UniqueConstraint('room_id', 'label', name='uq_bed_room_label')
    )
    with op.batch_alter_table('bed', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bed_room_id'), ['room_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_bed_ward_id'), ['ward_id'], unique=False)

    op.create_table('stock_movement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=False),
    sa.Column('delta', sa.Integer(), nullable=False),
    sa.Column('balance_after', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=30), nullable=False),
    sa.Column('ref_type', sa.String(length=30), nullable=True),
    sa.Column('ref_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine.id'], name=op.f('fk_stock_movement_medicine_id_medicine')),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], name=op.f('fk_stock_movement_user_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_stock_movement'))
    )
    with op.batch_alter_table('stock_movement', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_stock_movement_medicine_id'), ['medicine_id'], unique=False)

    op.create_table('system_setting',
    sa.Column('key', sa.String(length=80), nullable=False),
    sa.Column('value', sa.JSON(), nullable=True),
    sa.Column('updated_by_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['updated_by_id'], ['app_user.id'], name=op.f('fk_system_setting_updated_by_id_app_user')),
    sa.PrimaryKeyConstraint('key', name=op.f('pk_system_setting'))
    )
    op.create_table('ai_conversation',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_ai_conversation_patient_id_patient')),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], name=op.f('fk_ai_conversation_user_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_conversation'))
    )
    with op.batch_alter_table('ai_conversation', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_conversation_patient_id'), ['patient_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_ai_conversation_user_id'), ['user_id'], unique=False)

    op.create_table('allergy',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('substance', sa.String(length=120), nullable=False),
    sa.Column('reaction', sa.String(length=200), nullable=True),
    sa.Column('severity', sa.String(length=20), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('recorded_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_allergy_patient_id_patient')),
    sa.ForeignKeyConstraint(['recorded_by_id'], ['app_user.id'], name=op.f('fk_allergy_recorded_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_allergy'))
    )
    with op.batch_alter_table('allergy', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_allergy_patient_id'), ['patient_id'], unique=False)

    op.create_table('critical_ack',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_type', sa.String(length=12), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('summary', sa.String(length=300), nullable=True),
    sa.Column('notify_user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ack_by_id', sa.Integer(), nullable=True),
    sa.Column('ack_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ack_note', sa.String(length=300), nullable=True),
    sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('escalated_to_role', sa.String(length=30), nullable=True),
    sa.CheckConstraint("status IN ('Pending','Acknowledged','Escalated')", name=op.f('ck_critical_ack_status_valid')),
    sa.ForeignKeyConstraint(['ack_by_id'], ['app_user.id'], name=op.f('fk_critical_ack_ack_by_id_app_user')),
    sa.ForeignKeyConstraint(['notify_user_id'], ['app_user.id'], name=op.f('fk_critical_ack_notify_user_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_critical_ack_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_critical_ack')),
    sa.UniqueConstraint('source_type', 'source_id', name='uq_critical_ack_source')
    )
    with op.batch_alter_table('critical_ack', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_critical_ack_patient_id'), ['patient_id'], unique=False)

    op.create_table('monitoring_device',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('kind', sa.String(length=60), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('is_simulated', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('api_key_hash', sa.String(length=128), nullable=True),
    sa.Column('api_key_prefix', sa.String(length=12), nullable=True),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_monitoring_device_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_monitoring_device_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_monitoring_device'))
    )
    with op.batch_alter_table('monitoring_device', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_monitoring_device_patient_id'), ['patient_id'], unique=False)

    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=30), nullable=True),
    sa.Column('kind', sa.String(length=40), nullable=False),
    sa.Column('severity', sa.String(length=10), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.String(length=400), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('ref_type', sa.String(length=30), nullable=True),
    sa.Column('ref_id', sa.Integer(), nullable=True),
    sa.Column('delivery', sa.String(length=12), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_notification_patient_id_patient')),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], name=op.f('fk_notification_user_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification'))
    )
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notification_role'), ['role'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_user_id'), ['user_id'], unique=False)

    op.create_table('patient_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('relation', sa.String(length=20), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_patient_assignment_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_patient_assignment_patient_id_patient')),
    sa.ForeignKeyConstraint(['user_id'], ['app_user.id'], name=op.f('fk_patient_assignment_user_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_patient_assignment'))
    )
    with op.batch_alter_table('patient_assignment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_patient_assignment_patient_id'), ['patient_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_patient_assignment_user_id'), ['user_id'], unique=False)
        batch_op.create_index('uq_patient_assignment_active', ['patient_id', 'user_id'], unique=True, sqlite_where=sa.text('active = 1'), postgresql_where=sa.text('active'))

    op.create_table('ai_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('conversation_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=10), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('mode', sa.String(length=12), nullable=True),
    sa.Column('status', sa.String(length=24), nullable=True),
    sa.Column('sources', sa.JSON(), nullable=True),
    sa.Column('limitations', sa.JSON(), nullable=True),
    sa.Column('provider', sa.String(length=30), nullable=True),
    sa.Column('model', sa.String(length=60), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['ai_conversation.id'], name=op.f('fk_ai_message_conversation_id_ai_conversation')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_message'))
    )
    with op.batch_alter_table('ai_message', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_ai_message_conversation_id'), ['conversation_id'], unique=False)

    op.create_table('encounter',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('encounter_type', sa.String(length=20), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('appointment_id', sa.Integer(), nullable=True),
    sa.Column('chief_complaint', sa.String(length=300), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], name=op.f('fk_encounter_appointment_id_appointment')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_encounter_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctor.id'], name=op.f('fk_encounter_doctor_id_doctor')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_encounter_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_encounter'))
    )
    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_encounter_patient_id'), ['patient_id'], unique=False)

    op.create_table('problem',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=300), nullable=False),
    sa.Column('code', sa.String(length=30), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('onset_on', sa.String(length=10), nullable=True),
    sa.Column('recorded_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], name=op.f('fk_problem_encounter_id_encounter')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_problem_patient_id_patient')),
    sa.ForeignKeyConstraint(['recorded_by_id'], ['app_user.id'], name=op.f('fk_problem_recorded_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_problem'))
    )
    with op.batch_alter_table('problem', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_problem_patient_id'), ['patient_id'], unique=False)

    op.create_table('bed_assignment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=False),
    sa.Column('bed_id', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reason', sa.String(length=30), nullable=True),
    sa.Column('end_reason', sa.String(length=30), nullable=True),
    sa.Column('moved_by_id', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_bed_assignment_admission_id_admission')),
    sa.ForeignKeyConstraint(['bed_id'], ['bed.id'], name=op.f('fk_bed_assignment_bed_id_bed')),
    sa.ForeignKeyConstraint(['moved_by_id'], ['app_user.id'], name=op.f('fk_bed_assignment_moved_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bed_assignment'))
    )
    with op.batch_alter_table('bed_assignment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bed_assignment_admission_id'), ['admission_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_bed_assignment_bed_id'), ['bed_id'], unique=False)
        batch_op.create_index('uq_bed_assignment_open_admission', ['admission_id'], unique=True, sqlite_where=sa.text('ended_at IS NULL'), postgresql_where=sa.text('ended_at IS NULL'))
        batch_op.create_index('uq_bed_assignment_open_bed', ['bed_id'], unique=True, sqlite_where=sa.text('ended_at IS NULL'), postgresql_where=sa.text('ended_at IS NULL'))

    op.create_table('care_plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('goals', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_care_plan_admission_id_admission')),
    sa.ForeignKeyConstraint(['author_id'], ['app_user.id'], name=op.f('fk_care_plan_author_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_care_plan_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_care_plan'))
    )
    with op.batch_alter_table('care_plan', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_care_plan_patient_id'), ['patient_id'], unique=False)

    op.create_table('clinical_note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('note_type', sa.String(length=30), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('amends_note_id', sa.Integer(), nullable=True),
    sa.Column('amendment_reason', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("status IN ('Final','Superseded')", name=op.f('ck_clinical_note_status_valid')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_clinical_note_admission_id_admission')),
    sa.ForeignKeyConstraint(['amends_note_id'], ['clinical_note.id'], name=op.f('fk_clinical_note_amends_note_id_clinical_note')),
    sa.ForeignKeyConstraint(['author_id'], ['app_user.id'], name=op.f('fk_clinical_note_author_id_app_user')),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], name=op.f('fk_clinical_note_encounter_id_encounter')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_clinical_note_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_clinical_note'))
    )
    with op.batch_alter_table('clinical_note', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_clinical_note_patient_id'), ['patient_id'], unique=False)

    op.create_table('follow_up',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('due_on', sa.String(length=10), nullable=True),
    sa.Column('instructions', sa.Text(), nullable=True),
    sa.Column('appointment_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_follow_up_admission_id_admission')),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointment.id'], name=op.f('fk_follow_up_appointment_id_appointment')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_follow_up_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], name=op.f('fk_follow_up_encounter_id_encounter')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_follow_up_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_follow_up'))
    )
    with op.batch_alter_table('follow_up', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_follow_up_patient_id'), ['patient_id'], unique=False)

    op.create_table('handover',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('ward_id', sa.Integer(), nullable=True),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('shift', sa.String(length=20), nullable=True),
    sa.Column('situation', sa.Text(), nullable=True),
    sa.Column('background', sa.Text(), nullable=True),
    sa.Column('assessment', sa.Text(), nullable=True),
    sa.Column('recommendation', sa.Text(), nullable=True),
    sa.Column('is_auto_draft', sa.Boolean(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('reviewed_by_id', sa.Integer(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_handover_admission_id_admission')),
    sa.ForeignKeyConstraint(['author_id'], ['app_user.id'], name=op.f('fk_handover_author_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_handover_patient_id_patient')),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['app_user.id'], name=op.f('fk_handover_reviewed_by_id_app_user')),
    sa.ForeignKeyConstraint(['ward_id'], ['ward.id'], name=op.f('fk_handover_ward_id_ward')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_handover'))
    )
    with op.batch_alter_table('handover', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_handover_patient_id'), ['patient_id'], unique=False)

    op.create_table('intake_output',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('kind', sa.String(length=10), nullable=False),
    sa.Column('item', sa.String(length=100), nullable=True),
    sa.Column('amount_ml', sa.Float(), nullable=False),
    sa.Column('recorded_by_id', sa.Integer(), nullable=True),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("kind IN ('Intake','Output')", name=op.f('ck_intake_output_kind_valid')),
    sa.CheckConstraint('amount_ml >= 0', name=op.f('ck_intake_output_amount_nonneg')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_intake_output_admission_id_admission')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_intake_output_patient_id_patient')),
    sa.ForeignKeyConstraint(['recorded_by_id'], ['app_user.id'], name=op.f('fk_intake_output_recorded_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_intake_output'))
    )
    with op.batch_alter_table('intake_output', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_intake_output_patient_id'), ['patient_id'], unique=False)

    op.create_table('med_reconciliation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('pharmacist_id', sa.Integer(), nullable=True),
    sa.Column('items', sa.JSON(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_med_reconciliation_admission_id_admission')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_med_reconciliation_patient_id_patient')),
    sa.ForeignKeyConstraint(['pharmacist_id'], ['app_user.id'], name=op.f('fk_med_reconciliation_pharmacist_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_med_reconciliation'))
    )
    with op.batch_alter_table('med_reconciliation', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_med_reconciliation_patient_id'), ['patient_id'], unique=False)

    op.create_table('observation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.Column('type_code', sa.String(length=30), nullable=False),
    sa.Column('value_num', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=False),
    sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('source', sa.String(length=12), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('recorded_by_id', sa.Integer(), nullable=True),
    sa.Column('validation_status', sa.String(length=20), nullable=False),
    sa.Column('supersedes_id', sa.Integer(), nullable=True),
    sa.Column('correction_reason', sa.String(length=300), nullable=True),
    sa.Column('group_id', sa.String(length=36), nullable=True),
    sa.Column('note', sa.String(length=300), nullable=True),
    sa.CheckConstraint("source IN ('manual','device','simulated')", name=op.f('ck_observation_source_valid')),
    sa.CheckConstraint("validation_status IN ('Valid','Unverified','Corrected','Entered in error')", name=op.f('ck_observation_validation_valid')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_observation_admission_id_admission')),
    sa.ForeignKeyConstraint(['device_id'], ['monitoring_device.id'], name=op.f('fk_observation_device_id_monitoring_device')),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], name=op.f('fk_observation_encounter_id_encounter')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_observation_patient_id_patient')),
    sa.ForeignKeyConstraint(['recorded_by_id'], ['app_user.id'], name=op.f('fk_observation_recorded_by_id_app_user')),
    sa.ForeignKeyConstraint(['supersedes_id'], ['observation.id'], name=op.f('fk_observation_supersedes_id_observation')),
    sa.ForeignKeyConstraint(['type_code'], ['observation_type.code'], name=op.f('fk_observation_type_code_observation_type')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_observation'))
    )
    with op.batch_alter_table('observation', schema=None) as batch_op:
        batch_op.create_index('ix_observation_patient_type_time', ['patient_id', 'type_code', 'observed_at'], unique=False)

    op.create_table('alert',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rule_id', sa.Integer(), nullable=False),
    sa.Column('rule_version', sa.Integer(), nullable=False),
    sa.Column('rule_snapshot', sa.JSON(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('observation_id', sa.Integer(), nullable=True),
    sa.Column('severity', sa.String(length=10), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('message', sa.String(length=300), nullable=True),
    sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_triggered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('occurrences', sa.Integer(), nullable=False),
    sa.Column('from_simulated_data', sa.Boolean(), nullable=False),
    sa.Column('responder_user_id', sa.Integer(), nullable=True),
    sa.Column('responder_role', sa.String(length=30), nullable=True),
    sa.Column('ack_by_id', sa.Integer(), nullable=True),
    sa.Column('ack_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('escalated_to_role', sa.String(length=30), nullable=True),
    sa.Column('resolved_by_id', sa.Integer(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolution_note', sa.String(length=300), nullable=True),
    sa.CheckConstraint("status IN ('Open','Acknowledged','Escalated','Resolved')", name=op.f('ck_alert_status_valid')),
    sa.ForeignKeyConstraint(['ack_by_id'], ['app_user.id'], name=op.f('fk_alert_ack_by_id_app_user')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_alert_admission_id_admission')),
    sa.ForeignKeyConstraint(['observation_id'], ['observation.id'], name=op.f('fk_alert_observation_id_observation')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_alert_patient_id_patient')),
    sa.ForeignKeyConstraint(['resolved_by_id'], ['app_user.id'], name=op.f('fk_alert_resolved_by_id_app_user')),
    sa.ForeignKeyConstraint(['responder_user_id'], ['app_user.id'], name=op.f('fk_alert_responder_user_id_app_user')),
    sa.ForeignKeyConstraint(['rule_id'], ['alert_rule.id'], name=op.f('fk_alert_rule_id_alert_rule')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_alert'))
    )
    with op.batch_alter_table('alert', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_alert_patient_id'), ['patient_id'], unique=False)
        batch_op.create_index('uq_alert_open_patient_rule', ['patient_id', 'rule_id'], unique=True, sqlite_where=sa.text("status <> 'Resolved'"), postgresql_where=sa.text("status <> 'Resolved'"))

    op.create_table('bill_adjustment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('reason', sa.String(length=300), nullable=False),
    sa.Column('requested_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('amount > 0', name=op.f('ck_bill_adjustment_amount_positive')),
    sa.ForeignKeyConstraint(['approved_by_id'], ['app_user.id'], name=op.f('fk_bill_adjustment_approved_by_id_app_user')),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], name=op.f('fk_bill_adjustment_bill_id_bill')),
    sa.ForeignKeyConstraint(['requested_by_id'], ['app_user.id'], name=op.f('fk_bill_adjustment_requested_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_bill_adjustment'))
    )
    with op.batch_alter_table('bill_adjustment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bill_adjustment_bill_id'), ['bill_id'], unique=False)

    op.create_table('care_task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('care_plan_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('category', sa.String(length=30), nullable=False),
    sa.Column('assigned_role', sa.String(length=30), nullable=True),
    sa.Column('assigned_user_id', sa.Integer(), nullable=True),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('priority', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_by_id', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("status IN ('Pending','Done','Cancelled')", name=op.f('ck_care_task_status_valid')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_care_task_admission_id_admission')),
    sa.ForeignKeyConstraint(['assigned_user_id'], ['app_user.id'], name=op.f('fk_care_task_assigned_user_id_app_user')),
    sa.ForeignKeyConstraint(['care_plan_id'], ['care_plan.id'], name=op.f('fk_care_task_care_plan_id_care_plan')),
    sa.ForeignKeyConstraint(['completed_by_id'], ['app_user.id'], name=op.f('fk_care_task_completed_by_id_app_user')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_care_task_created_by_id_app_user')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_care_task_patient_id_patient')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_care_task'))
    )
    with op.batch_alter_table('care_task', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_care_task_admission_id'), ['admission_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_care_task_due_at'), ['due_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_care_task_patient_id'), ['patient_id'], unique=False)

    op.create_table('dispense_event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prescription_id', sa.Integer(), nullable=False),
    sa.Column('medicine_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('dispensed_by_id', sa.Integer(), nullable=False),
    sa.Column('dispensed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('warnings_acknowledged', sa.JSON(), nullable=True),
    sa.Column('note', sa.String(length=300), nullable=True),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_dispense_event_qty_positive')),
    sa.ForeignKeyConstraint(['dispensed_by_id'], ['app_user.id'], name=op.f('fk_dispense_event_dispensed_by_id_app_user')),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicine.id'], name=op.f('fk_dispense_event_medicine_id_medicine')),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], name=op.f('fk_dispense_event_prescription_id_prescription')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_dispense_event'))
    )
    with op.batch_alter_table('dispense_event', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_dispense_event_prescription_id'), ['prescription_id'], unique=False)

    op.create_table('insurance_claim',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('provider', sa.String(length=120), nullable=False),
    sa.Column('policy_no', sa.String(length=60), nullable=True),
    sa.Column('claim_no', sa.String(length=60), nullable=True),
    sa.Column('amount_claimed', sa.Float(), nullable=True),
    sa.Column('amount_approved', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.String(length=300), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], name=op.f('fk_insurance_claim_bill_id_bill')),
    sa.ForeignKeyConstraint(['created_by_id'], ['app_user.id'], name=op.f('fk_insurance_claim_created_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_insurance_claim'))
    )
    with op.batch_alter_table('insurance_claim', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_insurance_claim_bill_id'), ['bill_id'], unique=False)

    op.create_table('lab_result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lab_report_id', sa.Integer(), nullable=False),
    sa.Column('analyte', sa.String(length=120), nullable=False),
    sa.Column('value_num', sa.Float(), nullable=True),
    sa.Column('value_text', sa.String(length=200), nullable=True),
    sa.Column('unit', sa.String(length=30), nullable=True),
    sa.Column('ref_low', sa.Float(), nullable=True),
    sa.Column('ref_high', sa.Float(), nullable=True),
    sa.Column('ref_text', sa.String(length=100), nullable=True),
    sa.Column('critical_low', sa.Float(), nullable=True),
    sa.Column('critical_high', sa.Float(), nullable=True),
    sa.Column('flag', sa.String(length=20), nullable=False),
    sa.Column('is_critical', sa.Boolean(), nullable=False),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('supersedes_id', sa.Integer(), nullable=True),
    sa.Column('correction_reason', sa.String(length=300), nullable=True),
    sa.Column('entered_by_id', sa.Integer(), nullable=True),
    sa.Column('entered_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['entered_by_id'], ['app_user.id'], name=op.f('fk_lab_result_entered_by_id_app_user')),
    sa.ForeignKeyConstraint(['lab_report_id'], ['lab_report.id'], name=op.f('fk_lab_result_lab_report_id_lab_report')),
    sa.ForeignKeyConstraint(['supersedes_id'], ['lab_result.id'], name=op.f('fk_lab_result_supersedes_id_lab_result')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lab_result'))
    )
    with op.batch_alter_table('lab_result', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_lab_result_lab_report_id'), ['lab_report_id'], unique=False)

    op.create_table('medical_document',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('public_id', sa.String(length=36), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('encounter_id', sa.Integer(), nullable=True),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('lab_report_id', sa.Integer(), nullable=True),
    sa.Column('radiology_id', sa.Integer(), nullable=True),
    sa.Column('doc_type', sa.String(length=40), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('original_filename', sa.String(length=200), nullable=True),
    sa.Column('mime_type', sa.String(length=80), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('storage_backend', sa.String(length=12), nullable=False),
    sa.Column('storage_key', sa.String(length=200), nullable=False),
    sa.Column('uploaded_by_id', sa.Integer(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('processing_status', sa.String(length=16), nullable=False),
    sa.Column('extraction_status', sa.String(length=24), nullable=False),
    sa.Column('extraction_method', sa.String(length=24), nullable=True),
    sa.Column('extraction_quality', sa.Float(), nullable=True),
    sa.Column('extraction_note', sa.String(length=300), nullable=True),
    sa.Column('page_count', sa.Integer(), nullable=True),
    sa.Column('review_status', sa.String(length=20), nullable=False),
    sa.Column('reviewed_by_id', sa.Integer(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('supersedes_id', sa.Integer(), nullable=True),
    sa.Column('is_image', sa.Boolean(), nullable=True),
    sa.Column('reprocess_count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_medical_document_admission_id_admission')),
    sa.ForeignKeyConstraint(['encounter_id'], ['encounter.id'], name=op.f('fk_medical_document_encounter_id_encounter')),
    sa.ForeignKeyConstraint(['lab_report_id'], ['lab_report.id'], name=op.f('fk_medical_document_lab_report_id_lab_report')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_medical_document_patient_id_patient')),
    sa.ForeignKeyConstraint(['radiology_id'], ['radiology_record.id'], name=op.f('fk_medical_document_radiology_id_radiology_record')),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['app_user.id'], name=op.f('fk_medical_document_reviewed_by_id_app_user')),
    sa.ForeignKeyConstraint(['supersedes_id'], ['medical_document.id'], name=op.f('fk_medical_document_supersedes_id_medical_document')),
    sa.ForeignKeyConstraint(['uploaded_by_id'], ['app_user.id'], name=op.f('fk_medical_document_uploaded_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_medical_document')),
    sa.UniqueConstraint('public_id', name=op.f('uq_medical_document_public_id'))
    )
    with op.batch_alter_table('medical_document', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_medical_document_patient_id'), ['patient_id'], unique=False)

    op.create_table('medication_administration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prescription_id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('admission_id', sa.Integer(), nullable=True),
    sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('administered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=False),
    sa.Column('dose_given', sa.String(length=60), nullable=True),
    sa.Column('identity_verified', sa.Boolean(), nullable=True),
    sa.Column('allergies_checked', sa.Boolean(), nullable=True),
    sa.Column('administered_by_id', sa.Integer(), nullable=True),
    sa.Column('note', sa.String(length=300), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['administered_by_id'], ['app_user.id'], name=op.f('fk_medication_administration_administered_by_id_app_user')),
    sa.ForeignKeyConstraint(['admission_id'], ['admission.id'], name=op.f('fk_medication_administration_admission_id_admission')),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], name=op.f('fk_medication_administration_patient_id_patient')),
    sa.ForeignKeyConstraint(['prescription_id'], ['prescription.id'], name=op.f('fk_medication_administration_prescription_id_prescription')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_medication_administration'))
    )
    with op.batch_alter_table('medication_administration', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_medication_administration_patient_id'), ['patient_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_medication_administration_prescription_id'), ['prescription_id'], unique=False)

    op.create_table('payment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.String(length=10), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('method', sa.String(length=30), nullable=True),
    sa.Column('reference', sa.String(length=80), nullable=True),
    sa.Column('reason', sa.String(length=300), nullable=True),
    sa.Column('received_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("kind IN ('Payment','Refund')", name=op.f('ck_payment_kind_valid')),
    sa.CheckConstraint('amount > 0', name=op.f('ck_payment_amount_positive')),
    sa.ForeignKeyConstraint(['approved_by_id'], ['app_user.id'], name=op.f('fk_payment_approved_by_id_app_user')),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], name=op.f('fk_payment_bill_id_bill')),
    sa.ForeignKeyConstraint(['received_by_id'], ['app_user.id'], name=op.f('fk_payment_received_by_id_app_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_payment'))
    )
    with op.batch_alter_table('payment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_payment_bill_id'), ['bill_id'], unique=False)

    op.create_table('radiology_report_version',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('radiology_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('findings', sa.Text(), nullable=True),
    sa.Column('impression', sa.Text(), nullable=True),
    sa.Column('recommendations', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=True),
    sa.Column('change_reason', sa.String(length=300), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['app_user.id'], name=op.f('fk_radiology_report_version_author_id_app_user')),
    sa.ForeignKeyConstraint(['radiology_id'], ['radiology_record.id'], name=op.f('fk_radiology_report_version_radiology_id_radiology_record')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_radiology_report_version'))
    )
    with op.batch_alter_table('radiology_report_version', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_radiology_report_version_radiology_id'), ['radiology_id'], unique=False)

    op.create_table('document_page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('page_no', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('method', sa.String(length=16), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('char_count', sa.Integer(), nullable=True),
    sa.Column('corrected_text', sa.Text(), nullable=True),
    sa.Column('corrected_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['corrected_by_id'], ['app_user.id'], name=op.f('fk_document_page_corrected_by_id_app_user')),
    sa.ForeignKeyConstraint(['document_id'], ['medical_document.id'], name=op.f('fk_document_page_document_id_medical_document')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_document_page')),
    sa.UniqueConstraint('document_id', 'page_no', name='uq_document_page')
    )
    with op.batch_alter_table('document_page', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_document_page_document_id'), ['document_id'], unique=False)

    with op.batch_alter_table('admission', schema=None) as batch_op:
        batch_op.add_column(sa.Column('encounter_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('responsible_doctor_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('admitted_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('discharged_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('expected_discharge_on', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('discharge_status', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('discharge_plan', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('discharge_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('discharge_authorized_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('discharge_authorized_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.create_index('uq_admission_active_patient', ['patient_id'], unique=True, sqlite_where=sa.text("status = 'Admitted'"), postgresql_where=sa.text("status = 'Admitted'"))
        batch_op.create_foreign_key(batch_op.f('fk_admission_responsible_doctor_id_doctor'), 'doctor', ['responsible_doctor_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_admission_created_by_id_app_user'), 'app_user', ['created_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_admission_discharge_authorized_by_id_app_user'), 'app_user', ['discharge_authorized_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_admission_encounter_id_encounter'), 'encounter', ['encounter_id'], ['id'])

    with op.batch_alter_table('appointment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration_min', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('visit_type', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('cancel_reason', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('reschedule_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index('ix_appointment_doctor_day', ['doctor_id', 'appointment_date'], unique=False)
        batch_op.create_index('ix_appointment_patient', ['patient_id'], unique=False)
        batch_op.create_index('uq_appointment_doctor_slot_active', ['doctor_id', 'appointment_date', 'appointment_time'], unique=True, sqlite_where=sa.text("status IN ('Scheduled','Checked-in')"), postgresql_where=sa.text("status IN ('Scheduled','Checked-in')"))
        batch_op.create_foreign_key(batch_op.f('fk_appointment_created_by_id_app_user'), 'app_user', ['created_by_id'], ['id'])

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('user_role', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('category', sa.String(length=16), nullable=True))
        batch_op.add_column(sa.Column('entity_type', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('entity_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('patient_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('outcome', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('ip', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('request_id', sa.String(length=36), nullable=True))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False,
               postgresql_using="created_at AT TIME ZONE 'UTC'")
        batch_op.create_index('ix_audit_log_created', ['created_at'], unique=False)
        batch_op.create_index('ix_audit_log_patient', ['patient_id'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_audit_log_patient_id_patient'), 'patient', ['patient_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_audit_log_user_id_app_user'), 'app_user', ['user_id'], ['id'])

    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.add_column(sa.Column('other_charges', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('encounter_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('admission_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('created_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('voided_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False,
               postgresql_using="created_at AT TIME ZONE 'UTC'")
        batch_op.create_foreign_key(batch_op.f('fk_bill_created_by_id_app_user'), 'app_user', ['created_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_bill_encounter_id_encounter'), 'encounter', ['encounter_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_bill_admission_id_admission'), 'admission', ['admission_id'], ['id'])

    with op.batch_alter_table('doctor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('registration_no', sa.String(length=60), nullable=True))

    with op.batch_alter_table('lab_report', schema=None) as batch_op:
        batch_op.add_column(sa.Column('encounter_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('admission_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ordered_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('accession_no', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('specimen_type', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('clinical_info', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('ordered_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('collected_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('collected_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('received_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('resulted_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('resulted_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('verified_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('released_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('released_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('rejected_reason', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('amendment_count', sa.Integer(), nullable=True))
        batch_op.create_index('ix_lab_report_patient_status', ['patient_id', 'status'], unique=False)
        batch_op.create_unique_constraint(batch_op.f('uq_lab_report_accession_no'), ['accession_no'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_admission_id_admission'), 'admission', ['admission_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_ordered_by_id_app_user'), 'app_user', ['ordered_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_released_by_id_app_user'), 'app_user', ['released_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_verified_by_id_app_user'), 'app_user', ['verified_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_collected_by_id_app_user'), 'app_user', ['collected_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_encounter_id_encounter'), 'encounter', ['encounter_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_lab_report_resulted_by_id_app_user'), 'app_user', ['resulted_by_id'], ['id'])

    with op.batch_alter_table('medicine', schema=None) as batch_op:
        batch_op.add_column(sa.Column('generic_name', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('strength', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('form', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('batch_no', sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))

    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('emergency_contact_phone', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('emergency_contact_relation', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('identifier_label', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('identifier_last4', sa.String(length=4), nullable=True))
        batch_op.add_column(sa.Column('identity_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('identity_verified_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('identity_verified_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('consent_data_sharing', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('consent_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('insurance_provider', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('insurance_policy_no', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('data_origin', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False,
               postgresql_using="created_at AT TIME ZONE 'UTC'")
        batch_op.create_foreign_key(batch_op.f('fk_patient_identity_verified_by_id_app_user'), 'app_user', ['identity_verified_by_id'], ['id'])

    with op.batch_alter_table('prescription', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ordered_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('encounter_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('admission_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('medicine_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('route', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('frequency', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('duration_days', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_prn', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(length=24), nullable=True))
        batch_op.add_column(sa.Column('allergy_override_reason', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('warnings', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('verified_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('cancelled_reason', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('dispensed_quantity', sa.Integer(), nullable=True))
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False,
               postgresql_using="created_at AT TIME ZONE 'UTC'")
        batch_op.create_index('ix_prescription_patient_status', ['patient_id', 'status'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_prescription_ordered_by_id_app_user'), 'app_user', ['ordered_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_prescription_admission_id_admission'), 'admission', ['admission_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_prescription_medicine_id_medicine'), 'medicine', ['medicine_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_prescription_encounter_id_encounter'), 'encounter', ['encounter_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_prescription_verified_by_id_app_user'), 'app_user', ['verified_by_id'], ['id'])

    with op.batch_alter_table('radiology_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('encounter_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('admission_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ordered_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('order_status', sa.String(length=12), nullable=True))
        batch_op.add_column(sa.Column('study_description', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('indication', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('performed_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('performed_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('impression', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('recommendations', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('reported_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('reported_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('authorized_by_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('authorized_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('urgent_finding', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('amendment_count', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('ordered_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index('ix_radiology_patient', ['patient_id'], unique=False)
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_authorized_by_id_app_user'), 'app_user', ['authorized_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_admission_id_admission'), 'admission', ['admission_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_performed_by_id_app_user'), 'app_user', ['performed_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_encounter_id_encounter'), 'encounter', ['encounter_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_reported_by_id_app_user'), 'app_user', ['reported_by_id'], ['id'])
        batch_op.create_foreign_key(batch_op.f('fk_radiology_record_ordered_by_id_app_user'), 'app_user', ['ordered_by_id'], ['id'])

    _backfill_legacy_rows()
    _add_legacy_table_constraints()


def downgrade():
    # Intentionally unsupported: reverting would drop clinical, audit and document tables.
    raise RuntimeError("Downgrading below the CareFlow schema would destroy data and is not supported. Restore from a backup instead.")
