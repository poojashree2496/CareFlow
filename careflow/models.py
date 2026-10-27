"""SQLAlchemy models for CareFlow.

The ten original tables (patient, doctor, appointment, admission, lab_report,
medicine, prescription, bill, radiology_record, audit_log) keep their names and
original columns so existing data and integrations keep working; new columns are
additive and nullable/defaulted.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Index, UniqueConstraint, text
from sqlalchemy.types import DateTime, TypeDecorator

from .constants import ACTIVE_APPOINTMENT
from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UTCDateTime(TypeDecorator):
    """Timezone-aware UTC timestamps on both PostgreSQL and SQLite."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone(timezone.utc)
        return value if dialect.name == "postgresql" else value.replace(tzinfo=None)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


def _ts(**kw):
    return db.Column(UTCDateTime, **kw)


def _created():
    return db.Column(UTCDateTime, default=utcnow, nullable=False)


# =========================================================================== #
# Facilities
# =========================================================================== #
class Department(db.Model):
    __tablename__ = "department"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = _created()


class Ward(db.Model):
    __tablename__ = "ward"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"))
    specialty = db.Column(db.String(100), default="")
    floor = db.Column(db.String(20), default="")
    daily_rate = db.Column(db.Float, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    department = db.relationship("Department")


class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    ward_id = db.Column(db.Integer, db.ForeignKey("ward.id"), nullable=False, index=True)
    label = db.Column(db.String(30), nullable=False)
    ward = db.relationship("Ward", backref="rooms")
    __table_args__ = (UniqueConstraint("ward_id", "label", name="uq_room_ward_label"),)


class Bed(db.Model):
    __tablename__ = "bed"
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("room.id"), nullable=False, index=True)
    ward_id = db.Column(db.Integer, db.ForeignKey("ward.id"), nullable=False, index=True)
    label = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(40), unique=True, nullable=False)
    status = db.Column(db.String(20), default="Available", nullable=False)
    status_note = db.Column(db.String(200), default="")
    status_changed_at = _ts(default=utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    room = db.relationship("Room", backref="beds")
    ward = db.relationship("Ward")
    __table_args__ = (
        CheckConstraint("status IN ('Available','Occupied','Cleaning','Reserved','Maintenance')", name="status_valid"),
        UniqueConstraint("room_id", "label", name="uq_bed_room_label"),
    )


# =========================================================================== #
# Identity & access
# =========================================================================== #
class Doctor(db.Model):
    __tablename__ = "doctor"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), default="General")
    phone = db.Column(db.String(30), default="")
    available = db.Column(db.Boolean, default=True)
    registration_no = db.Column(db.String(60), default="")


class AppUser(db.Model):
    __tablename__ = "app_user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(30), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), unique=True)
    ward_id = db.Column(db.Integer, db.ForeignKey("ward.id"))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id", use_alter=True, name="fk_app_user_patient_id_patient"), unique=True)   # only for role 'patient': the one record this login may view
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_demo = db.Column(db.Boolean, default=False, nullable=False)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    failed_logins = db.Column(db.Integer, default=0, nullable=False)
    locked_until = _ts()
    last_login_at = _ts()
    password_changed_at = _ts()
    session_epoch = db.Column(db.Integer, default=1, nullable=False)
    created_at = _created()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    doctor = db.relationship("Doctor")
    ward = db.relationship("Ward")
    patient = db.relationship("Patient", foreign_keys=[patient_id])
    __table_args__ = (
        CheckConstraint("role IN ('super_admin','hospital_admin','doctor','nurse','lab_staff','pharmacist','radiology_staff','billing_staff','patient')", name="role_valid"),
        CheckConstraint("(role = 'patient') = (patient_id IS NOT NULL)", name="patient_link_matches_role"),
    )


class SystemSetting(db.Model):
    __tablename__ = "system_setting"
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.JSON)
    updated_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    updated_at = _ts(default=utcnow, onupdate=utcnow)


