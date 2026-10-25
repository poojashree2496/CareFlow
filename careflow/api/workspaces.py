"""Role-specific workspace data. The server only serves a workspace to roles that are authorised for it,
and every patient row inside it is filtered through the same scope rules as the rest of the API."""
from __future__ import annotations

from datetime import date, timedelta
from functools import wraps

from flask import Blueprint, current_app, g, jsonify
from sqlalchemy import func, select

from .. import constants as C
from ..access import ROLE_WORKSPACES, bulk_scopes, workspaces_for, visible_patient_filter
from ..extensions import db
from ..models import (Admission, Alert, Appointment, AppUser, AuditLog, Bed, Bill, CareTask, CriticalAck, InsuranceClaim, LabReport, Medicine,
                      MedicalDocument, MedicationAdministration, Patient, Prescription, RadiologyRecord, utcnow)
from ..services import journey, monitoring
from ..utils import ApiError, age_from_dob, iso

bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")
SEV = {"Critical": 3, "Warning": 2, "Info": 1}


def workspace(name):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if g.user is None:
                raise ApiError("Authentication required", 401)
            if name not in ROLE_WORKSPACES.get(g.user.role, []):
                from ..audit import audit
                audit("access.denied", category="security", outcome="denied", details=f"workspace={name}", commit=True)
                raise ApiError("This workspace is not available for your role", 403)
            return fn(*a, **kw)
        return wrapper
    return deco


@bp.get("")
def list_workspaces():
    ws = workspaces_for(g.user)
    return jsonify(ok=True, items=ws, default=ws[0]["id"] if ws else None)


def _name(p, held):
    return {"id": p.id, "name": p.name, "patient_code": p.patient_code, "age": age_from_dob(p.dob), "gender": p.gender}


def _attention(pids, sc):
    """Per-patient reasons a clinician should look first. Everything is derived from stored records."""
    now = utcnow()
    reasons: dict[int, list[dict]] = {p: [] for p in pids}
    obs_ok = [p for p in pids if "observations" in sc.get(p, ())]
    for a in db.session.execute(select(Alert).where(Alert.patient_id.in_(obs_ok or [0]), Alert.status != "Resolved")).scalars():
        reasons[a.patient_id].append({"kind": "alert", "severity": a.severity, "text": f"{a.severity} alert: {a.message}", "ref": a.id, "weight": 30 + 10 * SEV[a.severity] + (15 if a.status == "Open" else 0)})
    fr = monitoring.freshness(obs_ok)
    adm = {a.patient_id for a in db.session.execute(select(Admission).where(Admission.patient_id.in_(obs_ok or [0]), Admission.status == "Admitted")).scalars()}
    for pid, f in fr.items():
        if pid in adm and f["state"] in ("overdue", "none"):
            reasons[pid].append({"kind": "stale_obs", "severity": "Warning", "text": "No recent observations" if f["state"] == "none" else f"Observations overdue ({f['age_min']} min old)", "weight": 25})
    lab_ok = [p for p in pids if "labs" in sc.get(p, ())]
    for c in db.session.execute(select(CriticalAck).where(CriticalAck.patient_id.in_(lab_ok or [0]), CriticalAck.status != "Acknowledged")).scalars():
        reasons[c.patient_id].append({"kind": "critical_result", "severity": "Critical", "text": f"Critical result awaiting acknowledgement: {c.summary}", "ref": c.id, "weight": 70 if c.status == "Escalated" else 60})
    for l in db.session.execute(select(LabReport).where(LabReport.patient_id.in_(lab_ok or [0]), LabReport.released_at.is_not(None), LabReport.released_at > now - timedelta(hours=24))).scalars():
        reasons[l.patient_id].append({"kind": "new_result", "severity": "Info", "text": f"New result released: {l.test_name}", "ref": l.id, "weight": 8})
    cl_ok = [p for p in pids if "clinical" in sc.get(p, ())]
    for t in db.session.execute(select(CareTask).where(CareTask.patient_id.in_(cl_ok or [0]), CareTask.status == "Pending", CareTask.due_at < now)).scalars():
        reasons[t.patient_id].append({"kind": "overdue_task", "severity": "Warning", "text": f"Overdue task: {t.title}", "ref": t.id, "weight": 18})
    for a in db.session.execute(select(Admission).where(Admission.patient_id.in_(cl_ok or [0]), Admission.status == "Admitted", Admission.discharge_status == "Authorized")).scalars():
        reasons[a.patient_id].append({"kind": "discharge_ready", "severity": "Info", "text": "Discharge authorised: completion pending", "weight": 10})
    return reasons


