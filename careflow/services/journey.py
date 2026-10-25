"""Longitudinal patient journey: snapshot + chronological timeline, scope-filtered."""
from __future__ import annotations

from sqlalchemy import select

from ..access import can_see_doc_type
from ..extensions import db
from ..models import (Admission, Alert, Allergy, Appointment, AppUser, Bed, BedAssignment, Bill, ClinicalNote, CriticalAck,
                      Doctor, DispenseEvent, Encounter, FollowUp, LabReport, MedicalDocument, MedicationAdministration,
                      Observation, PatientAssignment, Prescription, Problem, RadiologyRecord, CareTask, Ward)
from ..utils import iso
from . import monitoring
from .orders import ACTIVE_RX, bill_figures

LAB_VISIBLE_TO_CLINICIAN = ("Released",)


def _names(ids):
    ids = {i for i in ids if i}
    if not ids:
        return {}
    return {u.id: u.name for u in db.session.execute(select(AppUser).where(AppUser.id.in_(ids))).scalars()}


def current_stay(patient_id: int):
    adm = db.session.execute(select(Admission).where(Admission.patient_id == patient_id, Admission.status == "Admitted")).scalar_one_or_none()
    if not adm:
        return None
    ba = db.session.execute(select(BedAssignment).where(BedAssignment.admission_id == adm.id, BedAssignment.ended_at.is_(None))).scalar_one_or_none()
    bed = db.session.get(Bed, ba.bed_id) if ba else None
    doc = db.session.get(Doctor, adm.responsible_doctor_id) if adm.responsible_doctor_id else None
    return {
        "admission_id": adm.id, "admitted_at": iso(adm.admitted_at), "admitted_on": adm.admitted_on, "reason": adm.reason,
        "expected_discharge_on": adm.expected_discharge_on, "discharge_status": adm.discharge_status,
        "discharge_plan": adm.discharge_plan, "discharge_summary": adm.discharge_summary,
        "ward": bed.ward.name if bed else adm.ward, "ward_id": bed.ward_id if bed else None,
        "bed": {"id": bed.id, "code": bed.code, "label": bed.label, "room": bed.room.label} if bed else None,
        "responsible_doctor": {"id": doc.id, "name": doc.name, "specialty": doc.specialty} if doc else None,
    }


def care_team(patient_id: int):
    rows = db.session.execute(select(PatientAssignment).where(PatientAssignment.patient_id == patient_id, PatientAssignment.active.is_(True))).scalars().all()
    return [{"assignment_id": a.id, "user_id": a.user_id, "name": a.user.name, "role": a.user.role, "relation": a.relation} for a in rows]


def build_snapshot(patient, scopes, user) -> dict:
    pid = patient.id
    out: dict = {"stay": None, "team": [], "allergies": [], "problems": [], "medications": [], "vitals": None,
                 "alerts": [], "tasks": [], "pending_results": [], "critical_pending": [], "freshness": None}
    if "clinical" in scopes or "identity" in scopes:
        out["stay"] = current_stay(pid)
    if "clinical" in scopes:
        out["team"] = care_team(pid)
        out["problems"] = [{"id": p.id, "description": p.description, "code": p.code, "status": p.status, "onset_on": p.onset_on}
                           for p in db.session.execute(select(Problem).where(Problem.patient_id == pid, Problem.status == "Active").order_by(Problem.created_at.desc())).scalars()]
        tasks = db.session.execute(select(CareTask).where(CareTask.patient_id == pid, CareTask.status == "Pending").order_by(CareTask.due_at)).scalars().all()
        from ..models import utcnow
        now = utcnow()
        out["tasks"] = [{"id": t.id, "title": t.title, "category": t.category, "priority": t.priority, "due_at": iso(t.due_at),
                         "overdue": bool(t.due_at and t.due_at < now), "assigned_role": t.assigned_role} for t in tasks]
    if "allergies" in scopes:
        out["allergies"] = [{"id": a.id, "substance": a.substance, "reaction": a.reaction, "severity": a.severity}
                            for a in db.session.execute(select(Allergy).where(Allergy.patient_id == pid, Allergy.status == "Active")).scalars()]
        out["allergies_text"] = patient.allergies
    if "meds" in scopes:
        out["medications"] = [{"id": r.id, "medicine": r.medicine, "dosage": r.dosage, "route": r.route, "frequency": r.frequency, "status": r.status,
                               "is_prn": bool(r.is_prn)} for r in db.session.execute(select(Prescription).where(Prescription.patient_id == pid, Prescription.status.in_(ACTIVE_RX)).order_by(Prescription.created_at.desc())).scalars()]
    if "observations" in scopes:
        out["vitals"] = latest_vitals(pid)
        out["freshness"] = monitoring.freshness([pid]).get(pid)
        out["alerts"] = [alert_row(a) for a in db.session.execute(select(Alert).where(Alert.patient_id == pid, Alert.status != "Resolved").order_by(Alert.triggered_at.desc())).scalars()]
    pend = []
    if "labs" in scopes:
        for l in db.session.execute(select(LabReport).where(LabReport.patient_id == pid, LabReport.status.notin_(("Released", "Cancelled", "Rejected", "Completed")))).scalars():
            pend.append({"kind": "lab", "id": l.id, "title": l.test_name, "status": l.status if l.status != "Pending" else "Ordered", "priority": l.priority})
    if "radiology" in scopes:
        for r in db.session.execute(select(RadiologyRecord).where(RadiologyRecord.patient_id == pid, RadiologyRecord.order_status.notin_(("Final", "Cancelled")))).scalars():
            pend.append({"kind": "radiology", "id": r.id, "title": f"{r.modality} {r.study_description}".strip(), "status": r.order_status, "priority": r.priority})
    out["pending_results"] = pend
    if "labs" in scopes or "radiology" in scopes:
        out["critical_pending"] = [{"id": c.id, "source_type": c.source_type, "source_id": c.source_id, "summary": c.summary, "status": c.status, "created_at": iso(c.created_at)}
                                   for c in db.session.execute(select(CriticalAck).where(CriticalAck.patient_id == pid, CriticalAck.status != "Acknowledged")).scalars()]
    return out


