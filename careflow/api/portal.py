"""Read-only patient portal. A patient login sees ONLY its own record, and only material that has been released to the patient:
released lab results, final radiology reports, documents staff have shared, dispensed/administered medicines, bills and hand-over status.
Clinical notes, drafts, unreleased results and monitoring alerts are staff-internal and never appear here."""
from __future__ import annotations

import io

from flask import Blueprint, current_app, g, jsonify, redirect, render_template_string, request, send_file, make_response
from sqlalchemy import select

from .. import constants as C
from ..access import require_perm
from ..audit import audit
from ..extensions import db
from ..models import (Admission, Allergy, Appointment, Bill, Deliverable, Doctor, FollowUp, LabReport, LabResult, MedicalDocument,
                      MedicationAdministration, Observation, ObservationType, Patient, Prescription, Problem, RadiologyRecord)
from ..services import deliverables as dsvc
from ..services import journey, monitoring
from ..services.orders import bill_figures
from ..utils import ApiError, age_from_dob, iso

bp = Blueprint("portal", __name__, url_prefix="/api/portal")


def _me() -> Patient:
    if g.user.role != C.PATIENT or not g.user.patient_id:
        raise ApiError("The patient portal is only available to patient accounts", 403)
    p = db.session.get(Patient, g.user.patient_id)
    if p is None:
        raise ApiError("Your account is not linked to a patient record. Please contact the hospital.", 404)
    return p


def _doc_card(d: MedicalDocument) -> dict:
    return {"id": d.id, "title": d.title, "doc_type": d.doc_type, "mime_type": d.mime_type, "size_bytes": d.size_bytes, "is_image": bool(d.is_image),
            "uploaded_at": iso(d.uploaded_at), "download_url": f"/api/portal/documents/{d.id}/download"}