def _my_patients(limit=60):
    return db.session.execute(select(Patient).where(visible_patient_filter(g.user), Patient.archived_at.is_(None)).order_by(Patient.id.desc()).limit(limit)).scalars().all()


def _attention_list(patients):
    sc = bulk_scopes(g.user, [p.id for p in patients])
    pids = [p.id for p in patients if "identity" in sc.get(p.id, ())]
    reasons = _attention(pids, sc)
    stays = {a.patient_id: a for a in db.session.execute(select(Admission).where(Admission.patient_id.in_(pids or [0]), Admission.status == "Admitted")).scalars()}
    out = []
    for p in patients:
        if p.id not in reasons:
            continue
        rs = sorted(reasons[p.id], key=lambda r: -r["weight"])
        score = sum(r["weight"] for r in rs[:4])
        a = stays.get(p.id)
        out.append({**_name(p, sc[p.id]), "admitted": bool(a), "ward": a.ward if a else None, "bed": a.bed if a else None, "score": score, "reasons": rs[:6]})
    out.sort(key=lambda x: (-x["score"], x["name"]))
    return out


@bp.get("/doctor")
@workspace("doctor")
def doctor():
    monitoring.run_sweeps()
    pts = _my_patients()
    items = _attention_list(pts)
    today = date.today().isoformat()
    appts = []
    if g.user.doctor_id:
        for a in db.session.execute(select(Appointment).where(Appointment.doctor_id == g.user.doctor_id, Appointment.appointment_date == today, Appointment.status.in_(C.ACTIVE_APPOINTMENT))
                                    .order_by(Appointment.appointment_time)).scalars():
            appts.append({"id": a.id, "time": a.appointment_time, "patient_id": a.patient_id, "patient": a.patient.name, "reason": a.reason, "status": a.status, "visit_type": a.visit_type})
    ids = [i["id"] for i in items]
    crit = db.session.execute(select(CriticalAck).where(CriticalAck.patient_id.in_(ids or [0]), CriticalAck.status != "Acknowledged")).scalars().all()
    return jsonify(ok=True, summary={"patients": len(items), "admitted": sum(1 for i in items if i["admitted"]), "needing_attention": sum(1 for i in items if i["score"] >= 25),
                                     "critical_results_pending": len(crit), "appointments_today": len(appts)},
                   attention=[i for i in items if i["reasons"]][:25], quiet=[{k: i[k] for k in ("id", "name", "patient_code", "admitted", "ward", "bed")} for i in items if not i["reasons"]][:25],
                   appointments_today=appts, generated_at=iso(utcnow()), note="Ordering reflects recorded alerts, overdue observations/tasks and unacknowledged results. It is a worklist aid, not a clinical risk score.")


