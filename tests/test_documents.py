import io
import os

import pytest
from sqlalchemy import select

from careflow.extensions import db
from careflow.models import AuditLog, MedicalDocument

PDF = (b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
       b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
       b"4 0 obj<</Length 58>>stream\nBT /F1 12 Tf 20 100 Td (Haemoglobin 11.2 g/dL) Tj ET\nendstream endobj\n"
       b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\ntrailer<</Root 1 0 R/Size 6>>\n%%EOF\n")


def up(api, pid, name, data, doc_type="Other", **extra):
    return api.post(f"/api/patients/{pid}/documents", data={"file": (io.BytesIO(data), name), "doc_type": doc_type, **extra}, content_type="multipart/form-data")


def test_text_upload_is_stored_privately_and_extracted(app, as_user, ids):
    d1 = as_user("doctor1")
    r = up(d1, ids.patient["Maya Rao"], "note.txt", b"Plain text clinical letter.\nBP 120/80")
    assert r.status_code == 200
    doc = r.json["document"]
    assert doc["extraction_status"] == "Complete" and doc["extraction_method"] == "plain-text" and doc["mime_type"] == "text/plain"
    full = d1.get(f"/api/documents/{doc['id']}?text=1").json
    assert "BP 120/80" in full["pages"][0]["text"]
    row = db.session.get(MedicalDocument, doc["id"])
    assert row.storage_backend == "local" and "note.txt" not in row.storage_key and len(row.sha256) == 64
    # stored under the private upload directory, not under the static folder
    assert os.path.exists(os.path.join(app.config["UPLOAD_DIR"], row.storage_key))
    assert not os.path.exists(os.path.join(app.static_folder, row.storage_key))


def test_pdf_with_embedded_text_is_extracted_without_ocr(as_user, ids):
    d1 = as_user("doctor1")
    r = up(d1, ids.patient["Maya Rao"], "lab.pdf", PDF, "Other")
    assert r.status_code == 200, r.json
    d = r.json["document"]
    assert d["page_count"] == 1 and d["extraction_method"] in ("embedded-text", "mixed")
    assert "Haemoglobin 11.2" in d1.get(f"/api/documents/{d['id']}?text=1").json["pages"][0]["text"]


@pytest.mark.parametrize("name,data", [
    ("evil.pdf", b"MZ\x90\x00 this is an executable"),
    ("evil.png", b"<script>alert(1)</script>"),
    ("run.exe", b"MZ\x90\x00"),
    ("empty.txt", b""),
    ("bin.txt", b"abc\x00\x01\x02def"),
    ("a.pdf", b"%PDF-1.4 truncated"),
    ("x.html", b"<html><script>1</script></html>"),
    ("doc.docx", b"PK\x03\x04junk"),
])
def test_invalid_or_disguised_files_are_rejected(as_user, ids, name, data):
    r = up(as_user("doctor1"), ids.patient["Maya Rao"], name, data)
    assert r.status_code == 400, (name, r.status_code)


def test_content_type_must_match_extension(as_user, ids):
    assert up(as_user("doctor1"), ids.patient["Maya Rao"], "photo.png", PDF).status_code == 400


def test_oversize_upload_rejected(app, as_user, ids):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    assert up(as_user("doctor1"), ids.patient["Maya Rao"], "big.txt", b"a" * 5000).status_code == 413


def test_filenames_are_sanitised_and_never_used_as_paths(as_user, ids):
    r = up(as_user("doctor1"), ids.patient["Maya Rao"], "../../etc/passwd.txt", b"hello")
    assert r.status_code == 200
    d = r.json["document"]
    assert "/" not in d["original_filename"] and ".." not in d["original_filename"]
    row = db.session.get(MedicalDocument, d["id"])
    assert ".." not in row.storage_key and not row.storage_key.startswith("/")


def test_upload_requires_patient_access_and_matching_doc_type(as_user, ids):
    assert up(as_user("doctor2"), ids.patient["Maya Rao"], "n.txt", b"hello").status_code in (403, 404)
    assert up(as_user("billing"), ids.patient["Maya Rao"], "n.txt", b"hello", "Laboratory report").status_code in (403, 404)
    lab = as_user("lab")
    assert up(lab, ids.patient["Maya Rao"], "n.txt", b"Hb 11.2", "Clinical letter").status_code == 403    # lab staff only handle lab reports
    assert up(lab, ids.patient["Maya Rao"], "n.txt", b"Hb 11.2", "Laboratory report").status_code == 200


def test_document_visibility_by_type_and_download_authorisation(as_user, ids):
    d1 = as_user("doctor1")
    maya = ids.patient["Maya Rao"]
    letter = up(d1, maya, "l.txt", b"Private letter", "Clinical letter").json["document"]["id"]
    labdoc = up(as_user("lab"), maya, "r.txt", b"Hb 11.2", "Laboratory report").json["document"]["id"]
    lab = as_user("lab")
    assert lab.get(f"/api/documents/{letter}").status_code == 404                      # type not visible to lab staff
    assert lab.get(f"/api/documents/{labdoc}").status_code == 200
    assert [x["id"] for x in lab.get(f"/api/patients/{maya}/documents").json["items"]] == [labdoc]
    other = as_user("doctor2")
    assert other.get(f"/api/documents/{letter}").status_code == 404
    assert other.get(f"/api/documents/{letter}/download").status_code == 404
    r = d1.get(f"/api/documents/{letter}/download")
    assert r.status_code == 200 and r.data == b"Private letter"
    assert "attachment" in r.headers.get("Content-Disposition", "") and r.headers["X-Content-Type-Options"] == "nosniff"
    acts = [a.action for a in db.session.execute(select(AuditLog)).scalars()]
    assert "document.uploaded" in acts and any(a.startswith("document.") and "download" in a for a in acts)


def test_review_and_correction_preserve_original_text(as_user, ids):
    d1 = as_user("doctor1")
    maya = ids.patient["Maya Rao"]
    did = up(d1, maya, "t.txt", b"Hb 1l.2 g/dL").json["document"]["id"]
    assert d1.put(f"/api/documents/{did}/pages/1", {"text": "Hb 11.2 g/dL"}).status_code == 200
    page = d1.get(f"/api/documents/{did}?text=1").json["pages"][0]
    assert page["text"] == "Hb 1l.2 g/dL" and page["corrected_text"] == "Hb 11.2 g/dL"
    assert d1.post(f"/api/documents/{did}/review", {"status": "Reviewed"}).status_code == 200
    assert d1.post(f"/api/documents/{did}/reprocess").status_code == 200
    page = d1.get(f"/api/documents/{did}?text=1").json["pages"][0]
    assert page["corrected_text"] == "Hb 11.2 g/dL"                                    # reviewer correction survives reprocessing


def test_corrupt_stored_file_degrades_gracefully(app, as_user, ids):
    d1 = as_user("doctor1")
    did = up(d1, ids.patient["Maya Rao"], "t.txt", b"hello").json["document"]["id"]
    row = db.session.get(MedicalDocument, did)
    os.remove(os.path.join(app.config["UPLOAD_DIR"], row.storage_key))
    assert d1.get(f"/api/documents/{did}/download").status_code in (404, 410, 500, 503)
    assert d1.get(f"/api/documents/{did}").status_code == 200


def test_ocr_unavailable_is_reported_honestly_for_images(app, as_user, ids):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (80, 40), "white").save(buf, "PNG")
    r = up(as_user("doctor1"), ids.patient["Maya Rao"], "scan.png", buf.getvalue())
    assert r.status_code == 200
    d = r.json["document"]
    assert d["is_image"] and d["extraction_status"] in ("OCR unavailable", "Partial", "Failed", "Complete")
    if d["extraction_status"] == "OCR unavailable":
        assert "OCR" in d["extraction_note"]
