"""Additional sample records: a larger set of patients (including one named Pooja Shree), staff, wards,
admissions, lab and radiology results, prescriptions, bills, payments, appointments and hand-over items.
Idempotent: running it twice does nothing the second time. Requires `seed-demo` to have been run first."""
from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy import select

from . import constants as C
from .api.auth import demo_password
from .api.patients import next_patient_code
from .audit import audit
from .extensions import db
from .models import (Allergy, Appointment, AppUser, Bed, Bill, ClinicalNote, Department, Doctor, LabReport, LabResult, Medicine, Patient,
                     PatientAssignment, Payment, Prescription, Problem, RadiologyRecord, RadiologyReportVersion, Room, Ward, utcnow)
from .security import hash_password
from .services import beds as bedsvc
from .services import deliverables as dsvc
from .services import monitoring, orders as osvc
from .seed import DOMAIN

MARKER_NAME = "Pooja Shree"

EXTRA_DOCTORS = [("Dr. Meera Iyer", "Cardiology", "Cardiology", "REG-003", "doctor3"), ("Dr. Arjun Nair", "Orthopaedics", "Surgery", "REG-004", "doctor4"),
                 ("Dr. Fatima Sheikh", "Paediatrics", "Paediatrics", "REG-005", "doctor5"), ("Dr. Rohan Das", "General Surgery", "Surgery", "REG-006", "doctor6"),
                 ("Dr. Sunita Rao", "Obstetrics and Gynaecology", "Maternity", "REG-007", "doctor7")]
EXTRA_NURSES = [("nurse2", "Kavya Menon"), ("nurse3", "Anita Joseph"), ("nurse4", "Deepa Nambiar")]
EXTRA_WARDS = [("Ward B", "General Medicine", "General medicine", 140.0, 8), ("Cardiac Care", "Cardiology", "Cardiology", 300.0, 4), ("Surgical Ward", "Surgery", "Surgery", 180.0, 6)]