@bp.get("/nurse")
@workspace("nurse")
def nurse():
    monitoring.run_sweeps()
    q = select(Admission, Patient).join(Patient, Patient.id == Admission.patient_id).where(Admission.status == "Admitted")
    rows = db.session.execute(q).all()
    sc = bulk_scopes(g.user, [p.id for _, p in rows])
    mine = [(a, p) for a, p in rows if "identity" in sc.get(p.id, ())]
    pids = [p.id for _, p in mine]
    reasons = _attention(pids, sc)
    now = utcnow()
    tasks = [t for t in db.session.execute(select(CareTask).where(CareTask.patient_id.in_(pids or [0]), CareTask.status == "Pending").order_by(CareTask.due_at)).scalars()
             if "clinical" in sc.get(t.patient_id, ())]
    meds_due = []
    for m in db.session.execute(select(MedicationAdministration).where(MedicationAdministration.patient_id.in_(pids or [0]), MedicationAdministration.status == "Scheduled").order_by(MedicationAdministration.scheduled_at)).scalars():
        if "meds" in sc.get(m.patient_id, ()):
            rx = db.session.get(Prescription, m.prescription_id)
            meds_due.append({"id": m.id, "prescription_id": m.prescription_id, "patient_id": m.patient_id, "medicine": rx.medicine if rx else "", "dosage": rx.dosage if rx else "", "scheduled_at": iso(m.scheduled_at), "overdue": bool(m.scheduled_at and m.scheduled_at < now)})
    pat = {p.id: p for _, p in mine}
    fr = monitoring.freshness([i for i in pids if "observations" in sc.get(i, ())])
    return jsonify(ok=True, patients=[{**_name(p, sc[p.id]), "ward": a.ward, "bed": a.bed, "admission_id": a.id, "freshness": fr.get(p.id),
                                       "alerts": [r for r in reasons.get(p.id, []) if r["kind"] == "alert"], "attention": sorted(reasons.get(p.id, []), key=lambda r: -r["weight"])[:4]} for a, p in mine],
                   tasks=[{"id": t.id, "patient_id": t.patient_id, "patient": pat[t.patient_id].name if t.patient_id in pat else "", "title": t.title, "category": t.category, "priority": t.priority, "due_at": iso(t.due_at), "overdue": bool(t.due_at and t.due_at < now)} for t in tasks[:80]],
                   medications_due=meds_due[:80], generated_at=iso(now))


@bp.get("/lab")
@workspace("lab")
def lab():
    rows = db.session.execute(select(LabReport.status, func.count(LabReport.id)).group_by(LabReport.status)).all()
    counts = {("Ordered" if s == "Pending" else "Released" if s == "Completed" else s): n for s, n in rows}
    open_ = db.session.execute(select(LabReport, Patient).join(Patient, Patient.id == LabReport.patient_id).where(LabReport.status.in_(("Ordered", "Pending", "Collected", "Received", "Resulted", "Verified")))
                               .order_by(LabReport.priority.desc(), LabReport.ordered_at).limit(100)).all()
    crit = db.session.execute(select(CriticalAck).where(CriticalAck.source_type == "lab", CriticalAck.status != "Acknowledged")).scalars().all()
    return jsonify(ok=True, counts=counts, queue=[{"id": l.id, "patient_id": p.id, "patient": p.name, "patient_code": p.patient_code, "test": l.test_name, "status": "Ordered" if l.status == "Pending" else l.status,
                                                   "priority": l.priority, "ordered_at": iso(l.ordered_at), "accession_no": l.accession_no} for l, p in open_],
                   critical_unacknowledged=[{"id": c.id, "patient_id": c.patient_id, "summary": c.summary, "status": c.status, "since": iso(c.created_at)} for c in crit])


@bp.get("/radiology")
@workspace("radiology")
def radiology():
    rows = db.session.execute(select(RadiologyRecord, Patient).join(Patient, Patient.id == RadiologyRecord.patient_id).where(RadiologyRecord.order_status.notin_(("Final", "Cancelled")))
                              .order_by(RadiologyRecord.priority.desc(), RadiologyRecord.ordered_at).limit(100)).all()
    counts = dict(db.session.execute(select(RadiologyRecord.order_status, func.count(RadiologyRecord.id)).group_by(RadiologyRecord.order_status)).all())
    return jsonify(ok=True, counts=counts, queue=[{"id": r.id, "patient_id": p.id, "patient": p.name, "patient_code": p.patient_code, "modality": r.modality, "description": r.study_description,
                                                   "status": r.order_status, "priority": r.priority, "indication": r.indication, "scheduled_at": iso(r.scheduled_at), "urgent_finding": bool(r.urgent_finding)} for r, p in rows])


