"""Wards, rooms, beds, the live bedboard and the admission/discharge workflow."""
from __future__ import annotations

from flask import Blueprint, g, jsonify, request
from sqlalchemy import func, select

from .. import constants as C
from ..access import bulk_scopes, get_authorized_patient, has_perm, patient_scopes, require_perm
from ..audit import audit
from ..extensions import db
from ..models import (Admission, Alert, AppUser, Bed, BedAssignment, CareTask, Department, Doctor, Patient, PatientAssignment, Room,
                      Ward, utcnow)
from ..services import beds as bedsvc
from ..services import monitoring
from ..utils import ApiError, age_from_dob, commit, iso, need, ok, page_args, payload, s, to_float, to_int, valid_date

bp = Blueprint("beds", __name__, url_prefix="/api")


# --------------------------------------------------------------------------- #
# Facilities configuration
# --------------------------------------------------------------------------- #
@bp.get("/facilities")
def facilities():
    wards = db.session.execute(select(Ward).order_by(Ward.name)).scalars().all()
    out = []
    for w in wards:
        rooms = db.session.execute(select(Room).where(Room.ward_id == w.id).order_by(Room.label)).scalars().all()
        beds = db.session.execute(select(Bed).where(Bed.ward_id == w.id).order_by(Bed.code)).scalars().all()
        out.append({"id": w.id, "name": w.name, "specialty": w.specialty, "floor": w.floor, "daily_rate": w.daily_rate, "is_active": w.is_active,
                    "department": w.department.name if w.department else "",
                    "rooms": [{"id": r.id, "label": r.label} for r in rooms],
                    "beds": [{"id": b.id, "code": b.code, "label": b.label, "room_id": b.room_id, "status": b.status, "is_active": b.is_active} for b in beds]})
    return jsonify(ok=True, wards=out, departments=[{"id": d.id, "name": d.name} for d in db.session.execute(select(Department).order_by(Department.name)).scalars()])


@bp.post("/departments")
@require_perm("bed.configure")
def add_department():
    d = payload()
    need(d, "name")
    dep = Department(name=s(d, "name", 100))
    db.session.add(dep)
    audit("department.created", category="admin", entity_type="department", details=dep.name)
    commit()
    return ok("Department added", id=dep.id)


@bp.post("/wards")
@require_perm("bed.configure")
def add_ward():
    d = payload()
    need(d, "name")
    w = Ward(name=s(d, "name", 80), specialty=s(d, "specialty", 100), floor=s(d, "floor", 20), daily_rate=to_float(d.get("daily_rate", 0) or 0, "daily_rate", 0, 1_000_000),
             department_id=to_int(d["department_id"], "department_id") if d.get("department_id") else None)
    db.session.add(w)
    audit("ward.created", category="admin", entity_type="ward", details=w.name)
    commit()
    return ok("Ward added", id=w.id)


@bp.patch("/wards/<int:wid>")
@require_perm("bed.configure")
def update_ward(wid):
    w = db.session.get(Ward, wid)
    if not w:
        raise ApiError("Ward not found", 404)
    d = payload()
    for k, mx in (("name", 80), ("specialty", 100), ("floor", 20)):
        if k in d:
            setattr(w, k, s(d, k, mx))
    if "daily_rate" in d:
        w.daily_rate = to_float(d["daily_rate"], "daily_rate", 0, 1_000_000)
    if "is_active" in d:
        active = str(d["is_active"]).lower() in ("1", "true", "yes")
        if not active and db.session.execute(select(Bed.id).where(Bed.ward_id == wid, Bed.status == "Occupied")).first():
            raise ApiError("Cannot deactivate a ward with occupied beds", 409)
        w.is_active = active
    audit("ward.updated", category="admin", entity_type="ward", entity_id=wid)
    commit()
    return ok("Ward updated")


@bp.post("/rooms")
@require_perm("bed.configure")
def add_room():
    d = payload()
    need(d, "ward_id", "label")
    r = Room(ward_id=to_int(d["ward_id"], "ward_id"), label=s(d, "label", 30))
    db.session.add(r)
    audit("room.created", category="admin", entity_type="room", details=r.label)
    commit()
    return ok("Room added", id=r.id)