@bp.get("/overview")
@require_perm("portal.view")
def overview():
    p = _me()
    pid = p.id
    docs = db.session.execute(select(MedicalDocument).where(MedicalDocument.patient_id == pid, MedicalDocument.patient_visible.is_(True))
                              .order_by(MedicalDocument.uploaded_at.desc())).scalars().all()
    by_lab, by_rad = {}, {}
    for d in docs:
        if d.lab_report_id:
            by_lab.setdefault(d.lab_report_id, []).append(_doc_card(d))
        if d.radiology_id:
            by_rad.setdefault(d.radiology_id, []).append(_doc_card(d))

    # ---- identity & stay
    patient = {"name": p.name, "patient_code": p.patient_code, "dob": p.dob, "age": age_from_dob(p.dob), "gender": p.gender, "blood_group": p.blood_group, "phone": p.phone,
               "email": p.email, "address": p.address, "emergency_contact": p.emergency_contact, "emergency_contact_phone": p.emergency_contact_phone,
               "insurance_provider": p.insurance_provider, "insurance_policy_no": p.insurance_policy_no}
    stay = journey.current_stay(pid)
    if stay:
        stay.pop("discharge_summary", None)   # only shown once discharge is complete
    past = []
    for a in db.session.execute(select(Admission).where(Admission.patient_id == pid).order_by(Admission.id.desc())).scalars():
        done = a.status != "Admitted"
        doc = db.session.get(Doctor, a.responsible_doctor_id) if a.responsible_doctor_id else None
        past.append({"id": a.id, "ward": a.ward, "bed": a.bed, "admitted_on": a.admitted_on, "discharged_on": a.discharged_on, "status": a.status, "reason": a.reason,
                     "doctor": doc.name if doc else "", "discharge_summary": a.discharge_summary if done else "", "discharge_plan": a.discharge_plan if a.discharge_status in ("Authorized", "Completed") else ""})
    team = [{"name": t["name"], "role": C.ROLE_LABELS.get(t["role"], t["role"]), "relation": t["relation"]} for t in journey.care_team(pid)]

    appts = [{"id": a.id, "date": a.appointment_date, "time": a.appointment_time, "doctor": a.doctor.name if a.doctor else "", "status": a.status, "reason": a.reason, "visit_type": a.visit_type}
             for a in db.session.execute(select(Appointment).where(Appointment.patient_id == pid).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(30)).scalars()]

    allergies = [{"substance": a.substance, "reaction": a.reaction, "severity": a.severity} for a in db.session.execute(select(Allergy).where(Allergy.patient_id == pid, Allergy.status == "Active")).scalars()]
    problems = [{"description": x.description, "status": x.status, "onset_on": x.onset_on} for x in db.session.execute(select(Problem).where(Problem.patient_id == pid, Problem.status == "Active")).scalars()]

    # ---- medicines: what was ordered vs dispensed vs actually given are different facts
    meds = []
    rx = db.session.execute(select(Prescription).where(Prescription.patient_id == pid, Prescription.status != "Cancelled").order_by(Prescription.id.desc()).limit(40)).scalars().all()
    last = {}
    for m in db.session.execute(select(MedicationAdministration).where(MedicationAdministration.patient_id == pid).order_by(MedicationAdministration.id)).scalars():
        last[m.prescription_id] = m
    for r in rx:
        m = last.get(r.id)
        meds.append({"id": r.id, "medicine": r.medicine, "dosage": r.dosage, "route": r.route, "frequency": r.frequency, "instructions": r.instructions, "status": r.status,
                     "dispensed_quantity": r.dispensed_quantity or 0, "prescribed_by": r.doctor_name, "ordered_at": iso(r.created_at),
                     "last_dose": {"status": m.status, "at": iso(m.administered_at or m.scheduled_at)} if m else None})

    # ---- vital signs (latest per type) with provenance and freshness
    types = {t.code: t for t in db.session.execute(select(ObservationType)).scalars()}
    vitals = []
    for code, t in types.items():
        o = db.session.execute(select(Observation).where(Observation.patient_id == pid, Observation.type_code == code, Observation.validation_status.in_(("Valid", "Unverified")))
                               .order_by(Observation.observed_at.desc()).limit(1)).scalar_one_or_none()
        if o:
            vitals.append({"label": t.label, "value": o.value_num, "unit": o.unit, "observed_at": iso(o.observed_at), "source": o.source})
    fresh = monitoring.freshness([pid]).get(pid)

    # ---- results released to the patient
    labs = []
    for l in db.session.execute(select(LabReport).where(LabReport.patient_id == pid, LabReport.status.in_(("Released", "Completed"))).order_by(LabReport.id.desc()).limit(40)).scalars():
        res = db.session.execute(select(LabResult).where(LabResult.lab_report_id == l.id, LabResult.status != "Superseded")).scalars().all()
        labs.append({"id": l.id, "test_name": l.test_name, "sample_date": l.sample_date, "released_at": iso(l.released_at), "summary": (l.result or "")[:600],
                     "results": [{"analyte": r.analyte, "value": r.value_num if r.value_num is not None else r.value_text, "unit": r.unit, "reference": r.ref_text or
                                  (f"{r.ref_low:g}-{r.ref_high:g}" if r.ref_low is not None and r.ref_high is not None else ""), "flag": r.flag} for r in res],
                     "files": by_lab.get(l.id, [])})
    radiology = []
    for r in db.session.execute(select(RadiologyRecord).where(RadiologyRecord.patient_id == pid).order_by(RadiologyRecord.id.desc()).limit(30)).scalars():
        if not (r.order_status == "Final" or (r.order_status is None and r.report_status == "Final")):
            continue
        radiology.append({"id": r.id, "modality": r.modality, "description": r.study_description, "study_date": r.study_date, "reported_at": iso(r.authorized_at or r.reported_at),
                          "findings": r.findings, "impression": r.impression, "recommendations": r.recommendations, "files": by_rad.get(r.id, [])})

    bills = []
    for b in db.session.execute(select(Bill).where(Bill.patient_id == pid, Bill.status != "Void").order_by(Bill.id.desc()).limit(30)).scalars():
        f = bill_figures(b)
        bills.append({"id": b.id, "description": b.description, "created_at": iso(b.created_at), "total": b.total, "paid": f["paid"], "adjustments": f["adjustments"], "balance": f["balance"],
                      "insurance_status": b.insurance_status, "insurance_provider": b.insurance_provider, "claim_approved": f["claim_approved"],
                      "payments": [{"kind": x.kind, "amount": x.amount, "method": x.method, "at": iso(x.created_at)} for x in sorted(b.payments, key=lambda y: y.id)]})

    follow = [{"due_on": f.due_on, "instructions": f.instructions} for f in db.session.execute(select(FollowUp).where(FollowUp.patient_id == pid, FollowUp.status == "Planned")).scalars()]
    items = [dsvc.row(d) for d in db.session.execute(select(Deliverable).where(Deliverable.patient_id == pid).order_by(Deliverable.id.desc())).scalars()]
    for it in items:   # patient never sees internal ids of staff
        it.pop("handed_over_by", None)
        it["document"] = next((x for x in docs if x.id == it["document_id"]), None)
        it["document"] = _doc_card(it["document"]) if it["document"] else None
        it["copy_url"] = f"/api/portal/deliverables/{it['id']}/copy"

    audit("portal.viewed", category="access", patient_id=pid, entity_type="patient", entity_id=pid)
    db.session.commit()
    return jsonify(ok=True, patient=patient, stay=stay, admissions=past, care_team=team, appointments=appts, allergies=allergies, problems=problems, medications=meds,
                   vitals={"items": vitals, "freshness": fresh, "contains_simulated": any(v["source"] == "simulated" for v in vitals)}, labs=labs, radiology=radiology,
                   documents=[_doc_card(d) for d in docs], bills=bills, follow_ups=follow, deliverables=items, read_only=True,
                   notice="This is a read-only view of your record. For changes or questions, please speak to your care team. Use the assistant for help understanding it.")


