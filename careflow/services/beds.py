"""Admission, bed allocation, transfer and discharge workflows.

Consistency is enforced twice: row locks + status checks inside a transaction,
and partial unique indexes (one open assignment per bed / per admission) in the
database, so concurrent allocation attempts cannot both succeed.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from ..audit import audit
from ..constants import BED_MANUAL_TRANSITIONS
from ..extensions import db
from ..models import (Admission, Alert, Bed, BedAssignment, CareTask, Doctor, Encounter, Patient, Ward, utcnow)
from ..utils import ApiError


def _lock_bed(bed_id: int) -> Bed:
    bed = db.session.execute(select(Bed).where(Bed.id == bed_id).with_for_update()).scalar_one_or_none()
    if bed is None or not bed.is_active:
        raise ApiError("Bed not found or inactive", 404)
    return bed


def current_assignment(admission_id: int):
    return db.session.execute(
        select(BedAssignment).where(BedAssignment.admission_id == admission_id, BedAssignment.ended_at.is_(None))
    ).scalar_one_or_none()


def _flush_or_conflict():
    try:
        db.session.flush()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("That bed or admission was just changed by someone else. Refresh and retry.", 409)
    except OperationalError as exc:
        db.session.rollback()
        if "locked" in str(exc).lower():
            raise ApiError("The database is busy with a competing update. Please retry.", 409)
        raise


def _sync_legacy(admission: Admission, bed: Bed | None):
    if bed is None:
        admission.bed = "Unassigned"
        return
    admission.ward = bed.ward.name
    admission.bed = bed.code


def _occupy(admission: Admission, bed: Bed, user, reason: str, note: str = ""):
    if bed.status not in ("Available", "Reserved"):
        raise ApiError(f"Bed {bed.code} is {bed.status} and cannot be allocated", 409)
    if db.session.execute(select(BedAssignment.id).where(BedAssignment.bed_id == bed.id, BedAssignment.ended_at.is_(None))).first():
        raise ApiError(f"Bed {bed.code} already has a patient assigned", 409)
    db.session.add(BedAssignment(admission_id=admission.id, bed_id=bed.id, reason=reason, moved_by_id=getattr(user, "id", None), note=note[:300]))
    bed.status = "Occupied"
    bed.status_note = ""
    bed.status_changed_at = utcnow()
    _sync_legacy(admission, bed)
    _flush_or_conflict()


def admit(patient: Patient, *, user, ward_name: str = "", bed_id: int | None = None, doctor_id: int | None = None,
          admitted_on: str = "", reason: str = "", notes: str = "", expected_discharge_on: str = "") -> Admission:
    if db.session.execute(select(Admission.id).where(Admission.patient_id == patient.id, Admission.status == "Admitted")).first():
        raise ApiError("Patient already has an active admission", 409)
    doctor = None
    if doctor_id:
        doctor = db.session.get(Doctor, doctor_id)
        if not doctor:
            raise ApiError("Responsible doctor not found", 404)
    bed = None
    if bed_id:
        bed = _lock_bed(bed_id)
        ward_name = bed.ward.name
    if not ward_name:
        raise ApiError("A ward or a bed is required for admission")
    enc = Encounter(patient_id=patient.id, encounter_type="Inpatient", status="Open", doctor_id=doctor_id,
                    chief_complaint=reason[:300], created_by_id=getattr(user, "id", None))
    db.session.add(enc)
    db.session.flush()
    adm = Admission(patient_id=patient.id, ward=ward_name, bed="Unassigned", admitted_on=admitted_on or date.today().isoformat(),
                    admitted_at=utcnow(), notes=notes, reason=reason, encounter_id=enc.id, responsible_doctor_id=doctor_id,
                    expected_discharge_on=expected_discharge_on, status="Admitted", discharge_status="None",
                    created_by_id=getattr(user, "id", None))
    db.session.add(adm)
    _flush_or_conflict()
    if bed:
        _occupy(adm, bed, user, "Admission")
    audit("admission.created", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=patient.id,
          details=f"ward={adm.ward} bed={adm.bed}")
    return adm


def assign_bed(adm: Admission, bed_id: int, user, note: str = ""):
    """Give an admitted-but-unassigned patient a bed."""
    if adm.status != "Admitted":
        raise ApiError("Admission is not active", 409)
    if current_assignment(adm.id):
        raise ApiError("Admission already has a bed; use transfer", 409)
    bed = _lock_bed(bed_id)
    _occupy(adm, bed, user, "Admission", note)
    audit("bed.assigned", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=adm.patient_id, details=f"bed={bed.code}")


def transfer(adm: Admission, new_bed_id: int, user, reason: str = ""):
    if adm.status != "Admitted":
        raise ApiError("Only active admissions can be transferred", 409)
    old = current_assignment(adm.id)
    if old is None:
        raise ApiError("Admission has no current bed; assign one instead", 409)
    if old.bed_id == new_bed_id:
        raise ApiError("Patient is already in that bed", 409)
    # lock in id order to avoid deadlocks between simultaneous transfers
    first, second = sorted([old.bed_id, new_bed_id])
    _lock_bed(first)
    _lock_bed(second)
    new_bed = db.session.get(Bed, new_bed_id)
    if new_bed.status not in ("Available", "Reserved"):
        raise ApiError(f"Bed {new_bed.code} is {new_bed.status} and cannot be allocated", 409)
    old_bed = db.session.get(Bed, old.bed_id)
    old.ended_at = utcnow()
    old.end_reason = "Transfer"
    old_bed.status = "Cleaning"
    old_bed.status_changed_at = utcnow()
    _flush_or_conflict()
    _occupy(adm, new_bed, user, "Transfer", reason)
    audit("bed.transferred", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=adm.patient_id,
          details=f"{old_bed.code} -> {new_bed.code}")


def plan_discharge(adm: Admission, user, plan: str, expected_on: str = ""):
    if adm.status != "Admitted":
        raise ApiError("Admission is not active", 409)
    adm.discharge_status = "Planned" if adm.discharge_status in ("None", "Planned") else adm.discharge_status
    adm.discharge_plan = plan
    if expected_on:
        adm.expected_discharge_on = expected_on
    audit("discharge.planned", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=adm.patient_id)


def authorize_discharge(adm: Admission, user, summary: str):
    if adm.status != "Admitted":
        raise ApiError("Admission is not active", 409)
    if not summary.strip():
        raise ApiError("A discharge summary is required to authorize discharge")
    adm.discharge_summary = summary
    adm.discharge_status = "Authorized"
    adm.discharge_authorized_by_id = user.id
    adm.discharge_authorized_at = utcnow()
    audit("discharge.authorized", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=adm.patient_id)


def complete_discharge(adm: Admission, user):
    if adm.status != "Admitted":
        raise ApiError("Admission is already discharged", 409)
    if adm.discharge_status != "Authorized":
        raise ApiError("Discharge must be authorized by the responsible clinician first", 409)
    assignment = current_assignment(adm.id)
    if assignment:
        bed = _lock_bed(assignment.bed_id)
        assignment.ended_at = utcnow()
        assignment.end_reason = "Discharge"
        bed.status = "Cleaning"
        bed.status_changed_at = utcnow()
    adm.status = "Discharged"
    adm.discharge_status = "Completed"
    adm.discharged_on = date.today().isoformat()
    adm.discharged_at = utcnow()
    if adm.encounter_id:
        enc = db.session.get(Encounter, adm.encounter_id)
        if enc and enc.status == "Open":
            enc.status, enc.ended_at = "Closed", utcnow()
    for t in db.session.execute(select(CareTask).where(CareTask.admission_id == adm.id, CareTask.status == "Pending")).scalars():
        t.status, t.notes = "Cancelled", (t.notes + " [auto-cancelled at discharge]").strip()
    for a in db.session.execute(select(Alert).where(Alert.admission_id == adm.id, Alert.status != "Resolved")).scalars():
        a.status, a.resolved_at, a.resolution_note = "Resolved", utcnow(), "Closed at discharge"
    _flush_or_conflict()
    from . import deliverables as dsvc
    item = dsvc.ensure(adm.patient_id, "Discharge summary", f"Discharge summary - {adm.ward} ({adm.admitted_on} to {adm.discharged_on})", "admission", adm.id, digital=True, created_by_id=user.id)
    if item.physical_status == "Not requested":
        item.physical_status = "Ready for collection"
    audit("discharge.completed", category="clinical", entity_type="admission", entity_id=adm.id, patient_id=adm.patient_id)


def set_bed_status(bed: Bed, new_status: str, user, note: str = ""):
    """Manual bed state changes: cleaning done, reserve, maintenance."""
    bed = _lock_bed(bed.id)
    if bed.status == "Occupied":
        raise ApiError("An occupied bed cannot be changed manually; transfer or discharge the patient", 409)
    if new_status not in BED_MANUAL_TRANSITIONS.get(bed.status, set()):
        raise ApiError(f"Bed cannot move from {bed.status} to {new_status}", 409)
    old = bed.status
    bed.status, bed.status_note, bed.status_changed_at = new_status, note[:200], utcnow()
    audit("bed.status_changed", category="clinical", entity_type="bed", entity_id=bed.id, details=f"{bed.code}: {old} -> {new_status}")
    return bed