# (name, dob, sex, blood, allergy, problem, ward or None)
PATIENTS = [
    ("Pooja Shree", "1994-05-17", "Female", "B+", "Penicillin", "Migraine with aura", "Ward B"),
    ("Ishita Sharma", "1988-11-03", "Female", "O+", "", "Hypothyroidism", "Ward B"),
    ("Keerthi Nair", "2000-07-25", "Female", "A+", "", "Iron-deficiency anaemia", None),
    ("Janaki Iyer", "1976-02-09", "Female", "AB+", "Aspirin", "Type 2 diabetes mellitus", "Ward A"),
    ("Riya Patel", "1999-09-30", "Female", "B-", "", "Acute appendicitis", "Surgical Ward"),
    ("Sravani Reddy", "1983-12-12", "Female", "O-", "", "Hypertension", None),
    ("Nithya Menon", "1965-04-21", "Female", "A-", "Sulfonamides", "Unstable angina", "Cardiac Care"),
    ("Aarav Mehta", "2015-03-08", "Male", "B+", "", "Bronchiolitis", None), ("Diya Kapoor", "2018-10-19", "Female", "A+", "Peanuts", "Asthma", None),
    ("Arjun Pillai", "1979-01-28", "Male", "O+", "", "Fractured tibia", "Surgical Ward"), ("Sneha Gupta", "1992-06-14", "Female", "AB-", "", "Gestational diabetes", None),
    ("Rahul Verma", "1969-08-05", "Male", "B+", "", "Coronary artery disease", "Cardiac Care"), ("Ananya Das", "1996-02-27", "Female", "O+", "", "Urinary tract infection", None),
    ("Vikram Singh", "1955-11-16", "Male", "A+", "Penicillin", "COPD exacerbation", "Ward A"), ("Kavita Joshi", "1973-05-02", "Female", "B+", "", "Osteoarthritis, knee", None),
    ("Mohammed Rafiq", "1962-09-09", "Male", "O+", "", "Chronic kidney disease", "Ward B"), ("Lakshmi Narayanan", "1950-12-24", "Female", "A-", "", "Heart failure", "Cardiac Care"),
    ("Suresh Babu", "1958-07-07", "Male", "B-", "", "Stroke, rehabilitation", "Ward B"), ("Nisha Thomas", "1990-01-15", "Female", "O+", "Latex", "Cholelithiasis", "Surgical Ward"),
    ("Karthik Subramanian", "1985-10-10", "Male", "A+", "", "Dengue fever", "Ward A"), ("Fatima Noor", "1978-03-31", "Female", "AB+", "", "Pre-eclampsia", None),
    ("Rohit Malhotra", "1994-12-01", "Male", "O-", "", "Road traffic injury", "Surgical Ward"), ("Priyanka Chopra", "1987-04-18", "Female", "B+", "", "Pneumonia", "Ward A"),
    ("Imran Khan", "1974-06-22", "Male", "A+", "", "Type 2 diabetes mellitus", None), ("Meenakshi Sundaram", "1948-08-13", "Female", "O+", "Codeine", "Hip fracture", "Surgical Ward"),
    ("Gautham Raj", "2002-11-29", "Male", "B+", "", "Tonsillitis", None), ("Harini Venkat", "1997-09-04", "Female", "A+", "", "Gastroenteritis", "Ward B"),
    ("Anil Kumar", "1960-02-17", "Male", "O+", "", "Hypertension", None), ("Shreya Ghoshal", "1991-05-26", "Female", "AB+", "", "Anxiety disorder", None),
    ("Deepak Chawla", "1968-10-03", "Male", "B+", "", "Peptic ulcer disease", "Ward A"), ("Revathi Krishnan", "1953-01-20", "Female", "A+", "", "Atrial fibrillation", "Cardiac Care"),
    ("Naveen Prasad", "1989-07-12", "Male", "O+", "", "Hernia repair", "Surgical Ward"), ("Zainab Qureshi", "1981-03-05", "Female", "B-", "", "Thyroid nodule", None),
    ("Balaji Murthy", "1972-12-30", "Male", "A+", "", "Sleep apnoea", None), ("Tara Fernandes", "2010-04-09", "Female", "O+", "", "Appendicectomy follow-up", None),
    ("Siddharth Rao", "1984-08-21", "Male", "AB-", "", "Lower back pain", None), ("Isha Bhatt", "1995-06-06", "Female", "B+", "", "Polycystic ovary syndrome", None),
    ("Ramesh Iyengar", "1945-05-11", "Male", "A+", "", "Prostate enlargement", "Ward B"), ("Jaya Prakash", "1967-09-18", "Female", "O+", "", "Rheumatoid arthritis", None),
    ("Omar Farooq", "1993-02-02", "Male", "B+", "", "Cellulitis", "Ward A"), ("Lalitha Devi", "1957-11-07", "Female", "A+", "", "Chronic kidney disease", None),
]
TESTS = [("Complete blood count", [("Haemoglobin", "g/dL", 12.0, 15.5, 7.0, 20.0), ("White cell count", "x10^9/L", 4.0, 11.0, 2.0, 30.0), ("Platelets", "x10^9/L", 150, 400, 20, 1000)]),
         ("Lipid profile", [("Total cholesterol", "mg/dL", 0, 200, None, None), ("LDL cholesterol", "mg/dL", 0, 130, None, None), ("HDL cholesterol", "mg/dL", 40, 90, None, None)]),
         ("Liver function", [("ALT", "U/L", 7, 40, None, None), ("AST", "U/L", 10, 40, None, None), ("Bilirubin", "mg/dL", 0.1, 1.2, None, 15.0)]),
         ("Thyroid panel", [("TSH", "mIU/L", 0.4, 4.0, None, None), ("Free T4", "ng/dL", 0.8, 1.8, None, None)]),
         ("Blood glucose", [("Fasting glucose", "mg/dL", 70, 100, 40, 500)]), ("Renal function", [("Creatinine", "mg/dL", 0.6, 1.2, None, None), ("Urea", "mg/dL", 15, 40, None, None)])]
IMAGING = [("X-ray", "Chest, PA", "Lungs are clear. No acute abnormality.", "No acute cardiopulmonary abnormality."), ("Ultrasound", "Abdomen", "Normal liver echotexture. No free fluid.", "Normal abdominal ultrasound."),
           ("CT", "Head, plain", "No intracranial haemorrhage or mass effect.", "No acute intracranial abnormality."), ("MRI", "Lumbar spine", "Mild disc bulge at L4-L5 without cord compression.", "Mild degenerative change."),
           ("X-ray", "Knee, AP/lateral", "Reduced joint space medially with small osteophytes.", "Features of osteoarthritis.")]
RX = [("Paracetamol 500 mg", "500 mg", "Three times daily", 15, 5), ("Amoxicillin 500 mg", "500 mg", "Three times daily", 21, 7), ("Metformin 500 mg", "500 mg", "Twice daily", 60, 30),
      ("Aspirin 75 mg", "75 mg", "Once daily", 30, 30), ("Furosemide 40 mg", "40 mg", "Once daily", 14, 14)]
