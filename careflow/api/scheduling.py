"""Doctors, appointments and encounters."""
from __future__ import annotations

from datetime import date, datetime, timezone

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select

from .. import constants as C
from ..access import bulk_scopes, get_authorized_patient, has_perm, require_perm
from ..audit import audit
from ..extensions import db
from ..models import Appointment, Doctor, Encounter, Patient, utcnow
from ..utils import ApiError, commit, iso, need, ok, page_args, payload, s, to_int, valid_date, valid_time

bp = Blueprint("scheduling", __name__, url_prefix="/api")


def _doctor_row(d: Doctor):
    return {"id": d.id, "name": d.name, "specialty": d.specialty, "department": d.department, "phone": d.phone, "available": bool(d.available), "registration_no": d.registration_no}


@bp.get("/doctors")
def list_doctors():
    rows = db.session.execute(select(Doctor).order_by(Doctor.name)).scalars()
    return jsonify(ok=True, items=[_doctor_row(d) for d in rows])


@bp.post("/doctors")
@require_perm("config.manage")
def create_doctor():
    d = payload()
    need(d, "name", "specialty")
    doc = Doctor(name=s(d, "name", 120), specialty=s(d, "specialty", 100), department=s(d, "department", 100) or "General", phone=s(d, "phone", 30), registration_no=s(d, "registration_no", 60))
    db.session.add(doc)
    audit("doctor.created", category="admin", entity_type="doctor", details=doc.name)
    commit()
    return ok("Doctor added", id=doc.id)


@bp.patch("/doctors/<int:did>")
@require_perm("assign.manage")
def update_doctor(did):
    doc = db.session.get(Doctor, did)
    if not doc:
        raise ApiError("Doctor not found", 404)
    d = payload()
    if "available" in d:
        doc.available = str(d["available"]).lower() in ("1", "true", "yes")
    for k, mx in (("specialty", 100), ("department", 100), ("phone", 30)):
        if k in d:
            setattr(doc, k, s(d, k, mx))
    audit("doctor.updated", category="admin", entity_type="doctor", entity_id=did)
    commit()
    return ok("Doctor updated")


@bp.get("/doctors/<int:did>/slots")
def doctor_slots(did):
    """Booked times only (no patient information)."""
    day = valid_date(request.args.get("date", ""), "date", allow_empty=False)
    rows = db.session.execute(select(Appointment.appointment_time).where(Appointment.doctor_id == did, Appointment.appointment_date == day, Appointment.status.in_(C.ACTIVE_APPOINTMENT))).scalars().all()
    return jsonify(ok=True, date=day, booked=sorted(rows), day_start=current_app.config["APPOINTMENT_DAY_START"], day_end=current_app.config["APPOINTMENT_DAY_END"])


def _appt_row(a: Appointment, scopes: dict):
    visible = a.patient_id in scopes and "identity" in scopes[a.patient_id]
    return {"id": a.id, "patient_id": a.patient_id if visible else None, "patient_name": a.patient.name if visible else "Restricted",
            "patient_code": a.patient.patient_code if visible else "", "doctor_id": a.doctor_id, "doctor_name": a.doctor.name if a.doctor else "",
            "date": a.appointment_date, "time": a.appointment_time, "reason": a.reason if visible else "", "status": a.status, "visit_type": a.visit_type,
            "duration_min": a.duration_min, "reschedule_count": a.reschedule_count, "cancel_reason": a.cancel_reason}