# =========================================================================== #
# Patients
# =========================================================================== #
class Patient(db.Model):
    __tablename__ = "patient"
    id = db.Column(db.Integer, primary_key=True)
    patient_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.String(10), default="")
    gender = db.Column(db.String(30), default="Not specified")
    phone = db.Column(db.String(30), default="")
    email = db.Column(db.String(120), default="")
    blood_group = db.Column(db.String(5), default="")
    allergies = db.Column(db.Text, default="")  # legacy free text; structured allergies live in `allergy`
    emergency_contact = db.Column(db.String(120), default="")
    medical_history = db.Column(db.Text, default="")
    created_at = _created()
    # --- CareFlow additions ---
    address = db.Column(db.Text, default="")
    emergency_contact_phone = db.Column(db.String(30), default="")
    emergency_contact_relation = db.Column(db.String(60), default="")
    identifier_label = db.Column(db.String(60), default="")   # e.g. "National ID" (type only)
    identifier_last4 = db.Column(db.String(4), default="")    # never the full number
    identity_verified = db.Column(db.Boolean, default=False)
    identity_verified_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    identity_verified_at = _ts()
    consent_data_sharing = db.Column(db.Boolean, default=False)
    consent_notes = db.Column(db.Text, default="")
    insurance_provider = db.Column(db.String(120), default="")
    insurance_policy_no = db.Column(db.String(60), default="")
    data_origin = db.Column(db.String(20), default="manual")  # manual | demo | imported
    archived_at = _ts()
    updated_at = _ts(onupdate=utcnow)


class PatientAssignment(db.Model):
    """Care relationship: grants a clinician access to a specific patient."""
    __tablename__ = "patient_assignment"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False, index=True)
    relation = db.Column(db.String(20), default="primary", nullable=False)  # primary | consulting | covering
    active = db.Column(db.Boolean, default=True, nullable=False)
    starts_at = _ts(default=utcnow)
    ends_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    user = db.relationship("AppUser", foreign_keys=[user_id])
    patient = db.relationship("Patient")
    __table_args__ = (
        Index("uq_patient_assignment_active", "patient_id", "user_id", unique=True,
              sqlite_where=text("active = 1"), postgresql_where=text("active")),
    )