@bp.get("/documents/<int:did>/download")
@require_perm("portal.view")
def download(did):
    p = _me()
    d = db.session.get(MedicalDocument, did)
    # identical answer for "missing", "someone else's" and "not shared" so identifiers cannot be probed
    if d is None or d.patient_id != p.id or not d.patient_visible:
        raise ApiError("Document not found", 404)
    from ..services import documents as docsvc
    audit("portal.document_downloaded", category="access", entity_type="medical_document", entity_id=did, patient_id=p.id)
    db.session.commit()
    storage = docsvc.get_storage(d.storage_backend)
    data = storage.get(d.storage_key)
    inline = request.args.get("inline") == "1" and d.mime_type in ("image/png", "image/jpeg", "application/pdf")
    resp = send_file(io.BytesIO(data), mimetype=d.mime_type, as_attachment=not inline, download_name=d.original_filename or f"document-{d.id}")
    resp.headers["Content-Security-Policy"] = "sandbox; default-src 'none'; img-src 'self' data:"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


_COPY_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title><style>
body{font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif;max-width:760px;margin:1rem auto;padding:0 1rem;color:#111}
h1{font-size:1.3rem;margin:.2rem 0}h2{font-size:1.05rem;margin:1.2rem 0 .3rem}table{border-collapse:collapse;width:100%}
th,td{border-bottom:1px solid #ccc;padding:.35rem .4rem;text-align:left;vertical-align:top}.meta{color:#555;font-size:.9rem}
pre{white-space:pre-wrap;font:inherit;margin:.2rem 0}button{font:inherit;padding:.4rem .9rem;margin:.5rem 0}
@media print{button{display:none}}</style></head><body>
<button onclick="window.print()">Print / save as PDF</button>
<h1>{{ title }}</h1><div class="meta">{{ patient.name }} · {{ patient.patient_code }} · {{ note }}</div>
{% for h, body in sections %}<h2>{{ h }}</h2>{% if body is string %}<pre>{{ body }}</pre>{% else %}
<table><tr>{% for c in body[0] %}<th>{{ c }}</th>{% endfor %}</tr>{% for row in body[1:] %}<tr>{% for c in row %}<td>{{ c }}</td>{% endfor %}</tr>{% endfor %}</table>{% endif %}{% endfor %}
<p class="meta">Copy generated by CareFlow for the patient. Demonstration data is not for clinical use.</p></body></html>"""


def _fmt_num(v):
    return "" if v is None else (f"{v:g}" if isinstance(v, (int, float)) else str(v))


@bp.get("/deliverables/<int:did>/copy")
@require_perm("portal.view")
def deliverable_copy(did):
    """Download (attached file) or printable copy (generated page) of one hand-over item. Released items only."""
    p = _me()
    d = db.session.get(Deliverable, did)
    if d is None or d.patient_id != p.id:
        raise ApiError("Item not found", 404)
    doc = db.session.get(MedicalDocument, d.document_id) if d.document_id else None
    if doc is not None and doc.patient_visible and doc.patient_id == p.id:
        return redirect(f"/api/portal/documents/{doc.id}/download", code=302)
    sections, note, title = [], "", d.title
    if d.ref_type == "lab":
        l = db.session.get(LabReport, d.ref_id)
        if not l or l.patient_id != p.id or l.status not in ("Released", "Completed"):
            raise ApiError("This report has not been released yet", 404)
        rows = db.session.execute(select(LabResult).where(LabResult.lab_report_id == l.id, LabResult.status != "Superseded")).scalars().all()
        note = f"Laboratory report · sample {l.sample_date or ''}"
        if rows:
            sections.append(("Results", [["Test", "Result", "Reference", "Flag"]] + [[r.analyte, f"{_fmt_num(r.value_num if r.value_num is not None else r.value_text)} {r.unit or ''}".strip(),
                            r.ref_text or (f"{r.ref_low:g}-{r.ref_high:g}" if r.ref_low is not None and r.ref_high is not None else ""), r.flag or ""] for r in rows]))
        if l.result:
            sections.append(("Report", l.result))
    elif d.ref_type == "radiology":
        r = db.session.get(RadiologyRecord, d.ref_id)
        if not r or r.patient_id != p.id or not (r.order_status == "Final" or (r.order_status is None and r.report_status == "Final")):
            raise ApiError("This report has not been released yet", 404)
        note = f"Imaging report · {r.modality or ''} · {r.study_date or ''}"
        for h, v in (("Findings", r.findings), ("Impression", r.impression), ("Recommendations", r.recommendations)):
            if v:
                sections.append((h, v))
    elif d.ref_type == "bill":
        b = db.session.get(Bill, d.ref_id)
        if not b or b.patient_id != p.id or b.status == "Void":
            raise ApiError("Bill not found", 404)
        f = bill_figures(b)
        note = "Invoice / receipt"
        sections.append((b.description or f"Bill #{b.id}", [["Item", "Amount"], ["Total", f"{b.total:.2f}"], ["Paid", f"{f['paid']:.2f}"], ["Balance", f"{f['balance']:.2f}"],
                                                           ["Insurance", f"{b.insurance_provider or '-'} · {b.insurance_status or '-'}"]]))
    else:
        raise ApiError("No downloadable copy is available for this item yet. Ask the front desk.", 404)
    audit("portal.copy_viewed", category="access", entity_type="deliverable", entity_id=did, patient_id=p.id)
    db.session.commit()
    resp = make_response(render_template_string(_COPY_PAGE, title=title, patient=p, note=note, sections=sections))
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'"
    resp.headers["Cache-Control"] = "private, no-store"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp
