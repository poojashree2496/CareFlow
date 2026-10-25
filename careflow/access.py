"""Role permissions and per-patient (resource-level) authorisation.

Authorisation is always decided here on the server. Nothing the browser sends
(role, patient id, workspace name) is trusted without being re-checked.
"""
from __future__ import annotations

from functools import wraps

from flask import g, has_request_context, request
from sqlalchemy import and_, exists, or_, select

from . import constants as C
from .extensions import db
from .models import (Admission, Appointment, AppUser, Bed, BedAssignment, Bill, Encounter, LabReport,
                     Patient, PatientAssignment, Prescription, RadiologyRecord)
from .utils import ApiError

# --------------------------------------------------------------------------- #
# Role -> permissions
# --------------------------------------------------------------------------- #
_CLINICAL_READ = {"obs.read", "lab.read", "rad.read", "rx.read", "doc.read", "ai.use", "alert.view"}

ROLE_PERMS: dict[str, set[str]] = {
    C.SUPER_ADMIN: {
        "patient.register", "patient.update", "patient.registry", "appointment.manage", "admission.manage", "bed.operate",
        "bed.configure", "billing.read", "billing.write", "billing.adjust", "billing.refund", "report.view", "audit.view",
        "security.view", "user.manage", "user.manage_privileged", "config.manage", "assign.manage", "export.run",
        "inventory.manage", "alert.configure", "sim.run", "doc.upload", "doc.review", "doc.read", "ai.use", "obs.read",
        "lab.read", "rad.read", "rx.read", "alert.view", "patient.verify_identity", "workspace.admin",
    },
    C.HOSPITAL_ADMIN: {
        "patient.register", "patient.update", "patient.registry", "appointment.manage", "admission.manage", "bed.operate",
        "bed.configure", "billing.read", "billing.write", "billing.adjust", "billing.refund", "report.view", "audit.view", "user.manage",
        "config.manage", "assign.manage", "export.run", "inventory.manage", "patient.verify_identity", "workspace.admin", "alert.view",
    },
    C.DOCTOR: _CLINICAL_READ | {
        "patient.register", "patient.update", "patient.registry", "appointment.manage", "encounter.manage", "admission.manage",
        "bed.operate", "note.write", "problem.write", "allergy.write", "task.write", "task.complete", "handover.write",
        "obs.record", "alert.act", "lab.order", "rx.prescribe", "rad.order", "discharge.authorize", "doc.upload",
        "followup.write", "sim.run", "report.view", "care.plan", "doc.review",
    },
    C.NURSE: _CLINICAL_READ | {
        "patient.register", "patient.registry", "appointment.checkin", "admission.manage", "bed.operate", "task.write",
        "task.complete", "handover.write", "obs.record", "alert.act", "rx.administer", "io.record", "allergy.write", "note.write",
        "doc.upload", "sim.run", "patient.verify_identity", "report.view",
    },
    C.LAB_STAFF: {"lab.read", "lab.process", "lab.verify", "doc.read", "doc.upload", "doc.review", "report.view", "ai.use", "alert.view"},
    C.PHARMACIST: {"rx.read", "rx.dispense", "rx.verify", "inventory.manage", "doc.read", "doc.upload", "report.view", "ai.use"},
    C.RADIOLOGY_STAFF: {"rad.read", "rad.perform", "rad.report", "rad.authorize", "doc.read", "doc.upload", "doc.review", "report.view", "ai.use"},
    C.BILLING_STAFF: {"billing.read", "billing.write", "billing.adjust", "report.view", "patient.registry", "patient.update_insurance", "doc.read", "doc.upload", "ai.use"},
    # A patient may only read their own record through /api/portal and ask the assistant about it. No write permission exists.
    C.PATIENT: {"ai.use", "portal.view"},
}
# Everyone who handles a patient's reports/medicines/invoices can record physical hand-over of the printed copy.
for _r in (C.SUPER_ADMIN, C.HOSPITAL_ADMIN, C.DOCTOR, C.NURSE, C.LAB_STAFF, C.PHARMACIST, C.RADIOLOGY_STAFF, C.BILLING_STAFF):
    ROLE_PERMS[_r] = ROLE_PERMS[_r] | {"deliverable.manage"}
# Administrators can read submitted lab/radiology reports (released/final results only; they cannot process or edit them).
ROLE_PERMS[C.HOSPITAL_ADMIN] = ROLE_PERMS[C.HOSPITAL_ADMIN] | {"lab.read", "rad.read", "doc.read"}

# Workspaces (UI areas) per role; the server returns only these to the client.
ROLE_WORKSPACES: dict[str, list[str]] = {
    C.SUPER_ADMIN: ["admin", "doctor", "bedboard", "nurse", "lab", "pharmacy", "radiology", "billing", "patients", "appointments", "ai"],
    C.HOSPITAL_ADMIN: ["admin", "bedboard", "lab", "radiology", "patients", "appointments", "billing"],
    C.DOCTOR: ["doctor", "bedboard", "patients", "appointments", "ai"],
    C.NURSE: ["nurse", "bedboard", "patients", "ai"],
    C.LAB_STAFF: ["lab", "ai"],
    C.PHARMACIST: ["pharmacy", "ai"],
    C.RADIOLOGY_STAFF: ["radiology", "ai"],
    C.BILLING_STAFF: ["billing", "patients", "ai"],
    C.PATIENT: ["portal", "ai"],
}
WORKSPACE_LABELS = {
    "admin": "Operations Console", "doctor": "Clinical Command Center", "bedboard": "Live Bedboard",
    "nurse": "Nursing Workbench", "lab": "Laboratory", "pharmacy": "Pharmacy", "radiology": "Radiology",
    "billing": "Billing & Insurance", "portal": "My Care", "patients": "Patients", "appointments": "Appointments", "ai": "CareFlow AI",
}

# Patient-level scopes granted by role once a care relationship exists.
ROLE_SCOPES: dict[str, set[str]] = {
    C.DOCTOR: {"identity", "contact", "allergies", "clinical", "observations", "labs", "radiology", "meds", "documents"},
    C.NURSE: {"identity", "contact", "allergies", "clinical", "observations", "labs", "meds", "documents"},
    C.LAB_STAFF: {"identity", "labs", "documents"},
    C.PHARMACIST: {"identity", "allergies", "meds", "documents"},
    C.RADIOLOGY_STAFF: {"identity", "radiology", "documents"},
    C.BILLING_STAFF: {"identity", "contact", "billing", "documents"},
    C.HOSPITAL_ADMIN: {"identity", "contact", "billing", "labs", "radiology", "documents"},
}
# A patient reads their own record only. Staff-internal material (clinical notes, drafts, unreleased results) is filtered where it is served.
PATIENT_SCOPES = {"identity", "contact", "allergies", "clinical", "observations", "labs", "radiology", "meds", "billing", "documents"}
ALL_SCOPES = {"identity", "contact", "allergies", "clinical", "observations", "labs", "radiology", "meds", "billing", "documents"}

# Which document types each role may see.
DOC_TYPES_BY_ROLE = {
    C.LAB_STAFF: {"Laboratory report"},
    C.RADIOLOGY_STAFF: {"Radiology report"},
    C.PHARMACIST: {"Prescription"},
    C.BILLING_STAFF: {"Insurance"},
    C.HOSPITAL_ADMIN: {"Laboratory report", "Radiology report", "Discharge summary", "Insurance"},
}

# Evidence kinds the AI may retrieve -> scope required.
AI_EVIDENCE_SCOPE = {
    "lab": "labs", "radiology": "radiology", "medication": "meds", "allergy": "allergies", "vitals": "observations",
    "admission": "clinical", "note": "clinical", "problem": "clinical", "followup": "clinical", "document": "documents",
    "billing": "billing", "demographics": "identity",
}


def has_perm(user, perm: str) -> bool:
    return bool(user) and user.is_active and perm in ROLE_PERMS.get(user.role, set())


def workspaces_for(user) -> list[dict]:
    return [{"id": w, "label": WORKSPACE_LABELS[w]} for w in ROLE_WORKSPACES.get(user.role, [])]


