"""Laboratory, radiology, pharmacy, billing and critical-result workflows."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import func, or_, select

from .. import constants as C
from ..access import bulk_scopes, get_authorized_patient, has_perm, patient_scopes, require_perm
from ..audit import audit
from ..extensions import db
from ..models import (MedicalDocument, Admission, AppUser, Bill, BillAdjustment, CriticalAck, DispenseEvent, InsuranceClaim, LabReport, LabResult, MedReconciliation,
                      Medicine, MedicationAdministration, Notification, Patient, Payment, Prescription, RadiologyRecord, RadiologyReportVersion,
                      StockMovement, utcnow)
from ..services import deliverables as dsvc
from ..services import monitoring
from ..services import orders as osvc
from ..utils import (ApiError, commit, iso, need, ok, page_args, parse_dt, payload, s, to_float, to_int, valid_date)

bp = Blueprint("orders", __name__, url_prefix="/api")


def _user_names(ids):
    ids = {i for i in ids if i}
    return {u.id: u.name for u in db.session.execute(select(AppUser).where(AppUser.id.in_(ids))).scalars()} if ids else {}


# =========================================================================== #
# LABORATORY
# =========================================================================== #
LAB_STAFF_ROLES = (C.LAB_STAFF, C.SUPER_ADMIN)


def _lab_status(l: LabReport) -> str:
    return {"Pending": "Ordered", "Completed": "Released"}.get(l.status, l.status)


def _can_see_results(user, l: LabReport) -> bool:
    return user.role in LAB_STAFF_ROLES or _lab_status(l) == "Released"


def _result_row(r: LabResult):
    return {"id": r.id, "analyte": r.analyte, "value_num": r.value_num, "value_text": r.value_text, "unit": r.unit, "ref_low": r.ref_low, "ref_high": r.ref_high,
            "ref_text": r.ref_text or (f"{r.ref_low:g}-{r.ref_high:g}" if r.ref_low is not None and r.ref_high is not None else ""), "critical_low": r.critical_low,
            "critical_high": r.critical_high, "flag": r.flag, "is_critical": r.is_critical, "status": r.status, "version": r.version, "correction_reason": r.correction_reason}


def _attached_files(user, *, lab_report_id=None, radiology_id=None) -> list[dict]:
    """Files attached to a lab/radiology order that this user's role may see (download goes through /api/documents/<id>/download)."""
    from ..access import can_see_doc_type
    if not has_perm(user, "doc.read"):
        return []
    cond = MedicalDocument.lab_report_id == lab_report_id if lab_report_id else MedicalDocument.radiology_id == radiology_id
    rows = db.session.execute(select(MedicalDocument).where(cond).order_by(MedicalDocument.id)).scalars().all()
    return [{"id": d.id, "title": d.title, "doc_type": d.doc_type, "mime_type": d.mime_type, "size_bytes": d.size_bytes, "uploaded_at": iso(d.uploaded_at),
             "uploaded_by": d.uploaded_by.name if d.uploaded_by else "", "patient_visible": bool(d.patient_visible)} for d in rows if can_see_doc_type(user, d.doc_type)]


def _lab_row(l: LabReport, user, patient=None, detail=False, names=None):
    names = names or {}
    st = _lab_status(l)
    row = {"id": l.id, "patient_id": l.patient_id, "test_name": l.test_name, "status": st, "priority": l.priority or "Routine", "specimen_type": l.specimen_type,
           "accession_no": l.accession_no, "ordered_at": iso(l.ordered_at), "sample_date": l.sample_date, "collected_at": iso(l.collected_at), "received_at": iso(l.received_at),
           "resulted_at": iso(l.resulted_at), "verified_at": iso(l.verified_at), "released_at": iso(l.released_at), "rejected_reason": l.rejected_reason,
           "ordered_by": names.get(l.ordered_by_id) or l.ordered_by, "clinical_info": l.clinical_info, "amendment_count": l.amendment_count or 0}
    if patient is not None:
        row.update(patient_name=patient.name, patient_code=patient.patient_code)
    if _can_see_results(user, l):
        live = [r for r in l.results if r.status != "Superseded"]
        row["has_critical"] = any(r.is_critical for r in live)
        row["has_abnormal"] = any(r.flag not in ("Normal", "Not assessed") for r in live)
        if detail:
            row["results"] = [_result_row(r) for r in sorted(l.results, key=lambda x: (x.analyte, -x.version))]
            row["summary"] = l.result if st == "Released" else osvc.summarize_results(l)
            row["files"] = _attached_files(user, lab_report_id=l.id)
    elif detail:
        row["results"], row["summary"] = [], "Result not yet released."
    return row


@bp.get("/labs")
@require_perm("lab.read")
def list_labs():
    page, per = page_args(50, 200)
    q = select(LabReport, Patient).join(Patient, Patient.id == LabReport.patient_id)
    if request.args.get("patient_id"):
        q = q.where(LabReport.patient_id == to_int(request.args["patient_id"], "patient_id"))
    st = request.args.get("status")
    if st:
        legacy = {"Ordered": ("Ordered", "Pending"), "Released": ("Released", "Completed")}.get(st, (st,))
        q = q.where(LabReport.status.in_(legacy))
    rows = db.session.execute(q.order_by(LabReport.ordered_at.desc(), LabReport.id.desc()).limit(500)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    rows = [(l, p) for l, p in rows if "labs" in sc.get(p.id, ())]
    total = len(rows)
    rows = rows[(page - 1) * per: page * per]
    names = _user_names({l.ordered_by_id for l, _ in rows})
    return jsonify(ok=True, items=[_lab_row(l, g.user, p, names=names) for l, p in rows], page=page, per_page=per, total=total)


@bp.get("/labs/<int:lid>")
@require_perm("lab.read")
def get_lab(lid):
    l = db.session.get(LabReport, lid)
    if not l:
        raise ApiError("Lab record not found", 404)
    p = get_authorized_patient(l.patient_id, "labs")
    audit("lab.viewed", category="access", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id)
    db.session.commit()
    return jsonify(ok=True, **_lab_row(l, g.user, p, detail=True, names=_user_names({l.ordered_by_id, l.verified_by_id, l.released_by_id, l.resulted_by_id})))


@bp.post("/labs")
@require_perm("lab.order")
def create_lab():
    d = payload()
    need(d, "patient_id", "test_name")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "labs")
    prio = s(d, "priority", 10) or "Routine"
    if prio not in ("Routine", "Urgent", "STAT"):
        raise ApiError("priority must be Routine, Urgent or STAT")
    adm = monitoring.active_admission(p.id)
    l = LabReport(patient_id=p.id, test_name=s(d, "test_name", 120), sample_date=valid_date(d.get("sample_date", ""), "sample_date") or date.today().isoformat(), result="Pending",
                  status="Ordered", ordered_by=g.user.name, ordered_by_id=g.user.id, priority=prio, specimen_type=s(d, "specimen_type", 60),
                  clinical_info=s(d, "clinical_info", 300), admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None, ordered_at=utcnow())
    db.session.add(l)
    audit("lab.ordered", category="clinical", entity_type="lab_report", patient_id=p.id, details=l.test_name)
    commit()
    note = "Lab test ordered" + (" (result values are entered by laboratory staff; the 'result' field was ignored)" if d.get("result") else "")
    return ok(note, id=l.id)


def _lab_or_404(lid) -> LabReport:
    l = db.session.get(LabReport, lid)
    if not l:
        raise ApiError("Lab record not found", 404)
    return l