class Allergy(db.Model):
    __tablename__ = "allergy"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    substance = db.Column(db.String(120), nullable=False)
    reaction = db.Column(db.String(200), default="")
    severity = db.Column(db.String(20), default="Unknown")
    status = db.Column(db.String(20), default="Active", nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    patient = db.relationship("Patient")


class Problem(db.Model):
    """Problem list / diagnoses."""
    __tablename__ = "problem"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    description = db.Column(db.String(300), nullable=False)
    code = db.Column(db.String(30), default="")
    status = db.Column(db.String(20), default="Active", nullable=False)
    onset_on = db.Column(db.String(10), default="")
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    resolved_at = _ts()
    patient = db.relationship("Patient")


# =========================================================================== #
# Scheduling, encounters, admissions, beds
# =========================================================================== #
class Appointment(db.Model):
    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    appointment_date = db.Column(db.String(10), nullable=False)
    appointment_time = db.Column(db.String(5), nullable=False)
    reason = db.Column(db.String(300), default="")
    status = db.Column(db.String(30), default="Scheduled")
    patient = db.relationship("Patient")
    doctor = db.relationship("Doctor")
    # --- CareFlow additions ---
    duration_min = db.Column(db.Integer, default=15)
    visit_type = db.Column(db.String(30), default="Consultation")
    cancel_reason = db.Column(db.String(200), default="")
    reschedule_count = db.Column(db.Integer, default=0)
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _ts(default=utcnow)
    updated_at = _ts(onupdate=utcnow)
    __table_args__ = (
        Index("ix_appointment_doctor_day", "doctor_id", "appointment_date"),
        Index("ix_appointment_patient", "patient_id"),
        # DB-level double-booking guard for live appointments.
        Index("uq_appointment_doctor_slot_active", "doctor_id", "appointment_date", "appointment_time", unique=True,
              sqlite_where=text("status IN ('Scheduled','Checked-in')"),
              postgresql_where=text("status IN ('Scheduled','Checked-in')")),
    )


class Encounter(db.Model):
    __tablename__ = "encounter"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    encounter_type = db.Column(db.String(20), default="Outpatient", nullable=False)
    status = db.Column(db.String(20), default="Open", nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    chief_complaint = db.Column(db.String(300), default="")
    started_at = _ts(default=utcnow)
    ended_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    patient = db.relationship("Patient")
    doctor = db.relationship("Doctor")


class Admission(db.Model):
    __tablename__ = "admission"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    ward = db.Column(db.String(80), nullable=False)          # legacy display copy, kept in sync with bed assignment
    bed = db.Column(db.String(30), default="Unassigned")     # legacy display copy
    admitted_on = db.Column(db.String(10), nullable=False)
    discharged_on = db.Column(db.String(10), default="")
    status = db.Column(db.String(30), default="Admitted")
    notes = db.Column(db.Text, default="")
    patient = db.relationship("Patient")
    # --- CareFlow additions ---
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    responsible_doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"))
    admitted_at = _ts(default=utcnow)
    discharged_at = _ts()
    expected_discharge_on = db.Column(db.String(10), default="")
    reason = db.Column(db.Text, default="")
    discharge_status = db.Column(db.String(20), default="None")
    discharge_plan = db.Column(db.Text, default="")
    discharge_summary = db.Column(db.Text, default="")
    discharge_authorized_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    discharge_authorized_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    responsible_doctor = db.relationship("Doctor")
    __table_args__ = (
        Index("uq_admission_active_patient", "patient_id", unique=True,
              sqlite_where=text("status = 'Admitted'"), postgresql_where=text("status = 'Admitted'")),
    )


class BedAssignment(db.Model):
    """History of every bed a patient admission has occupied."""
    __tablename__ = "bed_assignment"
    id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"), nullable=False, index=True)
    bed_id = db.Column(db.Integer, db.ForeignKey("bed.id"), nullable=False, index=True)
    started_at = _ts(default=utcnow, nullable=False)
    ended_at = _ts()
    reason = db.Column(db.String(30), default="Admission")  # Admission | Transfer
    end_reason = db.Column(db.String(30), default="")        # Transfer | Discharge
    moved_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    note = db.Column(db.String(300), default="")
    admission = db.relationship("Admission", backref="bed_assignments")
    bed = db.relationship("Bed", backref="assignments")
    __table_args__ = (
        # A bed can have only one open assignment; an admission can occupy only one bed at a time.
        Index("uq_bed_assignment_open_bed", "bed_id", unique=True,
              sqlite_where=text("ended_at IS NULL"), postgresql_where=text("ended_at IS NULL")),
        Index("uq_bed_assignment_open_admission", "admission_id", unique=True,
              sqlite_where=text("ended_at IS NULL"), postgresql_where=text("ended_at IS NULL")),
    )


# =========================================================================== #
# Clinical documentation
# =========================================================================== #
class ClinicalNote(db.Model):
    __tablename__ = "clinical_note"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False)
    note_type = db.Column(db.String(30), default="Progress", nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Final", nullable=False)  # Final | Superseded
    amends_note_id = db.Column(db.Integer, db.ForeignKey("clinical_note.id"))
    amendment_reason = db.Column(db.String(300), default="")
    created_at = _created()
    author = db.relationship("AppUser")
    __table_args__ = (CheckConstraint("status IN ('Final','Superseded')", name="status_valid"),)


class CarePlan(db.Model):
    __tablename__ = "care_plan"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    title = db.Column(db.String(200), nullable=False)
    goals = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="Active", nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()


class CareTask(db.Model):
    __tablename__ = "care_task"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"), index=True)
    care_plan_id = db.Column(db.Integer, db.ForeignKey("care_plan.id"))
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(30), default="Other", nullable=False)
    assigned_role = db.Column(db.String(30), default="nurse")
    assigned_user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    due_at = _ts(index=True)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    priority = db.Column(db.String(20), default="Routine", nullable=False)
    notes = db.Column(db.Text, default="")
    completed_at = _ts()
    completed_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    patient = db.relationship("Patient")
    __table_args__ = (CheckConstraint("status IN ('Pending','Done','Cancelled')", name="status_valid"),)


class Handover(db.Model):
    __tablename__ = "handover"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    ward_id = db.Column(db.Integer, db.ForeignKey("ward.id"))
    kind = db.Column(db.String(20), default="Nursing", nullable=False)  # Nursing | Medical
    shift = db.Column(db.String(20), default="Day")
    situation = db.Column(db.Text, default="")
    background = db.Column(db.Text, default="")
    assessment = db.Column(db.Text, default="")
    recommendation = db.Column(db.Text, default="")
    is_auto_draft = db.Column(db.Boolean, default=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    reviewed_at = _ts()
    created_at = _created()
    patient = db.relationship("Patient")
    author = db.relationship("AppUser", foreign_keys=[author_id])


class IntakeOutput(db.Model):
    __tablename__ = "intake_output"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    kind = db.Column(db.String(10), nullable=False)  # Intake | Output
    item = db.Column(db.String(100), default="")
    amount_ml = db.Column(db.Float, nullable=False)
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    recorded_at = _ts(default=utcnow, nullable=False)
    __table_args__ = (CheckConstraint("kind IN ('Intake','Output')", name="kind_valid"), CheckConstraint("amount_ml >= 0", name="amount_nonneg"))


class FollowUp(db.Model):
    __tablename__ = "follow_up"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    due_on = db.Column(db.String(10), default="")
    instructions = db.Column(db.Text, default="")
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"))
    status = db.Column(db.String(20), default="Planned", nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()


# =========================================================================== #
# Observations, monitoring & alerts
# =========================================================================== #
class ObservationType(db.Model):
    __tablename__ = "observation_type"
    code = db.Column(db.String(30), primary_key=True)
    label = db.Column(db.String(80), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    plausible_min = db.Column(db.Float)   # typo guard, not a clinical threshold
    plausible_max = db.Column(db.Float)
    decimals = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class MonitoringDevice(db.Model):
    __tablename__ = "monitoring_device"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(60), default="Bedside monitor")
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), index=True)
    is_simulated = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    api_key_hash = db.Column(db.String(128))
    api_key_prefix = db.Column(db.String(12))
    last_seen_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()


class Observation(db.Model):
    __tablename__ = "observation"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    type_code = db.Column(db.String(30), db.ForeignKey("observation_type.code"), nullable=False)
    value_num = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    observed_at = _ts(nullable=False)
    recorded_at = _ts(default=utcnow, nullable=False)
    source = db.Column(db.String(12), default="manual", nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("monitoring_device.id"))
    recorded_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    validation_status = db.Column(db.String(20), default="Valid", nullable=False)
    supersedes_id = db.Column(db.Integer, db.ForeignKey("observation.id"))
    correction_reason = db.Column(db.String(300), default="")
    group_id = db.Column(db.String(36), default="")
    note = db.Column(db.String(300), default="")
    type = db.relationship("ObservationType")
    __table_args__ = (
        Index("ix_observation_patient_type_time", "patient_id", "type_code", "observed_at"),
        CheckConstraint("source IN ('manual','device','simulated')", name="source_valid"),
        CheckConstraint("validation_status IN ('Valid','Unverified','Corrected','Entered in error')", name="validation_valid"),
    )


class AlertRule(db.Model):
    __tablename__ = "alert_rule"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300), default="")
    rule_kind = db.Column(db.String(12), default="threshold", nullable=False)  # threshold | missing
    type_code = db.Column(db.String(30), db.ForeignKey("observation_type.code"))
    operator = db.Column(db.String(3), default=">")
    threshold = db.Column(db.Float)
    severity = db.Column(db.String(10), default="Warning", nullable=False)
    window_minutes = db.Column(db.Integer)           # for 'missing' rules
    cooldown_minutes = db.Column(db.Integer, default=30)
    active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)
    review_status = db.Column(db.String(12), default="Unreviewed", nullable=False)
    reviewed_by = db.Column(db.String(120), default="")
    reviewed_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    updated_at = _ts(default=utcnow, onupdate=utcnow)
    __table_args__ = (
        CheckConstraint("rule_kind IN ('threshold','missing')", name="kind_valid"),
        CheckConstraint("severity IN ('Info','Warning','Critical')", name="severity_valid"),
    )


