"""Clinical and operational workflows end-to-end against the real database."""
from datetime import date, timedelta

from sqlalchemy import select

from careflow.extensions import db
from careflow.models import (Admission, Alert, Bed, ClinicalNote, CriticalAck, LabReport, Medicine, MedicationAdministration, Prescription,
                             RadiologyRecord, RadiologyReportVersion)

FUTURE = (date.today() + timedelta(days=30))
while FUTURE.weekday() > 4:
    FUTURE += timedelta(days=1)
DAY = FUTURE.isoformat()


def free_bed(ward_name):
    return db.session.execute(select(Bed).where(Bed.status == "Available", Bed.ward.has(name=ward_name)).order_by(Bed.code)).scalars().first()


# ---------------------------------------------------------------- scheduling
def test_double_booking_is_rejected(as_user, ids):
    admin = as_user("admin")
    did = db.session.execute(select(Admission.responsible_doctor_id).limit(1)).scalar()
    body = {"patient_id": ids.patient["Zoe Hart"], "doctor_id": did, "appointment_date": DAY, "appointment_time": "10:00", "reason": "check"}
    assert admin.post("/api/appointments", body).status_code == 200
    r = admin.post("/api/appointments", {**body, "patient_id": ids.patient["Tomas Ek"]})
    assert r.status_code in (400, 409)


def test_appointment_outside_working_hours_or_past_is_rejected(as_user, ids):
    admin = as_user("admin")
    did = db.session.execute(select(Admission.responsible_doctor_id).limit(1)).scalar()
    base = {"patient_id": ids.patient["Zoe Hart"], "doctor_id": did, "appointment_time": "10:00"}
    assert admin.post("/api/appointments", {**base, "appointment_date": "2001-01-01"}).status_code == 400
    assert admin.post("/api/appointments", {**base, "appointment_date": DAY, "appointment_time": "03:00"}).status_code == 400
    assert admin.post("/api/appointments", {**base, "appointment_date": "not-a-date"}).status_code == 400


# ---------------------------------------------------------------- admissions & beds
def test_admission_bed_transfer_and_discharge_lifecycle(as_user, ids):
    d1 = as_user("doctor1")
    zoe = ids.patient["Zoe Hart"]
    bed = free_bed("Ward A")
    r = d1.post("/api/admissions", {"patient_id": zoe, "bed_id": bed.id, "reason": "Observation"})
    assert r.status_code == 200, r.json
    aid = r.json["id"]
    assert db.session.get(Bed, bed.id).status == "Occupied"
    # a second active admission for the same patient is refused
    assert d1.post("/api/admissions", {"patient_id": zoe, "ward": "Ward A"}).status_code == 409
    # an occupied bed cannot be taken by someone else
    other = ids.patient["Tomas Ek"]
    assert as_user("nurse").post(f"/api/admissions/{db.session.execute(select(Admission.id).where(Admission.patient_id == other)).scalar()}/assign-bed", {"bed_id": bed.id}).status_code == 409
    # transfer frees the old bed (to Cleaning) and occupies the new one
    new = free_bed("Ward A")
    assert d1.post(f"/api/admissions/{aid}/transfer", {"bed_id": new.id, "reason": "Closer to nurses' station"}).status_code == 200
    assert db.session.get(Bed, bed.id).status == "Cleaning" and db.session.get(Bed, new.id).status == "Occupied"
    # discharge: cannot complete before it is planned and authorised
    assert d1.post(f"/api/admissions/{aid}/discharge/complete").status_code in (400, 409)
    assert d1.post(f"/api/admissions/{aid}/discharge/plan", {"plan": "Home with follow-up"}).status_code == 200
    assert as_user("nurse").post(f"/api/admissions/{aid}/discharge/authorize", {"summary": "x"}).status_code == 403   # nurses cannot authorise
    assert d1.post(f"/api/admissions/{aid}/discharge/authorize", {"summary": "Recovered. Follow up in 2 weeks."}).status_code == 200
    assert d1.post(f"/api/admissions/{aid}/discharge/complete").status_code == 200
    assert db.session.get(Bed, new.id).status == "Cleaning"
    assert db.session.get(Admission, aid).status == "Discharged"


def test_bed_status_rules(as_user):
    admin = as_user("admin")
    bed = free_bed("Ward A")
    assert admin.post(f"/api/beds/{bed.id}/status", {"status": "Occupied"}).status_code in (400, 409)   # occupancy only through admission
    assert admin.post(f"/api/beds/{bed.id}/status", {"status": "Maintenance", "note": "leak"}).status_code == 200
    assert admin.post(f"/api/beds/{bed.id}/status", {"status": "Reserved"}).status_code in (400, 409)    # Maintenance -> Reserved not allowed