@bp.post("/beds")
@require_perm("bed.configure")
def add_bed():
    d = payload()
    need(d, "room_id", "label")
    room = db.session.get(Room, to_int(d["room_id"], "room_id"))
    if not room:
        raise ApiError("Room not found", 404)
    label = s(d, "label", 30)
    b = Bed(room_id=room.id, ward_id=room.ward_id, label=label, code=f"{room.ward.name[:6].upper().replace(' ', '')}-{room.label}-{label}"[:40])
    db.session.add(b)
    audit("bed.created", category="admin", entity_type="bed", details=b.code)
    commit()
    return ok("Bed added", id=b.id, code=b.code)


@bp.patch("/beds/<int:bid>")
@require_perm("bed.configure")
def configure_bed(bid):
    b = db.session.get(Bed, bid)
    if not b:
        raise ApiError("Bed not found", 404)
    d = payload()
    if "is_active" in d:
        active = str(d["is_active"]).lower() in ("1", "true", "yes")
        if not active and b.status == "Occupied":
            raise ApiError("Cannot deactivate an occupied bed", 409)
        b.is_active = active
    audit("bed.configured", category="admin", entity_type="bed", entity_id=bid)
    commit()
    return ok("Bed updated")


@bp.post("/beds/<int:bid>/status")
@require_perm("bed.operate")
def bed_status(bid):
    b = db.session.get(Bed, bid)
    if not b:
        raise ApiError("Bed not found", 404)
    d = payload()
    need(d, "status")
    bedsvc.set_bed_status(b, s(d, "status", 20), g.user, s(d, "note", 200))
    commit()
    return ok(f"Bed {b.code} is now {b.status}")


# --------------------------------------------------------------------------- #
# Live bedboard
# --------------------------------------------------------------------------- #
@bp.get("/bedboard")
def bedboard():
    monitoring.run_sweeps()
    ward_id = request.args.get("ward_id", type=int)
    q = (request.args.get("q") or "").strip().lower()
    wards = db.session.execute(select(Ward).where(Ward.is_active.is_(True)).order_by(Ward.name)).scalars().all()
    bq = select(Bed).where(Bed.is_active.is_(True))
    if ward_id:
        bq = bq.where(Bed.ward_id == ward_id)
    beds = db.session.execute(bq.order_by(Bed.ward_id, Bed.code)).scalars().all()
    # current assignments in one query
    bed_ids = [b.id for b in beds]
    rows = db.session.execute(
        select(BedAssignment, Admission, Patient).join(Admission, Admission.id == BedAssignment.admission_id)
        .join(Patient, Patient.id == Admission.patient_id).where(BedAssignment.ended_at.is_(None), BedAssignment.bed_id.in_(bed_ids or [0]))).all()
    occ = {ba.bed_id: (ba, adm, pat) for ba, adm, pat in rows}
    pids = [pat.id for _, _, pat in rows]
    sc = bulk_scopes(g.user, pids)
    fresh = monitoring.freshness([p for p in pids if "observations" in sc.get(p, ())])
    now = utcnow()
    alerts = {}
    tasks_due = {}
    if pids:
        for a in db.session.execute(select(Alert).where(Alert.patient_id.in_(pids), Alert.status != "Resolved")).scalars():
            if "observations" in sc.get(a.patient_id, ()):
                rank = {"Info": 1, "Warning": 2, "Critical": 3}[a.severity]
                cur = alerts.get(a.patient_id)
                if not cur or rank > cur["rank"]:
                    alerts[a.patient_id] = {"rank": rank, "severity": a.severity, "count": (cur or {}).get("count", 0) + 1}
                else:
                    cur["count"] += 1
        for t in db.session.execute(select(CareTask).where(CareTask.patient_id.in_(pids), CareTask.status == "Pending")).scalars():
            if "clinical" in sc.get(t.patient_id, ()):
                d = tasks_due.setdefault(t.patient_id, {"pending": 0, "overdue": 0})
                d["pending"] += 1
                if t.due_at and t.due_at < now:
                    d["overdue"] += 1
    docs = {d.id: d for d in db.session.execute(select(Doctor)).scalars()}
    out = []
    for b in beds:
        item = {"id": b.id, "code": b.code, "label": b.label, "room": b.room.label, "ward_id": b.ward_id, "ward": b.ward.name, "status": b.status,
                "status_note": b.status_note, "status_since": iso(b.status_changed_at), "patient": None}
        if b.status == "Occupied" and b.id in occ:
            ba, adm, pat = occ[b.id]
            held = sc.get(pat.id, frozenset())
            if "identity" in held:
                pi = {"id": pat.id, "name": pat.name, "patient_code": pat.patient_code, "age": age_from_dob(pat.dob), "gender": pat.gender, "admission_id": adm.id,
                      "restricted": False}
                if "clinical" in held:
                    doc = docs.get(adm.responsible_doctor_id)
                    pi.update(responsible_doctor=doc.name if doc else None, admitted_on=adm.admitted_on, expected_discharge_on=adm.expected_discharge_on,
                              discharge_status=adm.discharge_status, tasks=tasks_due.get(pat.id, {"pending": 0, "overdue": 0}))
                if "observations" in held:
                    pi.update(alert=alerts.get(pat.id), freshness=fresh.get(pat.id))
                item["patient"] = pi
            else:
                item["patient"] = {"restricted": True}
        out.append(item)
    if q:
        def hit(i):
            p = i["patient"] or {}
            hay = " ".join([i["code"], i["room"], i["ward"], i["status"], p.get("name", "") or "", p.get("patient_code", "") or ""]).lower()
            return q in hay
        out = [i for i in out if hit(i)]
    stats = []
    for w in wards:
        wb = [i for i in out if i["ward_id"] == w.id] if not q else [i for i in out if i["ward_id"] == w.id]
        total = db.session.execute(select(func.count(Bed.id)).where(Bed.ward_id == w.id, Bed.is_active.is_(True))).scalar()
        by = dict(db.session.execute(select(Bed.status, func.count(Bed.id)).where(Bed.ward_id == w.id, Bed.is_active.is_(True)).group_by(Bed.status)).all())
        stats.append({"ward_id": w.id, "ward": w.name, "specialty": w.specialty, "total": total, "occupied": by.get("Occupied", 0), "available": by.get("Available", 0),
                      "cleaning": by.get("Cleaning", 0), "reserved": by.get("Reserved", 0), "maintenance": by.get("Maintenance", 0),
                      "occupancy_pct": round(100 * by.get("Occupied", 0) / total, 1) if total else 0})
    awaiting = db.session.execute(
        select(Admission, Patient).join(Patient, Patient.id == Admission.patient_id)
        .where(Admission.status == "Admitted", ~Admission.id.in_(select(BedAssignment.admission_id).where(BedAssignment.ended_at.is_(None))))).all()
    asc = bulk_scopes(g.user, [p.id for _, p in awaiting])
    waiting = [{"admission_id": a.id, "patient_id": p.id, "name": p.name, "patient_code": p.patient_code, "ward": a.ward, "admitted_on": a.admitted_on}
               for a, p in awaiting if "identity" in asc.get(p.id, ())]
    return jsonify(ok=True, wards=stats, beds=out, awaiting_bed=waiting, generated_at=iso(now))