EXTRA_MEDS = [("Atorvastatin 20 mg", "Atorvastatin", "20 mg", "Tablet", 250, 50, 0.15), ("Pantoprazole 40 mg", "Pantoprazole", "40 mg", "Tablet", 300, 60, 0.12),
              ("Levothyroxine 50 mcg", "Levothyroxine", "50 mcg", "Tablet", 200, 40, 0.08), ("Salbutamol inhaler", "Salbutamol", "100 mcg", "Inhaler", 80, 20, 3.5),
              ("Amlodipine 5 mg", "Amlodipine", "5 mg", "Tablet", 260, 50, 0.07), ("Ibuprofen 400 mg", "Ibuprofen", "400 mg", "Tablet", 320, 60, 0.06)]


def already_added() -> bool:
    return db.session.execute(select(Patient.id).where(Patient.name == MARKER_NAME)).first() is not None


def run() -> dict:
    rng = random.Random(2026)
    now = utcnow()
    today = date.today()
    pw = hash_password(demo_password())
    admin = db.session.execute(select(AppUser).where(AppUser.email == f"admin@{DOMAIN}")).scalar_one_or_none()
    if admin is None:
        raise RuntimeError("Run `seed-demo` first; the base staff accounts are missing.")
    lab_u = db.session.execute(select(AppUser).where(AppUser.email == f"lab@{DOMAIN}")).scalar_one()
    rad_u = db.session.execute(select(AppUser).where(AppUser.email == f"radiology@{DOMAIN}")).scalar_one()
    bill_u = db.session.execute(select(AppUser).where(AppUser.email == f"billing@{DOMAIN}")).scalar_one()

    # Departments and wards
    for dname in {w[1] for w in EXTRA_WARDS} | {d[2] for d in EXTRA_DOCTORS}:
        if db.session.execute(select(Department.id).where(Department.name == dname)).first() is None:
            db.session.add(Department(name=dname))
    db.session.flush()
    dep = {d.name: d for d in db.session.execute(select(Department)).scalars()}
    wards = {w.name: w for w in db.session.execute(select(Ward)).scalars()}
    for name, dept, spec, rate, nbeds in EXTRA_WARDS:
        if name in wards:
            continue
        w = Ward(name=name, department_id=dep[dept].id, specialty=spec, daily_rate=rate)
        db.session.add(w)
        db.session.flush()
        for ri in range(1, (nbeds + 1) // 2 + 1):
            room = Room(ward_id=w.id, label=f"{name.split()[0][0]}{ri}")
            db.session.add(room)
            db.session.flush()
            for bi in (1, 2):
                if (ri - 1) * 2 + bi <= nbeds:
                    db.session.add(Bed(room_id=room.id, ward_id=w.id, label=f"Bed {bi}", code=f"{name.replace(' ', '')}-{room.label}-{bi}"))
        wards[name] = w
    db.session.flush()

    # Staff
    doctors = list(db.session.execute(select(Doctor)).scalars())
    users = {}
    for name, spec, dept, reg, key in EXTRA_DOCTORS:
        d = next((x for x in doctors if x.registration_no == reg), None)
        if d is None:
            d = Doctor(name=name, specialty=spec, department=dept, registration_no=reg)
            db.session.add(d)
            db.session.flush()
            doctors.append(d)
        u = AppUser(email=f"{key}@{DOMAIN}", name=name, role=C.DOCTOR, doctor_id=d.id, password_hash=pw, is_demo=True, must_change_password=False, password_changed_at=now)
        if db.session.execute(select(AppUser.id).where(AppUser.email == u.email)).first() is None:
            db.session.add(u)
    ward_cycle = ["Ward B", "Cardiac Care", "Surgical Ward", "Ward A"]
    for i, (key, name) in enumerate(EXTRA_NURSES):
        email = f"{key}@{DOMAIN}"
        if db.session.execute(select(AppUser.id).where(AppUser.email == email)).first() is None:
            db.session.add(AppUser(email=email, name=name, role=C.NURSE, ward_id=wards[ward_cycle[i]].id, password_hash=pw, is_demo=True, must_change_password=False, password_changed_at=now))
    db.session.flush()
    doctor_users = {u.doctor_id: u for u in db.session.execute(select(AppUser).where(AppUser.role == C.DOCTOR)).scalars()}
    nurse_by_ward = {u.ward_id: u for u in db.session.execute(select(AppUser).where(AppUser.role == C.NURSE)).scalars()}

    meds = {m.name: m for m in db.session.execute(select(Medicine)).scalars()}
    for name, gen, st, form, stock, rl, price in EXTRA_MEDS:
        if name not in meds:
            m = Medicine(name=name, generic_name=gen, strength=st, form=form, stock=stock, reorder_level=rl, unit_price=price, expiry_date=(today + timedelta(days=360)).isoformat(), batch_no="B-2026")
            db.session.add(m)
            meds[name] = m
    db.session.flush()

    spec_doc = {"Cardiac Care": "Cardiology", "Surgical Ward": "Surgery", "Ward A": "General Medicine", "Ward B": "General Medicine"}
    created, portal_logins = [], []
    slots = set()
    for idx, (name, dob, sex, bg, allergy, prob, ward) in enumerate(PATIENTS):
        p = Patient(patient_code=next_patient_code(), name=name, dob=dob, gender=sex, blood_group=bg, data_origin="demo",
                    phone=f"98{rng.randint(10000000, 99999999)}", address=rng.choice(["Anna Nagar, Chennai", "T. Nagar, Chennai", "Indiranagar, Bengaluru", "Kochi", "Hyderabad", "Coimbatore", "Mysuru", "Madurai"]),
                    consent_data_sharing=False, allergies="")
        db.session.add(p)
        db.session.flush()
        created.append(p)
        pool = [d for d in doctors if d.department == spec_doc.get(ward or "", "General Medicine")] or doctors
        doc = pool[idx % len(pool)]
        duser = doctor_users.get(doc.id)
        if allergy:
            db.session.add(Allergy(patient_id=p.id, substance=allergy, reaction=rng.choice(["Rash", "Hives", "Swelling"]), severity=rng.choice(["Mild", "Moderate"]), recorded_by_id=(duser or admin).id))
        db.session.add(Problem(patient_id=p.id, description=prob, status="Active", onset_on=(today - timedelta(days=rng.randint(5, 400))).isoformat(), recorded_by_id=(duser or admin).id))
        if duser:
            db.session.add(PatientAssignment(patient_id=p.id, user_id=duser.id, relation="primary", created_by_id=admin.id))
        nurse = nurse_by_ward.get(wards[ward].id) if ward else None
        if nurse:
            db.session.add(PatientAssignment(patient_id=p.id, user_id=nurse.id, relation="primary", created_by_id=admin.id))
        # Appointment (unique slot per doctor/day)
        for _ in range(20):
            day = (today + timedelta(days=rng.randint(-10, 14))).isoformat()
            tm = f"{rng.randint(9, 16):02d}:{rng.choice(['00', '15', '30', '45'])}"
            if (doc.id, day, tm) not in slots:
                slots.add((doc.id, day, tm))
                past = day < today.isoformat()
                db.session.add(Appointment(patient_id=p.id, doctor_id=doc.id, appointment_date=day, appointment_time=tm, reason=prob,
                                           status="Completed" if past else "Scheduled", visit_type=rng.choice(["Consultation", "Follow-up", "Review"]), created_by_id=admin.id))
                break
        # Admission
        adm = None
        if ward:
            free = db.session.execute(select(Bed).where(Bed.ward_id == wards[ward].id, Bed.status == "Available").order_by(Bed.code)).scalars().first()
            if free:
                adm = bedsvc.admit(p, user=duser or admin, bed_id=free.id, doctor_id=doc.id, reason=prob, admitted_on=(today - timedelta(days=rng.randint(1, 5))).isoformat())
                db.session.add(ClinicalNote(patient_id=p.id, admission_id=adm.id, encounter_id=adm.encounter_id, author_id=(duser or admin).id, note_type="Admission",
                                            body=f"Admitted with {prob.lower()}. Treatment plan agreed with the patient.", status="Final"))
                monitoring.record_observation(p, "heart_rate", rng.randint(66, 105), source="simulated", observed_at=now - timedelta(minutes=rng.randint(5, 90)), note="")
                monitoring.record_observation(p, "spo2", rng.randint(94, 99), source="simulated", observed_at=now - timedelta(minutes=rng.randint(5, 90)), note="")
                monitoring.record_observation(p, "temperature", round(rng.uniform(36.4, 38.2), 1), source="simulated", observed_at=now - timedelta(minutes=rng.randint(5, 90)), note="")
        # Labs: released for most, a few still pending
        lab_total = 0.0
        for test, analytes in rng.sample(TESTS, rng.randint(1, 2)):
            pending = rng.random() < 0.2
            rep = LabReport(patient_id=p.id, test_name=test, sample_date=(today - timedelta(days=rng.randint(0, 6))).isoformat(), status="Ordered" if pending else "Released",
                            ordered_by=(duser or admin).name, ordered_by_id=(duser or admin).id, accession_no=osvc.next_accession(), ordered_at=now - timedelta(hours=rng.randint(2, 70)))
            db.session.add(rep)
            db.session.flush()
            lab_total += 25.0
            if pending:
                continue
            summary = []
            for analyte, unit, lo, hi, cl, ch in analytes:
                val = round(rng.uniform(lo * 0.85 if lo else 0, hi * 1.25), 1)
                flag, is_crit = osvc.compute_flag(val, lo, hi, cl, ch)
                db.session.add(LabResult(lab_report_id=rep.id, analyte=analyte, value_num=val, unit=unit, ref_low=lo, ref_high=hi, critical_low=cl, critical_high=ch, flag=flag,
                                         is_critical=is_crit, status="Final", entered_by_id=lab_u.id))
                summary.append(f"{analyte}: {val:g} {unit}")
            rep.resulted_at = rep.verified_at = rep.released_at = now - timedelta(hours=rng.randint(1, 30))
            rep.resulted_by_id = rep.verified_by_id = rep.released_by_id = lab_u.id
            rep.result = "; ".join(summary)
            db.session.flush()
            dsvc.ensure(p.id, "Laboratory report", f"{rep.test_name} ({rep.sample_date})", "lab", rep.id, digital=True, created_by_id=lab_u.id).physical_status = rng.choice(["Ready for collection", "Requested", "Handed over", "Not requested"])
        # Radiology for about half
        if idx % 2 == 0:
            mod, desc, findings, impression = IMAGING[idx % len(IMAGING)]
            rr = RadiologyRecord(patient_id=p.id, modality=mod, study_date=(today - timedelta(days=rng.randint(0, 5))).isoformat(), study_description=desc, indication=prob,
                                 ordered_by_id=(duser or admin).id, order_status="Final", report_status="Final", findings=findings, impression=impression,
                                 performed_at=now - timedelta(hours=10), performed_by_id=rad_u.id, reported_at=now - timedelta(hours=8), reported_by_id=rad_u.id,
                                 authorized_at=now - timedelta(hours=8), authorized_by_id=rad_u.id)
            db.session.add(rr)
            db.session.flush()
            db.session.add(RadiologyReportVersion(radiology_id=rr.id, version=1, findings=findings, impression=impression, status="Final", author_id=rad_u.id))
            dsvc.ensure(p.id, "Radiology report", f"{mod} {desc}", "radiology", rr.id, digital=True, created_by_id=rad_u.id)
        # Prescription
        med, dose, freq, qty, days = rng.choice(RX)
        m = meds[med]
        db.session.add(Prescription(patient_id=p.id, doctor_name=(duser or admin).name, medicine=m.name, medicine_id=m.id, dosage=dose, route="Oral", frequency=freq, status="Ordered",
                                    ordered_by_id=(duser or admin).id, quantity=qty, duration_days=days))
        # Bill and payments
        cons = float(rng.choice([150, 200, 250, 300]))
        room = round(wards[ward].daily_rate * rng.randint(1, 4), 2) if ward else 0.0
        b = Bill(patient_id=p.id, description="Inpatient bill" if ward else "Outpatient bill", consultation=cons, laboratory=lab_total, pharmacy=round(rng.uniform(20, 120), 2), room=room,
                 status="Issued", created_by_id=bill_u.id, admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None)
        db.session.add(b)
        db.session.flush()
        total = cons + lab_total + b.pharmacy + room
        r = rng.random()
        if r < 0.45:
            db.session.add(Payment(bill_id=b.id, kind="Payment", amount=round(total, 2), method=rng.choice(["Cash", "Card", "UPI"]), reference=f"RCPT-{b.id:05d}", received_by_id=bill_u.id))
        elif r < 0.75:
            db.session.add(Payment(bill_id=b.id, kind="Payment", amount=round(total * 0.5, 2), method=rng.choice(["Cash", "Card", "UPI"]), reference=f"RCPT-{b.id:05d}", received_by_id=bill_u.id))
        db.session.flush()
        osvc.refresh_bill_status(b)
        dsvc.ensure(p.id, "Invoice / receipt", b.description, "bill", b.id, digital=True, created_by_id=bill_u.id)
        # Portal logins for the first three patients in the list
        if idx < 3:
            email = f"patient{len(portal_logins) + 2}@{DOMAIN}"
            db.session.add(AppUser(email=email, name=name, role=C.PATIENT, patient_id=p.id, password_hash=pw, is_demo=True, must_change_password=False, password_changed_at=now))
            portal_logins.append((email, name))
    audit("seed.sample_patients", category="admin", details=f"{len(created)} additional sample patients loaded", user=admin)
    db.session.commit()
    return {"patients": len(created), "portal_logins": portal_logins}