class Alert(db.Model):
    __tablename__ = "alert"
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("alert_rule.id"), nullable=False)
    rule_version = db.Column(db.Integer, nullable=False)
    rule_snapshot = db.Column(db.JSON)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    observation_id = db.Column(db.Integer, db.ForeignKey("observation.id"))
    severity = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(12), default="Open", nullable=False)
    message = db.Column(db.String(300), default="")
    triggered_at = _ts(default=utcnow, nullable=False)
    last_triggered_at = _ts(default=utcnow)
    occurrences = db.Column(db.Integer, default=1, nullable=False)
    from_simulated_data = db.Column(db.Boolean, default=False, nullable=False)
    responder_user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    responder_role = db.Column(db.String(30), default="nurse")
    ack_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    ack_at = _ts()
    escalated_at = _ts()
    escalated_to_role = db.Column(db.String(30), default="")
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    resolved_at = _ts()
    resolution_note = db.Column(db.String(300), default="")
    rule = db.relationship("AlertRule")
    patient = db.relationship("Patient")
    __table_args__ = (
        Index("uq_alert_open_patient_rule", "patient_id", "rule_id", unique=True,
              sqlite_where=text("status <> 'Resolved'"), postgresql_where=text("status <> 'Resolved'")),
        CheckConstraint("status IN ('Open','Acknowledged','Escalated','Resolved')", name="status_valid"),
    )


