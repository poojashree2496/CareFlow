"""Editable role dashboards (lab/radiology submit) and the read-only patient portal."""
import io

import pytest
from sqlalchemy import select

from careflow.ai.providers import MockProvider
from careflow.extensions import db
from careflow.models import AppUser, Deliverable, LabReport, MedicalDocument, RadiologyRecord
from conftest import DEMO_PW

PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 144]>>endobj\ntrailer<</Root 1 0 R/Size 4>>\n%%EOF\n"


def upload(api, pid, name, data, doc_type, **extra):
    return api.post(f"/api/patients/{pid}/documents", data={"file": (io.BytesIO(data), name), "doc_type": doc_type, **extra}, content_type="multipart/form-data")


def lab_for(pid, status=None):
    q = select(LabReport).where(LabReport.patient_id == pid)
    if status:
        q = q.where(LabReport.status == status)
    return db.session.execute(q.order_by(LabReport.id)).scalars().first()


def _activate(email):
    """Accounts created by an administrator carry a temporary password; the tests skip the forced change."""
    u = db.session.execute(select(AppUser).where(AppUser.email == email)).scalar_one()
    u.must_change_password = False
    db.session.commit()


@pytest.fixture()
def tomas_portal(app, as_user, ids):
    """A portal login for Tomas (whose HbA1c is still only 'Ordered')."""
    adm = as_user("admin")
    r = adm.post("/api/admin/users", {"email": "tomas.portal@example.org", "name": "Tomas Ek", "role": "patient", "patient_id": ids.patient["Tomas Ek"], "password": "Portal-Pass-Long-2026!"})
    assert r.status_code == 200, r.json
    _activate("tomas.portal@example.org")
    from conftest import Api
    a = Api(app)
    assert a.login("tomas.portal@example.org", "Portal-Pass-Long-2026!").status_code == 200
    return a


# ------------------------------------------------------------------ patient role boundaries
def test_patient_gets_only_portal_and_assistant(as_user):
    p = as_user("patient1")
    me = p.get("/api/auth/me").json["user"]
    assert me["role"] == "patient" and [w["id"] for w in me["workspaces"]] == ["portal", "ai"]
    assert sorted(me["permissions"]) == ["ai.use", "portal.view"]


@pytest.mark.parametrize("method,url", [("get", "/api/patients"), ("get", "/api/labs"), ("get", "/api/bills"), ("get", "/api/admin/users"), ("get", "/api/bedboard"),
                                        ("get", "/api/patients/1/journey"), ("get", "/api/workspaces/doctor"), ("post", "/api/prescriptions"),
                                        ("post", "/api/patients/1/notes"), ("post", "/api/labs/1/submit"), ("patch", "/api/deliverables/1")])
def test_patient_cannot_reach_staff_endpoints(as_user, method, url):
    p = as_user("patient1")
    r = getattr(p, method)(url) if method == "get" else getattr(p, method)(url, {})
    assert r.status_code == 403, (url, r.status_code)


def test_patient_sees_own_released_record_and_nothing_else(as_user, ids):
    p = as_user("patient1")
    o = p.get("/api/portal/overview").json
    assert o["read_only"] and o["patient"]["name"].startswith("Maya Rao")
    assert [l["test_name"] for l in o["labs"]] == ["Complete blood count"] and any(r["analyte"] == "Haemoglobin" for r in o["labs"][0]["results"])
    assert o["radiology"] and "opacity" in o["radiology"][0]["findings"]
    assert o["stay"] and o["bills"] and o["medications"]
    blob = str(o)
    for other in ("Tomas", "Lina", "Ravi", "Zoe", "Basic metabolic", "HbA1c"):
        assert other not in blob
    assert "Admission note" not in blob                      # clinician working notes are staff-internal
    kinds = {d["kind"] for d in o["deliverables"]}
    assert {"Laboratory report", "Radiology report", "Invoice / receipt"} <= kinds
    lab_item = next(d for d in o["deliverables"] if d["kind"] == "Laboratory report")
    assert lab_item["digital_available"] and lab_item["physical_status"] == "Ready for collection"


def test_unreleased_result_is_invisible_to_patient_until_submitted(as_user, ids, tomas_portal):
    assert tomas_portal.get("/api/portal/overview").json["labs"] == []
    lab = lab_for(ids.patient["Tomas Ek"], "Ordered")
    lab_id = lab.id
    labuser = as_user("lab")
    # no file and no values -> refuse
    r = labuser.post(f"/api/labs/{lab_id}/submit", {})
    assert r.status_code == 409 and "Attach" in r.json["error"]
    up = upload(labuser, ids.patient["Tomas Ek"], "hba1c.pdf", PDF, "Laboratory report", lab_report_id=str(lab_id))
    assert up.status_code == 200, up.json
    doc_id = up.json["document"]["id"]
    assert up.json["document"]["patient_visible"] is False
    assert tomas_portal.get(f"/api/portal/documents/{doc_id}/download").status_code == 404          # attached but not yet released
    r = labuser.post(f"/api/labs/{lab_id}/submit", {"results": [{"analyte": "HbA1c", "value": 6.1, "unit": "%", "ref_low": 4, "ref_high": 5.6}]})
    assert r.status_code == 200, r.json
    assert r.json["status"] == "Released" and r.json["steps"] == ["collected", "received", "results entered", "verified", "released"]
    # a second submit is refused
    assert labuser.post(f"/api/labs/{lab_id}/submit", {}).status_code == 409
    # now visible to the patient, with the attached file
    o = tomas_portal.get("/api/portal/overview").json
    assert [l["test_name"] for l in o["labs"]] == ["HbA1c"] and o["labs"][0]["results"][0]["flag"] == "High"
    assert o["labs"][0]["files"][0]["id"] == doc_id
    dl = tomas_portal.get(f"/api/portal/documents/{doc_id}/download")
    assert dl.status_code == 200 and dl.data.startswith(b"%PDF")
    # ...and to the doctor, admin and super admin, each with the file
    for who in ("doctor1", "admin", "super"):
        d = as_user(who).get(f"/api/labs/{lab_id}")
        assert d.status_code == 200, (who, d.json)
        assert d.json["status"] == "Released" and d.json["files"] and d.json["files"][0]["id"] == doc_id
    # a doctor with no care relationship cannot
    assert as_user("doctor2").get(f"/api/labs/{lab_id}").status_code in (403, 404)
    # an auto-created hand-over item exists in digital form
    item = db.session.execute(select(Deliverable).where(Deliverable.ref_type == "lab", Deliverable.ref_id == lab_id)).scalar_one()
    assert item.digital_available and item.physical_status == "Not requested"


def test_report_only_submission_with_attachment_and_no_values(as_user, ids):
    lab_id = lab_for(ids.patient["Tomas Ek"], "Ordered").id
    labuser = as_user("lab")
    assert upload(labuser, ids.patient["Tomas Ek"], "r.pdf", PDF, "Laboratory report", lab_report_id=str(lab_id)).status_code == 200
    r = labuser.post(f"/api/labs/{lab_id}/submit", {})
    assert r.status_code == 200 and r.json["status"] == "Released"
    assert db.session.get(LabReport, lab_id).result.startswith("Report attached")


def test_only_lab_staff_can_submit_lab_reports(as_user, ids):
    lab_id = lab_for(ids.patient["Tomas Ek"], "Ordered").id
    for who in ("doctor1", "admin", "nurse", "pharmacist", "billing"):
        assert as_user(who).post(f"/api/labs/{lab_id}/submit", {}).status_code == 403, who


def test_admin_reads_lab_but_cannot_edit_it(as_user, ids):
    adm = as_user("admin")
    assert adm.get("/api/labs").status_code == 200
    lab_id = lab_for(ids.patient["Maya Rao"], "Released").id
    assert adm.get(f"/api/labs/{lab_id}").status_code == 200
    assert adm.put(f"/api/labs/{lab_id}/results", {"results": [{"analyte": "x", "value": 1}]}).status_code == 403
    assert adm.post(f"/api/labs/{lab_id}/release", {}).status_code == 403


def test_radiology_submit_releases_report_to_patient(as_user, ids, app):
    adm = as_user("admin")
    adm.post("/api/admin/users", {"email": "lina.portal@example.org", "name": "Lina Okafor", "role": "patient", "patient_id": ids.patient["Lina Okafor"], "password": "Portal-Pass-Long-2026!"})
    _activate("lina.portal@example.org")
    from conftest import Api
    lina = Api(app)
    assert lina.login("lina.portal@example.org", "Portal-Pass-Long-2026!").status_code == 200
    d1 = as_user("doctor2")
    r = d1.post("/api/radiology", {"patient_id": ids.patient["Lina Okafor"], "modality": "CT", "study_description": "Abdomen", "indication": "post-op pain"})
    assert r.status_code == 200, r.json
    rid = r.json["id"]
    rad = as_user("radiology")
    assert rad.post(f"/api/radiology/{rid}/submit", {}).status_code == 409                       # findings required
    up = upload(rad, ids.patient["Lina Okafor"], "scan.pdf", PDF, "Radiology report", radiology_id=str(rid))
    assert up.status_code == 200, up.json
    assert lina.get("/api/portal/overview").json["radiology"] == []
    r = rad.post(f"/api/radiology/{rid}/submit", {"findings": "No acute abnormality.", "impression": "Normal study."})
    assert r.status_code == 200 and r.json["steps"] == ["performed", "reported", "authorized"], r.json
    o = lina.get("/api/portal/overview").json
    assert o["radiology"][0]["impression"] == "Normal study." and o["radiology"][0]["files"]
    assert as_user("super").get(f"/api/radiology/{rid}").json["files"]