# --------------------------------------------------------------------------- #
# Admissions
# --------------------------------------------------------------------------- #
def _adm_row(a: Admission, p: Patient, bed=None):
    return {"id": a.id, "patient_id": p.id, "patient_name": p.name, "patient_code": p.patient_code, "ward": a.ward, "bed": a.bed, "status": a.status,
            "admitted_on": a.admitted_on, "discharged_on": a.discharged_on, "reason": a.reason, "discharge_status": a.discharge_status,
            "expected_discharge_on": a.expected_discharge_on, "responsible_doctor": a.responsible_doctor.name if a.responsible_doctor else None,
            "responsible_doctor_id": a.responsible_doctor_id, "notes": a.notes}


@bp.get("/admissions")
def list_admissions():
    status = request.args.get("status")
    q = select(Admission, Patient).join(Patient, Patient.id == Admission.patient_id)
    if status:
        q = q.where(Admission.status == status)
    rows = db.session.execute(q.order_by(Admission.admitted_at.desc()).limit(300)).all()
    sc = bulk_scopes(g.user, [p.id for _, p in rows])
    return jsonify(ok=True, items=[_adm_row(a, p) for a, p in rows if "identity" in sc.get(p.id, ())])


@bp.get("/admissions/<int:aid>")
def get_admission(aid):
    a = db.session.get(Admission, aid)
    if not a:
        raise ApiError("Admission not found", 404)
    p = get_authorized_patient(a.patient_id, "identity")
    hist = db.session.execute(select(BedAssignment).where(BedAssignment.admission_id == aid).order_by(BedAssignment.started_at)).scalars().all()
    out = _adm_row(a, p)
    out["bed_history"] = [{"bed": x.bed.code, "ward": x.bed.ward.name, "from": iso(x.started_at), "to": iso(x.ended_at), "reason": x.reason, "end_reason": x.end_reason, "note": x.note} for x in hist]
    if "clinical" in patient_scopes(g.user, p.id):
        out.update(discharge_plan=a.discharge_plan, discharge_summary=a.discharge_summary)
    return jsonify(ok=True, **out)


