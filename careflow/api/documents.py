"""Document upload, extraction review and authorised download."""
from __future__ import annotations

import io

from flask import Blueprint, current_app, g, jsonify, redirect, request, send_file
from sqlalchemy import select

from .. import constants as C
from ..access import can_see_doc_type, get_authorized_patient, require_perm
from ..audit import audit
from ..extensions import db
from ..models import DocumentPage, LabReport, MedicalDocument, RadiologyRecord, utcnow
from ..services import documents as docsvc
from ..services import monitoring
from ..utils import ApiError, commit, iso, ok, payload, s, to_int

bp = Blueprint("documents", __name__, url_prefix="/api")


def _doc_row(d: MedicalDocument, detail=False):
    row = {"id": d.id, "patient_id": d.patient_id, "doc_type": d.doc_type, "title": d.title, "original_filename": d.original_filename, "mime_type": d.mime_type,
           "size_bytes": d.size_bytes, "uploaded_at": iso(d.uploaded_at), "uploaded_by": d.uploaded_by.name if d.uploaded_by else "", "processing_status": d.processing_status,
           "extraction_status": d.extraction_status, "extraction_method": d.extraction_method, "extraction_quality": d.extraction_quality, "extraction_note": d.extraction_note,
           "page_count": d.page_count, "review_status": d.review_status, "version": d.version, "is_image": d.is_image, "lab_report_id": d.lab_report_id,
           "radiology_id": d.radiology_id, "patient_visible": bool(d.patient_visible), "supersedes_id": d.supersedes_id, "reprocess_count": d.reprocess_count, "sha256": d.sha256[:12]}
    return row


def _doc_for(did: int, *scopes) -> MedicalDocument:
    d = db.session.get(MedicalDocument, did)
    # identical response for "missing" and "not allowed" so identifiers cannot be probed
    if d is None:
        raise ApiError("Document not found", 404)
    try:
        get_authorized_patient(d.patient_id, "documents")
    except ApiError:
        raise ApiError("Document not found", 404)
    if not can_see_doc_type(g.user, d.doc_type):
        raise ApiError("Document not found", 404)
    return d


def process_document(d: MedicalDocument, data: bytes):
    ex = docsvc.extract(data, d.mime_type)
    # Reviewer corrections (corrected_text) live in their own column and survive reprocessing.
    existing = {p.page_no: p for p in d.pages}
    for pr in ex.pages:
        row = existing.get(pr.page_no) or DocumentPage(document_id=d.id, page_no=pr.page_no)
        row.text, row.method, row.confidence, row.char_count = pr.text, pr.method, pr.confidence, len(pr.text)
        db.session.add(row)
    d.page_count = len(ex.pages)
    d.extraction_status, d.extraction_method, d.extraction_quality, d.extraction_note = ex.status, ex.method, ex.quality, ex.note
    d.processing_status = "Processed"
    d.review_status = "Unreviewed"


@bp.post("/patients/<int:pid>/documents")
@require_perm("doc.upload")
def upload_document(pid):
    get_authorized_patient(pid, "documents")
    f = request.files.get("file")
    if f is None or not f.filename:
        raise ApiError("Choose a file to upload")
    doc_type = (request.form.get("doc_type") or "Other").strip()
    if doc_type not in C.DOC_TYPES:
        raise ApiError("doc_type must be one of: " + ", ".join(C.DOC_TYPES))
    if not can_see_doc_type(g.user, doc_type):
        raise ApiError(f"Your role may only upload documents of type: {', '.join(sorted(__import__('careflow.access', fromlist=['x']).DOC_TYPES_BY_ROLE[g.user.role]))}", 403)
    data = f.read(current_app.config["MAX_CONTENT_LENGTH"] + 1)
    if len(data) > current_app.config["MAX_CONTENT_LENGTH"]:
        raise ApiError("File is larger than the permitted size", 413)
    mime, ext = docsvc.sniff_and_validate(data, f.filename)
    title = (request.form.get("title") or "").strip()[:200] or docsvc.safe_display_name(f.filename)
    lab_id = to_int(request.form["lab_report_id"], "lab_report_id") if request.form.get("lab_report_id") else None
    rad_id = to_int(request.form["radiology_id"], "radiology_id") if request.form.get("radiology_id") else None
    if lab_id and not db.session.execute(select(LabReport.id).where(LabReport.id == lab_id, LabReport.patient_id == pid)).first():
        raise ApiError("lab_report_id does not belong to this patient", 400)
    if rad_id and not db.session.execute(select(RadiologyRecord.id).where(RadiologyRecord.id == rad_id, RadiologyRecord.patient_id == pid)).first():
        raise ApiError("radiology_id does not belong to this patient", 400)
    sup = None
    if request.form.get("supersedes_id"):
        sup = _doc_for(to_int(request.form["supersedes_id"], "supersedes_id"))
        if sup.patient_id != pid:
            raise ApiError("supersedes_id belongs to another patient", 400)
    storage = docsvc.get_storage()
    key = docsvc.new_storage_key(pid, ext)
    storage.put(key, data, mime)
    adm = monitoring.active_admission(pid)
    d = MedicalDocument(patient_id=pid, admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None, doc_type=doc_type, title=title,
                        original_filename=docsvc.safe_display_name(f.filename), mime_type=mime, size_bytes=len(data), sha256=docsvc.sha256(data), storage_backend=storage.name,
                        storage_key=key, uploaded_by_id=g.user.id, lab_report_id=lab_id, radiology_id=rad_id, is_image=mime.startswith("image/"),
                        version=(sup.version + 1) if sup else 1, supersedes_id=sup.id if sup else None,
                        patient_visible=str(request.form.get("patient_visible", "")).lower() in ("1", "true", "yes"))
    db.session.add(d)
    db.session.flush()
    try:
        process_document(d, data)
    except Exception as exc:
        current_app.logger.exception("Document extraction failed for document %s", d.id)
        d.processing_status, d.extraction_status, d.extraction_note = "Failed", "Failed", f"Extraction error: {exc.__class__.__name__}"
    audit("document.uploaded", category="clinical", entity_type="medical_document", entity_id=d.id, patient_id=pid, details=f"{doc_type} {mime} {len(data)}B")
    commit()
    return jsonify(ok=True, message="Document stored privately and processed", document=_doc_row(d))