def alert_row(a: Alert) -> dict:
    return {"id": a.id, "patient_id": a.patient_id, "severity": a.severity, "status": a.status, "message": a.message, "triggered_at": iso(a.triggered_at),
            "last_triggered_at": iso(a.last_triggered_at), "occurrences": a.occurrences, "rule": a.rule.name if a.rule else "", "rule_version": a.rule_version,
            "rule_review_status": (a.rule_snapshot or {}).get("review_status", "Unreviewed"), "simulated": a.from_simulated_data,
            "ack_at": iso(a.ack_at), "escalated_at": iso(a.escalated_at), "resolved_at": iso(a.resolved_at), "resolution_note": a.resolution_note,
            "responder_role": a.responder_role}


def latest_vitals(pid: int) -> dict:
    from ..models import ObservationType
    out = {}
    for t in db.session.execute(select(ObservationType).where(ObservationType.is_active.is_(True))).scalars():
        o = db.session.execute(select(Observation).where(Observation.patient_id == pid, Observation.type_code == t.code,
                                                         Observation.validation_status.notin_(("Entered in error", "Corrected")))
                               .order_by(Observation.observed_at.desc()).limit(1)).scalar_one_or_none()
        if o:
            out[t.code] = {"label": t.label, "value": o.value_num, "unit": o.unit, "observed_at": iso(o.observed_at), "source": o.source, "id": o.id,
                           "validation_status": o.validation_status}
    return out