def test_bedboard_hides_restricted_patient_details(as_user, ids):
    board = as_user("nurse").get("/api/bedboard").json["beds"]
    names = [b["patient"].get("name") for b in board if b["patient"] and not b["patient"].get("restricted")]
    assert "Maya Rao" in names and "Lina Okafor" not in names
    assert any(b["patient"] and b["patient"].get("restricted") for b in board)


# ---------------------------------------------------------------- laboratory
def test_lab_workflow_and_critical_result_acknowledgement(as_user, ids):
    d1, lab = as_user("doctor1"), as_user("lab")
    zoe = ids.patient["Zoe Hart"]
    lid = d1.post("/api/labs", {"patient_id": zoe, "test_name": "Potassium", "priority": "Urgent", "result": "FAKE NORMAL"}).json["id"]
    assert db.session.get(LabReport, lid).result != "FAKE NORMAL"           # clinicians cannot type results
    assert lab.post(f"/api/labs/{lid}/release").status_code == 409          # cannot skip steps
    assert lab.post(f"/api/labs/{lid}/collect").status_code == 200
    assert lab.post(f"/api/labs/{lid}/receive").status_code == 200
    res = [{"analyte": "Potassium", "value": 6.8, "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.1, "critical_high": 6.2}]
    assert d1.put(f"/api/labs/{lid}/results", {"results": res}).status_code == 403
    assert lab.put(f"/api/labs/{lid}/results", {"results": res}).status_code == 200
    # still hidden from the clinician until verified AND released
    assert d1.get(f"/api/labs/{lid}").json["results"] == []
    assert lab.post(f"/api/labs/{lid}/verify").status_code == 200
    assert d1.get(f"/api/labs/{lid}").json["results"] == []
    assert lab.post(f"/api/labs/{lid}/release").status_code == 200
    shown = d1.get(f"/api/labs/{lid}").json["results"]
    assert shown and shown[0]["flag"] == "Critical High" and shown[0]["is_critical"]
    ack = db.session.execute(select(CriticalAck).where(CriticalAck.source_type == "lab", CriticalAck.source_id == lid)).scalar_one()
    assert ack.status == "Pending"
    assert as_user("nurse").post(f"/api/critical/{ack.id}/ack", {"note": "x"}).status_code in (403, 404)
    assert d1.post(f"/api/critical/{ack.id}/ack", {"note": "Informed team, repeat sample sent"}).status_code == 200
    assert d1.post(f"/api/critical/{ack.id}/ack", {}).status_code == 409


def test_released_lab_result_can_only_be_amended_with_reason_and_keeps_history(as_user, ids):
    lab = as_user("lab")
    lid = db.session.execute(select(LabReport.id).where(LabReport.patient_id == ids.patient["Maya Rao"], LabReport.status == "Released")).scalar()
    res = [{"analyte": "Haemoglobin", "value": 11.9, "unit": "g/dL", "ref_low": 12.0, "ref_high": 15.5}]
    assert lab.post(f"/api/labs/{lid}/amend", {"results": res}).status_code == 400
    assert lab.post(f"/api/labs/{lid}/amend", {"results": res, "reason": "Transcription error"}).status_code == 200
    detail = lab.get(f"/api/labs/{lid}").json
    assert any(r.get("version", 1) >= 2 for r in detail["results"]) or detail.get("amendment_count", 0) >= 1


def test_lab_rejection_requires_reason(as_user, ids):
    d1, lab = as_user("doctor1"), as_user("lab")
    lid = d1.post("/api/labs", {"patient_id": ids.patient["Zoe Hart"], "test_name": "CBC"}).json["id"]
    assert lab.post(f"/api/labs/{lid}/collect").status_code == 200
    assert lab.post(f"/api/labs/{lid}/reject", {}).status_code == 400
    assert lab.post(f"/api/labs/{lid}/reject", {"reason": "Haemolysed sample"}).status_code == 200


# ---------------------------------------------------------------- pharmacy
def test_prescribe_verify_dispense_administer_are_separate_steps(as_user, ids):
    d1, ph, nurse = as_user("doctor1"), as_user("pharmacist"), as_user("nurse")
    rx = db.session.execute(select(Prescription).where(Prescription.patient_id == ids.patient["Tomas Ek"])).scalars().first()
    med = db.session.get(Medicine, rx.medicine_id)
    before = med.stock
    assert nurse.post(f"/api/prescriptions/{rx.id}/administer", {"identity_verified": True, "allergies_checked": True}).status_code == 409   # not yet verified/dispensed
    assert ph.post(f"/api/prescriptions/{rx.id}/verify").status_code == 200
    assert ph.post(f"/api/prescriptions/{rx.id}/dispense", {"quantity": 10}).status_code == 200
    db.session.expire_all()
    assert db.session.get(Medicine, med.id).stock == before - 10
    assert db.session.get(Prescription, rx.id).status in ("Dispensed", "Partially Dispensed")
    assert not db.session.execute(select(MedicationAdministration).where(MedicationAdministration.prescription_id == rx.id)).first()   # dispensing != giving
    assert nurse.post(f"/api/prescriptions/{rx.id}/administer", {"status": "Given"}).status_code == 409                                  # safety checks required
    assert nurse.post(f"/api/prescriptions/{rx.id}/administer", {"status": "Given", "identity_verified": True, "allergies_checked": True}).status_code == 200
    assert nurse.post(f"/api/prescriptions/{rx.id}/administer", {"status": "Held"}).status_code == 400   # reason note needed
    assert db.session.execute(select(MedicationAdministration).where(MedicationAdministration.prescription_id == rx.id)).scalars().first().status == "Given"


def test_cannot_dispense_more_than_stock_or_ordered(as_user, ids):
    ph = as_user("pharmacist")
    rx = db.session.execute(select(Prescription).where(Prescription.patient_id == ids.patient["Tomas Ek"])).scalars().first()
    ph.post(f"/api/prescriptions/{rx.id}/verify")
    assert ph.post(f"/api/prescriptions/{rx.id}/dispense", {"quantity": 10_000}).status_code in (400, 409)
    assert ph.post(f"/api/prescriptions/{rx.id}/dispense", {"quantity": -5}).status_code == 400
    assert db.session.get(Medicine, rx.medicine_id).stock >= 0


def test_allergy_conflict_blocks_prescribing_unless_overridden_with_reason(as_user, ids):
    d1 = as_user("doctor1")
    tomas = ids.patient["Tomas Ek"]
    assert d1.post(f"/api/patients/{tomas}/allergies", {"substance": "Aspirin", "reaction": "Wheeze", "severity": "Severe"}).status_code == 200
    body = {"patient_id": tomas, "medicine": "Aspirin 75 mg", "dosage": "75 mg", "route": "Oral", "frequency": "Daily", "quantity": 7}
    r = d1.post("/api/prescriptions", body)
    assert r.status_code == 409 and "allerg" in str(r.json).lower()
    assert d1.post("/api/prescriptions", {**body, "override_reason": "ok"}).status_code == 409        # a throw-away reason is not accepted
    r2 = d1.post("/api/prescriptions", {**body, "override_reason": "Allergy reviewed with patient; benefit outweighs risk"})
    assert r2.status_code == 200
    rx = db.session.get(Prescription, r2.json["id"])
    assert rx.allergy_override_reason and rx.warnings


def test_duplicate_active_order_is_blocked(as_user, ids):
    d1 = as_user("doctor1")
    r = d1.post("/api/prescriptions", {"patient_id": ids.patient["Tomas Ek"], "medicine": "Metformin 500 mg", "dosage": "500 mg"})
    assert r.status_code == 409


def test_restock_and_negative_stock_guard(as_user):
    ph = as_user("pharmacist")
    mid = db.session.execute(select(Medicine.id).where(Medicine.name == "Furosemide 40 mg")).scalar()
    assert ph.post(f"/api/medicines/{mid}/restock", {"quantity": 0}).status_code == 400
    assert ph.patch(f"/api/medicines/{mid}", {"stock": -1}).status_code == 400
    assert ph.post(f"/api/medicines/{mid}/restock", {"quantity": 25}).status_code == 200
    assert ph.get(f"/api/medicines/{mid}/movements").json["items"][0]["delta"] == 25


# ---------------------------------------------------------------- radiology
def test_radiology_report_authorisation_and_amendment_versions(as_user, ids):
    d1, rad = as_user("doctor1"), as_user("radiology")
    rid = d1.post("/api/radiology", {"patient_id": ids.patient["Maya Rao"], "modality": "CT", "study_description": "Chest", "indication": "Follow-up", "findings": "FAKE"}).json["id"]
    assert db.session.get(RadiologyRecord, rid).findings == ""                      # clinicians cannot author findings
    assert rad.put(f"/api/radiology/{rid}/report", {"findings": "x"}).status_code == 409   # not yet performed
    assert rad.post(f"/api/radiology/{rid}/perform").status_code == 200
    assert d1.put(f"/api/radiology/{rid}/report", {"findings": "x"}).status_code == 403
    assert rad.put(f"/api/radiology/{rid}/report", {"findings": "No acute abnormality.", "impression": "Normal study."}).status_code == 200
    assert rad.post(f"/api/radiology/{rid}/authorize").status_code == 200
    assert rad.post(f"/api/radiology/{rid}/amend", {"findings": "Small nodule.", "impression": "Follow up CT."}).status_code == 400   # reason required
    assert rad.post(f"/api/radiology/{rid}/amend", {"findings": "Small nodule.", "impression": "Follow up CT.", "reason": "Addendum after review"}).status_code == 200
    versions = db.session.execute(select(RadiologyReportVersion).where(RadiologyReportVersion.radiology_id == rid)).scalars().all()
    assert len(versions) >= 3 and {v.status for v in versions} >= {"Final"}


# ---------------------------------------------------------------- billing
def test_billing_payment_refund_rules(as_user, ids):
    bill, admin = as_user("billing"), as_user("admin")
    maya = ids.patient["Maya Rao"]
    bid = bill.post("/api/bills", {"patient_id": maya, "description": "Test bill", "consultation": 100, "laboratory": 50}).json["id"]
    assert bill.post(f"/api/bills/{bid}/payments", {"amount": 500}).status_code == 409        # more than outstanding
    assert bill.post(f"/api/bills/{bid}/payments", {"amount": 0}).status_code == 400
    assert bill.post(f"/api/bills/{bid}/payments", {"amount": 60}).status_code == 200
    assert bill.post(f"/api/bills/{bid}/refunds", {"amount": 10, "reason": "x"}).status_code == 403   # refunds need a higher permission
    assert admin.post(f"/api/bills/{bid}/refunds", {"amount": 500, "reason": "x"}).status_code == 409
    assert admin.post(f"/api/bills/{bid}/refunds", {"amount": 10, "reason": "Duplicate charge"}).status_code == 200
    assert bill.post(f"/api/bills/{bid}/payments", {"amount": 100}).status_code == 200
    detail = bill.get(f"/api/bills/{bid}").json
    assert detail["balance"] == 0 and detail["paid"] is True


def test_clinicians_cannot_see_billing(as_user, ids):
    assert as_user("doctor1").get("/api/bills").status_code == 403


# ---------------------------------------------------------------- notes
def test_notes_are_append_only_with_amendment_chain(as_user, ids):
    d1, d2 = as_user("doctor1"), as_user("doctor2")
    maya = ids.patient["Maya Rao"]
    nid = d1.post(f"/api/patients/{maya}/notes", {"body": "Original plan", "note_type": "Progress"}).json["id"]
    assert d1.patch(f"/api/notes/{nid}", {"body": "silent edit"}).status_code in (404, 405)
    assert d2.post(f"/api/notes/{nid}/amend", {"body": "x", "reason": "y"}).status_code in (403, 404)
    assert d1.post(f"/api/notes/{nid}/amend", {"body": "Corrected plan"}).status_code == 400
    assert d1.post(f"/api/notes/{nid}/amend", {"body": "Corrected plan", "reason": "Wrong dose typed"}).status_code == 200
    old = db.session.get(ClinicalNote, nid)
    assert old.body == "Original plan" and old.status == "Superseded"
    assert d1.post(f"/api/notes/{nid}/amend", {"body": "again", "reason": "again"}).status_code == 409


def test_nurse_cannot_write_physician_note_types(as_user, ids):
    n = as_user("nurse")
    assert n.post(f"/api/patients/{ids.patient['Maya Rao']}/notes", {"body": "x", "note_type": "Discharge summary"}).status_code == 400


# ---------------------------------------------------------------- patient registry
def test_patient_registration_validation_and_duplicate_warning(as_user):
    d1 = as_user("doctor1")
    assert d1.post("/api/patients", {}).status_code == 400
    assert d1.post("/api/patients", {"name": "A"}).status_code == 400
    assert d1.post("/api/patients", {"name": "Future Baby", "dob": "2999-01-01"}).status_code == 400
    ok = d1.post("/api/patients", {"name": "Real Person", "dob": "1990-05-05", "gender": "Female"})
    assert ok.status_code == 200 and ok.json["patient_code"].startswith("P-")
    dup = d1.post("/api/patients", {"name": "Real Person", "dob": "1990-05-05", "gender": "Female"})
    assert dup.status_code in (200, 409)


def test_patient_search_does_not_leak_unrelated_patients(as_user):
    r = as_user("doctor2").get("/api/patients?q=Maya").json
    assert r["items"] == []
