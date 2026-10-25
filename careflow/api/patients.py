"""Patients and the clinical record that hangs off them."""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy import func, or_, select

from .. import constants as C
from ..access import (bulk_scopes, get_authorized_patient, has_perm, patient_scopes, patient_view, require_perm, visible_patient_filter)
from ..audit import audit
from ..extensions import db
from ..models import (Admission, Allergy, Appointment, AppUser, AuditLog, Bill, CarePlan, CareTask, ClinicalNote, Doctor, Encounter,
                      FollowUp, Handover, IntakeOutput, LabReport, MedicalDocument, Observation, Patient, PatientAssignment,
                      Prescription, Problem, RadiologyRecord, utcnow)
from ..services import journey, monitoring
from ..utils import (ApiError, age_from_dob, commit, iso, need, ok, page_args, parse_dt, payload, s, to_int, valid_date)

bp = Blueprint("patients", __name__, url_prefix="/api")

GENDERS = {"Male", "Female", "Other", "Not specified"}
BLOOD_GROUPS = {"", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
IDENTITY_FIELDS = ("name", "dob", "gender", "blood_group")
CONTACT_FIELDS = ("phone", "email", "address", "emergency_contact", "emergency_contact_phone", "emergency_contact_relation", "consent_data_sharing", "consent_notes")


def next_patient_code() -> str:
    for _ in range(8):
        code = "P-" + datetime.now(timezone.utc).strftime("%y%m%d") + "-" + os.urandom(2).hex().upper()
        if not db.session.execute(select(Patient.id).where(Patient.patient_code == code)).first():
            return code
    raise ApiError("Could not allocate a patient code, please retry", 503)


def _clean_patient_fields(d: dict, partial=False) -> dict:
    out = {}
    if not partial or "name" in d:
        need(d, "name")
        out["name"] = s(d, "name", 120)
        if len(out["name"]) < 2:
            raise ApiError("Name must be at least 2 characters")
    if "dob" in d:
        dob = valid_date(d.get("dob", ""), "Date of birth")
        if dob and dob > date.today().isoformat():
            raise ApiError("Date of birth cannot be in the future")
        out["dob"] = dob
    if "gender" in d:
        g_ = s(d, "gender", 30) or "Not specified"
        if g_ not in GENDERS:
            raise ApiError("gender must be one of: " + ", ".join(sorted(GENDERS)))
        out["gender"] = g_
    if "blood_group" in d:
        bg = s(d, "blood_group", 5)
        if bg not in BLOOD_GROUPS:
            raise ApiError("blood_group is not valid")
        out["blood_group"] = bg
    for k, mx in (("phone", 30), ("email", 120), ("address", 400), ("emergency_contact", 120), ("emergency_contact_phone", 30),
                  ("emergency_contact_relation", 60), ("consent_notes", 500), ("insurance_provider", 120), ("insurance_policy_no", 60),
                  ("allergies", 1000), ("medical_history", 4000)):
        if k in d:
            out[k] = s(d, k, mx)
    if "email" in out and out["email"] and ("@" not in out["email"] or " " in out["email"]):
        raise ApiError("email is not valid")
    if "consent_data_sharing" in d:
        out["consent_data_sharing"] = str(d["consent_data_sharing"]).lower() in ("1", "true", "yes", "on")
    return out


def _list_row(p: Patient, scopes=None):
    return {"id": p.id, "patient_code": p.patient_code, "name": p.name, "age": age_from_dob(p.dob), "dob": p.dob, "gender": p.gender,
            "data_origin": p.data_origin, "archived": p.archived_at is not None}


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
@bp.get("/patients")
def list_patients():
    q = request.args.get("q", "").strip()
    page, per = page_args(25)
    stmt = select(Patient).where(visible_patient_filter(g.user))
    if request.args.get("include_archived") != "1":
        stmt = stmt.where(Patient.archived_at.is_(None))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Patient.name.ilike(like), Patient.patient_code.ilike(like), Patient.phone.ilike(like)))
    total = db.session.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    rows = db.session.execute(stmt.order_by(Patient.created_at.desc()).limit(per).offset((page - 1) * per)).scalars().all()
    if q:
        audit("patient.search", category="access", details=f"results={len(rows)}")
        db.session.commit()
    return jsonify(ok=True, items=[_list_row(p) for p in rows], page=page, per_page=per, total=total)


@bp.post("/patients")
@require_perm("patient.register")
def create_patient():
    d = payload()
    f = _clean_patient_fields(d)
    if f.get("dob") and not d.get("confirm_duplicate"):
        dup = db.session.execute(select(Patient).where(func.lower(Patient.name) == f["name"].lower(), Patient.dob == f["dob"])).scalars().all()
        if dup:
            raise ApiError("A patient with the same name and date of birth is already registered. Confirm to register anyway.", 409,
                           possible_duplicates=[{"patient_code": x.patient_code} for x in dup])
    origin = "demo" if (g.user.is_demo or str(d.get("data_origin", "")).lower() == "demo") else "manual"
    p = Patient(patient_code=next_patient_code(), data_origin=origin, **{k: v for k, v in f.items() if k not in ("consent_data_sharing",)})
    p.consent_data_sharing = f.get("consent_data_sharing", False)
    db.session.add(p)
    db.session.flush()
    if g.user.role in (C.DOCTOR, C.NURSE):  # registering clinician starts the care relationship
        db.session.add(PatientAssignment(patient_id=p.id, user_id=g.user.id, relation="primary", created_by_id=g.user.id))
    audit("patient.registered", category="clinical", entity_type="patient", entity_id=p.id, patient_id=p.id, details=p.patient_code)
    commit()
    return jsonify(ok=True, message="Patient registered", id=p.id, patient_code=p.patient_code)


@bp.get("/patients/<int:pid>")
def get_patient(pid):
    p = get_authorized_patient(pid, "identity")
    sc = patient_scopes(g.user, pid)
    audit("patient.viewed", category="access", entity_type="patient", entity_id=pid, patient_id=pid)
    db.session.commit()
    return jsonify(ok=True, **patient_view(g.user, p, sc))


@bp.put("/patients/<int:pid>")
@bp.patch("/patients/<int:pid>")
def update_patient(pid):
    p = get_authorized_patient(pid, "identity")
    sc = patient_scopes(g.user, pid)
    d = payload()
    f = _clean_patient_fields(d, partial=True)
    denied = []
    for k in f:
        if k in IDENTITY_FIELDS and not has_perm(g.user, "patient.update"):
            denied.append(k)
        elif k in CONTACT_FIELDS and not (has_perm(g.user, "patient.update") and "contact" in sc):
            denied.append(k)
        elif k == "allergies" and not (has_perm(g.user, "allergy.write") and "allergies" in sc):
            denied.append(k)
        elif k == "medical_history" and not (has_perm(g.user, "note.write") and "clinical" in sc):
            denied.append(k)
        elif k in ("insurance_provider", "insurance_policy_no") and not ("billing" in sc and (has_perm(g.user, "patient.update") or has_perm(g.user, "patient.update_insurance"))):
            denied.append(k)
    if denied:
        raise ApiError("You may not edit: " + ", ".join(denied), 403)
    changed = []
    for k, v in f.items():
        if getattr(p, k) != v:
            setattr(p, k, v)
            changed.append(k)
    if any(k in changed for k in ("name", "dob")) and p.identity_verified:
        p.identity_verified = False  # identity details changed after verification
    audit("patient.updated", category="clinical", entity_type="patient", entity_id=pid, patient_id=pid, details="fields: " + ",".join(changed))
    commit()
    return ok("Patient updated")


@bp.post("/patients/<int:pid>/verify-identity")
@require_perm("patient.verify_identity")
def verify_identity(pid):
    p = get_authorized_patient(pid, "identity")
    d = payload()
    need(d, "identifier_label", "identifier_last4")
    last4 = s(d, "identifier_last4", 4)
    if not last4.isalnum() or len(last4) != 4:
        raise ApiError("identifier_last4 must be exactly the last 4 characters (the full number is never stored)")
    p.identifier_label, p.identifier_last4 = s(d, "identifier_label", 60), last4
    p.identity_verified, p.identity_verified_by_id, p.identity_verified_at = True, g.user.id, utcnow()
    audit("patient.identity_verified", category="clinical", entity_type="patient", entity_id=pid, patient_id=pid)
    commit()
    return ok("Identity verified")


@bp.post("/patients/<int:pid>/archive")
@require_perm("patient.update")
def archive_patient(pid):
    if g.user.role not in (C.HOSPITAL_ADMIN, C.SUPER_ADMIN):
        raise ApiError("Only administrators can archive patient records", 403)
    p = get_authorized_patient(pid, "identity")
    if db.session.execute(select(Admission.id).where(Admission.patient_id == pid, Admission.status == "Admitted")).first():
        raise ApiError("Cannot archive a patient with an active admission", 409)
    p.archived_at = utcnow()
    audit("patient.archived", category="admin", entity_type="patient", entity_id=pid, patient_id=pid)
    commit()
    return ok("Patient archived")


@bp.delete("/patients/<int:pid>")
def delete_patient(pid):
    if g.user.role != C.SUPER_ADMIN:
        raise ApiError("Only a super administrator may permanently delete a patient record", 403)
    p = get_authorized_patient(pid, "identity")
    for model in (Appointment, Admission, LabReport, Prescription, RadiologyRecord, Bill, ClinicalNote, Observation, MedicalDocument, Encounter):
        if db.session.execute(select(model.id).where(model.patient_id == pid).limit(1)).first():
            raise ApiError("Patient has linked clinical or financial records and cannot be deleted. Archive the record instead.", 409)
    db.session.query(PatientAssignment).filter_by(patient_id=pid).delete()
    db.session.query(Allergy).filter_by(patient_id=pid).delete()
    db.session.query(Problem).filter_by(patient_id=pid).delete()
    code = p.patient_code
    db.session.delete(p)
    audit("patient.deleted", category="admin", entity_type="patient", entity_id=pid, details=code)
    commit()
    return ok("Patient deleted")


# --------------------------------------------------------------------------- #
# Journey (snapshot + timeline)
# --------------------------------------------------------------------------- #
@bp.get("/patients/<int:pid>/journey")
def patient_journey(pid):
    p = get_authorized_patient(pid, "identity")
    sc = patient_scopes(g.user, pid)
    if g.user.role == C.SUPER_ADMIN:
        audit("privileged.journey_view", category="access", entity_type="patient", entity_id=pid, patient_id=pid)
    else:
        audit("patient.journey_viewed", category="access", entity_type="patient", entity_id=pid, patient_id=pid)
    snap = journey.build_snapshot(p, sc, g.user)
    timeline = journey.build_timeline(p, sc, g.user, limit=int(request.args.get("limit", 120)))
    db.session.commit()
    return jsonify(ok=True, patient=patient_view(g.user, p, sc), snapshot=snap, timeline=timeline, scopes=sorted(sc))


@bp.get("/patients/<int:pid>/audit")
def patient_audit(pid):
    get_authorized_patient(pid, "identity")
    if not (has_perm(g.user, "audit.view") or (g.user.role == C.DOCTOR and "clinical" in patient_scopes(g.user, pid))):
        raise ApiError("You do not have access to this patient's audit history", 403)
    page, per = page_args(50)
    rows = db.session.execute(select(AuditLog).where(AuditLog.patient_id == pid, AuditLog.category != "security").order_by(AuditLog.created_at.desc()).limit(per).offset((page - 1) * per)).scalars().all()
    users = {u.id: u for u in db.session.execute(select(AppUser).where(AppUser.id.in_({r.user_id for r in rows if r.user_id}))).scalars()} if rows else {}
    return jsonify(ok=True, items=[{"at": iso(r.created_at), "action": r.action, "category": r.category, "user": users[r.user_id].name if r.user_id in users else "system",
                                    "role": r.user_role, "details": r.details, "outcome": r.outcome} for r in rows])


# --------------------------------------------------------------------------- #
# Allergies & problems
# --------------------------------------------------------------------------- #
@bp.get("/patients/<int:pid>/allergies")
def list_allergies(pid):
    get_authorized_patient(pid, "allergies")
    rows = db.session.execute(select(Allergy).where(Allergy.patient_id == pid).order_by(Allergy.created_at.desc())).scalars()
    return jsonify(ok=True, items=[{"id": a.id, "substance": a.substance, "reaction": a.reaction, "severity": a.severity, "status": a.status, "created_at": iso(a.created_at)} for a in rows])