def build_timeline(patient, scopes, user, limit: int = 150) -> list[dict]:
    pid = patient.id
    ev: list[dict] = []
    uids: set = set()

    def add(at, kind, title, detail="", status="", source="", by=None, link=None):
        if at is None:
            return
        if by:
            uids.add(by)
        ev.append({"at": iso(at), "kind": kind, "title": title, "detail": detail, "status": status, "source": source, "by": by, "link": link})

    if "clinical" in scopes:
        for a in db.session.execute(select(Appointment).where(Appointment.patient_id == pid)).scalars():
            from datetime import datetime, timezone
            try:
                at = datetime.fromisoformat(f"{a.appointment_date}T{a.appointment_time}:00").replace(tzinfo=timezone.utc)
            except ValueError:
                at = None
            doc = a.doctor.name if a.doctor else ""
            add(at, "appointment", f"Appointment with {doc}", a.reason, a.status, "scheduling", a.created_by_id)
        for e in db.session.execute(select(Encounter).where(Encounter.patient_id == pid)).scalars():
            add(e.started_at, "encounter", f"{e.encounter_type} encounter opened", e.chief_complaint, e.status, "clinical", e.created_by_id)
            if e.ended_at:
                add(e.ended_at, "encounter", f"{e.encounter_type} encounter closed", "", "Closed", "clinical")
        for ad in db.session.execute(select(Admission).where(Admission.patient_id == pid)).scalars():
            add(ad.admitted_at, "admission", "Admitted", ad.reason or ad.notes, ad.status, "bedboard", ad.created_by_id, {"view": "admission", "id": ad.id})
            if ad.discharge_authorized_at:
                add(ad.discharge_authorized_at, "discharge", "Discharge authorized", "", "Authorized", "clinical", ad.discharge_authorized_by_id)
            if ad.discharged_at:
                add(ad.discharged_at, "discharge", "Discharged", "", "Discharged", "bedboard")
            for ba in db.session.execute(select(BedAssignment).where(BedAssignment.admission_id == ad.id)).scalars():
                bed = db.session.get(Bed, ba.bed_id)
                add(ba.started_at, "bed", f"{ba.reason}: bed {bed.code}", ba.note, "", "bedboard", ba.moved_by_id)
        for n in db.session.execute(select(ClinicalNote).where(ClinicalNote.patient_id == pid)).scalars():
            amend = " (amendment)" if n.amends_note_id else ""
            add(n.created_at, "note", f"{n.note_type} note{amend}", (n.body or "")[:220], n.status, "clinical", n.author_id, {"view": "note", "id": n.id})
        for f in db.session.execute(select(FollowUp).where(FollowUp.patient_id == pid)).scalars():
            add(f.created_at, "followup", f"Follow-up planned for {f.due_on or 'TBD'}", f.instructions[:200], f.status, "clinical", f.created_by_id)
        for t in db.session.execute(select(CareTask).where(CareTask.patient_id == pid, CareTask.status == "Done")).scalars():
            add(t.completed_at, "task", f"Task completed: {t.title}", "", "Done", "nursing", t.completed_by_id)
    if "observations" in scopes:
        seen = set()
        rows = db.session.execute(select(Observation).where(Observation.patient_id == pid, Observation.validation_status != "Entered in error")
                                  .order_by(Observation.observed_at.desc()).limit(120)).scalars().all()
        for o in rows:
            key = o.group_id or f"o{o.id}"
            if key in seen:
                continue
            seen.add(key)
            grp = [x for x in rows if (x.group_id or f"o{x.id}") == key]
            txt = ", ".join(f"{x.type_code.replace('_', ' ')} {x.value_num:g}{x.unit}" for x in grp)
            add(o.observed_at, "vitals", "Observations recorded", txt, o.validation_status, o.source, o.recorded_by_id, {"view": "vitals"})
        for a in db.session.execute(select(Alert).where(Alert.patient_id == pid)).scalars():
            add(a.triggered_at, "alert", f"{a.severity} alert: {a.rule.name if a.rule else ''}", a.message, a.status, "simulated" if a.from_simulated_data else "monitoring", None, {"view": "alert", "id": a.id})
            if a.resolved_at:
                add(a.resolved_at, "alert", "Alert resolved", a.resolution_note, "Resolved", "monitoring", a.resolved_by_id)
    if "labs" in scopes:
        for l in db.session.execute(select(LabReport).where(LabReport.patient_id == pid)).scalars():
            add(l.ordered_at or l.released_at, "lab", f"Lab ordered: {l.test_name}", f"Priority {l.priority or 'Routine'}", l.status, "laboratory", l.ordered_by_id, {"view": "lab", "id": l.id})
            if l.released_at:
                add(l.released_at, "lab", f"Lab result released: {l.test_name}", "", "Released", "laboratory", l.released_by_id, {"view": "lab", "id": l.id})
    if "radiology" in scopes:
        for r in db.session.execute(select(RadiologyRecord).where(RadiologyRecord.patient_id == pid)).scalars():
            add(r.ordered_at, "radiology", f"Imaging ordered: {r.modality}", r.indication, r.order_status, "radiology", r.ordered_by_id, {"view": "radiology", "id": r.id})
            if r.authorized_at:
                add(r.authorized_at, "radiology", f"Imaging report authorized: {r.modality}", "", "Final", "radiology", r.authorized_by_id, {"view": "radiology", "id": r.id})
    if "meds" in scopes:
        for p in db.session.execute(select(Prescription).where(Prescription.patient_id == pid)).scalars():
            add(p.created_at, "medication", f"Ordered: {p.medicine}", f"{p.dosage} {p.frequency}".strip(), p.status, "pharmacy", p.ordered_by_id, {"view": "medication", "id": p.id})
        for d in db.session.execute(select(DispenseEvent).join(Prescription, Prescription.id == DispenseEvent.prescription_id).where(Prescription.patient_id == pid)).scalars():
            rx = db.session.get(Prescription, d.prescription_id)
            add(d.dispensed_at, "dispense", f"Dispensed: {rx.medicine} x{d.quantity}", "", "Dispensed", "pharmacy", d.dispensed_by_id)
        for m in db.session.execute(select(MedicationAdministration).where(MedicationAdministration.patient_id == pid, MedicationAdministration.status != "Scheduled")).scalars():
            rx = db.session.get(Prescription, m.prescription_id)
            add(m.administered_at or m.created_at, "administration", f"{m.status}: {rx.medicine}", m.dose_given, m.status, "nursing", m.administered_by_id)
    if "documents" in scopes:
        for d in db.session.execute(select(MedicalDocument).where(MedicalDocument.patient_id == pid)).scalars():
            if can_see_doc_type(user, d.doc_type):
                add(d.uploaded_at, "document", f"Document uploaded: {d.title}", d.doc_type, d.review_status, "documents", d.uploaded_by_id, {"view": "document", "id": d.id})
    if "billing" in scopes:
        for b in db.session.execute(select(Bill).where(Bill.patient_id == pid)).scalars():
            f = bill_figures(b)
            add(b.created_at, "billing", f"Invoice #{b.id}: {b.description}", f"Total {f['total']:.2f}, balance {f['balance']:.2f}", "Paid" if b.paid else "Open", "billing", b.created_by_id, {"view": "bill", "id": b.id})
    names = _names(uids)
    for e in ev:
        by = e.pop("by")
        e["by_name"] = names.get(by, "") if by else ""
    ev.sort(key=lambda e: e["at"], reverse=True)
    return ev[:limit]
