"""Resource-level authorisation: knowing an id is never enough."""
from sqlalchemy import select

from careflow.extensions import db
from careflow.models import AiConversation, AuditLog, Bed, LabReport, PatientAssignment


def test_doctor_sees_only_own_patients(as_user, ids):
    d1, d2 = as_user("doctor1"), as_user("doctor2")
    maya, lina = ids.patient["Maya Rao"], ids.patient["Lina Okafor"]
    assert d1.get(f"/api/patients/{maya}").status_code == 200
    assert d1.get(f"/api/patients/{lina}").status_code == 404     # 404, not 403: existence is not revealed
    assert d2.get(f"/api/patients/{maya}").status_code == 404
    listed = {p["id"] for p in d1.get("/api/patients").json["items"]}
    assert maya in listed and lina not in listed


def test_every_patient_scoped_endpoint_rejects_unrelated_doctor(as_user, ids):
    d2 = as_user("doctor2")
    maya = ids.patient["Maya Rao"]
    for suffix in ("", "/journey", "/notes", "/allergies", "/problems", "/observations", "/medications", "/documents", "/tasks", "/handovers",
                   "/intake-output", "/follow-ups", "/assignments", "/encounters", "/care-plans", "/lab-trend?analyte=x"):
        r = d2.get(f"/api/patients/{maya}{suffix}")
        assert r.status_code in (403, 404), (suffix, r.status_code)
    assert d2.post(f"/api/patients/{maya}/notes", {"body": "x"}).status_code in (403, 404)
    assert d2.post(f"/api/patients/{maya}/observations", {"values": {"heart_rate": 80}}).status_code in (403, 404)


def test_object_ids_cannot_be_used_to_reach_other_patients_records(as_user, ids):
    d2 = as_user("doctor2")
    maya_lab = db.session.execute(select(LabReport.id).where(LabReport.patient_id == ids.patient["Maya Rao"])).scalar()
    assert d2.get(f"/api/labs/{maya_lab}").status_code in (403, 404)
    assert d2.post(f"/api/labs/{maya_lab}/amend", {"reason": "x", "results": [{"analyte": "a", "value": 1}]}).status_code in (403, 404)
    assert d2.get("/api/documents/99999").status_code == 404


def test_billing_staff_get_no_clinical_data(as_user, ids):
    b = as_user("billing")
    maya = ids.patient["Maya Rao"]
    body = b.get(f"/api/patients/{maya}").json
    assert "medical_history" not in str(body.get("patient", body)) or not body.get("patient", {}).get("medical_history")
    for suffix in ("/notes", "/observations", "/medications", "/allergies", "/journey/labs"):
        assert b.get(f"/api/patients/{maya}{suffix}").status_code in (403, 404)
    assert b.get(f"/api/labs/{db.session.execute(select(LabReport.id)).scalar()}").status_code in (403, 404)


def test_lab_staff_only_reach_patients_with_lab_orders(as_user, ids):
    lab = as_user("lab")
    assert lab.get(f"/api/patients/{ids.patient['Maya Rao']}").status_code == 200
    assert lab.get(f"/api/patients/{ids.patient['Zoe Hart']}").status_code == 404     # no lab order for Zoe
    assert lab.get(f"/api/patients/{ids.patient['Maya Rao']}/notes").status_code in (403, 404)
    assert lab.get(f"/api/patients/{ids.patient['Maya Rao']}/medications").status_code in (403, 404)


def test_nurse_is_limited_to_own_ward(as_user, ids):
    n = as_user("nurse")                     # Ward A
    assert n.get(f"/api/patients/{ids.patient['Maya Rao']}").status_code == 200
    assert n.get(f"/api/patients/{ids.patient['Lina Okafor']}").status_code == 404   # ICU
    assert n.post(f"/api/patients/{ids.patient['Lina Okafor']}/observations", {"values": {"heart_rate": 70}}).status_code == 404


def test_pharmacist_and_radiology_are_scoped_by_orders(as_user, ids):
    ph, rad = as_user("pharmacist"), as_user("radiology")
    assert ph.get(f"/api/patients/{ids.patient['Maya Rao']}/medications").status_code == 200
    assert ph.get(f"/api/patients/{ids.patient['Maya Rao']}/observations").status_code in (403, 404)
    assert ph.get(f"/api/patients/{ids.patient['Lina Okafor']}").status_code == 404
    assert rad.get(f"/api/patients/{ids.patient['Maya Rao']}").status_code == 200
    assert rad.get(f"/api/patients/{ids.patient['Tomas Ek']}").status_code == 404


def test_unreleased_lab_results_are_hidden_from_clinicians(as_user, ids):
    d1 = as_user("doctor1")
    pending = db.session.execute(select(LabReport.id).where(LabReport.patient_id == ids.patient["Tomas Ek"])).scalar()
    r = d1.get(f"/api/labs/{pending}").json
    assert r["results"] == [] and "not yet released" in (r.get("summary") or "").lower()


def test_super_admin_clinical_access_is_audited(as_user, ids):
    s = as_user("super")
    assert s.get(f"/api/patients/{ids.patient['Maya Rao']}/notes").status_code == 200
    acts = [a.action for a in db.session.execute(select(AuditLog)).scalars()]
    assert "privileged.clinical_access" in acts


def test_removing_assignment_revokes_access_including_ai_history(app, as_user, ids):
    zoe = ids.patient["Zoe Hart"]
    d1, admin = as_user("doctor1"), as_user("admin")
    assert d1.get(f"/api/patients/{zoe}").status_code == 200
    cid = d1.post("/api/ai/conversations", {"patient_id": zoe}).json["conversation_id"]
    aid = db.session.execute(select(PatientAssignment.id).where(PatientAssignment.patient_id == zoe, PatientAssignment.active.is_(True),
                                                                PatientAssignment.user_id == ids.user["doctor1"])).scalar()
    assert admin.delete(f"/api/assignments/{aid}").status_code == 200
    assert d1.get(f"/api/patients/{zoe}").status_code == 404
    assert d1.get(f"/api/ai/conversations/{cid}").status_code == 404
    assert d1.post(f"/api/ai/conversations/{cid}/ask", {"question": "summary"}).status_code == 404


def test_ai_conversations_are_private_to_their_owner(as_user, ids):
    d1, nurse = as_user("doctor1"), as_user("nurse")
    maya = ids.patient["Maya Rao"]
    cid = d1.post("/api/ai/conversations", {"patient_id": maya}).json["conversation_id"]
    assert nurse.get(f"/api/ai/conversations/{cid}").status_code == 404   # same patient, different user
    assert nurse.delete(f"/api/ai/conversations/{cid}").status_code == 404
    assert as_user("doctor2").post("/api/ai/conversations", {"patient_id": maya}).status_code == 404


def test_notifications_are_filtered_by_patient_access(as_user, ids):
    # critical-result broadcast about an ICU patient must not reach the Ward A nurse
    n = as_user("nurse").get("/api/auth/notifications").json
    lina_ravi = {ids.patient["Lina Okafor"], ids.patient["Ravi Menon"]}
    assert not [x for x in n["items"] if x["patient_id"] in lina_ravi]


def test_demo_user_cannot_escalate_via_payload(as_user, ids):
    d1 = as_user("doctor1")
    r = d1.post("/api/patients", {"name": "Hack Attempt", "role": "super_admin", "is_demo": False, "data_origin": "real"})
    assert r.status_code in (200, 400)
    assert d1.get("/api/admin/users").status_code == 403