@bp.post("/patients/<int:pid>/allergies")
@require_perm("allergy.write")
def add_allergy(pid):
    get_authorized_patient(pid, "allergies")
    d = payload()
    need(d, "substance")
    sev = s(d, "severity", 20) or "Unknown"
    if sev not in ("Mild", "Moderate", "Severe", "Unknown"):
        raise ApiError("severity must be Mild, Moderate, Severe or Unknown")
    a = Allergy(patient_id=pid, substance=s(d, "substance", 120), reaction=s(d, "reaction", 200), severity=sev, recorded_by_id=g.user.id)
    db.session.add(a)
    audit("allergy.added", category="clinical", entity_type="allergy", patient_id=pid, details=a.substance)
    commit()
    return ok("Allergy recorded", id=a.id)


@bp.patch("/allergies/<int:aid>")
@require_perm("allergy.write")
def update_allergy(aid):
    a = db.session.get(Allergy, aid)
    if not a:
        raise ApiError("Allergy not found", 404)
    get_authorized_patient(a.patient_id, "allergies")
    status = s(payload(), "status", 20)
    if status not in ("Active", "Inactive", "Entered in error"):
        raise ApiError("status must be Active, Inactive or Entered in error")
    a.status = status
    audit("allergy.status_changed", category="clinical", entity_type="allergy", entity_id=aid, patient_id=a.patient_id, details=status)
    commit()
    return ok("Allergy updated")


@bp.get("/patients/<int:pid>/problems")
def list_problems(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(Problem).where(Problem.patient_id == pid).order_by(Problem.created_at.desc())).scalars()
    return jsonify(ok=True, items=[{"id": p.id, "description": p.description, "code": p.code, "status": p.status, "onset_on": p.onset_on, "created_at": iso(p.created_at), "resolved_at": iso(p.resolved_at)} for p in rows])


@bp.post("/patients/<int:pid>/problems")
@require_perm("problem.write")
def add_problem(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "description")
    adm = monitoring.active_admission(pid)
    pr = Problem(patient_id=pid, description=s(d, "description", 300), code=s(d, "code", 30), onset_on=valid_date(d.get("onset_on", ""), "onset_on"),
                 recorded_by_id=g.user.id, encounter_id=adm.encounter_id if adm else None)
    db.session.add(pr)
    audit("problem.added", category="clinical", entity_type="problem", patient_id=pid, details=pr.description[:100])
    commit()
    return ok("Problem added", id=pr.id)


@bp.patch("/problems/<int:prid>")
@require_perm("problem.write")
def update_problem(prid):
    pr = db.session.get(Problem, prid)
    if not pr:
        raise ApiError("Problem not found", 404)
    get_authorized_patient(pr.patient_id, "clinical")
    status = s(payload(), "status", 20)
    if status not in ("Active", "Resolved", "Ruled out"):
        raise ApiError("status must be Active, Resolved or Ruled out")
    pr.status = status
    pr.resolved_at = utcnow() if status != "Active" else None
    audit("problem.status_changed", category="clinical", entity_type="problem", entity_id=prid, patient_id=pr.patient_id, details=status)
    commit()
    return ok("Problem updated")


# --------------------------------------------------------------------------- #
# Clinical notes (append-only with amendments)
# --------------------------------------------------------------------------- #
DOCTOR_NOTE_TYPES = ("Progress", "Consult", "Procedure", "Discharge", "Admission")
NURSE_NOTE_TYPES = ("Nursing",)


def _note_row(n: ClinicalNote):
    return {"id": n.id, "note_type": n.note_type, "body": n.body, "status": n.status, "author": n.author.name if n.author else "", "author_role": n.author.role if n.author else "",
            "created_at": iso(n.created_at), "amends_note_id": n.amends_note_id, "amendment_reason": n.amendment_reason, "admission_id": n.admission_id, "encounter_id": n.encounter_id}


@bp.get("/patients/<int:pid>/notes")
def list_notes(pid):
    get_authorized_patient(pid, "clinical")
    q = select(ClinicalNote).where(ClinicalNote.patient_id == pid)
    if request.args.get("include_superseded") != "1":
        q = q.where(ClinicalNote.status == "Final")
    rows = db.session.execute(q.order_by(ClinicalNote.created_at.desc()).limit(200)).scalars().all()
    audit("notes.viewed", category="access", entity_type="clinical_note", patient_id=pid, details=f"{len(rows)} note(s)")
    db.session.commit()
    return jsonify(ok=True, items=[_note_row(n) for n in rows])