class Notification(db.Model):
    """In-app notification. (Email/SMS delivery is not implemented.)"""
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), index=True)
    role = db.Column(db.String(30), index=True)
    kind = db.Column(db.String(40), nullable=False)
    severity = db.Column(db.String(10), default="Info")
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.String(400), default="")
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    ref_type = db.Column(db.String(30), default="")
    ref_id = db.Column(db.Integer)
    delivery = db.Column(db.String(12), default="in-app")
    created_at = _created()
    read_at = _ts()


class CriticalAck(db.Model):
    """Critical laboratory / radiology result notification with acknowledgment + escalation."""
    __tablename__ = "critical_ack"
    id = db.Column(db.Integer, primary_key=True)
    source_type = db.Column(db.String(12), nullable=False)  # lab | radiology
    source_id = db.Column(db.Integer, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    summary = db.Column(db.String(300), default="")
    notify_user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    status = db.Column(db.String(12), default="Pending", nullable=False)
    created_at = _created()
    ack_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    ack_at = _ts()
    ack_note = db.Column(db.String(300), default="")
    escalated_at = _ts()
    escalated_to_role = db.Column(db.String(30), default="")
    patient = db.relationship("Patient")
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_critical_ack_source"),
        CheckConstraint("status IN ('Pending','Acknowledged','Escalated')", name="status_valid"),
    )


# =========================================================================== #
# Laboratory
# =========================================================================== #
class LabReport(db.Model):
    __tablename__ = "lab_report"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    test_name = db.Column(db.String(120), nullable=False)
    sample_date = db.Column(db.String(10), nullable=False)
    result = db.Column(db.Text, default="Pending")   # legacy summary text
    status = db.Column(db.String(30), default="Pending")
    ordered_by = db.Column(db.String(120), default="")
    patient = db.relationship("Patient")
    # --- CareFlow additions ---
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    ordered_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    accession_no = db.Column(db.String(30), unique=True)
    priority = db.Column(db.String(10), default="Routine")
    specimen_type = db.Column(db.String(60), default="")
    clinical_info = db.Column(db.String(300), default="")
    ordered_at = _ts(default=utcnow)
    collected_at = _ts()
    collected_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    received_at = _ts()
    resulted_at = _ts()
    resulted_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    verified_at = _ts()
    verified_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    released_at = _ts()
    released_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    rejected_at = _ts()
    rejected_reason = db.Column(db.String(300), default="")
    amendment_count = db.Column(db.Integer, default=0)
    __table_args__ = (Index("ix_lab_report_patient_status", "patient_id", "status"),)


class LabResult(db.Model):
    __tablename__ = "lab_result"
    id = db.Column(db.Integer, primary_key=True)
    lab_report_id = db.Column(db.Integer, db.ForeignKey("lab_report.id"), nullable=False, index=True)
    analyte = db.Column(db.String(120), nullable=False)
    value_num = db.Column(db.Float)
    value_text = db.Column(db.String(200), default="")
    unit = db.Column(db.String(30), default="")
    ref_low = db.Column(db.Float)
    ref_high = db.Column(db.Float)
    ref_text = db.Column(db.String(100), default="")
    critical_low = db.Column(db.Float)
    critical_high = db.Column(db.Float)
    flag = db.Column(db.String(20), default="Not assessed", nullable=False)
    is_critical = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(12), default="Entered", nullable=False)  # Entered | Final | Superseded
    version = db.Column(db.Integer, default=1, nullable=False)
    supersedes_id = db.Column(db.Integer, db.ForeignKey("lab_result.id"))
    correction_reason = db.Column(db.String(300), default="")
    entered_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    entered_at = _created()
    report = db.relationship("LabReport", backref="results")


# =========================================================================== #
# Radiology
# =========================================================================== #
class RadiologyRecord(db.Model):
    __tablename__ = "radiology_record"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    modality = db.Column(db.String(50), nullable=False)
    study_date = db.Column(db.String(10), nullable=False)
    findings = db.Column(db.Text, default="")
    report_status = db.Column(db.String(30), default="Draft")
    patient = db.relationship("Patient")
    # --- CareFlow additions ---
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    ordered_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    order_status = db.Column(db.String(12), default="Ordered")
    study_description = db.Column(db.String(200), default="")
    indication = db.Column(db.String(300), default="")
    priority = db.Column(db.String(10), default="Routine")
    scheduled_at = _ts()
    performed_at = _ts()
    performed_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    impression = db.Column(db.Text, default="")
    recommendations = db.Column(db.Text, default="")
    reported_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    reported_at = _ts()
    authorized_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    authorized_at = _ts()
    urgent_finding = db.Column(db.Boolean, default=False)
    amendment_count = db.Column(db.Integer, default=0)
    ordered_at = _ts(default=utcnow)
    __table_args__ = (Index("ix_radiology_patient", "patient_id"),)


class RadiologyReportVersion(db.Model):
    __tablename__ = "radiology_report_version"
    id = db.Column(db.Integer, primary_key=True)
    radiology_id = db.Column(db.Integer, db.ForeignKey("radiology_record.id"), nullable=False, index=True)
    version = db.Column(db.Integer, nullable=False)
    findings = db.Column(db.Text, default="")
    impression = db.Column(db.Text, default="")
    recommendations = db.Column(db.Text, default="")
    status = db.Column(db.String(12), default="Draft")
    change_reason = db.Column(db.String(300), default="")
    author_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()


# =========================================================================== #
# Pharmacy
# =========================================================================== #
class Medicine(db.Model):
    __tablename__ = "medicine"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    category = db.Column(db.String(80), default="General")
    stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    unit_price = db.Column(db.Float, default=0)
    expiry_date = db.Column(db.String(10), default="")
    # --- CareFlow additions ---
    generic_name = db.Column(db.String(120), default="")
    strength = db.Column(db.String(40), default="")
    form = db.Column(db.String(40), default="")
    batch_no = db.Column(db.String(40), default="")
    is_active = db.Column(db.Boolean, default=True)
    __table_args__ = (CheckConstraint("stock >= 0", name="stock_nonneg"),)


class Prescription(db.Model):
    """Medication order (what was prescribed). Dispensing and administration are separate entities."""
    __tablename__ = "prescription"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    doctor_name = db.Column(db.String(120), default="")
    medicine = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(120), default="As directed by clinician")
    instructions = db.Column(db.Text, default="")
    created_at = _created()
    patient = db.relationship("Patient")
    # --- CareFlow additions ---
    ordered_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicine.id"))
    route = db.Column(db.String(30), default="")
    frequency = db.Column(db.String(60), default="")
    duration_days = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    is_prn = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(24), default="Ordered")
    allergy_override_reason = db.Column(db.String(300), default="")
    warnings = db.Column(db.JSON)
    verified_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    verified_at = _ts()
    cancelled_reason = db.Column(db.String(300), default="")
    dispensed_quantity = db.Column(db.Integer, default=0)
    __table_args__ = (Index("ix_prescription_patient_status", "patient_id", "status"),)


class DispenseEvent(db.Model):
    __tablename__ = "dispense_event"
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescription.id"), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicine.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dispensed_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False)
    dispensed_at = _ts(default=utcnow, nullable=False)
    warnings_acknowledged = db.Column(db.JSON)
    note = db.Column(db.String(300), default="")
    __table_args__ = (CheckConstraint("quantity > 0", name="qty_positive"),)


class MedicationAdministration(db.Model):
    """What a nurse actually gave (or withheld) - distinct from ordering and dispensing."""
    __tablename__ = "medication_administration"
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescription.id"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    scheduled_at = _ts()
    administered_at = _ts()
    status = db.Column(db.String(12), default="Scheduled", nullable=False)
    dose_given = db.Column(db.String(60), default="")
    identity_verified = db.Column(db.Boolean, default=False)
    allergies_checked = db.Column(db.Boolean, default=False)
    administered_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    note = db.Column(db.String(300), default="")
    created_at = _created()


class StockMovement(db.Model):
    __tablename__ = "stock_movement"
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicine.id"), nullable=False, index=True)
    delta = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(30), nullable=False)  # dispense | restock | adjustment | expired
    ref_type = db.Column(db.String(30), default="")
    ref_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()