# ------------------------------------------------------------------ physical / digital hand-over
def test_physical_handover_is_recorded_and_patient_sees_it(as_user, ids):
    p = as_user("patient1")
    item = next(d for d in p.get("/api/portal/overview").json["deliverables"] if d["kind"] == "Laboratory report")
    assert p.patch(f"/api/deliverables/{item['id']}", {"physical_status": "Handed over"}).status_code == 403
    lab = as_user("lab")
    assert lab.patch(f"/api/deliverables/{item['id']}", {"physical_status": "Handed over"}).status_code == 400       # who received it?
    r = lab.patch(f"/api/deliverables/{item['id']}", {"physical_status": "Handed over", "received_by_name": "Maya Rao"})
    assert r.status_code == 200
    now = next(d for d in p.get("/api/portal/overview").json["deliverables"] if d["id"] == item["id"])
    assert now["physical_status"] == "Handed over" and now["received_by_name"] == "Maya Rao" and now["handed_over_at"]
    assert lab.patch(f"/api/deliverables/{item['id']}", {"physical_status": "Requested"}).status_code == 409        # no silent rewinding
    # staff outside the patient's care cannot touch it (doctor2 is not Maya's doctor)
    assert as_user("doctor2").patch(f"/api/deliverables/{item['id']}", {"physical_note": "x"}).status_code == 404


def test_dispensing_creates_a_physical_item_ready_for_collection(as_user, ids):
    from careflow.models import Prescription
    rx = db.session.execute(select(Prescription).where(Prescription.patient_id == ids.patient["Maya Rao"])).scalars().first()
    ph = as_user("pharmacist")
    r = ph.post(f"/api/prescriptions/{rx.id}/dispense", {"quantity": 7, "acknowledged_warnings": ["Penicillin"]})
    assert r.status_code == 200, r.json
    p = as_user("patient1").get("/api/portal/overview").json
    item = next(d for d in p["deliverables"] if d["kind"] == "Prescription / medicine label")
    assert item["physical_status"] == "Ready for collection"
    assert p["medications"][0]["dispensed_quantity"] == 7


# ------------------------------------------------------------------ account management
def test_patient_accounts_are_linked_one_to_one_and_cannot_be_repurposed(as_user, ids):
    adm = as_user("admin")
    body = {"email": "x1@example.org", "name": "Zoe Hart", "role": "patient", "patient_id": ids.patient["Zoe Hart"], "password": "Portal-Pass-Long-2026!"}
    assert adm.post("/api/admin/users", body).status_code == 200
    assert adm.post("/api/admin/users", {**body, "email": "x2@example.org"}).status_code == 409           # that patient already has a login
    assert adm.post("/api/admin/users", {**body, "email": "x3@example.org", "patient_id": None}).status_code == 400
    assert adm.post("/api/admin/users", {"email": "n@example.org", "name": "Some Nurse", "role": "nurse", "patient_id": ids.patient["Zoe Hart"], "password": "Portal-Pass-Long-2026!"}).status_code == 400
    u = db.session.execute(select(AppUser).where(AppUser.email == "x1@example.org")).scalar_one()
    assert adm.patch(f"/api/admin/users/{u.id}", {"role": "doctor"}).status_code == 409
    assert u.must_change_password is True


# ------------------------------------------------------------------ assistant for patients
@pytest.fixture()
def mock_ai(app):
    app.config.update(AI_PROVIDER="mock", AI_MODEL="mock", TESTING=True)
    MockProvider.calls = []
    MockProvider.responder = None
    yield MockProvider
    app.config.update(AI_PROVIDER="")


