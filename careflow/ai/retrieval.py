"""Scope-gated evidence retrieval for the patient-aware assistant.

Exact values (labs, vitals, medications...) come from direct database queries, never from
free-text similarity. Uploaded document text is searched with BM25 and treated as untrusted.
Identity (name, contact, identifiers) is never placed in evidence: the model only sees age and sex.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import select

from .. import constants as C
from ..access import AI_EVIDENCE_SCOPE, can_see_doc_type
from ..extensions import db
from ..models import (Admission, Alert, Allergy, ClinicalNote, DocumentPage, FollowUp, LabReport, LabResult, MedicalDocument,
                      MedicationAdministration, Observation, ObservationType, Patient, Prescription, Problem, RadiologyRecord, Bill)
from ..services import monitoring
from ..utils import age_from_dob, iso
from .safety import sanitize_untrusted

KIND_WORDS = {
    "lab": r"\blab|blood test|result|haemoglobin|hemoglobin|creatinine|glucose|hba1c|sodium|potassium|wbc|platelet|cholesterol|test",
    "radiology": r"radiolog|x-?ray|\bct\b|\bmri\b|ultrasound|scan|imaging|echo",
    "medication": r"medic|drug|prescri|tablet|dose|\brx\b|dispens|administ|insulin|antibiotic",
    "allergy": r"allerg|reaction|intoleran",
    "vitals": r"vital|blood pressure|\bbp\b|pulse|heart rate|oxygen|spo2|temperature|fever|respirat|observation|trend",
    "admission": r"admi[st]|ward|bed|discharge|stay|hospital",
    "note": r"\bnote|progress|handover|plan|assessment|summary|summari[sz]e",
    "problem": r"problem|diagnos|condition|history|disease",
    "followup": r"follow.?up|review|appointment",
    "document": r"document|report|upload|pdf|letter|scan|attached|file",
    "billing": r"bill|invoice|payment|insurance|claim|charge|cost",
}
BROAD = ("demographics", "allergy", "problem", "medication", "admission", "vitals", "lab")
STOP = set("the a an of and or to in on for with is are was were what how why when who which does did do has have had this that these those it its be been by at as from about patient please tell me show give any there their his her".split())


@dataclass
class Evidence:
    id: str
    kind: str
    title: str
    text: str
    ref: dict = field(default_factory=dict)
    as_of: str = ""
    untrusted: bool = False
    note: str = ""

    def public(self) -> dict:
        return {"id": self.id, "kind": self.kind, "title": self.title, "ref": self.ref, "as_of": self.as_of, "untrusted": self.untrusted, "note": self.note}


def classify(question: str) -> list[str]:
    kinds = [k for k, rx in KIND_WORDS.items() if re.search(rx, question or "", re.I)]
    return kinds


def tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9][a-z0-9.%/-]*", (text or "").lower()) if t not in STOP and len(t) > 1]


def bm25_rank(query: str, docs: list[str], k1=1.4, b=0.75) -> list[float]:
    q = set(tokens(query))
    toks = [tokens(d) for d in docs]
    if not q or not toks:
        return [0.0] * len(docs)
    avg = (sum(len(t) for t in toks) / len(toks)) or 1
    df = Counter(w for t in toks for w in set(t) if w in q)
    n = len(docs)
    out = []
    for t in toks:
        tf = Counter(t)
        sc = 0.0
        for w in q:
            if tf[w]:
                idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
                sc += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        out.append(sc)
    return out


class Builder:
    def __init__(self, user, patient: Patient, scopes: frozenset, question: str, max_chars: int):
        self.user, self.p, self.scopes, self.q = user, patient, scopes, question
        self.items: list[Evidence] = []
        self.limits: list[str] = []
        self.max_chars = max_chars
        self.used = 0
        self.truncated = False

    def add(self, kind, title, text, ref=None, as_of="", untrusted=False, note="") -> Evidence | None:
        if self.used + len(text) > self.max_chars:
            self.truncated = True
            return None
        ev = Evidence(f"E{len(self.items) + 1}", kind, title, text, ref or {}, as_of, untrusted, note)
        self.items.append(ev)
        self.used += len(text)
        return ev

    def allowed(self, kind) -> bool:
        need = AI_EVIDENCE_SCOPE[kind]
        if need in self.scopes:
            return True
        label = {"labs": "laboratory results", "radiology": "radiology reports", "meds": "medications", "allergies": "allergies", "observations": "vital signs",
                 "clinical": "clinical notes, problems and admissions", "documents": "documents", "billing": "billing", "identity": "demographics"}[need]
        msg = f"Your role does not have access to {label} for this patient, so they were not consulted."
        if msg not in self.limits:
            self.limits.append(msg)
        return False

    # ---- builders -----------------------------------------------------------
    def demographics(self):
        if not self.allowed("demographics"):
            return
        age = age_from_dob(self.p.dob)
        self.add("demographics", "Patient demographics", f"Age: {age if age is not None else 'not recorded'}; sex: {self.p.gender or 'not recorded'}; blood group: {self.p.blood_group or 'not recorded'}.", {"type": "patient", "id": self.p.id})

    def allergy(self):
        if not self.allowed("allergy"):
            return
        rows = db.session.execute(select(Allergy).where(Allergy.patient_id == self.p.id, Allergy.status == "Active")).scalars().all()
        if rows:
            txt = "; ".join(f"{a.substance} (reaction: {a.reaction or 'not recorded'}; severity: {a.severity})" for a in rows)
        elif self.p.allergies:
            txt = f"Legacy free-text allergy note: {self.p.allergies[:300]}"
        else:
            txt = "No allergies are recorded. This does not confirm there are none."
        self.add("allergy", "Active allergies", txt, {"type": "allergy"})

    def problem(self):
        if not self.allowed("problem"):
            return
        rows = db.session.execute(select(Problem).where(Problem.patient_id == self.p.id, Problem.status == "Active").order_by(Problem.id.desc()).limit(25)).scalars().all()
        txt = "; ".join(f"{r.description}" + (f" (since {r.onset_on})" if r.onset_on else "") for r in rows) if rows else "No active problems are recorded."
        self.add("problem", "Problem list (recorded by clinicians)", txt, {"type": "problem"})

    def medication(self):
        if not self.allowed("medication"):
            return
        rows = db.session.execute(select(Prescription).where(Prescription.patient_id == self.p.id, Prescription.status.notin_(("Cancelled",))).order_by(Prescription.id.desc()).limit(25)).scalars().all()
        if not rows:
            self.add("medication", "Medication orders", "No medication orders are recorded.", {"type": "prescription"})
            return
        given = {}
        for m in db.session.execute(select(MedicationAdministration).where(MedicationAdministration.patient_id == self.p.id, MedicationAdministration.prescription_id.in_([r.id for r in rows]))
                                    .order_by(MedicationAdministration.id)).scalars():
            given[m.prescription_id] = m
        lines = []
        for r in rows:
            m = given.get(r.id)
            adm = f"last administration record: {m.status} at {iso(m.administered_at or m.scheduled_at)}" if m else "no administration recorded"
            lines.append(f"{r.medicine} {r.dosage} {r.route} {r.frequency}".strip() + f" - order status {r.status}; dispensed qty {r.dispensed_quantity or 0}; {adm}")
        self.add("medication", "Medication orders (ordered, dispensed and administered are separate facts)", "\n".join(lines), {"type": "prescription"}, as_of=iso(rows[0].created_at))

    def admission(self):
        if not self.allowed("admission"):
            return
        a = db.session.execute(select(Admission).where(Admission.patient_id == self.p.id).order_by(Admission.id.desc())).scalars().first()
        if not a:
            self.add("admission", "Admission", "The patient has no admission on record.", {"type": "admission"})
            return
        txt = f"Status: {a.status}; ward: {a.ward}; bed: {a.bed}; admitted on {a.admitted_on}" + (f"; discharged on {a.discharged_on}" if a.discharged_on else "")
        if a.reason:
            txt += f"; reason: {a.reason[:300]}"
        if a.discharge_status and a.discharge_status != "None":
            txt += f"; discharge status: {a.discharge_status}"
        self.add("admission", "Latest admission", txt, {"type": "admission", "id": a.id}, as_of=a.admitted_on)

    def vitals(self):
        if not self.allowed("vitals"):
            return
        types = db.session.execute(select(ObservationType)).scalars().all()
        lines, latest = [], None
        for t in types:
            rows = db.session.execute(select(Observation).where(Observation.patient_id == self.p.id, Observation.type_code == t.code, Observation.validation_status.in_(("Valid", "Unverified")))
                                      .order_by(Observation.observed_at.desc()).limit(4)).scalars().all()
            if not rows:
                continue
            latest = max(latest, rows[0].observed_at) if latest else rows[0].observed_at
            lines.append(f"{t.label}: " + "; ".join(f"{r.value_num:g} {r.unit} at {iso(r.observed_at)} ({r.source})" for r in rows))
        fr = monitoring.freshness([self.p.id]).get(self.p.id, {})
        head = f"Monitoring freshness: {fr.get('state', 'none')}" + (f" (last reading {fr['age_min']} min ago)" if fr.get("age_min") is not None else "")
        sim = db.session.execute(select(Observation.id).where(Observation.patient_id == self.p.id, Observation.source == "simulated").limit(1)).first()
        note = "Some readings are SIMULATED test data, not real measurements." if sim else ""
        if sim:
            self.limits.append(note)
        self.add("vitals", "Recent vital signs (most recent first)", head + ("\n" + "\n".join(lines) if lines else "\nNo vital signs are recorded."), {"type": "observation"}, as_of=iso(latest) if latest else "", note=note)
        al = [] if self.user.role == C.PATIENT else db.session.execute(select(Alert).where(Alert.patient_id == self.p.id, Alert.status != "Resolved").order_by(Alert.id.desc()).limit(5)).scalars().all()
        if al:
            self.add("vitals", "Open monitoring alerts (require clinician review)", "\n".join(f"{x.severity}: {x.message} (status {x.status}, since {iso(x.triggered_at)})" for x in al), {"type": "alert"})

    def lab(self):
        if not self.allowed("lab"):
            return
        from ..access import has_perm
        staff = has_perm(self.user, "lab.process")
        stmt = select(LabReport).where(LabReport.patient_id == self.p.id).order_by(LabReport.id.desc()).limit(8)
        reports = db.session.execute(stmt).scalars().all()
        shown = 0
        for rep in reports:
            released = rep.status in ("Released", "Completed")
            if not released and not staff:
                continue
            res = db.session.execute(select(LabResult).where(LabResult.lab_report_id == rep.id, LabResult.status != "Superseded")).scalars().all()
            if res:
                body = "\n".join(f"{r.analyte}: {r.value_num:g} {r.unit}".rstrip() + f" [flag: {r.flag}; ref {r.ref_text or ((str(r.ref_low) + '-' + str(r.ref_high)) if r.ref_low is not None and r.ref_high is not None else 'not given')}]"
                                 if r.value_num is not None else f"{r.analyte}: {r.value_text or 'no value'} [flag: {r.flag}]" for r in res)
            else:
                body = (rep.result or "No result recorded.")[:400]
            self.add("lab", f"{rep.test_name} (status {rep.status}, sampled {rep.sample_date})", body, {"type": "lab", "id": rep.id}, as_of=iso(rep.released_at) or rep.sample_date,
                     note="" if released else "Not yet released: preliminary.")
            shown += 1
            if shown >= 6:
                break
        if not shown:
            self.add("lab", "Laboratory results", "No released laboratory results are available.", {"type": "lab"})

    def radiology(self):
        if not self.allowed("radiology"):
            return
        from ..access import has_perm
        staff = has_perm(self.user, "rad.report")
        recs = db.session.execute(select(RadiologyRecord).where(RadiologyRecord.patient_id == self.p.id).order_by(RadiologyRecord.id.desc()).limit(6)).scalars().all()
        n = 0
        for r in recs:
            final = r.order_status == "Final" or r.report_status in ("Final", "Completed")
            if not final and not staff:
                continue
            body = f"Findings: {r.findings or 'not recorded'}\nImpression: {r.impression or 'not recorded'}" + (f"\nRecommendations: {r.recommendations}" if r.recommendations else "")
            self.add("radiology", f"{r.modality} {r.study_description or ''} ({r.study_date}; report {r.order_status or r.report_status})".replace("  ", " "), body, {"type": "radiology", "id": r.id},
                     as_of=r.study_date, note="" if final else "Not finalised: preliminary report.")
            n += 1
        if not n:
            self.add("radiology", "Radiology", "No finalised radiology reports are available.", {"type": "radiology"})
        if n:
            self.limits.append("Radiology answers use the written report text only; the images themselves were not analysed.")

    def note(self):
        if not self.allowed("note"):
            return
        if self.user.role == C.PATIENT:   # clinician working notes are staff-internal; patients get the released record, not drafts of thinking
            self.limits.append("Clinicians' working notes are not part of the assistant's view for patients. Ask your care team about your plan.")
            return
        rows = db.session.execute(select(ClinicalNote).where(ClinicalNote.patient_id == self.p.id, ClinicalNote.status == "Final").order_by(ClinicalNote.id.desc()).limit(4)).scalars().all()
        for n in rows:
            self.add("note", f"{n.note_type} note by {n.author.name if n.author else 'clinician'}", n.body[:1200], {"type": "note", "id": n.id}, as_of=iso(n.created_at))

    def followup(self):
        if not self.allowed("followup"):
            return
        rows = db.session.execute(select(FollowUp).where(FollowUp.patient_id == self.p.id, FollowUp.status == "Planned").order_by(FollowUp.id.desc()).limit(5)).scalars().all()
        if rows:
            self.add("followup", "Planned follow-up", "\n".join(f"Due {r.due_on or 'date not set'}: {r.instructions[:200]}" for r in rows), {"type": "followup"})

    def billing(self):
        if not self.allowed("billing"):
            return
        rows = db.session.execute(select(Bill).where(Bill.patient_id == self.p.id, Bill.status != "Void").order_by(Bill.id.desc()).limit(5)).scalars().all()
        self.add("billing", "Recent bills", "\n".join(f"{b.description}: total {b.total:.2f}; paid: {'yes' if b.paid else 'no'}; insurance: {b.insurance_status}" for b in rows) if rows else "No bills are recorded.", {"type": "billing"})

    def documents(self, doc_ids=None):
        if not self.allowed("document"):
            return
        docs = [d for d in db.session.execute(select(MedicalDocument).where(MedicalDocument.patient_id == self.p.id, MedicalDocument.processing_status == "Processed")
                                              .order_by(MedicalDocument.id.desc()).limit(60)).scalars() if can_see_doc_type(self.user, d.doc_type)
                and (self.user.role != C.PATIENT or d.patient_visible)]
        if doc_ids:
            docs = [d for d in docs if d.id in doc_ids]
        chunks = []
        for d in docs:
            if d.extraction_status in ("Failed", "OCR unavailable", "Not applicable"):
                self.limits.append(f"Document '{d.title}' has no readable text ({d.extraction_status}); it was not used.")
                continue
            pages = db.session.execute(select(DocumentPage).where(DocumentPage.document_id == d.id).order_by(DocumentPage.page_no)).scalars().all()
            if d.extraction_quality is not None and d.extraction_quality < 0.6 and d.review_status != "Reviewed":
                self.limits.append(f"Document '{d.title}' has low extraction quality ({d.extraction_quality:.0%}) and is unreviewed; text may contain errors.")
            if d.is_image:
                self.limits.append(f"'{d.title}' is an image; only its extracted text was used, not the image itself.")
            for pg in pages:
                t = pg.corrected_text if pg.corrected_text else pg.text
                for i in range(0, len(t or ""), 900):
                    seg = t[i:i + 900].strip()
                    if seg:
                        chunks.append((d, pg, seg))
        if not chunks:
            return
        scores = bm25_rank(self.q, [c[2] for c in chunks])
        ranked = sorted(zip(scores, chunks), key=lambda x: -x[0])
        top = [c for s_, c in ranked if s_ > 0][:4] or ([c for _, c in ranked[:2]] if not doc_ids and len(chunks) <= 2 else [])
        for d, pg, seg in top:
            clean, flagged = sanitize_untrusted(seg)
            note = "UNTRUSTED document text" + (f"; {flagged} instruction-like line(s) removed" if flagged else "")
            if flagged:
                self.limits.append(f"Instruction-like text inside '{d.title}' was removed and ignored.")
            self.add("document", f"{d.doc_type}: {d.title} (page {pg.page_no}, {d.extraction_method or 'text'}, {d.review_status})", clean, {"type": "document", "id": d.id, "page": pg.page_no},
                     as_of=iso(d.uploaded_at), untrusted=True, note=note)


def gather(user, patient: Patient, scopes: frozenset, question: str, *, max_chars: int, doc_ids=None):
    b = Builder(user, patient, scopes, question, max_chars)
    kinds = classify(question)
    order = list(dict.fromkeys(["demographics", "allergy"] + (kinds or list(BROAD))))
    if doc_ids and "document" not in order:
        order.append("document")
    for k in order:
        getattr(b, {"demographics": "demographics", "allergy": "allergy", "problem": "problem", "medication": "medication", "admission": "admission", "vitals": "vitals", "lab": "lab",
                    "radiology": "radiology", "note": "note", "followup": "followup", "billing": "billing", "document": "documents"}[k])(*([doc_ids] if k == "document" else []))
    if not kinds:  # broad question: also consult uploaded documents
        b.documents(doc_ids)
    if b.truncated:
        b.limits.append("The record was larger than the assistant can read at once; older items were left out.")
    return b.items, list(dict.fromkeys(b.limits)), kinds