def require_perm(perm: str):
    """Route decorator: authenticated user must hold ``perm`` (checked on every request)."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            user = getattr(g, "user", None)
            if user is None:
                raise ApiError("Authentication required", 401)
            if not has_perm(user, perm):
                from .audit import audit
                audit("access.denied", category="security", outcome="denied", details=f"perm={perm} route={fn.__name__}", commit=True)
                raise ApiError("You do not have permission to perform this action", 403)
            return fn(*a, **kw)
        return wrapper
    return deco


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if getattr(g, "user", None) is None:
            raise ApiError("Authentication required", 401)
        return fn(*a, **kw)
    return wrapper


# --------------------------------------------------------------------------- #
# Patient scope resolution
# --------------------------------------------------------------------------- #
def bulk_scopes(user, patient_ids) -> dict[int, frozenset]:
    """Compute the scopes ``user`` holds on each patient id using a handful of set queries."""
    pids = {int(p) for p in patient_ids if p is not None}
    if not pids or user is None or not user.is_active:
        return {}
    role = user.role
    if role == C.PATIENT:
        own = getattr(user, "patient_id", None)
        return {own: frozenset(PATIENT_SCOPES)} if own in pids else {}
    if role == C.SUPER_ADMIN:
        return {p: frozenset(ALL_SCOPES) for p in pids}
    base = ROLE_SCOPES.get(role, set())
    if not base:
        return {}
    ex = db.session.execute
    out: dict[int, frozenset] = {}

    if role in (C.BILLING_STAFF, C.HOSPITAL_ADMIN):
        return {p: frozenset(base) for p in pids}

    related: set[int] = set()
    # explicit, active assignments apply to clinicians
    if role in (C.DOCTOR, C.NURSE):
        related |= set(ex(select(PatientAssignment.patient_id).where(
            PatientAssignment.user_id == user.id, PatientAssignment.active.is_(True), PatientAssignment.patient_id.in_(pids))).scalars())
    if role == C.DOCTOR and user.doctor_id:
        d = user.doctor_id
        related |= set(ex(select(Admission.patient_id).where(
            Admission.responsible_doctor_id == d, Admission.status == "Admitted", Admission.patient_id.in_(pids))).scalars())
        related |= set(ex(select(Appointment.patient_id).where(
            Appointment.doctor_id == d, Appointment.status != "Cancelled", Appointment.patient_id.in_(pids))).scalars())
        related |= set(ex(select(Encounter.patient_id).where(
            Encounter.doctor_id == d, Encounter.patient_id.in_(pids))).scalars())
    if role == C.NURSE and user.ward_id:
        related |= set(ex(
            select(Admission.patient_id)
            .join(BedAssignment, BedAssignment.admission_id == Admission.id)
            .join(Bed, Bed.id == BedAssignment.bed_id)
            .where(Admission.status == "Admitted", BedAssignment.ended_at.is_(None), Bed.ward_id == user.ward_id,
                   Admission.patient_id.in_(pids))).scalars())
    if role == C.LAB_STAFF:
        related |= set(ex(select(LabReport.patient_id).where(LabReport.patient_id.in_(pids))).scalars())
    if role == C.PHARMACIST:
        related |= set(ex(select(Prescription.patient_id).where(Prescription.patient_id.in_(pids))).scalars())
    if role == C.RADIOLOGY_STAFF:
        related |= set(ex(select(RadiologyRecord.patient_id).where(RadiologyRecord.patient_id.in_(pids))).scalars())

    for p in related:
        out[p] = frozenset(base)
    return out


def patient_scopes(user, patient_id: int) -> frozenset:
    # Cache per HTTP request (never per application context, which may outlive a request in tests/CLI).
    if not has_request_context():
        return bulk_scopes(user, [patient_id]).get(patient_id, frozenset())
    cache = request.environ.setdefault("careflow.scope_cache", {})
    key = (getattr(user, "id", None), patient_id)
    if key not in cache:
        cache[key] = bulk_scopes(user, [patient_id]).get(patient_id, frozenset())
    return cache[key]


def get_authorized_patient(patient_id: int, *scopes: str, user=None) -> Patient:
    """Load a patient the current user may access with every requested scope.

    Returns 404 when the user has no relationship with the patient at all (does not
    reveal existence) and 403 when they lack the specific scope.
    """
    user = user or getattr(g, "user", None)
    if user is None:
        raise ApiError("Authentication required", 401)
    patient = db.session.get(Patient, patient_id)
    held = patient_scopes(user, patient_id) if patient else frozenset()
    if patient is None or "identity" not in held:
        raise ApiError("Patient not found", 404)
    missing = [sc for sc in scopes if sc not in held]
    if missing:
        from .audit import audit
        audit("access.denied", category="security", outcome="denied", patient_id=patient_id,
              details=f"missing scope(s): {','.join(missing)}", commit=True)
        raise ApiError("You do not have access to this part of the patient record", 403)
    if user.role == C.SUPER_ADMIN and any(sc in ("clinical", "labs", "radiology", "meds", "observations", "documents") for sc in scopes):
        from .audit import audit
        audit("privileged.clinical_access", category="access", patient_id=patient_id, entity_type="patient", entity_id=patient_id,
              details=f"super_admin accessed {','.join(scopes)}")
    return patient


def can_see_doc_type(user, doc_type: str) -> bool:
    allowed = DOC_TYPES_BY_ROLE.get(user.role)
    return allowed is None or doc_type in allowed


def visible_patient_filter(user):
    """SQLAlchemy criterion limiting Patient rows to those the user holds 'identity' scope on."""
    role = user.role
    if role == C.PATIENT:
        return Patient.id == user.patient_id if user.patient_id else False
    if role in (C.SUPER_ADMIN, C.HOSPITAL_ADMIN, C.BILLING_STAFF):
        return True
    conds = []
    if role in (C.DOCTOR, C.NURSE):
        conds.append(exists().where(and_(PatientAssignment.patient_id == Patient.id, PatientAssignment.user_id == user.id, PatientAssignment.active.is_(True))))
    if role == C.DOCTOR and user.doctor_id:
        d = user.doctor_id
        conds.append(exists().where(and_(Admission.patient_id == Patient.id, Admission.responsible_doctor_id == d, Admission.status == "Admitted")))
        conds.append(exists().where(and_(Appointment.patient_id == Patient.id, Appointment.doctor_id == d, Appointment.status != "Cancelled")))
        conds.append(exists().where(and_(Encounter.patient_id == Patient.id, Encounter.doctor_id == d)))
    if role == C.NURSE and user.ward_id:
        conds.append(exists().where(and_(
            Admission.patient_id == Patient.id, Admission.status == "Admitted",
            BedAssignment.admission_id == Admission.id, BedAssignment.ended_at.is_(None),
            Bed.id == BedAssignment.bed_id, Bed.ward_id == user.ward_id)))
    if role == C.LAB_STAFF:
        conds.append(exists().where(LabReport.patient_id == Patient.id))
    if role == C.PHARMACIST:
        conds.append(exists().where(Prescription.patient_id == Patient.id))
    if role == C.RADIOLOGY_STAFF:
        conds.append(exists().where(RadiologyRecord.patient_id == Patient.id))
    return or_(*conds) if conds else False


def patient_view(user, patient: Patient, scopes: frozenset) -> dict:
    """Field-level filtering of the patient record according to scopes."""
    from .utils import iso, age_from_dob
    out = {"id": patient.id, "patient_code": patient.patient_code, "name": patient.name, "dob": patient.dob,
           "age": age_from_dob(patient.dob), "gender": patient.gender, "blood_group": patient.blood_group,
           "data_origin": patient.data_origin, "identity_verified": bool(patient.identity_verified)}
    if "contact" in scopes:
        out.update(phone=patient.phone, email=patient.email, address=patient.address,
                   emergency_contact=patient.emergency_contact, emergency_contact_phone=patient.emergency_contact_phone,
                   emergency_contact_relation=patient.emergency_contact_relation, consent_data_sharing=bool(patient.consent_data_sharing),
                   consent_notes=patient.consent_notes)
    if "allergies" in scopes:
        out["allergies_text"] = patient.allergies
    if "clinical" in scopes:
        out["medical_history"] = patient.medical_history
    if "billing" in scopes:
        out.update(insurance_provider=patient.insurance_provider, insurance_policy_no=patient.insurance_policy_no)
    out["identifier_label"] = patient.identifier_label
    out["identifier_last4"] = patient.identifier_last4
    out["identity_verified_at"] = iso(patient.identity_verified_at)
    out["scopes"] = sorted(scopes)
    return out
