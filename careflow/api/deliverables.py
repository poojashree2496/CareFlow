"""Hand-over tracking for physical copies (and digital availability) of everything a patient is given."""
from __future__ import annotations

from flask import Blueprint, g, jsonify
from sqlalchemy import select

from .. import constants as C
from ..access import get_authorized_patient, require_perm
from ..audit import audit
from ..extensions import db
from ..models import Deliverable, MedicalDocument, utcnow
from ..services import deliverables as dsvc
from ..utils import ApiError, commit, ok, payload, s, to_int

bp = Blueprint("deliverables", __name__, url_prefix="/api")


@bp.get("/patients/<int:pid>/deliverables")
@require_perm("deliverable.manage")
def list_deliverables(pid):
    get_authorized_patient(pid, "identity")
    rows = db.session.execute(select(Deliverable).where(Deliverable.patient_id == pid).order_by(Deliverable.id.desc())).scalars().all()
    return jsonify(ok=True, items=[dsvc.row(d) for d in rows], kinds=list(C.DELIVERABLE_KINDS), statuses=list(C.PHYSICAL_STATUSES))


@bp.post("/patients/<int:pid>/deliverables")
@require_perm("deliverable.manage")
def create_deliverable(pid):
    get_authorized_patient(pid, "identity")
    d = payload()
    kind = s(d, "kind", 40)
    if kind not in C.DELIVERABLE_KINDS:
        raise ApiError("kind must be one of: " + ", ".join(C.DELIVERABLE_KINDS))
    title = s(d, "title", 200)
    if len(title) < 2:
        raise ApiError("A title is required")
    doc = None
    if d.get("document_id"):
        doc = db.session.get(MedicalDocument, to_int(d["document_id"], "document_id"))
        if not doc or doc.patient_id != pid:
            raise ApiError("document_id does not belong to this patient", 400)
    row = Deliverable(patient_id=pid, kind=kind, title=title, ref_type="manual", ref_id=None, document_id=doc.id if doc else None,
                      digital_available=bool(doc), physical_status=s(d, "physical_status", 24) or "Not requested", physical_note=s(d, "physical_note", 300), created_by_id=g.user.id)
    if row.physical_status not in C.PHYSICAL_STATUSES:
        raise ApiError("physical_status must be one of: " + ", ".join(C.PHYSICAL_STATUSES))
    db.session.add(row)
    db.session.flush()
    audit("deliverable.created", category="clinical", entity_type="deliverable", entity_id=row.id, patient_id=pid, details=f"{kind}")
    commit()
    return ok("Item recorded", id=row.id)


@bp.get("/deliverables/<int:did>/print")
@require_perm("deliverable.manage")
def print_deliverable(did):
    """Printable copy with verification QR for staff to hand over (released items only)."""
    from .portal import render_copy
    from ..models import Patient
    row = db.session.get(Deliverable, did)
    if not row:
        raise ApiError("Item not found", 404)
    get_authorized_patient(row.patient_id, "identity")
    return render_copy(row, db.session.get(Patient, row.patient_id))


@bp.patch("/deliverables/<int:did>")
@require_perm("deliverable.manage")
def update_deliverable(did):
    row = db.session.get(Deliverable, did)
    if not row:
        raise ApiError("Item not found", 404)
    get_authorized_patient(row.patient_id, "identity")
    d = payload()
    st = s(d, "physical_status", 24)
    if st:
        if st not in C.PHYSICAL_STATUSES:
            raise ApiError("physical_status must be one of: " + ", ".join(C.PHYSICAL_STATUSES))
        if st == "Handed over":
            who = s(d, "received_by_name", 120)
            if len(who) < 2:
                raise ApiError("Record who received the printed copy (name of the patient or their representative)")
            row.received_by_name, row.handed_over_at, row.handed_over_by_id = who, utcnow(), g.user.id
        elif row.physical_status == "Handed over":
            raise ApiError("A handed-over item cannot be moved back; record a new item if a reprint is needed", 409)
        row.physical_status = st
    if "physical_note" in d:
        row.physical_note = s(d, "physical_note", 300)
    audit("deliverable.updated", category="clinical", entity_type="deliverable", entity_id=did, patient_id=row.patient_id, details=f"physical={row.physical_status}")
    commit()
    return ok("Item updated", item=dsvc.row(row))