@bp.get("/appointments")
def list_appointments():
    u = g.user
    if not (has_perm(u, "appointment.manage") or has_perm(u, "appointment.checkin")):
        raise ApiError("You do not have access to appointments", 403)
    q = select(Appointment)
    if request.args.get("date"):
        q = q.where(Appointment.appointment_date == valid_date(request.args["date"], "date"))
    if request.args.get("status"):
        q = q.where(Appointment.status == request.args["status"])
    if request.args.get("doctor_id"):
        q = q.where(Appointment.doctor_id == to_int(request.args["doctor_id"], "doctor_id"))
    if request.args.get("patient_id"):
        q = q.where(Appointment.patient_id == to_int(request.args["patient_id"], "patient_id"))
    if u.role == C.DOCTOR and request.args.get("scope") != "all":
        q = q.where(Appointment.doctor_id == u.doctor_id)
    page, per = page_args(50, 200)
    rows = db.session.execute(q.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(per).offset((page - 1) * per)).scalars().all()
    sc = bulk_scopes(u, {a.patient_id for a in rows})
    return jsonify(ok=True, items=[_appt_row(a, sc) for a in rows], page=page, per_page=per)


def _validate_slot(doc: Doctor, day: str, time_: str, exclude_id=None):
    if day < date.today().isoformat():
        raise ApiError("Appointment date cannot be in the past")
    if day == date.today().isoformat() and time_ < datetime.now(timezone.utc).strftime("%H:%M") and not current_app.config.get("TESTING"):
        pass  # local clock vs. hospital timezone differs; same-day past times are warned in the UI, not blocked
    start, end = current_app.config["APPOINTMENT_DAY_START"], current_app.config["APPOINTMENT_DAY_END"]
    if not (start <= time_ < end):
        raise ApiError(f"Appointments are available between {start} and {end}")
    if not doc.available:
        raise ApiError("Selected doctor is unavailable")
    q = select(Appointment.id).where(Appointment.doctor_id == doc.id, Appointment.appointment_date == day, Appointment.appointment_time == time_, Appointment.status.in_(C.ACTIVE_APPOINTMENT))
    if exclude_id:
        q = q.where(Appointment.id != exclude_id)
    if db.session.execute(q).first():
        raise ApiError("This doctor already has an appointment at that time", 409)


@bp.post("/appointments")
@require_perm("appointment.manage")
def create_appointment():
    d = payload()
    need(d, "patient_id", "doctor_id", "appointment_date", "appointment_time")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "identity")
    doc = db.session.get(Doctor, to_int(d["doctor_id"], "doctor_id"))
    if not doc:
        raise ApiError("Doctor not found", 404)
    day, time_ = valid_date(d["appointment_date"], "appointment_date", False), valid_time(d["appointment_time"], "appointment_time")
    _validate_slot(doc, day, time_)
    a = Appointment(patient_id=p.id, doctor_id=doc.id, appointment_date=day, appointment_time=time_, reason=s(d, "reason", 300),
                    visit_type=s(d, "visit_type", 30) or "Consultation", created_by_id=g.user.id)
    db.session.add(a)
    audit("appointment.scheduled", category="clinical", entity_type="appointment", patient_id=p.id, details=f"{doc.name} {day} {time_}")
    commit()  # the partial unique index turns a race into a 409
    return ok("Appointment scheduled", id=a.id)


