"""Demonstration data. Every record is fictional and marked data_origin='demo'.
Never run against a database holding real patients (the CLI refuses unless explicitly forced)."""
from __future__ import annotations

import os
from datetime import date, timedelta

from sqlalchemy import select

from . import constants as C
from .api.auth import demo_password
from .api.patients import next_patient_code
from .audit import audit
from .extensions import db
from .models import (Alert, AlertRule, Allergy, AppUser, Bed, Bill, Department, Doctor, Encounter, LabReport, LabResult, Medicine, Patient,
                     PatientAssignment, Prescription, Problem, RadiologyRecord, RadiologyReportVersion, Room, Ward, ClinicalNote, CareTask, utcnow)
from .security import hash_password
from .services import beds as bedsvc
from .services import monitoring, orders as osvc

DOMAIN = "careflow.demo.example"


def seeded() -> bool:
    return db.session.execute(select(AppUser.id).where(AppUser.is_demo.is_(True)).limit(1)).first() is not None


def run() -> dict:
    monitoring.ensure_reference_data()
    now = utcnow()
    today = date.today()
    pw = hash_password(demo_password())

    gm, sg, cc = (Department(name=n) for n in ("General Medicine", "Surgery", "Critical Care"))
    for d in (gm, sg, cc):
        if db.session.execute(select(Department.id).where(Department.name == d.name)).first() is None:
            db.session.add(d)
    db.session.flush()
    dep = {d.name: d for d in db.session.execute(select(Department)).scalars()}
    wards = {}
    for name, dept, spec, rate, nbeds in (("Ward A", "General Medicine", "General medicine", 120.0, 6), ("ICU", "Critical Care", "Intensive care", 480.0, 2)):
        w = db.session.execute(select(Ward).where(Ward.name == name)).scalar_one_or_none()
        if w is None:
            w = Ward(name=name, department_id=dep[dept].id, specialty=spec, daily_rate=rate)
            db.session.add(w)
            db.session.flush()
            for ri in range(1, (nbeds + 1) // 2 + 1):
                room = Room(ward_id=w.id, label=f"{name[-1]}{ri}")
                db.session.add(room)
                db.session.flush()
                for bi in (1, 2):
                    if (ri - 1) * 2 + bi <= nbeds:
                        db.session.add(Bed(room_id=room.id, ward_id=w.id, label=f"Bed {bi}", code=f"{name.replace(' ', '')}-{room.label}-{bi}"))
        wards[name] = w
    db.session.flush()

    docs = [Doctor(name="Dr. Asha Verma", specialty="Internal Medicine", department="General Medicine", registration_no="REG-001"),
            Doctor(name="Dr. Kenji Mori", specialty="Critical Care", department="Critical Care", registration_no="REG-002")]
    db.session.add_all(docs)
    db.session.flush()
    spec = [("super", "Sam Root", C.SUPER_ADMIN, None, None), ("admin", "Hana Admin", C.HOSPITAL_ADMIN, None, None),
            ("doctor1", docs[0].name, C.DOCTOR, docs[0].id, None), ("doctor2", docs[1].name, C.DOCTOR, docs[1].id, None),
            ("nurse", "Nora Nurse", C.NURSE, None, wards["Ward A"].id), ("icunurse", "Ivy ICU Nurse", C.NURSE, None, wards["ICU"].id),
            ("lab", "Leo Lab", C.LAB_STAFF, None, None), ("pharmacist", "Priya Pharm", C.PHARMACIST, None, None),
            ("radiology", "Rae Radiology", C.RADIOLOGY_STAFF, None, None), ("billing", "Bill Billing", C.BILLING_STAFF, None, None)]
    users = {}
    for key, name, role, did, wid in spec:
        u = AppUser(email=f"{key}@{DOMAIN}", name=name, role=role, doctor_id=did, ward_id=wid, password_hash=pw, is_demo=True, must_change_password=False, password_changed_at=now)
        db.session.add(u)
        users[key] = u
    db.session.flush()

    meds = [("Paracetamol 500 mg", "Paracetamol", "500 mg", "Tablet", 400, 80, 0.05), ("Amoxicillin 500 mg", "Amoxicillin", "500 mg", "Capsule", 150, 60, 0.4),
            ("Metformin 500 mg", "Metformin", "500 mg", "Tablet", 300, 60, 0.1), ("Furosemide 40 mg", "Furosemide", "40 mg", "Tablet", 8, 40, 0.2),
            ("Warfarin 5 mg", "Warfarin", "5 mg", "Tablet", 120, 30, 0.3), ("Aspirin 75 mg", "Aspirin", "75 mg", "Tablet", 200, 50, 0.04)]
    mrow = {}
    for name, gen, st, form, stock, rl, price in meds:
        m = db.session.execute(select(Medicine).where(Medicine.name == name)).scalar_one_or_none()
        if m is None:
            m = Medicine(name=name, generic_name=gen, strength=st, form=form, stock=stock, reorder_level=rl, unit_price=price, expiry_date=(today + timedelta(days=300)).isoformat(), batch_no="DEMO-B1")
            db.session.add(m)
        mrow[name] = m
    db.session.flush()

    # Alert rules are CONFIGURED SAMPLES awaiting clinical review - not clinical standards.
    for name, code, op, thr, sev in (("Sample: SpO2 below configured limit", "spo2", "<", 92, "Critical"), ("Sample: Heart rate above configured limit", "heart_rate", ">", 130, "Warning"),
                                      ("Sample: Systolic BP below configured limit", "bp_systolic", "<", 90, "Critical")):
        if db.session.execute(select(AlertRule.id).where(AlertRule.name == name)).first() is None:
            db.session.add(AlertRule(name=name, description="Demonstration threshold. Requires clinical review before real use.", type_code=code, operator=op, threshold=thr, severity=sev, review_status="Unreviewed"))
    if db.session.execute(select(AlertRule.id).where(AlertRule.rule_kind == "missing")).first() is None:
        db.session.add(AlertRule(name="Sample: observations overdue", rule_kind="missing", window_minutes=240, severity="Warning", description="Demonstration data-freshness rule.", review_status="Unreviewed"))
    db.session.flush()

    people = [("Maya Rao", "1958-03-14", "Female", "O+", "Penicillin", "Pneumonia, community-acquired", "Ward A", docs[0], "nurse"),
              ("Tomas Ek", "1971-09-02", "Male", "A+", "", "Type 2 diabetes mellitus", "Ward A", docs[0], "nurse"),
              ("Lina Okafor", "1989-12-21", "Female", "B+", "Sulfonamides", "Post-operative monitoring", "ICU", docs[1], "icunurse"),
              ("Ravi Menon", "1946-06-30", "Male", "AB-", "", "Congestive heart failure", "ICU", docs[1], "icunurse"),
              ("Zoe Hart", "2001-02-11", "Female", "O-", "", "", None, docs[0], None)]
    created = []
    for i, (name, dob, sex, bg, allergy, prob, ward, doc, nurse) in enumerate(people):
        p = Patient(patient_code=next_patient_code(), name=name, dob=dob, gender=sex, blood_group=bg, data_origin="demo", phone="000-000-0000", consent_data_sharing=False, allergies="")
        db.session.add(p)
        db.session.flush()
        if allergy:
            db.session.add(Allergy(patient_id=p.id, substance=allergy, reaction="Rash", severity="Moderate", recorded_by_id=users["doctor1"].id))
        if prob:
            db.session.add(Problem(patient_id=p.id, description=prob, status="Active", onset_on=(today - timedelta(days=30 + i)).isoformat(), recorded_by_id=users["doctor1"].id))
        for dkey in ("doctor1" if doc is docs[0] else "doctor2",):
            db.session.add(PatientAssignment(patient_id=p.id, user_id=users[dkey].id, relation="primary", created_by_id=users["admin"].id))
        if nurse:
            db.session.add(PatientAssignment(patient_id=p.id, user_id=users[nurse].id, relation="primary", created_by_id=users["admin"].id))
        created.append(p)
    db.session.flush()

    free = {w: [b for b in db.session.execute(select(Bed).where(Bed.ward_id == wards[w].id, Bed.status == "Available").order_by(Bed.code)).scalars()] for w in wards}
    for p, (name, dob, sex, bg, allergy, prob, ward, doc, nurse) in zip(created, people):
        if not ward:
            continue
        bed = free[ward].pop(0)
        adm = bedsvc.admit(p, user=users["doctor1"], bed_id=bed.id, doctor_id=doc.id, reason=prob or "Observation", admitted_on=(today - timedelta(days=2)).isoformat())
        db.session.add(ClinicalNote(patient_id=p.id, admission_id=adm.id, encounter_id=adm.encounter_id, author_id=users["doctor1"].id, note_type="Admission",
                                    body=f"Admission note: {prob}. Plan recorded by treating team.", status="Final"))
        db.session.add(CareTask(patient_id=p.id, admission_id=adm.id, title="Repeat observations", category="Observation", assigned_role="nurse", due_at=now - timedelta(minutes=20), created_by_id=users["doctor1"].id))
    db.session.flush()

    # Demo vitals (provenance: simulated). One deliberately low SpO2 to exercise the alert workflow.
    plan = {created[0]: dict(heart_rate=92, bp_systolic=128, bp_diastolic=78, resp_rate=18, spo2=95, temperature=37.8),
            created[2]: dict(heart_rate=88, bp_systolic=118, bp_diastolic=70, resp_rate=16, spo2=98, temperature=36.9),
            created[3]: dict(heart_rate=104, bp_systolic=108, bp_diastolic=64, resp_rate=22, spo2=89, temperature=36.7)}
    for p, vals in plan.items():
        for k, v in vals.items():
            monitoring.record_observation(p, k, v, source="simulated", observed_at=now - timedelta(minutes=12), note="demo data")
    db.session.flush()

    # Released lab with a critical value, a pending lab, a final radiology report, orders and a bill.
    def lab(p, test, results, status="Released", ordered_by=users["doctor1"]):
        rep = LabReport(patient_id=p.id, test_name=test, sample_date=today.isoformat(), status=status, ordered_by=ordered_by.name, ordered_by_id=ordered_by.id, accession_no=osvc.next_accession(),
                        ordered_at=now - timedelta(hours=6), collected_at=now - timedelta(hours=5), received_at=now - timedelta(hours=5))
        db.session.add(rep)
        db.session.flush()
        crit = False
        for analyte, val, unit, lo, hi, cl, ch in results:
            flag, is_crit = osvc.compute_flag(val, lo, hi, cl, ch)
            db.session.add(LabResult(lab_report_id=rep.id, analyte=analyte, value_num=val, unit=unit, ref_low=lo, ref_high=hi, critical_low=cl, critical_high=ch, flag=flag,
                                     is_critical=is_crit, status="Final", entered_by_id=users["lab"].id))
            crit = crit or is_crit
        if status == "Released":
            rep.resulted_at = rep.verified_at = rep.released_at = now - timedelta(hours=1)
            rep.resulted_by_id = rep.verified_by_id = rep.released_by_id = users["lab"].id
            rep.result = "; ".join(f"{a}: {v:g} {u}" for a, v, u, *_ in results)
        db.session.flush()
        if crit:
            osvc.notify_critical("lab", rep.id, p.id, f"{test}: critical value", ordered_by.id)
        return rep
    lab(created[0], "Complete blood count", [("Haemoglobin", 11.2, "g/dL", 12.0, 15.5, 7.0, 20.0), ("White cell count", 14.8, "x10^9/L", 4.0, 11.0, 2.0, 30.0)])
    lab(created[3], "Basic metabolic panel", [("Potassium", 6.7, "mmol/L", 3.5, 5.1, 2.8, 6.2), ("Creatinine", 1.6, "mg/dL", 0.6, 1.2, None, None)])
    db.session.add(LabReport(patient_id=created[1].id, test_name="HbA1c", sample_date=today.isoformat(), status="Ordered", ordered_by=users["doctor1"].name, ordered_by_id=users["doctor1"].id,
                             accession_no=osvc.next_accession(), ordered_at=now - timedelta(hours=1)))

    rr = RadiologyRecord(patient_id=created[0].id, modality="X-ray", study_date=today.isoformat(), study_description="Chest, PA", indication="Cough and fever", ordered_by_id=users["doctor1"].id,
                         order_status="Final", report_status="Final", findings="Report: patchy opacity in the right lower zone.", impression="Appearances may represent consolidation. Clinical correlation advised.",
                         performed_at=now - timedelta(hours=8), performed_by_id=users["radiology"].id, reported_at=now - timedelta(hours=7), reported_by_id=users["radiology"].id,
                         authorized_at=now - timedelta(hours=7), authorized_by_id=users["radiology"].id)
    db.session.add(rr)
    db.session.flush()
    db.session.add(RadiologyReportVersion(radiology_id=rr.id, version=1, findings=rr.findings, impression=rr.impression, status="Final", author_id=users["radiology"].id))

    for p, med, dose, freq, did in ((created[0], "Amoxicillin 500 mg", "500 mg", "Three times daily", "doctor1"), (created[1], "Metformin 500 mg", "500 mg", "Twice daily", "doctor1")):
        m = mrow[med]
        db.session.add(Prescription(patient_id=p.id, doctor_name=users[did].name, medicine=m.name, medicine_id=m.id, dosage=dose, route="Oral", frequency=freq, status="Ordered",
                                    ordered_by_id=users[did].id, quantity=21, duration_days=7))
    b = Bill(patient_id=created[0].id, description="Inpatient bill", consultation=150.0, laboratory=80.0, pharmacy=35.5, room=240.0, status="Issued", created_by_id=users["billing"].id)
    db.session.add(b)
    db.session.flush()
    # A demonstration patient portal login (read-only) for the first demo patient, plus tracked hand-over items.
    db.session.add(AppUser(email=f"patient1@{DOMAIN}", name=created[0].name, role=C.PATIENT, patient_id=created[0].id, password_hash=pw, is_demo=True,
                           must_change_password=False, password_changed_at=now))
    from .services import deliverables as dsvc
    for lr in db.session.execute(select(LabReport).where(LabReport.patient_id == created[0].id, LabReport.status == "Released")).scalars():
        dsvc.ensure(created[0].id, "Laboratory report", f"{lr.test_name} ({lr.sample_date})", "lab", lr.id, digital=True, created_by_id=users["lab"].id).physical_status = "Ready for collection"
    dsvc.ensure(created[0].id, "Radiology report", "X-ray Chest, PA", "radiology", rr.id, digital=True, created_by_id=users["radiology"].id)
    dsvc.ensure(created[0].id, "Invoice / receipt", b.description, "bill", b.id, digital=True, created_by_id=users["billing"].id)
    audit("seed.demo", category="admin", details="demonstration data loaded", user=users["super"])
    db.session.commit()
    return {"users": len(users), "patients": len(created), "wards": len(wards)}