def test_patient_assistant_is_scoped_simple_and_excludes_staff_material(as_user, ids, mock_ai):
    p = as_user("patient1")
    assert p.post("/api/ai/conversations", {"patient_id": ids.patient["Tomas Ek"]}).status_code in (403, 404)       # another patient
    cid = p.post("/api/ai/conversations", {"patient_id": ids.patient["Maya Rao"]}).json["conversation_id"]
    r = p.post(f"/api/ai/conversations/{cid}/ask", {"question": "Summarise my notes and my blood results", "mode": "clinical"})
    assert r.status_code == 200, r.json
    sent = "\n".join(m["content"] for m in MockProvider.calls[-1]["messages"])
    system = MockProvider.calls[-1].get("system", "")
    assert "Admission note" not in sent and "Haemoglobin" in sent
    assert "PATIENT themself" in system and "Style: plain" in system and "clinicians" not in system.split("Style:")[1][:40]
    assert r.json["message"]["mode"] == "simple"


def test_patient_assistant_never_reads_unshared_documents(as_user, ids, mock_ai):
    d1 = as_user("doctor1")
    up = upload(d1, ids.patient["Maya Rao"], "letter.txt", b"Internal letter: SECRETWORD-77 about care plan.", "Clinical letter")
    assert up.status_code == 200
    p = as_user("patient1")
    cid = p.post("/api/ai/conversations", {"patient_id": ids.patient["Maya Rao"]}).json["conversation_id"]
    p.post(f"/api/ai/conversations/{cid}/ask", {"question": "What does my uploaded document letter say?"})
    assert "SECRETWORD-77" not in "\n".join(m["content"] for m in (MockProvider.calls[-1]["messages"] if MockProvider.calls else []))
    d1.post(f"/api/documents/{up.json['document']['id']}/visibility", {"patient_visible": True})
    p.post(f"/api/ai/conversations/{cid}/ask", {"question": "What does my uploaded document letter say?"})
    assert "SECRETWORD-77" in "\n".join(m["content"] for m in MockProvider.calls[-1]["messages"])


def test_printable_copy_for_released_items_only_and_own_items_only(app, as_user, ids):
    from careflow.models import Deliverable
    pat = as_user("patient1")
    items = pat.get("/api/portal/overview").json["deliverables"]
    assert items and all(i["copy_url"].startswith("/api/portal/deliverables/") for i in items)
    for i in items:
        r = pat.get(i["copy_url"])
        assert r.status_code in (200, 302), (i["kind"], r.status_code)
        if r.status_code == 200:
            assert b"Print / save as PDF" in r.data and r.headers["Content-Security-Policy"].startswith("default-src 'none'")
    own = {i["id"] for i in items}
    other = db.session.execute(select(Deliverable).where(Deliverable.id.notin_(own))).scalars().first()
    if other is not None:
        assert pat.get(f"/api/portal/deliverables/{other.id}/copy").status_code == 404
    assert as_user("doctor1").get(f"/api/portal/deliverables/{items[0]['id']}/copy").status_code == 403


def test_admin_can_create_and_delete_accounts_with_guards(app, as_user, ids):
    sa, ha = as_user("super"), as_user("admin")
    r = sa.post("/api/admin/users", {"email": "new.nurse@example.org", "name": "New Nurse", "role": "nurse", "password": "Brisk-Lantern-Orbit-7!"})
    assert r.status_code == 200, r.json
    uid = r.json["user"]["id"]
    assert sa.post("/api/admin/users", {"email": "new.admin@example.org", "name": "New Admin", "role": "hospital_admin", "password": "Brisk-Lantern-Orbit-7!"}).status_code == 200
    assert ha.post("/api/admin/users", {"email": "x.admin@example.org", "name": "X Admin", "role": "hospital_admin", "password": "Brisk-Lantern-Orbit-7!"}).status_code == 403   # only a super admin makes admins
    me = sa.get("/api/auth/me").json["user"]["id"]
    assert sa.delete(f"/api/admin/users/{me}").status_code == 409
    d = sa.delete(f"/api/admin/users/{uid}")
    assert d.status_code == 200 and d.json["deleted"] is True
    # an account with history is disabled rather than erased
    doc = ids.user["doctor1"]
    d2 = sa.delete(f"/api/admin/users/{doc}")
    assert d2.status_code == 200
    assert d2.json["deleted"] is False and d2.json["disabled"] is True      # seeded doctor authored orders -> disabled, not erased
    assert not db.session.get(AppUser, doc).is_active
    assert as_user("nurse").delete(f"/api/admin/users/{ids.user['lab']}").status_code == 403