class MedReconciliation(db.Model):
    __tablename__ = "med_reconciliation"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    pharmacist_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    items = db.Column(db.JSON)
    notes = db.Column(db.Text, default="")
    created_at = _created()


# =========================================================================== #
# Billing & insurance
# =========================================================================== #
class Bill(db.Model):
    __tablename__ = "bill"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    consultation = db.Column(db.Float, default=0)
    laboratory = db.Column(db.Float, default=0)
    pharmacy = db.Column(db.Float, default=0)
    room = db.Column(db.Float, default=0)
    insurance_provider = db.Column(db.String(120), default="")
    insurance_status = db.Column(db.String(40), default="Not submitted")
    paid = db.Column(db.Boolean, default=False)
    created_at = _created()
    patient = db.relationship("Patient")
    # --- CareFlow additions ---
    other_charges = db.Column(db.Float, default=0)
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    status = db.Column(db.String(12), default="Issued")  # Issued | Void
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    voided_at = _ts()

    @property
    def total(self):
        return round(sum((getattr(self, k) or 0) for k in ("consultation", "laboratory", "pharmacy", "room", "other_charges")), 2)


class Payment(db.Model):
    __tablename__ = "payment"
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bill.id"), nullable=False, index=True)
    kind = db.Column(db.String(10), default="Payment", nullable=False)  # Payment | Refund
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(30), default="Cash")
    reference = db.Column(db.String(80), default="")
    reason = db.Column(db.String(300), default="")
    received_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    bill = db.relationship("Bill", backref="payments")
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"), CheckConstraint("kind IN ('Payment','Refund')", name="kind_valid"))


class BillAdjustment(db.Model):
    __tablename__ = "bill_adjustment"
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bill.id"), nullable=False, index=True)
    kind = db.Column(db.String(20), nullable=False)  # Discount | Write-off | Correction
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(300), nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    approved_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    bill = db.relationship("Bill", backref="adjustments")
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)


class InsuranceClaim(db.Model):
    __tablename__ = "insurance_claim"
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bill.id"), nullable=False, index=True)
    provider = db.Column(db.String(120), nullable=False)
    policy_no = db.Column(db.String(60), default="")
    claim_no = db.Column(db.String(60), default="")
    amount_claimed = db.Column(db.Float, default=0)
    amount_approved = db.Column(db.Float)
    status = db.Column(db.String(20), default="Draft", nullable=False)
    notes = db.Column(db.String(300), default="")
    submitted_at = _ts()
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    updated_at = _ts(default=utcnow, onupdate=utcnow)
    bill = db.relationship("Bill", backref="claims")