@bp.post("/patients/<int:pid>/notes")
@require_perm("note.write")
def add_note(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "body")
    allowed = NURSE_NOTE_TYPES if g.user.role == C.NURSE else DOCTOR_NOTE_TYPES
    ntype = s(d, "note_type", 30) or allowed[0]
    if ntype not in allowed:
        raise ApiError("Your role may write these note types: " + ", ".join(allowed))
    adm = monitoring.active_admission(pid)
    n = ClinicalNote(patient_id=pid, author_id=g.user.id, note_type=ntype, body=s(d, "body", 8000), admission_id=adm.id if adm else None,
                     encounter_id=adm.encounter_id if adm else None)
    db.session.add(n)
    audit("note.created", category="clinical", entity_type="clinical_note", patient_id=pid, details=ntype)
    commit()
    return ok("Note saved", id=n.id)


@bp.post("/notes/<int:nid>/amend")
@require_perm("note.write")
def amend_note(nid):
    old = db.session.get(ClinicalNote, nid)
    if not old:
        raise ApiError("Note not found", 404)
    get_authorized_patient(old.patient_id, "clinical")
    if old.author_id != g.user.id:
        raise ApiError("Only the author may amend a note; other clinicians should add a new note", 403)
    if old.status != "Final":
        raise ApiError("This note has already been superseded by an amendment", 409)
    d = payload()
    need(d, "body", "reason")
    new = ClinicalNote(patient_id=old.patient_id, author_id=g.user.id, note_type=old.note_type, body=s(d, "body", 8000), admission_id=old.admission_id,
                       encounter_id=old.encounter_id, amends_note_id=old.id, amendment_reason=s(d, "reason", 300))
    old.status = "Superseded"  # original text is preserved, never overwritten
    db.session.add(new)
    audit("note.amended", category="clinical", entity_type="clinical_note", entity_id=old.id, patient_id=old.patient_id, details=new.amendment_reason)
    commit()
    return ok("Amendment saved; the original note is preserved in history", id=new.id)


# --------------------------------------------------------------------------- #
# Care tasks, plans, intake/output, handover, follow-up
# --------------------------------------------------------------------------- #
def _task_row(t: CareTask, now=None, patient=None):
    now = now or utcnow()
    r = {"id": t.id, "patient_id": t.patient_id, "title": t.title, "category": t.category, "priority": t.priority, "status": t.status, "assigned_role": t.assigned_role,
         "assigned_user_id": t.assigned_user_id, "due_at": iso(t.due_at), "overdue": bool(t.status == "Pending" and t.due_at and t.due_at < now), "notes": t.notes,
         "completed_at": iso(t.completed_at)}
    if patient is not None:
        r["patient_name"], r["patient_code"] = patient.name, patient.patient_code
    return r


@bp.get("/patients/<int:pid>/tasks")
def patient_tasks(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(CareTask).where(CareTask.patient_id == pid).order_by(CareTask.status.desc(), CareTask.due_at)).scalars().all()
    return jsonify(ok=True, items=[_task_row(t) for t in rows])


@bp.post("/patients/<int:pid>/tasks")
@require_perm("task.write")
def add_task(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "title")
    cat = s(d, "category", 30) or "Other"
    if cat not in C.CARE_TASK_CATEGORIES:
        raise ApiError("category must be one of: " + ", ".join(C.CARE_TASK_CATEGORIES))
    prio = s(d, "priority", 20) or "Routine"
    if prio not in ("Routine", "Urgent"):
        raise ApiError("priority must be Routine or Urgent")
    adm = monitoring.active_admission(pid)
    t = CareTask(patient_id=pid, admission_id=adm.id if adm else None, title=s(d, "title", 200), category=cat, priority=prio,
                 assigned_role=s(d, "assigned_role", 30) or "nurse", due_at=parse_dt(d.get("due_at"), "due_at"), notes=s(d, "notes", 500), created_by_id=g.user.id)
    db.session.add(t)
    audit("task.created", category="clinical", entity_type="care_task", patient_id=pid, details=t.title[:100])
    commit()
    return ok("Task created", id=t.id)


@bp.patch("/tasks/<int:tid>")
@require_perm("task.complete")
def update_task(tid):
    t = db.session.get(CareTask, tid)
    if not t:
        raise ApiError("Task not found", 404)
    get_authorized_patient(t.patient_id, "clinical")
    status = s(payload(), "status", 20)
    if t.status != "Pending":
        raise ApiError(f"Task is already {t.status}", 409)
    if status not in ("Done", "Cancelled"):
        raise ApiError("status must be Done or Cancelled")
    t.status = status
    if status == "Done":
        t.completed_at, t.completed_by_id = utcnow(), g.user.id
    audit("task.completed" if status == "Done" else "task.cancelled", category="clinical", entity_type="care_task", entity_id=tid, patient_id=t.patient_id)
    commit()
    return ok("Task updated")


@bp.get("/tasks")
def list_tasks():
    """Cross-patient task list restricted to patients the user may see clinically."""
    now = utcnow()
    q = select(CareTask, Patient).join(Patient, Patient.id == CareTask.patient_id).where(CareTask.status == "Pending")
    if request.args.get("overdue") == "1":
        q = q.where(CareTask.due_at < now)
    rows = db.session.execute(q.order_by(CareTask.due_at).limit(500)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    out = [_task_row(t, now, p) for t, p in rows if "clinical" in sc.get(p.id, ())]
    if request.args.get("role") == "mine":
        out = [t for t in out if t["assigned_role"] == g.user.role or t["assigned_user_id"] == g.user.id]
    return jsonify(ok=True, items=out[:200])


@bp.post("/patients/<int:pid>/care-plans")
@require_perm("care.plan")
def add_care_plan(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "title")
    adm = monitoring.active_admission(pid)
    cp = CarePlan(patient_id=pid, admission_id=adm.id if adm else None, title=s(d, "title", 200), goals=s(d, "goals", 2000), author_id=g.user.id)
    db.session.add(cp)
    audit("careplan.created", category="clinical", entity_type="care_plan", patient_id=pid)
    commit()
    return ok("Care plan saved", id=cp.id)


@bp.get("/patients/<int:pid>/care-plans")
def list_care_plans(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(CarePlan).where(CarePlan.patient_id == pid).order_by(CarePlan.created_at.desc())).scalars()
    return jsonify(ok=True, items=[{"id": c.id, "title": c.title, "goals": c.goals, "status": c.status, "created_at": iso(c.created_at)} for c in rows])


@bp.get("/patients/<int:pid>/intake-output")
def list_io(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(IntakeOutput).where(IntakeOutput.patient_id == pid).order_by(IntakeOutput.recorded_at.desc()).limit(100)).scalars().all()
    since = utcnow() - timedelta(hours=24)
    tot = {"Intake": 0.0, "Output": 0.0}
    for r in rows:
        if r.recorded_at >= since:
            tot[r.kind] += r.amount_ml
    return jsonify(ok=True, totals_24h=tot, items=[{"id": r.id, "kind": r.kind, "item": r.item, "amount_ml": r.amount_ml, "recorded_at": iso(r.recorded_at)} for r in rows])


@bp.post("/patients/<int:pid>/intake-output")
@require_perm("io.record")
def add_io(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "kind", "amount_ml")
    kind = s(d, "kind", 10)
    if kind not in ("Intake", "Output"):
        raise ApiError("kind must be Intake or Output")
    from ..utils import to_float
    adm = monitoring.active_admission(pid)
    r = IntakeOutput(patient_id=pid, admission_id=adm.id if adm else None, kind=kind, item=s(d, "item", 100), amount_ml=to_float(d["amount_ml"], "amount_ml", 0, 10000), recorded_by_id=g.user.id)
    db.session.add(r)
    audit("io.recorded", category="clinical", entity_type="intake_output", patient_id=pid, details=kind)
    commit()
    return ok("Recorded")


def _handover_row(h: Handover):
    return {"id": h.id, "kind": h.kind, "shift": h.shift, "situation": h.situation, "background": h.background, "assessment": h.assessment, "recommendation": h.recommendation,
            "is_auto_draft": h.is_auto_draft, "author": h.author.name if h.author else "", "created_at": iso(h.created_at), "reviewed_at": iso(h.reviewed_at), "patient_id": h.patient_id}


@bp.get("/patients/<int:pid>/handovers")
def list_handovers(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(Handover).where(Handover.patient_id == pid).order_by(Handover.created_at.desc()).limit(30)).scalars()
    return jsonify(ok=True, items=[_handover_row(h) for h in rows])


@bp.get("/patients/<int:pid>/handover-draft")
@require_perm("handover.write")
def handover_draft(pid):
    """Deterministic SBAR draft compiled from structured records. It is a draft: a clinician must review it."""
    p = get_authorized_patient(pid, "clinical")
    sc = patient_scopes(g.user, pid)
    snap = journey.build_snapshot(p, sc, g.user)
    stay = snap["stay"]
    age = age_from_dob(p.dob)
    sit = f"{p.name} ({p.patient_code}), {age if age is not None else '?'}y {p.gender}"
    if stay:
        sit += f", {stay['ward']} / bed {stay['bed']['code'] if stay['bed'] else 'unassigned'}, admitted {stay['admitted_on']}"
        if stay.get("reason"):
            sit += f" for: {stay['reason']}"
    bg = []
    if snap["problems"]:
        bg.append("Active problems: " + "; ".join(x["description"] for x in snap["problems"]))
    if snap["allergies"]:
        bg.append("Allergies: " + "; ".join(f"{a['substance']} ({a['reaction'] or 'reaction not recorded'})" for a in snap["allergies"]))
    elif patient_view(g.user, p, sc).get("allergies_text"):
        bg.append("Allergies (free text): " + p.allergies)
    else:
        bg.append("No allergies documented in the record (this does not confirm there are none).")
    if snap["medications"]:
        bg.append("Active medication orders: " + "; ".join(f"{m['medicine']} {m['dosage']}" for m in snap["medications"]))
    ass = []
    v = snap["vitals"] or {}
    if v:
        ass.append("Latest observations: " + ", ".join(f"{x['label']} {x['value']:g} {x['unit']} ({x['source']}, {x['observed_at']})" for x in v.values()))
    else:
        ass.append("No observations recorded.")
    if snap["alerts"]:
        ass.append("Open alerts: " + "; ".join(f"{a['severity']} - {a['message']} [{a['status']}]" for a in snap["alerts"]))
    if snap["critical_pending"]:
        ass.append("UNACKNOWLEDGED critical results: " + "; ".join(c["summary"] for c in snap["critical_pending"]))
    rec = []
    if snap["tasks"]:
        rec.append("Outstanding tasks: " + "; ".join(f"{t['title']}{' (OVERDUE)' if t['overdue'] else ''}" for t in snap["tasks"]))
    if snap["pending_results"]:
        rec.append("Results pending: " + "; ".join(f"{r['title']} [{r['status']}]" for r in snap["pending_results"]))
    if stay and stay["discharge_status"] != "None":
        rec.append(f"Discharge status: {stay['discharge_status']}")
    rec.append("Clinician to add plan and escalation criteria.")
    audit("handover.draft_generated", category="ai", entity_type="patient", entity_id=pid, patient_id=pid, details="deterministic compile, no external service")
    db.session.commit()
    return jsonify(ok=True, is_auto_draft=True, notice="Automatically compiled from structured records. Review and edit before use.",
                   situation=sit, background="\n".join(bg), assessment="\n".join(ass), recommendation="\n".join(rec))


@bp.post("/patients/<int:pid>/handovers")
@require_perm("handover.write")
def add_handover(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    kind = "Medical" if g.user.role == C.DOCTOR else "Nursing"
    adm = monitoring.active_admission(pid)
    h = Handover(patient_id=pid, admission_id=adm.id if adm else None, kind=kind, shift=s(d, "shift", 20) or "Day",
                 situation=s(d, "situation", 3000), background=s(d, "background", 3000), assessment=s(d, "assessment", 3000),
                 recommendation=s(d, "recommendation", 3000), is_auto_draft=bool(d.get("is_auto_draft")), author_id=g.user.id)
    if not any((h.situation, h.background, h.assessment, h.recommendation)):
        raise ApiError("Handover is empty")
    db.session.add(h)
    audit("handover.saved", category="clinical", entity_type="handover", patient_id=pid, details=f"{kind}/{h.shift}")
    commit()
    return ok("Handover saved", id=h.id)


@bp.post("/handovers/<int:hid>/review")
@require_perm("handover.write")
def review_handover(hid):
    h = db.session.get(Handover, hid)
    if not h:
        raise ApiError("Handover not found", 404)
    get_authorized_patient(h.patient_id, "clinical")
    if h.author_id == g.user.id:
        raise ApiError("A handover must be reviewed by someone other than its author", 409)
    h.reviewed_by_id, h.reviewed_at = g.user.id, utcnow()
    audit("handover.reviewed", category="clinical", entity_type="handover", entity_id=hid, patient_id=h.patient_id)
    commit()
    return ok("Handover acknowledged")


@bp.get("/patients/<int:pid>/follow-ups")
def list_followups(pid):
    get_authorized_patient(pid, "clinical")
    rows = db.session.execute(select(FollowUp).where(FollowUp.patient_id == pid).order_by(FollowUp.created_at.desc())).scalars()
    return jsonify(ok=True, items=[{"id": f.id, "due_on": f.due_on, "instructions": f.instructions, "status": f.status, "appointment_id": f.appointment_id, "created_at": iso(f.created_at)} for f in rows])


@bp.post("/patients/<int:pid>/follow-ups")
@require_perm("followup.write")
def add_followup(pid):
    get_authorized_patient(pid, "clinical")
    d = payload()
    need(d, "instructions")
    adm = monitoring.active_admission(pid)
    f = FollowUp(patient_id=pid, admission_id=adm.id if adm else None, due_on=valid_date(d.get("due_on", ""), "due_on"), instructions=s(d, "instructions", 2000), created_by_id=g.user.id)
    db.session.add(f)
    audit("followup.created", category="clinical", entity_type="follow_up", patient_id=pid)
    commit()
    return ok("Follow-up planned", id=f.id)


# --------------------------------------------------------------------------- #
# Care-team assignments
# --------------------------------------------------------------------------- #
@bp.get("/patients/<int:pid>/assignments")
def list_assignments(pid):
    get_authorized_patient(pid, "identity")
    return jsonify(ok=True, items=journey.care_team(pid))


@bp.post("/patients/<int:pid>/assignments")
def add_assignment(pid):
    get_authorized_patient(pid, "identity")
    d = payload()
    need(d, "user_id")
    relation = s(d, "relation", 20) or "primary"
    if relation not in ("primary", "consulting", "covering"):
        raise ApiError("relation must be primary, consulting or covering")
    can_admin = has_perm(g.user, "assign.manage")
    if not can_admin and not (g.user.role == C.DOCTOR and "clinical" in patient_scopes(g.user, pid) and relation in ("consulting", "covering")):
        raise ApiError("You may not manage this patient's care team", 403)
    target = db.session.get(AppUser, to_int(d["user_id"], "user_id"))
    if not target or not target.is_active or target.role not in (C.DOCTOR, C.NURSE):
        raise ApiError("Assignee must be an active doctor or nurse", 404)
    existing = db.session.execute(select(PatientAssignment).where(PatientAssignment.patient_id == pid, PatientAssignment.user_id == target.id, PatientAssignment.active.is_(True))).scalar_one_or_none()
    if existing:
        raise ApiError("That clinician is already on this patient's care team", 409)
    db.session.add(PatientAssignment(patient_id=pid, user_id=target.id, relation=relation, created_by_id=g.user.id))
    audit("assignment.added", category="admin", entity_type="patient_assignment", patient_id=pid, details=f"user={target.id} {relation}")
    commit()
    return ok("Care team updated")


@bp.delete("/assignments/<int:aid>")
def end_assignment(aid):
    a = db.session.get(PatientAssignment, aid)
    if not a:
        raise ApiError("Assignment not found", 404)
    if not has_perm(g.user, "assign.manage"):
        raise ApiError("Only administrators may remove care-team assignments", 403)
    a.active, a.ends_at = False, utcnow()
    audit("assignment.ended", category="admin", entity_type="patient_assignment", entity_id=aid, patient_id=a.patient_id)
    commit()
    return ok("Assignment ended")