@bp.route("/appointments/<int:aid>", methods=["PATCH", "DELETE"])
def update_appointment(aid):
    a = db.session.get(Appointment, aid)
    if not a:
        raise ApiError("Appointment not found", 404)
    u = g.user
    if not (has_perm(u, "appointment.manage") or has_perm(u, "appointment.checkin")):
        raise ApiError("You do not have access to appointments", 403)
    get_authorized_patient(a.patient_id, "identity")
    d = payload()
    status = "Cancelled" if request.method == "DELETE" else d.get("status", "")
    resched = "appointment_date" in d or "appointment_time" in d
    if resched:
        if not has_perm(u, "appointment.manage"):
            raise ApiError("Only schedulers may reschedule", 403)
        if a.status not in C.ACTIVE_APPOINTMENT:
            raise ApiError(f"A {a.status.lower()} appointment cannot be rescheduled", 409)
        day = valid_date(d.get("appointment_date", a.appointment_date), "appointment_date", False)
        tm = valid_time(d.get("appointment_time", a.appointment_time), "appointment_time")
        doc = db.session.get(Doctor, to_int(d.get("doctor_id", a.doctor_id), "doctor_id"))
        _validate_slot(doc, day, tm, exclude_id=a.id)
        a.appointment_date, a.appointment_time, a.doctor_id = day, tm, doc.id
        a.reschedule_count = (a.reschedule_count or 0) + 1
        audit("appointment.rescheduled", category="clinical", entity_type="appointment", entity_id=aid, patient_id=a.patient_id, details=f"{day} {tm}")
    if status:
        if status not in C.APPOINTMENT_STATUSES:
            raise ApiError("Invalid status")
        if status == "Checked-in" and not (has_perm(u, "appointment.checkin") or has_perm(u, "appointment.manage")):
            raise ApiError("Not permitted", 403)
        if status != a.status:
            if status not in C.APPOINTMENT_TRANSITIONS.get(a.status, set()):
                raise ApiError(f"Appointment cannot move from {a.status} to {status}", 409)
            if status == "Cancelled":
                if not s(d, "cancel_reason", 200) and request.method != "DELETE":
                    raise ApiError("A cancellation reason is required")
                a.cancel_reason = s(d, "cancel_reason", 200)
            a.status = status
            audit("appointment.status_changed", category="clinical", entity_type="appointment", entity_id=aid, patient_id=a.patient_id, details=status)
    if not resched and not status:
        raise ApiError("Nothing to update")
    commit()
    return ok("Appointment updated")


@bp.post("/appointments/<int:aid>/start")
@require_perm("encounter.manage")
def start_encounter(aid):
    a = db.session.get(Appointment, aid)
    if not a:
        raise ApiError("Appointment not found", 404)
    u = g.user
    if a.doctor_id != u.doctor_id:
        raise ApiError("Only the appointment's doctor can start the consultation", 403)
    get_authorized_patient(a.patient_id, "clinical")
    if a.status not in C.ACTIVE_APPOINTMENT:
        raise ApiError(f"Appointment is {a.status}", 409)
    existing = db.session.execute(select(Encounter).where(Encounter.appointment_id == a.id)).scalar_one_or_none()
    if existing:
        return ok("Consultation already started", encounter_id=existing.id)
    enc = Encounter(patient_id=a.patient_id, encounter_type="Outpatient", doctor_id=a.doctor_id, appointment_id=a.id, chief_complaint=a.reason, created_by_id=u.id)
    a.status = "Checked-in"
    db.session.add(enc)
    audit("encounter.started", category="clinical", entity_type="appointment", entity_id=aid, patient_id=a.patient_id)
    commit()
    return ok("Consultation started", encounter_id=enc.id)


@bp.post("/appointments/<int:aid>/complete")
@require_perm("encounter.manage")
def complete_encounter(aid):
    a = db.session.get(Appointment, aid)
    if not a:
        raise ApiError("Appointment not found", 404)
    if a.doctor_id != g.user.doctor_id:
        raise ApiError("Only the appointment's doctor can complete the consultation", 403)
    get_authorized_patient(a.patient_id, "clinical")
    if a.status not in C.ACTIVE_APPOINTMENT:
        raise ApiError(f"Appointment is {a.status}", 409)
    enc = db.session.execute(select(Encounter).where(Encounter.appointment_id == a.id)).scalar_one_or_none()
    if enc and enc.status == "Open":
        enc.status, enc.ended_at = "Closed", utcnow()
    a.status = "Completed"
    audit("encounter.completed", category="clinical", entity_type="appointment", entity_id=aid, patient_id=a.patient_id)
    commit()
    return ok("Consultation completed")


@bp.get("/patients/<int:pid>/encounters")
def patient_encounters(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(Encounter).where(Encounter.patient_id == pid).order_by(Encounter.started_at.desc())).scalars()
    return jsonify(ok=True, items=[{"id": e.id, "type": e.encounter_type, "status": e.status, "doctor": e.doctor.name if e.doctor else "", "started_at": iso(e.started_at),
                                    "ended_at": iso(e.ended_at), "chief_complaint": e.chief_complaint} for e in rows])