# =========================================================================== #
# Documents (private storage + extracted text)
# =========================================================================== #
class MedicalDocument(db.Model):
    __tablename__ = "medical_document"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("encounter.id"))
    admission_id = db.Column(db.Integer, db.ForeignKey("admission.id"))
    lab_report_id = db.Column(db.Integer, db.ForeignKey("lab_report.id"))
    radiology_id = db.Column(db.Integer, db.ForeignKey("radiology_record.id"))
    doc_type = db.Column(db.String(40), default="Other", nullable=False)
    title = db.Column(db.String(200), nullable=False)
    original_filename = db.Column(db.String(200), default="")
    mime_type = db.Column(db.String(80), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    sha256 = db.Column(db.String(64), nullable=False)
    storage_backend = db.Column(db.String(12), default="local", nullable=False)
    storage_key = db.Column(db.String(200), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False)
    uploaded_at = _created()
    processing_status = db.Column(db.String(16), default="Pending", nullable=False)  # Pending | Processed | Failed
    extraction_status = db.Column(db.String(24), default="Pending", nullable=False)   # Pending | Complete | Partial | Failed | Not applicable | OCR unavailable
    extraction_method = db.Column(db.String(24), default="")                          # embedded-text | ocr | mixed | plain-text | none
    extraction_quality = db.Column(db.Float)                                          # 0..1
    extraction_note = db.Column(db.String(300), default="")
    page_count = db.Column(db.Integer, default=0)
    review_status = db.Column(db.String(20), default="Unreviewed", nullable=False)    # Unreviewed | Reviewed | Needs correction
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    reviewed_at = _ts()
    version = db.Column(db.Integer, default=1, nullable=False)
    supersedes_id = db.Column(db.Integer, db.ForeignKey("medical_document.id"))
    is_image = db.Column(db.Boolean, default=False)
    reprocess_count = db.Column(db.Integer, default=0)
    patient_visible = db.Column(db.Boolean, default=False, nullable=False, server_default=db.false())  # shown in the patient's own portal
    patient = db.relationship("Patient")
    uploaded_by = db.relationship("AppUser", foreign_keys=[uploaded_by_id])


class Deliverable(db.Model):
    """Something the hospital gives a patient, tracked in digital and/or physical form (report, film/CD, invoice, label...)."""
    __tablename__ = "patient_deliverable"
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    kind = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    ref_type = db.Column(db.String(20), default="")          # lab | radiology | prescription | bill | admission | ""
    ref_id = db.Column(db.Integer)
    document_id = db.Column(db.Integer, db.ForeignKey("medical_document.id"))
    digital_available = db.Column(db.Boolean, default=False, nullable=False)
    physical_status = db.Column(db.String(24), default="Not requested", nullable=False)
    physical_note = db.Column(db.String(300), default="")
    received_by_name = db.Column(db.String(120), default="")
    handed_over_at = _ts()
    handed_over_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    created_at = _created()
    updated_at = _ts(default=utcnow, onupdate=utcnow)
    document = db.relationship("MedicalDocument")
    handed_over_by = db.relationship("AppUser", foreign_keys=[handed_over_by_id])
    __table_args__ = (
        CheckConstraint("physical_status IN ('Not requested','Requested','Ready for collection','Handed over')", name="physical_status_valid"),
        UniqueConstraint("patient_id", "ref_type", "ref_id", "kind", name="uq_deliverable_ref"),
    )


class DocumentPage(db.Model):
    __tablename__ = "document_page"
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("medical_document.id"), nullable=False, index=True)
    page_no = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, default="")
    method = db.Column(db.String(16), default="")
    confidence = db.Column(db.Float)
    char_count = db.Column(db.Integer, default=0)
    corrected_text = db.Column(db.Text)           # reviewer correction; original extraction preserved in `text`
    corrected_by_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    document = db.relationship("MedicalDocument", backref="pages")
    __table_args__ = (UniqueConstraint("document_id", "page_no", name="uq_document_page"),)


# =========================================================================== #
# AI assistant
# =========================================================================== #
class AiConversation(db.Model):
    __tablename__ = "ai_conversation"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    title = db.Column(db.String(200), default="")
    created_at = _created()
    updated_at = _ts(default=utcnow, onupdate=utcnow)
    deleted_at = _ts()
    messages = db.relationship("AiMessage", backref="conversation", order_by="AiMessage.id", cascade="all, delete-orphan")


class AiMessage(db.Model):
    __tablename__ = "ai_message"
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.String(36), db.ForeignKey("ai_conversation.id"), nullable=False, index=True)
    role = db.Column(db.String(10), nullable=False)  # user | assistant
    content = db.Column(db.Text, nullable=False)
    mode = db.Column(db.String(12), default="simple")
    status = db.Column(db.String(24), default="ok")
    sources = db.Column(db.JSON)
    limitations = db.Column(db.JSON)
    provider = db.Column(db.String(30), default="")
    model = db.Column(db.String(60), default="")
    created_at = _created()


# =========================================================================== #
# Audit
# =========================================================================== #
class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(120), nullable=False)
    details = db.Column(db.Text, default="")
    created_at = _created()
    # --- CareFlow additions ---
    user_id = db.Column(db.Integer, db.ForeignKey("app_user.id"))
    user_role = db.Column(db.String(30), default="")
    category = db.Column(db.String(16), default="system")  # access | clinical | admin | security | export | ai | system
    entity_type = db.Column(db.String(40), default="")
    entity_id = db.Column(db.Integer)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"))
    outcome = db.Column(db.String(10), default="success")
    ip = db.Column(db.String(64), default="")
    request_id = db.Column(db.String(36), default="")
    # --- tamper evidence: each row stores the previous row's hash and its own (see careflow/audit_chain.py) ---
    prev_hash = db.Column(db.String(64))
    entry_hash = db.Column(db.String(64))
    __table_args__ = (Index("ix_audit_log_created", "created_at"), Index("ix_audit_log_patient", "patient_id"))

