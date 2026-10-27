"""Items the hospital gives a patient (reports, scans, medicine labels, invoices...), tracked in digital and physical form."""
from __future__ import annotations

from sqlalchemy import select, update

from ..extensions import db
from ..models import Deliverable, MedicalDocument


def ensure(patient_id: int, kind: str, title: str, ref_type: str, ref_id: int, *, digital: bool = False, created_by_id=None) -> Deliverable:
    """Create the tracking row for an item once (idempotent). ``digital`` says whether a viewable digital copy exists."""
    row = db.session.execute(select(Deliverable).where(Deliverable.patient_id == patient_id, Deliverable.ref_type == ref_type,
                                                       Deliverable.ref_id == ref_id, Deliverable.kind == kind)).scalar_one_or_none()
    if row is None:
        row = Deliverable(patient_id=patient_id, kind=kind, title=title[:200], ref_type=ref_type, ref_id=ref_id, digital_available=digital, created_by_id=created_by_id)
        db.session.add(row)
        db.session.flush()
    elif digital and not row.digital_available:
        row.digital_available = True
    return row


def share_documents_with_patient(*, lab_report_id=None, radiology_id=None) -> int:
    """Make files attached to a released lab report / authorised radiology report visible in the patient's portal."""
    cond = MedicalDocument.lab_report_id == lab_report_id if lab_report_id else MedicalDocument.radiology_id == radiology_id
    res = db.session.execute(update(MedicalDocument).where(cond, MedicalDocument.patient_visible.is_(False)).values(patient_visible=True))
    return res.rowcount or 0


def row(d: Deliverable) -> dict:
    from ..utils import iso
    return {"id": d.id, "patient_id": d.patient_id, "kind": d.kind, "title": d.title, "ref_type": d.ref_type, "ref_id": d.ref_id, "document_id": d.document_id,
            "digital_available": bool(d.digital_available), "physical_status": d.physical_status, "physical_note": d.physical_note, "received_by_name": d.received_by_name,
            "handed_over_at": iso(d.handed_over_at), "handed_over_by": d.handed_over_by.name if d.handed_over_by else "", "created_at": iso(d.created_at)}