@bp.post("/labs/<int:lid>/collect")
@require_perm("lab.process")
def lab_collect(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    d = payload()
    osvc.lab_transition(l, "Collected")
    l.collected_at, l.collected_by_id = utcnow(), g.user.id
    l.specimen_type = s(d, "specimen_type", 60) or l.specimen_type
    l.accession_no = l.accession_no or osvc.next_accession()
    audit("lab.collected", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details=l.accession_no)
    commit()
    return ok("Specimen collected", accession_no=l.accession_no)


@bp.post("/labs/<int:lid>/receive")
@require_perm("lab.process")
def lab_receive(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    osvc.lab_transition(l, "Received")
    l.received_at = utcnow()
    audit("lab.received", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id)
    commit()
    return ok("Specimen received in laboratory")


@bp.post("/labs/<int:lid>/reject")
@require_perm("lab.process")
def lab_reject(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    reason = s(payload(), "reason", 300)
    if not reason:
        raise ApiError("A rejection reason is required")
    osvc.lab_transition(l, "Rejected")
    l.rejected_at, l.rejected_reason = utcnow(), reason
    db.session.add(Notification(user_id=l.ordered_by_id, kind="specimen-rejected", severity="Warning", title="Specimen rejected", body=f"{l.test_name}: {reason}"[:400], patient_id=l.patient_id, ref_type="lab", ref_id=l.id))
    audit("lab.rejected", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details=reason)
    commit()
    return ok("Specimen rejected; the ordering clinician was notified")


@bp.post("/labs/<int:lid>/reorder")
@require_perm("lab.process")
def lab_reorder(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    osvc.lab_transition(l, "Ordered")
    l.rejected_reason, l.collected_at, l.received_at = "", None, None
    audit("lab.recollection_requested", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id)
    commit()
    return ok("Order re-opened for recollection")


def _parse_result_items(items) -> list[dict]:
    if not isinstance(items, list) or not items:
        raise ApiError("results must be a non-empty list")
    out = []
    for i, it in enumerate(items, 1):
        if not isinstance(it, dict):
            raise ApiError(f"results[{i}] is invalid")
        analyte = s(it, "analyte", 120)
        if not analyte:
            raise ApiError(f"results[{i}]: analyte is required")
        raw = it.get("value")
        value_num, value_text = None, s(it, "value_text", 200)
        if raw not in (None, ""):
            try:
                value_num = float(str(raw).strip())
                if value_num != value_num or abs(value_num) == float("inf"):
                    raise ValueError
            except ValueError:
                value_text = str(raw).strip()[:200]
        if value_num is None and not value_text:
            raise ApiError(f"{analyte}: a value is required")
        def opt(k):
            v = it.get(k)
            return None if v in (None, "") else to_float(v, f"{analyte} {k}")
        out.append(dict(analyte=analyte, value_num=value_num, value_text=value_text, unit=s(it, "unit", 30), ref_low=opt("ref_low"), ref_high=opt("ref_high"),
                        ref_text=s(it, "ref_text", 100), critical_low=opt("critical_low"), critical_high=opt("critical_high"), manual_flag=s(it, "flag", 20)))
    return out


def _store_results(l: LabReport, items: list[dict]):
    if _lab_status(l) == "Resulted":
        for r in list(l.results):
            if r.status == "Entered":
                db.session.delete(r)
        db.session.flush()
    else:
        osvc.lab_transition(l, "Resulted")
    for it in items:
        it = dict(it)
        flag, crit = osvc.compute_flag(it["value_num"], it["ref_low"], it["ref_high"], it["critical_low"], it["critical_high"], it.pop("manual_flag"))
        db.session.add(LabResult(lab_report_id=l.id, flag=flag, is_critical=crit, entered_by_id=g.user.id, **it))
    l.resulted_at, l.resulted_by_id = utcnow(), g.user.id


@bp.put("/labs/<int:lid>/results")
@require_perm("lab.process")
def lab_enter_results(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    items = _parse_result_items(payload().get("results"))
    _store_results(l, items)
    audit("lab.resulted", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details=f"{len(items)} analyte(s)")
    commit()
    return ok("Results entered; awaiting verification")


@bp.post("/labs/<int:lid>/verify")
@require_perm("lab.verify")
def lab_verify(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    if current_app.config.get("LAB_DUAL_VERIFY") and l.resulted_by_id == g.user.id:
        raise ApiError("Verification must be performed by a different person than the one who entered the result", 409)
    osvc.lab_transition(l, "Verified")
    l.verified_at, l.verified_by_id = utcnow(), g.user.id
    audit("lab.verified", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id)
    commit()
    return ok("Results verified")


def _do_release(l: LabReport) -> list:
    """Release a verified result: finalise values, notify, share attached files with the patient and record the hand-over item."""
    osvc.lab_transition(l, "Released")
    l.released_at, l.released_by_id = utcnow(), g.user.id
    for r in l.results:
        if r.status == "Entered":
            r.status = "Final"
    l.result = osvc.summarize_results(l) or "Report attached - see the attached file."
    crit = [r for r in l.results if r.status != "Superseded" and r.is_critical]
    if crit:
        summary = f"{l.test_name}: " + "; ".join(f"{r.analyte} {r.value_num:g} {r.unit} ({r.flag})" if r.value_num is not None else f"{r.analyte} {r.value_text} ({r.flag})" for r in crit)
        osvc.notify_critical("lab", l.id, l.patient_id, summary, l.ordered_by_id)
    else:
        db.session.add(Notification(user_id=l.ordered_by_id, kind="result-released", severity="Info", title="Lab result released", body=f"{l.test_name} is available", patient_id=l.patient_id, ref_type="lab", ref_id=l.id))
    shared = dsvc.share_documents_with_patient(lab_report_id=l.id)
    dsvc.ensure(l.patient_id, "Laboratory report", f"{l.test_name} ({l.sample_date})", "lab", l.id, digital=True, created_by_id=g.user.id)
    return crit


@bp.post("/labs/<int:lid>/submit")
@require_perm("lab.verify")
def lab_submit(lid):
    """One-step 'attach report and mark complete'. Advances the order through the normal controlled states, recording each step
    (collect -> receive -> result -> verify -> release). Requires an attached report file and/or entered result values."""
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    if not has_perm(g.user, "lab.process"):
        raise ApiError("You do not have permission to process laboratory orders", 403)
    d = payload()
    st = _lab_status(l)
    if st == "Released":
        raise ApiError("This report has already been submitted and released", 409)
    if st in ("Rejected", "Cancelled"):
        raise ApiError(f"This order is {st.lower()}; it cannot be submitted", 409)
    items = _parse_result_items(d["results"]) if d.get("results") else None
    live = [r for r in l.results if r.status != "Superseded"]
    n_files = db.session.execute(select(func.count(MedicalDocument.id)).where(MedicalDocument.lab_report_id == l.id)).scalar() or 0
    if not items and not live and not n_files:
        raise ApiError("Attach the laboratory report file and/or enter result values before submitting", 409)
    now = utcnow()
    steps = []
    if st == "Ordered":
        osvc.lab_transition(l, "Collected")
        l.collected_at, l.collected_by_id = now, g.user.id
        l.specimen_type = s(d, "specimen_type", 60) or l.specimen_type
        l.accession_no = l.accession_no or osvc.next_accession()
        steps.append("collected")
        st = "Collected"
    if st == "Collected":
        osvc.lab_transition(l, "Received")
        l.received_at = now
        steps.append("received")
        st = "Received"
    if st in ("Received", "Resulted") and items:
        _store_results(l, items)
        steps.append("results entered")
        st = "Resulted"
    elif st == "Received":      # report supplied as an attached file only
        osvc.lab_transition(l, "Resulted")
        l.resulted_at, l.resulted_by_id = now, g.user.id
        steps.append("report attached")
        st = "Resulted"
    if current_app.config.get("LAB_DUAL_VERIFY") and l.resulted_by_id == g.user.id:
        audit("lab.submitted", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details="awaiting second verifier: " + ", ".join(steps))
        commit()
        return ok("Submitted. A second person must verify this result before it is released.", status=_lab_status(l), steps=steps)
    osvc.lab_transition(l, "Verified")
    l.verified_at, l.verified_by_id = now, g.user.id
    crit = _do_release(l)
    steps += ["verified", "released"]
    audit("lab.submitted", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details=", ".join(steps) + (" (critical)" if crit else ""))
    commit()
    return ok("Report submitted and released. Doctors, administrators and the patient can now view it." + (" CRITICAL value(s): acknowledgment workflow started." if crit else ""),
              status=_lab_status(l), steps=steps)


@bp.post("/labs/<int:lid>/release")
@require_perm("lab.verify")
def lab_release(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    crit = _do_release(l)
    audit("lab.released", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details="critical" if crit else "")
    commit()
    return ok("Result released to the ordering clinician" + (" - CRITICAL value(s): acknowledgment workflow started" if crit else ""))


@bp.post("/labs/<int:lid>/amend")
@require_perm("lab.verify")
def lab_amend(lid):
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    if _lab_status(l) != "Released":
        raise ApiError("Only released results are amended; edit unreleased results directly", 409)
    d = payload()
    reason = s(d, "reason", 300)
    if not reason:
        raise ApiError("A reason for the correction is required")
    items = _parse_result_items(d.get("results"))
    live = {r.analyte.lower(): r for r in l.results if r.status != "Superseded"}
    for it in items:
        old = live.get(it["analyte"].lower())
        flag, crit = osvc.compute_flag(it["value_num"], it["ref_low"], it["ref_high"], it["critical_low"], it["critical_high"], it.pop("manual_flag"))
        new = LabResult(lab_report_id=l.id, flag=flag, is_critical=crit, entered_by_id=g.user.id, status="Final", correction_reason=reason, **it)
        if old:
            old.status = "Superseded"
            new.version, new.supersedes_id = old.version + 1, old.id
        db.session.add(new)
    db.session.flush()
    l.amendment_count = (l.amendment_count or 0) + 1
    db.session.refresh(l)
    l.result = osvc.summarize_results(l)
    db.session.add(Notification(user_id=l.ordered_by_id, kind="result-amended", severity="Warning", title="Released lab result was CORRECTED", body=f"{l.test_name}: {reason}"[:400],
                                patient_id=l.patient_id, ref_type="lab", ref_id=l.id))
    crit = [r for r in l.results if r.status != "Superseded" and r.is_critical]
    if crit:
        ack = db.session.execute(select(CriticalAck).where(CriticalAck.source_type == "lab", CriticalAck.source_id == l.id)).scalar_one_or_none()
        if ack:
            ack.status, ack.ack_at, ack.ack_by_id = "Pending", None, None  # new critical value after correction needs a fresh acknowledgment
        else:
            osvc.notify_critical("lab", l.id, l.patient_id, f"{l.test_name} (corrected): critical value", l.ordered_by_id)
    audit("lab.amended", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details=reason)
    commit()
    return ok("Correction recorded. Previous values are retained in history.")


@bp.patch("/labs/<int:lid>")
@require_perm("lab.process")
def legacy_lab_result(lid):
    """Backward-compatible single-line result entry (maps onto the structured workflow)."""
    l = _lab_or_404(lid)
    get_authorized_patient(l.patient_id, "labs")
    text_ = s(payload(), "result", 200)
    if not text_:
        raise ApiError("A result value is required")
    st = _lab_status(l)
    if st in ("Verified", "Released", "Rejected", "Cancelled"):
        raise ApiError(f"Lab order is {st}; use the amendment workflow", 409)
    if st in ("Ordered", "Collected"):
        l.collected_at = l.collected_at or utcnow()
        l.accession_no = l.accession_no or osvc.next_accession()
        l.received_at = utcnow()
        l.status = "Received"
    if _lab_status(l) == "Resulted":
        for r in list(l.results):
            if r.status == "Entered":
                db.session.delete(r)
        db.session.flush()
    else:
        l.status = "Resulted"
    db.session.add(LabResult(lab_report_id=l.id, analyte=l.test_name, value_text=text_, flag="Not assessed", entered_by_id=g.user.id))
    l.resulted_at, l.resulted_by_id = utcnow(), g.user.id
    audit("lab.resulted", category="clinical", entity_type="lab_report", entity_id=lid, patient_id=l.patient_id, details="legacy single-value entry")
    commit()
    return ok("Result entered; awaiting verification")


@bp.get("/patients/<int:pid>/lab-trend")
def lab_trend(pid):
    """Time series of one analyte across the patient's released reports (units are preserved per point)."""
    get_authorized_patient(pid, "labs")
    analyte = (request.args.get("analyte") or "").strip().lower()
    if not analyte:
        raise ApiError("analyte is required")
    rows = db.session.execute(select(LabResult, LabReport).join(LabReport, LabReport.id == LabResult.lab_report_id)
                              .where(LabReport.patient_id == pid, LabReport.status.in_(("Released", "Completed")), LabResult.status != "Superseded",
                                     func.lower(LabResult.analyte).like(f"%{analyte}%")).order_by(LabReport.released_at)).all()
    return jsonify(ok=True, analyte=analyte, points=[{"at": iso(rep.released_at or rep.ordered_at), "value": r.value_num, "text": r.value_text, "unit": r.unit, "flag": r.flag,
                                                      "ref_low": r.ref_low, "ref_high": r.ref_high, "report_id": rep.id, "analyte": r.analyte} for r, rep in rows])


# =========================================================================== #
# CRITICAL RESULT ACKNOWLEDGMENT
# =========================================================================== #
def _crit_row(c: CriticalAck, p: Patient):
    return {"id": c.id, "source_type": c.source_type, "source_id": c.source_id, "patient_id": c.patient_id, "patient_name": p.name, "patient_code": p.patient_code,
            "summary": c.summary, "status": c.status, "created_at": iso(c.created_at), "ack_at": iso(c.ack_at), "ack_note": c.ack_note, "escalated_at": iso(c.escalated_at),
            "age_min": int((utcnow() - c.created_at).total_seconds() // 60)}


@bp.get("/critical")
def list_critical():
    monitoring.run_sweeps()
    status = request.args.get("status")
    q = select(CriticalAck, Patient).join(Patient, Patient.id == CriticalAck.patient_id)
    if status == "open":
        q = q.where(CriticalAck.status != "Acknowledged")
    rows = db.session.execute(q.order_by(CriticalAck.created_at.desc()).limit(200)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    def vis(c, p):
        need_scope = "labs" if c.source_type == "lab" else "radiology"
        return need_scope in sc.get(p.id, ())
    return jsonify(ok=True, items=[_crit_row(c, p) for c, p in rows if vis(c, p)])


@bp.post("/critical/<int:cid>/ack")
def ack_critical(cid):
    c = db.session.get(CriticalAck, cid)
    if not c:
        raise ApiError("Not found", 404)
    if g.user.role not in (C.DOCTOR,):
        raise ApiError("Critical results are acknowledged by a responsible clinician", 403)
    get_authorized_patient(c.patient_id, "labs" if c.source_type == "lab" else "radiology")
    if c.status == "Acknowledged":
        raise ApiError("Already acknowledged", 409)
    c.status, c.ack_by_id, c.ack_at, c.ack_note = "Acknowledged", g.user.id, utcnow(), s(payload(), "note", 300)
    audit("critical_result.acknowledged", category="clinical", entity_type=c.source_type, entity_id=c.source_id, patient_id=c.patient_id)
    commit()
    return ok("Critical result acknowledged")


# =========================================================================== #
# RADIOLOGY
# =========================================================================== #
MODALITIES = ("X-ray", "CT", "MRI", "Ultrasound", "Mammography", "Fluoroscopy", "Nuclear medicine", "Other")
RAD_STAFF = (C.RADIOLOGY_STAFF, C.SUPER_ADMIN)


def _rad_visible_report(user, r: RadiologyRecord) -> bool:
    return user.role in RAD_STAFF or r.order_status == "Final" or (r.order_status is None and r.report_status == "Final")


def _rad_row(r: RadiologyRecord, user, p=None, detail=False, names=None):
    names = names or {}
    st = r.order_status or ("Final" if r.report_status == "Final" else "Ordered")
    row = {"id": r.id, "patient_id": r.patient_id, "modality": r.modality, "study_description": r.study_description, "study_date": r.study_date, "order_status": st,
           "priority": r.priority or "Routine", "indication": r.indication, "scheduled_at": iso(r.scheduled_at), "performed_at": iso(r.performed_at),
           "reported_at": iso(r.reported_at), "authorized_at": iso(r.authorized_at), "urgent_finding": bool(r.urgent_finding), "amendment_count": r.amendment_count or 0,
           "ordered_by": names.get(r.ordered_by_id, ""), "report_status": r.report_status}
    if p is not None:
        row.update(patient_name=p.name, patient_code=p.patient_code)
    if detail:
        if _rad_visible_report(user, r):
            row.update(findings=r.findings, impression=r.impression, recommendations=r.recommendations)
            vers = db.session.execute(select(RadiologyReportVersion).where(RadiologyReportVersion.radiology_id == r.id).order_by(RadiologyReportVersion.version)).scalars().all()
            row["versions"] = [{"version": v.version, "status": v.status, "created_at": iso(v.created_at), "change_reason": v.change_reason, "findings": v.findings,
                                "impression": v.impression, "recommendations": v.recommendations} for v in vers]
        else:
            row.update(findings="", impression="", recommendations="", note="Report not yet authorized.")
        row["image_notice"] = "CareFlow stores reports and uploaded image files; it is not a PACS/DICOM viewer."
        row["files"] = _attached_files(user, radiology_id=r.id)
    return row


@bp.get("/radiology")
@require_perm("rad.read")
def list_radiology():
    page, per = page_args(50, 200)
    q = select(RadiologyRecord, Patient).join(Patient, Patient.id == RadiologyRecord.patient_id)
    if request.args.get("patient_id"):
        q = q.where(RadiologyRecord.patient_id == to_int(request.args["patient_id"], "patient_id"))
    rows = db.session.execute(q.order_by(RadiologyRecord.ordered_at.desc(), RadiologyRecord.id.desc()).limit(500)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    rows = [(r, p) for r, p in rows if "radiology" in sc.get(p.id, ())]
    total = len(rows)
    rows = rows[(page - 1) * per: page * per]
    names = _user_names({r.ordered_by_id for r, _ in rows})
    return jsonify(ok=True, items=[_rad_row(r, g.user, p, names=names) for r, p in rows], page=page, per_page=per, total=total)


@bp.get("/radiology/<int:rid>")
@require_perm("rad.read")
def get_radiology(rid):
    r = db.session.get(RadiologyRecord, rid)
    if not r:
        raise ApiError("Radiology record not found", 404)
    p = get_authorized_patient(r.patient_id, "radiology")
    audit("radiology.viewed", category="access", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id)
    db.session.commit()
    return jsonify(ok=True, **_rad_row(r, g.user, p, detail=True, names=_user_names({r.ordered_by_id, r.reported_by_id, r.authorized_by_id})))


@bp.post("/radiology")
@require_perm("rad.order")
def create_radiology():
    d = payload()
    need(d, "patient_id", "modality")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "radiology")
    modality = s(d, "modality", 50)
    if modality not in MODALITIES:
        raise ApiError("modality must be one of: " + ", ".join(MODALITIES))
    prio = s(d, "priority", 10) or "Routine"
    if prio not in ("Routine", "Urgent", "STAT"):
        raise ApiError("priority must be Routine, Urgent or STAT")
    adm = monitoring.active_admission(p.id)
    r = RadiologyRecord(patient_id=p.id, modality=modality, study_date=valid_date(d.get("study_date", ""), "study_date") or date.today().isoformat(), findings="", report_status="Draft",
                        order_status="Ordered", study_description=s(d, "study_description", 200), indication=s(d, "indication", 300), priority=prio, ordered_by_id=g.user.id,
                        admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None, ordered_at=utcnow())
    db.session.add(r)
    audit("radiology.ordered", category="clinical", entity_type="radiology_record", patient_id=p.id, details=modality)
    commit()
    return ok("Imaging study ordered" + (" (findings are written by radiology staff; the 'findings' field was ignored)" if d.get("findings") else ""), id=r.id)


def _rad_or_404(rid):
    r = db.session.get(RadiologyRecord, rid)
    if not r:
        raise ApiError("Radiology record not found", 404)
    return r


def _rad_move(r, new):
    cur = r.order_status or "Ordered"
    if new not in C.RAD_TRANSITIONS.get(cur, set()):
        raise ApiError(f"Study cannot move from {cur} to {new}", 409)
    r.order_status = new


@bp.post("/radiology/<int:rid>/schedule")
@require_perm("rad.perform")
def rad_schedule(rid):
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    when = parse_dt(payload().get("scheduled_at"), "scheduled_at", allow_empty=False)
    _rad_move(r, "Scheduled")
    r.scheduled_at = when
    audit("radiology.scheduled", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id)
    commit()
    return ok("Study scheduled")


@bp.post("/radiology/<int:rid>/perform")
@require_perm("rad.perform")
def rad_perform(rid):
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    _rad_move(r, "Performed")
    r.performed_at, r.performed_by_id = utcnow(), g.user.id
    audit("radiology.performed", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id)
    commit()
    return ok("Study marked as performed")


def _rad_version(r, status, reason=""):
    n = (db.session.execute(select(func.max(RadiologyReportVersion.version)).where(RadiologyReportVersion.radiology_id == r.id)).scalar() or 0) + 1
    db.session.add(RadiologyReportVersion(radiology_id=r.id, version=n, findings=r.findings, impression=r.impression, recommendations=r.recommendations,
                                          status=status, change_reason=reason, author_id=g.user.id))


@bp.put("/radiology/<int:rid>/report")
@require_perm("rad.report")
def rad_report(rid):
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    d = payload()
    need(d, "findings")
    st = r.order_status or "Ordered"
    if st in ("Ordered", "Scheduled"):
        raise ApiError("The study must be performed before it can be reported", 409)
    if st == "Final":
        raise ApiError("Report is final; use the amendment workflow", 409)
    if st == "Performed":
        _rad_move(r, "Reported")
    r.findings, r.impression, r.recommendations = s(d, "findings", 8000), s(d, "impression", 3000), s(d, "recommendations", 3000)
    r.urgent_finding = str(d.get("urgent_finding", "")).lower() in ("1", "true", "yes")
    r.reported_by_id, r.reported_at, r.report_status = g.user.id, utcnow(), "Draft"
    _rad_version(r, "Draft")
    audit("radiology.reported", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id)
    commit()
    return ok("Draft report saved")


def _do_authorize(r: RadiologyRecord):
    _rad_move(r, "Final")
    r.authorized_by_id, r.authorized_at, r.report_status = g.user.id, utcnow(), "Final"
    _rad_version(r, "Final", "Authorized")
    if r.urgent_finding:
        osvc.notify_critical("radiology", r.id, r.patient_id, f"{r.modality}: URGENT finding flagged by radiologist", r.ordered_by_id)
    else:
        db.session.add(Notification(user_id=r.ordered_by_id, kind="report-final", severity="Info", title="Imaging report available", body=f"{r.modality} report authorized", patient_id=r.patient_id, ref_type="radiology", ref_id=r.id))
    dsvc.share_documents_with_patient(radiology_id=r.id)
    dsvc.ensure(r.patient_id, "Radiology report", f"{r.modality} {r.study_description or ''} ({r.study_date})".replace("  ", " "), "radiology", r.id, digital=True, created_by_id=g.user.id)


@bp.post("/radiology/<int:rid>/submit")
@require_perm("rad.authorize")
def rad_submit(rid):
    """One-step 'attach scan/report and mark complete': perform -> report -> authorize, each step recorded."""
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    if not has_perm(g.user, "rad.report"):
        raise ApiError("You do not have permission to report imaging studies", 403)
    d = payload()
    st = r.order_status or "Ordered"
    if st == "Final":
        raise ApiError("This report is already final; use the amendment workflow", 409)
    if st == "Cancelled":
        raise ApiError("This study was cancelled", 409)
    findings = s(d, "findings", 8000) or (r.findings or "")
    if not findings.strip():
        raise ApiError("Enter the findings of the report before submitting", 409)
    steps = []
    if st in ("Ordered", "Scheduled"):
        _rad_move(r, "Performed")
        r.performed_at, r.performed_by_id = utcnow(), g.user.id
        steps.append("performed")
        st = "Performed"
    r.findings = findings
    r.impression = s(d, "impression", 3000) or r.impression or ""
    r.recommendations = s(d, "recommendations", 3000) or r.recommendations or ""
    if "urgent_finding" in d:
        r.urgent_finding = str(d.get("urgent_finding", "")).lower() in ("1", "true", "yes")
    if st == "Performed":
        _rad_move(r, "Reported")
    r.reported_by_id, r.reported_at, r.report_status = g.user.id, utcnow(), "Draft"
    _rad_version(r, "Draft")
    steps.append("reported")
    _do_authorize(r)
    steps.append("authorized")
    audit("radiology.submitted", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id, details=", ".join(steps) + (" (urgent)" if r.urgent_finding else ""))
    commit()
    return ok("Report submitted and released. Doctors, administrators and the patient can now view it." + ("; urgent-finding acknowledgment started." if r.urgent_finding else ""), status=r.order_status, steps=steps)


@bp.post("/radiology/<int:rid>/authorize")
@require_perm("rad.authorize")
def rad_authorize(rid):
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    if (r.order_status or "") != "Reported" or not (r.findings or "").strip():
        raise ApiError("A drafted report is required before authorization", 409)
    _do_authorize(r)
    audit("radiology.authorized", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id, details="urgent" if r.urgent_finding else "")
    commit()
    return ok("Report authorized and released" + ("; urgent-finding acknowledgment started" if r.urgent_finding else ""))


@bp.post("/radiology/<int:rid>/amend")
@require_perm("rad.authorize")
def rad_amend(rid):
    r = _rad_or_404(rid)
    get_authorized_patient(r.patient_id, "radiology")
    if (r.order_status or "") != "Final":
        raise ApiError("Only final reports are amended", 409)
    d = payload()
    need(d, "findings", "reason")
    r.findings, r.impression, r.recommendations = s(d, "findings", 8000), s(d, "impression", 3000), s(d, "recommendations", 3000)
    r.amendment_count = (r.amendment_count or 0) + 1
    _rad_version(r, "Final", s(d, "reason", 300))
    db.session.add(Notification(user_id=r.ordered_by_id, kind="report-amended", severity="Warning", title="Imaging report was AMENDED", body=f"{r.modality}: {s(d, 'reason', 300)}"[:400],
                                patient_id=r.patient_id, ref_type="radiology", ref_id=r.id))
    audit("radiology.amended", category="clinical", entity_type="radiology_record", entity_id=rid, patient_id=r.patient_id, details=s(d, "reason", 300))
    commit()
    return ok("Amendment recorded; earlier versions are preserved")


# =========================================================================== #
# PHARMACY
# =========================================================================== #
INVENTORY_ROLES = (C.PHARMACIST, C.HOSPITAL_ADMIN, C.SUPER_ADMIN)


def _med_row(m: Medicine, full: bool):
    today = date.today().isoformat()
    soon = (date.today() + timedelta(days=90)).isoformat()
    row = {"id": m.id, "name": m.name, "generic_name": m.generic_name, "strength": m.strength, "form": m.form, "category": m.category, "is_active": bool(m.is_active),
           "in_stock": (m.stock or 0) > 0, "expired": bool(m.expiry_date and m.expiry_date < today)}
    if full:
        row.update(stock=m.stock, reorder_level=m.reorder_level, unit_price=m.unit_price, expiry_date=m.expiry_date, batch_no=m.batch_no,
                   low_stock=(m.stock or 0) <= (m.reorder_level or 0), expiring_soon=bool(m.expiry_date and today <= m.expiry_date <= soon))
    return row


@bp.get("/medicines")
@require_perm("rx.read")
def list_medicines():
    full = g.user.role in INVENTORY_ROLES
    q = select(Medicine)
    term = (request.args.get("q") or "").strip()
    if term:
        q = q.where(or_(Medicine.name.ilike(f"%{term}%"), Medicine.generic_name.ilike(f"%{term}%")))
    if full and request.args.get("low_stock") == "1":
        q = q.where(Medicine.stock <= Medicine.reorder_level)
    rows = db.session.execute(q.order_by(Medicine.name).limit(500)).scalars().all()
    return jsonify(ok=True, items=[_med_row(m, full) for m in rows], full_detail=full)


@bp.post("/medicines")
@require_perm("inventory.manage")
def create_medicine():
    d = payload()
    need(d, "name")
    name = s(d, "name", 120)
    stock = to_int(d.get("stock", 0) or 0, "stock")
    price = to_float(d.get("unit_price", 0) or 0, "unit_price")
    if stock < 0 or price < 0:
        raise ApiError("Stock and price cannot be negative")
    if db.session.execute(select(Medicine.id).where(func.lower(Medicine.name) == name.lower())).first():
        raise ApiError("Medicine already exists", 409)
    m = Medicine(name=name, category=s(d, "category", 80) or "General", stock=0, reorder_level=to_int(d.get("reorder_level", 10) or 10, "reorder_level", 0), unit_price=price,
                 expiry_date=valid_date(d.get("expiry_date", ""), "expiry_date"), generic_name=s(d, "generic_name", 120), strength=s(d, "strength", 40), form=s(d, "form", 40), batch_no=s(d, "batch_no", 40))
    db.session.add(m)
    db.session.flush()
    if stock:
        osvc.adjust_stock(m, stock, "restock", g.user, "initial stock")
    audit("medicine.created", category="clinical", entity_type="medicine", entity_id=m.id, details=m.name)
    commit()
    return ok("Medicine added", id=m.id)


@bp.patch("/medicines/<int:mid>")
@require_perm("inventory.manage")
def update_medicine(mid):
    m = db.session.get(Medicine, mid)
    if not m:
        raise ApiError("Medicine not found", 404)
    d = payload()
    if "stock" in d:
        new = to_int(d["stock"], "stock")
        if new < 0:
            raise ApiError("Stock cannot be negative")
        if new != (m.stock or 0):
            osvc.adjust_stock(m, new - (m.stock or 0), "adjustment", g.user, "set via inventory screen")
    if "unit_price" in d:
        m.unit_price = to_float(d["unit_price"], "unit_price", 0)
    if "expiry_date" in d:
        m.expiry_date = valid_date(d["expiry_date"], "expiry_date")
    if "reorder_level" in d:
        m.reorder_level = to_int(d["reorder_level"], "reorder_level", 0)
    if "is_active" in d:
        m.is_active = str(d["is_active"]).lower() in ("1", "true", "yes")
    for k, mx in (("generic_name", 120), ("strength", 40), ("form", 40), ("batch_no", 40), ("category", 80)):
        if k in d:
            setattr(m, k, s(d, k, mx))
    audit("medicine.updated", category="clinical", entity_type="medicine", entity_id=mid, details=m.name)
    commit()
    return ok("Inventory updated")


@bp.post("/medicines/<int:mid>/restock")
@require_perm("inventory.manage")
def restock(mid):
    m = db.session.get(Medicine, mid)
    if not m:
        raise ApiError("Medicine not found", 404)
    d = payload()
    need(d, "quantity")
    q = to_int(d["quantity"], "quantity", 1, 1_000_000)
    osvc.adjust_stock(m, q, "restock", g.user, s(d, "batch_no", 30))
    if d.get("batch_no"):
        m.batch_no = s(d, "batch_no", 40)
    if d.get("expiry_date"):
        m.expiry_date = valid_date(d["expiry_date"], "expiry_date")
    commit()
    return ok(f"Restocked; balance {m.stock}")


@bp.get("/medicines/<int:mid>/movements")
@require_perm("inventory.manage")
def movements(mid):
    rows = db.session.execute(select(StockMovement).where(StockMovement.medicine_id == mid).order_by(StockMovement.created_at.desc()).limit(100)).scalars()
    return jsonify(ok=True, items=[{"at": iso(r.created_at), "delta": r.delta, "balance_after": r.balance_after, "reason": r.reason, "ref_type": r.ref_type, "ref_id": r.ref_id} for r in rows])


def _rx_row(r: Prescription, p=None, names=None):
    names = names or {}
    row = {"id": r.id, "patient_id": r.patient_id, "medicine": r.medicine, "medicine_id": r.medicine_id, "dosage": r.dosage, "route": r.route, "frequency": r.frequency,
           "duration_days": r.duration_days, "quantity": r.quantity, "dispensed_quantity": r.dispensed_quantity or 0, "is_prn": bool(r.is_prn), "instructions": r.instructions,
           "status": r.status or "Ordered", "prescriber": names.get(r.ordered_by_id) or r.doctor_name, "created_at": iso(r.created_at), "warnings": r.warnings or [],
           "allergy_override_reason": r.allergy_override_reason, "verified_at": iso(r.verified_at), "cancelled_reason": r.cancelled_reason}
    if p is not None:
        row.update(patient_name=p.name, patient_code=p.patient_code)
    return row


@bp.get("/prescriptions")
@require_perm("rx.read")
def list_prescriptions():
    q = select(Prescription, Patient).join(Patient, Patient.id == Prescription.patient_id)
    if request.args.get("patient_id"):
        q = q.where(Prescription.patient_id == to_int(request.args["patient_id"], "patient_id"))
    if request.args.get("status"):
        q = q.where(Prescription.status == request.args["status"])
    rows = db.session.execute(q.order_by(Prescription.created_at.desc()).limit(300)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    rows = [(r, p) for r, p in rows if "meds" in sc.get(p.id, ())]
    names = _user_names({r.ordered_by_id for r, _ in rows})
    return jsonify(ok=True, items=[_rx_row(r, p, names) for r, p in rows])


@bp.post("/prescriptions")
@require_perm("rx.prescribe")
def create_prescription():
    d = payload()
    need(d, "patient_id", "medicine")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "meds")
    med = db.session.get(Medicine, to_int(d["medicine_id"], "medicine_id")) if d.get("medicine_id") else None
    name = med.name if med else s(d, "medicine", 120)
    if med and (not med.is_active or (med.expiry_date and med.expiry_date < date.today().isoformat())):
        raise ApiError(f"{med.name} is inactive or expired in the catalogue", 409)
    warnings = osvc.medication_warnings(p, name, med.generic_name if med else "")
    blocking = [w for w in warnings if w["blocking"]]
    override = s(d, "override_reason", 300)
    if blocking and len(override) < 10:
        raise ApiError("Warnings require review. Provide an override_reason (at least 10 characters) to proceed.", 409, warnings=warnings)
    adm = monitoring.active_admission(p.id)
    r = Prescription(patient_id=p.id, doctor_name=g.user.name, medicine=name, medicine_id=med.id if med else None, dosage=s(d, "dosage", 120) or "As directed by clinician",
                     instructions=s(d, "instructions", 1000), route=s(d, "route", 30), frequency=s(d, "frequency", 60),
                     duration_days=to_int(d["duration_days"], "duration_days", 1, 365) if d.get("duration_days") else None,
                     quantity=to_int(d["quantity"], "quantity", 1, 100000) if d.get("quantity") else None, is_prn=str(d.get("is_prn", "")).lower() in ("1", "true", "yes"),
                     status="Ordered", ordered_by_id=g.user.id, allergy_override_reason=override if blocking else "", warnings=warnings,
                     admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None)
    db.session.add(r)
    audit("rx.ordered", category="clinical", entity_type="prescription", patient_id=p.id, details=f"{name}" + (" (override)" if blocking else ""))
    commit()
    return jsonify(ok=True, message="Medication ordered", id=r.id, warnings=warnings)


def _rx_or_404(rid):
    r = db.session.get(Prescription, rid)
    if not r:
        raise ApiError("Order not found", 404)
    return r


@bp.post("/prescriptions/check")
@require_perm("rx.prescribe")
def check_prescription():
    d = payload()
    need(d, "patient_id", "medicine")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "meds")
    return jsonify(ok=True, warnings=osvc.medication_warnings(p, s(d, "medicine", 120)), notice=osvc.INTERACTION_NOTICE)


@bp.post("/prescriptions/<int:rid>/verify")
@require_perm("rx.verify")
def verify_rx(rid):
    r = _rx_or_404(rid)
    p = get_authorized_patient(r.patient_id, "meds")
    if r.status != "Ordered":
        raise ApiError(f"Order is {r.status}", 409)
    med = db.session.get(Medicine, r.medicine_id) if r.medicine_id else None
    r.warnings = osvc.medication_warnings(p, r.medicine, med.generic_name if med else "", exclude_rx_id=r.id)
    r.status, r.verified_by_id, r.verified_at = "Verified", g.user.id, utcnow()
    audit("rx.verified", category="clinical", entity_type="prescription", entity_id=rid, patient_id=r.patient_id)
    commit()
    return jsonify(ok=True, message="Order verified", warnings=r.warnings)


@bp.post("/prescriptions/<int:rid>/cancel")
def cancel_rx(rid):
    r = _rx_or_404(rid)
    get_authorized_patient(r.patient_id, "meds")
    if not (has_perm(g.user, "rx.prescribe") or has_perm(g.user, "rx.verify")):
        raise ApiError("Not permitted", 403)
    if r.status not in ("Ordered", "Verified"):
        raise ApiError(f"A {r.status.lower()} order cannot be cancelled; discontinue it instead", 409)
    reason = s(payload(), "reason", 300)
    if not reason:
        raise ApiError("A reason is required")
    r.status, r.cancelled_reason = "Cancelled", reason
    audit("rx.cancelled", category="clinical", entity_type="prescription", entity_id=rid, patient_id=r.patient_id, details=reason)
    commit()
    return ok("Order cancelled")


@bp.post("/prescriptions/<int:rid>/discontinue")
@require_perm("rx.prescribe")
def discontinue_rx(rid):
    r = _rx_or_404(rid)
    get_authorized_patient(r.patient_id, "meds")
    if r.status not in ("Ordered", "Verified", "Dispensed", "Partially Dispensed"):
        raise ApiError(f"Order is {r.status}", 409)
    reason = s(payload(), "reason", 300)
    if not reason:
        raise ApiError("A reason is required")
    r.status, r.cancelled_reason = "Discontinued", reason
    audit("rx.discontinued", category="clinical", entity_type="prescription", entity_id=rid, patient_id=r.patient_id, details=reason)
    commit()
    return ok("Order discontinued")


@bp.post("/prescriptions/<int:rid>/dispense")
@require_perm("rx.dispense")
def dispense_rx(rid):
    r = _rx_or_404(rid)
    get_authorized_patient(r.patient_id, "meds")
    d = payload()
    need(d, "quantity")
    med = db.session.get(Medicine, to_int(d["medicine_id"], "medicine_id")) if d.get("medicine_id") else (db.session.get(Medicine, r.medicine_id) if r.medicine_id else None)
    if not med:
        raise ApiError("Select the catalogue medicine being dispensed (medicine_id)")
    ack = d.get("acknowledged_warnings") or []
    if not isinstance(ack, list):
        raise ApiError("acknowledged_warnings must be a list")
    osvc.dispense(r, med, to_int(d["quantity"], "quantity", 1, 100000), g.user, [str(a)[:200] for a in ack], s(d, "note", 300))
    commit()
    return ok(f"Dispensed. Stock now {med.stock}", status=r.status, stock=med.stock)


@bp.post("/prescriptions/<int:rid>/administer")
@require_perm("rx.administer")
def administer_rx(rid):
    r = _rx_or_404(rid)
    get_authorized_patient(r.patient_id, "meds")
    if r.status not in ("Verified", "Dispensed", "Partially Dispensed"):
        raise ApiError(f"Order is {r.status}; it must be pharmacist-verified or dispensed before administration", 409)
    d = payload()
    status = s(d, "status", 12) or "Given"
    if status not in ("Given", "Held", "Refused", "Missed"):
        raise ApiError("status must be Given, Held, Refused or Missed")
    ident = str(d.get("identity_verified", "")).lower() in ("1", "true", "yes")
    allergies = str(d.get("allergies_checked", "")).lower() in ("1", "true", "yes")
    if status == "Given" and not (ident and allergies):
        raise ApiError("Confirm patient identity and allergy check before recording a given dose", 409)
    if status != "Given" and not s(d, "note", 300):
        raise ApiError(f"A note is required when a dose is {status.lower()}")
    adm = monitoring.active_admission(r.patient_id)
    m = MedicationAdministration(prescription_id=r.id, patient_id=r.patient_id, admission_id=adm.id if adm else None, status=status, dose_given=s(d, "dose_given", 60) or r.dosage,
                                 identity_verified=ident, allergies_checked=allergies, administered_by_id=g.user.id, administered_at=utcnow(), note=s(d, "note", 300), scheduled_at=parse_dt(d.get("scheduled_at"), "scheduled_at"))
    db.session.add(m)
    audit("mar.recorded", category="clinical", entity_type="prescription", entity_id=rid, patient_id=r.patient_id, details=status)
    commit()
    return ok(f"Dose recorded as {status}")


@bp.get("/patients/<int:pid>/medications")
def patient_medications(pid):
    get_authorized_patient(pid, "meds")
    orders = db.session.execute(select(Prescription).where(Prescription.patient_id == pid).order_by(Prescription.created_at.desc())).scalars().all()
    names = _user_names({o.ordered_by_id for o in orders})
    disp = db.session.execute(select(DispenseEvent).join(Prescription, Prescription.id == DispenseEvent.prescription_id).where(Prescription.patient_id == pid).order_by(DispenseEvent.dispensed_at.desc())).scalars().all()
    mar = db.session.execute(select(MedicationAdministration).where(MedicationAdministration.patient_id == pid).order_by(MedicationAdministration.created_at.desc()).limit(100)).scalars().all()
    un = _user_names({x.dispensed_by_id for x in disp} | {m.administered_by_id for m in mar})
    return jsonify(ok=True, orders=[_rx_row(o, None, names) for o in orders],
                   dispensing=[{"id": x.id, "prescription_id": x.prescription_id, "quantity": x.quantity, "at": iso(x.dispensed_at), "by": un.get(x.dispensed_by_id, ""), "note": x.note} for x in disp],
                   administrations=[{"id": m.id, "prescription_id": m.prescription_id, "status": m.status, "dose_given": m.dose_given, "at": iso(m.administered_at), "by": un.get(m.administered_by_id, ""),
                                     "identity_verified": m.identity_verified, "allergies_checked": m.allergies_checked, "note": m.note} for m in mar])


@bp.get("/patients/<int:pid>/med-reconciliation")
def get_reconciliation(pid):
    p = get_authorized_patient(pid, "meds")
    active = [{"id": o.id, "medicine": o.medicine, "dosage": o.dosage, "frequency": o.frequency, "status": o.status}
              for o in db.session.execute(select(Prescription).where(Prescription.patient_id == pid, Prescription.status.in_(osvc.ACTIVE_RX))).scalars()]
    names_seen: dict[str, int] = {}
    for a in active:
        names_seen[a["medicine"].lower()] = names_seen.get(a["medicine"].lower(), 0) + 1
    dups = [n for n, c in names_seen.items() if c > 1]
    hist = db.session.execute(select(MedReconciliation).where(MedReconciliation.patient_id == pid).order_by(MedReconciliation.created_at.desc()).limit(10)).scalars().all()
    return jsonify(ok=True, active_orders=active, duplicate_active_orders=dups, allergy_text=p.allergies if "allergies" in patient_scopes(g.user, pid) else "",
                   history=[{"id": h.id, "items": h.items, "notes": h.notes, "at": iso(h.created_at)} for h in hist])


@bp.post("/patients/<int:pid>/med-reconciliation")
@require_perm("rx.verify")
def save_reconciliation(pid):
    get_authorized_patient(pid, "meds")
    d = payload()
    items = d.get("items")
    if not isinstance(items, list) or not items:
        raise ApiError("items must be a non-empty list")
    clean = []
    for it in items[:50]:
        if not isinstance(it, dict) or not str(it.get("medicine", "")).strip():
            raise ApiError("Each item needs a medicine")
        act = str(it.get("action", "Continue"))
        if act not in ("Continue", "Stop", "Modify", "Add"):
            raise ApiError("action must be Continue, Stop, Modify or Add")
        clean.append({"medicine": str(it["medicine"])[:120], "action": act, "note": str(it.get("note", ""))[:200]})
    adm = monitoring.active_admission(pid)
    db.session.add(MedReconciliation(patient_id=pid, admission_id=adm.id if adm else None, pharmacist_id=g.user.id, items=clean, notes=s(d, "notes", 1000)))
    audit("med.reconciled", category="clinical", entity_type="patient", entity_id=pid, patient_id=pid, details=f"{len(clean)} item(s)")
    commit()
    return ok("Reconciliation saved")


# =========================================================================== #
# BILLING & INSURANCE
# =========================================================================== #
def _bill_row(b: Bill, p=None, detail=False):
    f = osvc.bill_figures(b)
    row = {"id": b.id, "patient_id": b.patient_id, "description": b.description, "consultation": b.consultation or 0, "laboratory": b.laboratory or 0, "pharmacy": b.pharmacy or 0,
           "room": b.room or 0, "other_charges": b.other_charges or 0, "total": f["total"], "adjustments": f["adjustments"], "paid_amount": f["paid"], "balance": f["balance"],
           "paid": bool(b.paid), "status": b.status or "Issued", "insurance_provider": b.insurance_provider, "insurance_status": b.insurance_status, "claim_status": f["claim_status"],
           "created_at": iso(b.created_at), "admission_id": b.admission_id}
    if p is not None:
        row.update(patient_name=p.name, patient_code=p.patient_code)
    if detail:
        row["payments"] = [{"id": x.id, "kind": x.kind, "amount": x.amount, "method": x.method, "reference": x.reference, "reason": x.reason, "at": iso(x.created_at)} for x in sorted(b.payments, key=lambda x: x.id)]
        row["adjustment_items"] = [{"id": x.id, "kind": x.kind, "amount": x.amount, "reason": x.reason, "at": iso(x.created_at)} for x in sorted(b.adjustments, key=lambda x: x.id)]
        row["claims"] = [{"id": c.id, "provider": c.provider, "policy_no": c.policy_no, "claim_no": c.claim_no, "amount_claimed": c.amount_claimed, "amount_approved": c.amount_approved,
                          "status": c.status, "notes": c.notes, "submitted_at": iso(c.submitted_at)} for c in sorted(b.claims, key=lambda x: x.id)]
    return row


@bp.get("/bills")
@require_perm("billing.read")
def list_bills():
    page, per = page_args(50, 200)
    q = select(Bill, Patient).join(Patient, Patient.id == Bill.patient_id)
    if request.args.get("patient_id"):
        q = q.where(Bill.patient_id == to_int(request.args["patient_id"], "patient_id"))
    rows = db.session.execute(q.order_by(Bill.created_at.desc(), Bill.id.desc()).limit(1000)).all()
    items = [_bill_row(b, p) for b, p in rows]
    if request.args.get("status") == "unpaid":
        items = [i for i in items if i["balance"] > 0.005 and i["status"] != "Void"]
    total = len(items)
    return jsonify(ok=True, items=items[(page - 1) * per: page * per], page=page, per_page=per, total=total, outstanding=round(sum(i["balance"] for i in items if i["status"] != "Void" and i["balance"] > 0), 2))


@bp.get("/bills/<int:bid>")
@require_perm("billing.read")
def get_bill(bid):
    b = db.session.get(Bill, bid)
    if not b:
        raise ApiError("Bill not found", 404)
    p = get_authorized_patient(b.patient_id, "billing")
    audit("bill.viewed", category="access", entity_type="bill", entity_id=bid, patient_id=b.patient_id)
    db.session.commit()
    return jsonify(ok=True, **_bill_row(b, p, detail=True))


def _charges(d):
    values = {k: to_float(d.get(k, 0) or 0, k) for k in ("consultation", "laboratory", "pharmacy", "room", "other_charges")}
    if any(v < 0 for v in values.values()):
        raise ApiError("Charges cannot be negative")
    if any(v > 100_000_000 for v in values.values()):
        raise ApiError("Charge amount is unrealistically large")
    return values


@bp.post("/bills")
@require_perm("billing.write")
def create_bill():
    d = payload()
    need(d, "patient_id", "description")
    p = get_authorized_patient(to_int(d["patient_id"], "patient_id"), "billing")
    values = _charges(d)
    adm = to_int(d["admission_id"], "admission_id") if d.get("admission_id") else None
    b = Bill(patient_id=p.id, description=s(d, "description", 200), insurance_provider=s(d, "insurance_provider", 120) or p.insurance_provider, insurance_status=s(d, "insurance_status", 40) or "Not submitted",
             created_by_id=g.user.id, admission_id=adm, **values)
    db.session.add(b)
    db.session.flush()
    dsvc.ensure(p.id, "Invoice / receipt", b.description, "bill", b.id, digital=True, created_by_id=g.user.id)
    audit("bill.created", category="clinical", entity_type="bill", entity_id=b.id, patient_id=p.id, details=f"total={b.total:.2f}")
    commit()
    return jsonify(ok=True, message=f"Bill created. Total {b.total:.2f}", id=b.id, total=b.total)


@bp.post("/bills/from-admission/<int:aid>")
@require_perm("billing.write")
def bill_from_admission(aid):
    a = db.session.get(Admission, aid)
    if not a:
        raise ApiError("Admission not found", 404)
    p = get_authorized_patient(a.patient_id, "billing")
    from ..models import Ward
    ward = db.session.execute(select(Ward).where(Ward.name == a.ward)).scalar_one_or_none()
    rate = ward.daily_rate if ward else 0
    start = date.fromisoformat(a.admitted_on)
    end = date.fromisoformat(a.discharged_on) if a.discharged_on else date.today()
    days = max(1, (end - start).days + (0 if a.discharged_on else 1))
    b = Bill(patient_id=p.id, description=f"Admission charges: {a.ward} ({days} day(s) x {rate:g})", room=round(days * rate, 2), admission_id=a.id, created_by_id=g.user.id,
             insurance_provider=p.insurance_provider)
    db.session.add(b)
    db.session.flush()
    dsvc.ensure(p.id, "Invoice / receipt", b.description, "bill", b.id, digital=True, created_by_id=g.user.id)
    audit("bill.created", category="clinical", entity_type="bill", entity_id=b.id, patient_id=p.id, details=f"from admission {aid}")
    commit()
    return ok(f"Room charges calculated for {days} day(s)", id=b.id, total=b.total)


def _bill_or_404(bid):
    b = db.session.get(Bill, bid)
    if not b:
        raise ApiError("Bill not found", 404)
    if b.status == "Void":
        raise ApiError("Bill is void", 409)
    return b


@bp.patch("/bills/<int:bid>")
@require_perm("billing.write")
def update_bill(bid):
    b = _bill_or_404(bid)
    get_authorized_patient(b.patient_id, "billing")
    d = payload()
    if "paid" in d:
        if str(d["paid"]).lower() in ("true", "1", "yes", "paid"):
            bal = osvc.bill_figures(b)["balance"]
            if bal > 0.005:
                db.session.add(Payment(bill_id=b.id, amount=bal, method="Marked paid", reason="Settled via legacy toggle", received_by_id=g.user.id))
                db.session.flush()
                db.session.refresh(b)
        else:
            raise ApiError("A payment cannot be un-recorded. Use a refund, which requires administrator approval.", 409)
    if "insurance_status" in d:
        status = s(d, "insurance_status", 40)
        if status not in ("Not submitted", "Submitted", "Approved", "Rejected", "Pending"):
            raise ApiError("Invalid insurance_status")
        b.insurance_status = status
    osvc.refresh_bill_status(b)
    audit("bill.updated", category="clinical", entity_type="bill", entity_id=bid, patient_id=b.patient_id)
    commit()
    return ok("Bill updated")


@bp.post("/bills/<int:bid>/payments")
@require_perm("billing.write")
def add_payment(bid):
    b = _bill_or_404(bid)
    get_authorized_patient(b.patient_id, "billing")
    d = payload()
    need(d, "amount")
    amt = round(to_float(d["amount"], "amount", 0.01, 100_000_000), 2)
    bal = osvc.bill_figures(b)["balance"]
    if amt > bal + 0.005:
        raise ApiError(f"Payment exceeds the outstanding balance ({bal:.2f})", 409)
    db.session.add(Payment(bill_id=b.id, amount=amt, method=s(d, "method", 30) or "Cash", reference=s(d, "reference", 80), received_by_id=g.user.id))
    db.session.flush()
    db.session.refresh(b)
    osvc.refresh_bill_status(b)
    audit("payment.received", category="clinical", entity_type="bill", entity_id=bid, patient_id=b.patient_id, details=f"{amt:.2f}")
    commit()
    return ok("Payment recorded", balance=osvc.bill_figures(b)["balance"])


@bp.post("/bills/<int:bid>/refunds")
@require_perm("billing.refund")
def add_refund(bid):
    b = _bill_or_404(bid)
    get_authorized_patient(b.patient_id, "billing")
    d = payload()
    need(d, "amount", "reason")
    amt = round(to_float(d["amount"], "amount", 0.01, 100_000_000), 2)
    if amt > osvc.bill_figures(b)["paid"] + 0.005:
        raise ApiError("Refund exceeds the amount paid", 409)
    db.session.add(Payment(bill_id=b.id, kind="Refund", amount=amt, method=s(d, "method", 30) or "Cash", reason=s(d, "reason", 300), received_by_id=g.user.id, approved_by_id=g.user.id))
    db.session.flush()
    db.session.refresh(b)
    osvc.refresh_bill_status(b)
    audit("refund.issued", category="clinical", entity_type="bill", entity_id=bid, patient_id=b.patient_id, details=f"{amt:.2f}: {s(d, 'reason', 100)}")
    commit()
    return ok("Refund recorded")


@bp.post("/bills/<int:bid>/adjustments")
@require_perm("billing.adjust")
def add_adjustment(bid):
    b = _bill_or_404(bid)
    get_authorized_patient(b.patient_id, "billing")
    d = payload()
    need(d, "kind", "amount", "reason")
    kind = s(d, "kind", 20)
    if kind not in ("Discount", "Write-off", "Correction"):
        raise ApiError("kind must be Discount, Write-off or Correction")
    amt = round(to_float(d["amount"], "amount", 0.01, 100_000_000), 2)
    f = osvc.bill_figures(b)
    if amt > f["balance"] + 0.005:
        raise ApiError(f"Adjustment exceeds the outstanding balance ({f['balance']:.2f})", 409)
    limit_pct = float(current_app.config.get("BILLING_ADJUST_LIMIT_PCT", 10))
    approved_by = g.user.id if g.user.role in (C.HOSPITAL_ADMIN, C.SUPER_ADMIN) else None
    if approved_by is None and amt > b.total * limit_pct / 100:
        raise ApiError(f"Adjustments above {limit_pct:g}% of the bill total need administrator approval", 403)
    db.session.add(BillAdjustment(bill_id=b.id, kind=kind, amount=amt, reason=s(d, "reason", 300), requested_by_id=g.user.id, approved_by_id=approved_by))
    db.session.flush()
    db.session.refresh(b)
    osvc.refresh_bill_status(b)
    audit("bill.adjusted", category="clinical", entity_type="bill", entity_id=bid, patient_id=b.patient_id, details=f"{kind} {amt:.2f}: {s(d, 'reason', 100)}")
    commit()
    return ok("Adjustment recorded")


@bp.post("/bills/<int:bid>/void")
@require_perm("billing.refund")
def void_bill(bid):
    b = _bill_or_404(bid)
    get_authorized_patient(b.patient_id, "billing")
    if osvc.bill_figures(b)["paid"] > 0:
        raise ApiError("A bill with payments cannot be voided; refund first", 409)
    reason = s(payload(), "reason", 300)
    if not reason:
        raise ApiError("A reason is required")
    b.status, b.voided_at = "Void", utcnow()
    audit("bill.voided", category="clinical", entity_type="bill", entity_id=bid, patient_id=b.patient_id, details=reason)
    commit()
    return ok("Bill voided")


@bp.post("/bills/<int:bid>/claims")
@require_perm("billing.write")
def add_claim(bid):
    b = _bill_or_404(bid)
    p = get_authorized_patient(b.patient_id, "billing")
    d = payload()
    provider = s(d, "provider", 120) or b.insurance_provider or p.insurance_provider
    if not provider:
        raise ApiError("Insurance provider is required")
    claim = InsuranceClaim(bill_id=b.id, provider=provider, policy_no=s(d, "policy_no", 60) or p.insurance_policy_no, claim_no=s(d, "claim_no", 60),
                           amount_claimed=to_float(d.get("amount_claimed", b.total) or b.total, "amount_claimed", 0, 100_000_000), status="Draft", created_by_id=g.user.id, notes=s(d, "notes", 300))
    db.session.add(claim)
    db.session.flush()
    db.session.refresh(b)
    osvc.refresh_bill_status(b)
    audit("claim.created", category="clinical", entity_type="insurance_claim", entity_id=claim.id, patient_id=b.patient_id)
    commit()
    return ok("Claim drafted", id=claim.id)


@bp.patch("/claims/<int:cid>")
@require_perm("billing.write")
def update_claim(cid):
    c = db.session.get(InsuranceClaim, cid)
    if not c:
        raise ApiError("Claim not found", 404)
    b = c.bill
    get_authorized_patient(b.patient_id, "billing")
    d = payload()
    if "status" in d:
        st = s(d, "status", 20)
        if st not in C.CLAIM_STATUSES:
            raise ApiError("Invalid claim status")
        c.status = st
        if st == "Submitted" and not c.submitted_at:
            c.submitted_at = utcnow()
    if "amount_approved" in d:
        c.amount_approved = to_float(d["amount_approved"], "amount_approved", 0, 100_000_000)
    for k, mx in (("claim_no", 60), ("notes", 300)):
        if k in d:
            setattr(c, k, s(d, k, mx))
    db.session.flush()
    osvc.refresh_bill_status(b)
    audit("claim.updated", category="clinical", entity_type="insurance_claim", entity_id=cid, patient_id=b.patient_id, details=c.status)
    commit()
    return ok("Claim updated")