@bp.get("/patients/<int:pid>/documents")
def list_documents(pid):
    get_authorized_patient(pid, "documents")
    rows = db.session.execute(select(MedicalDocument).where(MedicalDocument.patient_id == pid).order_by(MedicalDocument.uploaded_at.desc())).scalars().all()
    return jsonify(ok=True, items=[_doc_row(d) for d in rows if can_see_doc_type(g.user, d.doc_type)])


@bp.get("/documents/<int:did>")
def get_document(did):
    d = _doc_for(did)
    out = _doc_row(d)
    if request.args.get("text") == "1":
        out["pages"] = [{"page_no": p.page_no, "method": p.method, "confidence": p.confidence, "text": p.text, "corrected_text": p.corrected_text, "char_count": p.char_count}
                        for p in sorted(d.pages, key=lambda x: x.page_no)]
        audit("document.text_viewed", category="access", entity_type="medical_document", entity_id=did, patient_id=d.patient_id)
        db.session.commit()
    return jsonify(ok=True, **out)


@bp.get("/documents/<int:did>/download")
@require_perm("doc.read")
def download_document(did):
    d = _doc_for(did)
    audit("document.downloaded", category="access", entity_type="medical_document", entity_id=did, patient_id=d.patient_id)
    db.session.commit()
    storage = docsvc.get_storage(d.storage_backend)
    inline = request.args.get("inline") == "1" and d.mime_type in ("image/png", "image/jpeg")
    url = storage.signed_url(d.storage_key, current_app.config["SIGNED_URL_SECONDS"])
    if url:  # short-lived signed URL from private object storage
        return redirect(url, code=302)
    data = storage.get(d.storage_key)
    resp = send_file(io.BytesIO(data), mimetype=d.mime_type, as_attachment=not inline, download_name=d.original_filename or f"document-{d.id}")
    resp.headers["Content-Security-Policy"] = "sandbox; default-src 'none'"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp


@bp.post("/documents/<int:did>/visibility")
@require_perm("doc.upload")
def set_visibility(did):
    """Share a file with the patient's own portal (or withdraw it). Lab/radiology files are shared automatically when the report is released."""
    d = _doc_for(did)
    want = str(payload().get("patient_visible", "")).lower() in ("1", "true", "yes")
    d.patient_visible = want
    audit("document.shared_with_patient" if want else "document.unshared_from_patient", category="clinical", entity_type="medical_document", entity_id=did, patient_id=d.patient_id)
    commit()
    return ok("Shared with the patient" if want else "No longer shared with the patient", patient_visible=want)


@bp.post("/documents/<int:did>/reprocess")
@require_perm("doc.review")
def reprocess_document(did):
    d = _doc_for(did)
    data = docsvc.get_storage(d.storage_backend).get(d.storage_key)  # original is never modified
    try:
        process_document(d, data)
    except Exception as exc:
        d.processing_status, d.extraction_status, d.extraction_note = "Failed", "Failed", f"Extraction error: {exc.__class__.__name__}"
    d.reprocess_count = (d.reprocess_count or 0) + 1
    audit("document.reprocessed", category="clinical", entity_type="medical_document", entity_id=did, patient_id=d.patient_id)
    commit()
    return jsonify(ok=True, message="Reprocessed from the original file", document=_doc_row(d))


@bp.post("/documents/<int:did>/review")
@require_perm("doc.review")
def review_document(did):
    d = _doc_for(did)
    st = s(payload(), "status", 20)
    if st not in ("Reviewed", "Needs correction"):
        raise ApiError("status must be Reviewed or Needs correction")
    d.review_status, d.reviewed_by_id, d.reviewed_at = st, g.user.id, utcnow()
    audit("document.reviewed", category="clinical", entity_type="medical_document", entity_id=did, patient_id=d.patient_id, details=st)
    commit()
    return ok("Review recorded")


@bp.put("/documents/<int:did>/pages/<int:page_no>")
@require_perm("doc.review")
def correct_page(did, page_no):
    d = _doc_for(did)
    pg = db.session.execute(select(DocumentPage).where(DocumentPage.document_id == did, DocumentPage.page_no == page_no)).scalar_one_or_none()
    if not pg:
        raise ApiError("Page not found", 404)
    pg.corrected_text = s(payload(), "text", 60000)
    pg.corrected_by_id = g.user.id
    d.review_status = "Reviewed"
    audit("document.text_corrected", category="clinical", entity_type="medical_document", entity_id=did, patient_id=d.patient_id, details=f"page {page_no}")
    commit()
    return ok("Correction saved; the originally extracted text is preserved")