@bp.post("/admissions")
@require_perm("admission.manage")
def create_admission():
    d = payload()
    need(d, "patient_id")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "identity")
    doctor_id = to_int(d["doctor_id"], "doctor_id") if d.get("doctor_id") else (g.user.doctor_id if g.user.role == C.DOCTOR else None)
    admitted_on = valid_date(d.get("admitted_on", ""), "admitted_on")
    adm = bedsvc.admit(p, user=g.user, ward_name=s(d, "ward", 80), bed_id=to_int(d["bed_id"], "bed_id") if d.get("bed_id") else None, doctor_id=doctor_id,
                       admitted_on=admitted_on, reason=s(d, "reason", 1000), notes=s(d, "notes", 2000), expected_discharge_on=valid_date(d.get("expected_discharge_on", ""), "expected_discharge_on"))
    if doctor_id:
        du = db.session.execute(select(AppUser).where(AppUser.doctor_id == doctor_id, AppUser.is_active.is_(True))).scalar_one_or_none()
        if du and not db.session.execute(select(PatientAssignment.id).where(PatientAssignment.patient_id == p.id, PatientAssignment.user_id == du.id, PatientAssignment.active.is_(True))).first():
            db.session.add(PatientAssignment(patient_id=p.id, user_id=du.id, relation="primary", created_by_id=g.user.id))
    commit()
    return ok("Admission recorded", id=adm.id, bed=adm.bed, ward=adm.ward)


def _adm_or_404(aid) -> Admission:
    a = db.session.get(Admission, aid)
    if not a:
        raise ApiError("Admission not found", 404)
    return a


@bp.post("/admissions/<int:aid>/assign-bed")
@require_perm("bed.operate")
def assign_bed(aid):
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "identity")
    d = payload()
    need(d, "bed_id")
    bedsvc.assign_bed(a, to_int(d["bed_id"], "bed_id"), g.user, s(d, "note", 300))
    commit()
    return ok(f"Assigned to bed {a.bed}")


@bp.post("/admissions/<int:aid>/transfer")
@require_perm("bed.operate")
def transfer(aid):
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "identity")
    d = payload()
    need(d, "bed_id")
    bedsvc.transfer(a, to_int(d["bed_id"], "bed_id"), g.user, s(d, "reason", 300))
    commit()
    return ok(f"Transferred to bed {a.bed}")


@bp.post("/admissions/<int:aid>/discharge/plan")
@require_perm("admission.manage")
def discharge_plan(aid):
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "clinical")
    d = payload()
    need(d, "plan")
    bedsvc.plan_discharge(a, g.user, s(d, "plan", 3000), valid_date(d.get("expected_discharge_on", ""), "expected_discharge_on"))
    commit()
    return ok("Discharge plan saved")


@bp.post("/admissions/<int:aid>/discharge/authorize")
@require_perm("discharge.authorize")
def discharge_authorize(aid):
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "clinical")
    d = payload()
    bedsvc.authorize_discharge(a, g.user, s(d, "summary", 8000))
    commit()
    return ok("Discharge authorized")


@bp.post("/admissions/<int:aid>/discharge/complete")
@require_perm("admission.manage")
def discharge_complete(aid):
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "identity")
    bedsvc.complete_discharge(a, g.user)
    commit()
    return ok("Patient discharged; bed moved to Cleaning")


@bp.post("/admissions/<int:aid>/discharge")
@require_perm("admission.manage")
def legacy_discharge(aid):
    """Backward-compatible one-step discharge: allowed only when authorization exists or the caller can authorize."""
    a = _adm_or_404(aid)
    get_authorized_patient(a.patient_id, "identity")
    d = payload()
    if a.discharge_status != "Authorized":
        if not has_perm(g.user, "discharge.authorize"):
            raise ApiError("Discharge must first be authorized by the responsible clinician", 409)
        get_authorized_patient(a.patient_id, "clinical")
        bedsvc.authorize_discharge(a, g.user, s(d, "summary", 8000))
    bedsvc.complete_discharge(a, g.user)
    commit()
    return ok("Patient discharged")