@bp.get("/pharmacy")
@workspace("pharmacy")
def pharmacy():
    rows = db.session.execute(select(Prescription, Patient).join(Patient, Patient.id == Prescription.patient_id).where(Prescription.status.in_(("Ordered", "Verified", "Partially Dispensed")))
                              .order_by(Prescription.created_at).limit(120)).all()
    meds = db.session.execute(select(Medicine).where(Medicine.is_active.is_(True))).scalars().all()
    soon = (date.today() + timedelta(days=60)).isoformat()
    return jsonify(ok=True, queue=[{"id": r.id, "patient_id": p.id, "patient": p.name, "patient_code": p.patient_code, "medicine": r.medicine, "dosage": r.dosage, "status": r.status, "quantity": r.quantity,
                                    "dispensed_quantity": r.dispensed_quantity or 0, "warnings": r.warnings or [], "created_at": iso(r.created_at)} for r, p in rows],
                   low_stock=[{"id": m.id, "name": m.name, "stock": m.stock, "reorder_level": m.reorder_level} for m in meds if (m.stock or 0) <= (m.reorder_level or 0)],
                   expiring=[{"id": m.id, "name": m.name, "expiry_date": m.expiry_date, "stock": m.stock} for m in meds if m.expiry_date and m.expiry_date <= soon and (m.stock or 0) > 0])


@bp.get("/billing")
@workspace("billing")
def billing():
    bills = db.session.execute(select(Bill, Patient).join(Patient, Patient.id == Bill.patient_id).where(Bill.status != "Void").order_by(Bill.id.desc()).limit(300)).all()
    unpaid = [(b, p) for b, p in bills if not b.paid]
    claims = dict(db.session.execute(select(InsuranceClaim.status, func.count(InsuranceClaim.id)).group_by(InsuranceClaim.status)).all())
    return jsonify(ok=True, summary={"bills": len(bills), "unpaid": len(unpaid), "unpaid_total": round(sum(b.total for b, _ in unpaid), 2), "claims_by_status": claims},
                   unpaid=[{"id": b.id, "patient_id": p.id, "patient": p.name, "patient_code": p.patient_code, "description": b.description, "total": b.total, "insurance_status": b.insurance_status} for b, p in unpaid[:60]])


@bp.get("/admin")
@workspace("admin")
def admin():
    from .. import schema_status
    from ..ai.providers import ProviderError, get_provider
    cfg = current_app.config
    users = dict(db.session.execute(select(AppUser.role, func.count(AppUser.id)).where(AppUser.is_active.is_(True)).group_by(AppUser.role)).all())
    beds = dict(db.session.execute(select(Bed.status, func.count(Bed.id)).where(Bed.is_active.is_(True)).group_by(Bed.status)).all())
    sec = db.session.execute(select(AuditLog).where(AuditLog.category == "security", AuditLog.created_at > utcnow() - timedelta(days=1))).scalars().all()
    ds = cfg["DATABASE_SETTINGS"]
    try:
        ai = get_provider(cfg).describe() | {"configured": True}
    except ProviderError as e:
        ai = {"configured": False, "message": e.message}
    return jsonify(ok=True, users_by_role=users, beds=beds, security_events_24h={"total": len(sec), "denied": sum(1 for a in sec if a.outcome == "denied")},
                   system={"environment": cfg["CAREFLOW_ENV"], "database_backend": ds.backend, "database_kind": ds.kind, "schema": schema_status(current_app), "demo_mode": cfg["DEMO_MODE"],
                           "storage_backend": cfg.get("STORAGE_BACKEND", "local"), "ai": ai},
                   open_alerts=db.session.execute(select(func.count(Alert.id)).where(Alert.status != "Resolved")).scalar())
