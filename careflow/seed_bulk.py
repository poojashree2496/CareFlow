"""Bulk sample records: many patients with individual details (age, contact, address, emergency contact, insurance,
history) and matching care records. Each run adds `count` new patients; running again adds more.
Also fills missing contact details on the earlier sample patients."""
from __future__ import annotations

import random
from datetime import date, timedelta

from sqlalchemy import func, select

from . import constants as C
from .api.auth import demo_password
from .api.patients import next_patient_code
from .audit import audit
from .extensions import db
from .models import (Allergy, Appointment, AppUser, Bed, Bill, ClinicalNote, Department, Doctor, LabReport, LabResult, Medicine, Patient,
                     PatientAssignment, Payment, Prescription, Problem, RadiologyRecord, RadiologyReportVersion, Room, Ward, utcnow)
from .seed import DOMAIN
from .seed_more import EXTRA_MEDS, IMAGING, RX, TESTS
from .services import beds as bedsvc
from .services import deliverables as dsvc
from .services import monitoring, orders as osvc

FEMALE = ["Aditi", "Aishwarya", "Akshara", "Amrutha", "Anjali", "Ankita", "Archana", "Bhavana", "Chitra", "Deepika", "Divya", "Gayathri", "Hema", "Indu", "Janani",
          "Kalpana", "Keerthana", "Lavanya", "Madhavi", "Mythili", "Nandini", "Neha", "Padma", "Pavithra", "Prerna", "Rekha", "Saranya", "Sowmya", "Swathi",
          "Tanvi", "Uma", "Vaishnavi", "Vidya", "Yamini", "Aisha", "Zara", "Sana", "Maria", "Priya", "Sangeetha", "Radhika", "Shobana", "Anitha", "Geetha", "Malini"]
MALE = ["Abhishek", "Adithya", "Ajay", "Akash", "Aravind", "Ashwin", "Bharath", "Chandran", "Dinesh", "Ganesh", "Gokul", "Harish", "Jagan", "Kiran", "Lokesh",
        "Manoj", "Mukesh", "Nikhil", "Pranav", "Prakash", "Rajesh", "Sanjay", "Sathish", "Srinivas", "Tarun", "Varun", "Vignesh", "Yash", "Zaheer", "Imran",
        "Faisal", "Joseph", "Thomas", "Daniel", "Arun", "Vijay", "Senthil", "Murugan", "Karthikeyan", "Naresh", "Ravi", "Hari", "Santhosh", "Mohan"]
SURNAME = ["Agarwal", "Balakrishnan", "Banerjee", "Chandrasekar", "Chatterjee", "Desai", "Dhanapal", "Gopal", "Hegde", "Jain", "Kannan", "Kulkarni", "Lal", "Mathew",
           "Mishra", "Mukherjee", "Nambiar", "Natarajan", "Pandey", "Pillai", "Rajan", "Ramaswamy", "Saxena", "Shetty", "Srinivasan", "Subramanian", "Tiwari", "Varghese",
           "Venkatesh", "Yadav", "Ahmed", "Ansari", "D'Souza", "Fernandes", "George", "Sebastian", "Thangavel", "Velu", "Kumar", "Reddy", "Naidu", "Chowdhury"]
AREAS = [("Anna Nagar", "Chennai", "600040"), ("Velachery", "Chennai", "600042"), ("Perungudi", "Chennai", "600096"), ("Adyar", "Chennai", "600020"),
         ("RS Puram", "Coimbatore", "641002"), ("Peelamedu", "Coimbatore", "641004"), ("Saibaba Colony", "Coimbatore", "641011"), ("Indiranagar", "Bengaluru", "560038"),
         ("Koramangala", "Bengaluru", "560034"), ("Banjara Hills", "Hyderabad", "500034"), ("Edappally", "Kochi", "682024"), ("Anna Nagar East", "Madurai", "625020"),
         ("Saravanampatti", "Coimbatore", "641035"), ("Tambaram", "Chennai", "600045"), ("Whitefield", "Bengaluru", "560066"), ("Gandhipuram", "Coimbatore", "641012")]
INSURERS = ["Star Health", "HDFC ERGO", "ICICI Lombard", "Niva Bupa", "Care Health", "New India Assurance", "Ayushman Bharat (PM-JAY)", "CGHS", ""]
RELATIONS = ["Spouse", "Father", "Mother", "Son", "Daughter", "Brother", "Sister", "Friend"]
# condition, applicable age range, needs_ward kind, preferred department, tests, imaging idx, rx name
CONDITIONS = [
    ("Type 2 diabetes mellitus", (35, 85), "Cardiology", [4, 5], None, "Metformin 500 mg"), ("Essential hypertension", (35, 88), "Cardiology", [1, 5], None, "Amlodipine 5 mg"),
    ("Community-acquired pneumonia", (5, 90), "General Medicine", [0], 0, "Amoxicillin 500 mg"), ("Acute gastroenteritis", (3, 70), "General Medicine", [5], None, "Pantoprazole 40 mg"),
    ("Asthma, moderate persistent", (4, 60), "General Medicine", [0], 0, "Salbutamol inhaler"), ("Hypothyroidism", (25, 70), "General Medicine", [3], None, "Levothyroxine 50 mcg"),
    ("Dengue fever", (6, 60), "General Medicine", [0], None, "Paracetamol 500 mg"), ("Urinary tract infection", (18, 80), "General Medicine", [5, 0], None, "Amoxicillin 500 mg"),
    ("Hyperlipidaemia", (35, 80), "Cardiology", [1], None, "Atorvastatin 20 mg"), ("Coronary artery disease", (50, 88), "Cardiology", [1, 0], 0, "Aspirin 75 mg"),
    ("Heart failure", (55, 90), "Cardiology", [5, 0], 0, "Furosemide 40 mg"), ("Fracture, forearm", (5, 75), "Surgery", [0], 4, "Ibuprofen 400 mg"),
    ("Acute appendicitis", (8, 50), "Surgery", [0], 1, "Paracetamol 500 mg"), ("Cholelithiasis", (25, 70), "Surgery", [2], 1, "Pantoprazole 40 mg"),
    ("Osteoarthritis, knee", (50, 90), "Surgery", [0], 4, "Ibuprofen 400 mg"), ("Migraine", (16, 55), "General Medicine", [0], 2, "Paracetamol 500 mg"),
    ("Iron-deficiency anaemia", (14, 65), "General Medicine", [0], None, "Paracetamol 500 mg"), ("Chronic kidney disease", (45, 88), "General Medicine", [5, 0], None, "Furosemide 40 mg"),
    ("Viral fever", (2, 70), "General Medicine", [0], None, "Paracetamol 500 mg"), ("Bronchiolitis", (0, 3), "Paediatrics", [0], 0, "Salbutamol inhaler"),
    ("Tonsillitis", (4, 25), "Paediatrics", [0], None, "Amoxicillin 500 mg"), ("Typhoid fever", (6, 50), "General Medicine", [0, 2], None, "Paracetamol 500 mg"),
    ("Peptic ulcer disease", (25, 75), "General Medicine", [2], 1, "Pantoprazole 40 mg"), ("Lower back pain", (25, 75), "Surgery", [0], 3, "Ibuprofen 400 mg"),
    ("Antenatal check-up, third trimester", (20, 38), "Maternity", [0, 4], 1, "Paracetamol 500 mg"), ("Anxiety disorder", (16, 60), "General Medicine", [3], None, "Paracetamol 500 mg"),
]
BULK_WARDS = [("Ward C", "General Medicine", "General medicine", 130.0, 10), ("Ward D", "General Medicine", "General medicine", 130.0, 10),
              ("Maternity Ward", "Maternity", "Obstetrics", 220.0, 8), ("Paediatric Ward", "Paediatrics", "Paediatrics", 160.0, 8),
              ("Orthopaedic Ward", "Surgery", "Orthopaedics", 190.0, 8), ("High Dependency Unit", "Critical Care", "High dependency", 380.0, 6)]


def _phone(rng):
    return f"{rng.choice(['98', '97', '96', '95', '90', '88', '63', '70'])}{rng.randint(10000000, 99999999)}"


def _person(rng, sex):
    first = rng.choice(FEMALE if sex == "Female" else MALE)
    return f"{first} {rng.choice(SURNAME)}"


def _enrich_existing(rng) -> int:
    n = 0
    for p in db.session.execute(select(Patient).where(Patient.data_origin == "demo", Patient.email == "")).scalars():
        sex = p.gender if p.gender in ("Male", "Female") else rng.choice(["Male", "Female"])
        area, city, pin = rng.choice(AREAS)
        p.email = f"{p.name.lower().replace(' ', '.').replace(chr(39), '')}{rng.randint(1, 99)}@example.com"
        if not p.phone or p.phone.startswith("000"):
            p.phone = _phone(rng)
        if not p.address:
            p.address = f"{rng.randint(1, 240)}, {rng.choice(['Gandhi Road', 'Temple Street', 'Lake View Road', 'Park Avenue', 'Main Road'])}, {area}, {city} {pin}"
        if not p.emergency_contact:
            rel = rng.choice(RELATIONS)
            p.emergency_contact = _person(rng, "Male" if rel in ("Father", "Son", "Brother", "Spouse") and sex == "Female" else "Female")
            p.emergency_contact_relation, p.emergency_contact_phone = rel, _phone(rng)
        if not p.insurance_provider:
            p.insurance_provider = rng.choice(INSURERS)
            if p.insurance_provider:
                p.insurance_policy_no = f"POL-{rng.randint(10000000, 99999999)}"
        n += 1
    return n


def run(count: int = 150) -> dict:
    existing = db.session.execute(select(func.count(Patient.id))).scalar() or 0
    rng = random.Random(7000 + existing)
    now, today = utcnow(), date.today()
    pw = None
    from .security import hash_password
    pw = hash_password(demo_password())
    admin = db.session.execute(select(AppUser).where(AppUser.email == f"admin@{DOMAIN}")).scalar_one_or_none()
    if admin is None:
        raise RuntimeError("Run `seed-demo` first.")
    lab_u = db.session.execute(select(AppUser).where(AppUser.email == f"lab@{DOMAIN}")).scalar_one()
    rad_u = db.session.execute(select(AppUser).where(AppUser.email == f"radiology@{DOMAIN}")).scalar_one()
    bill_u = db.session.execute(select(AppUser).where(AppUser.email == f"billing@{DOMAIN}")).scalar_one()
    enriched = _enrich_existing(rng)

    depts = {d.name: d for d in db.session.execute(select(Department)).scalars()}
    for dn in {w[1] for w in BULK_WARDS}:
        if dn not in depts:
            depts[dn] = Department(name=dn)
            db.session.add(depts[dn])
    db.session.flush()
    wards = {w.name: w for w in db.session.execute(select(Ward)).scalars()}
    for name, dept, spec, rate, nbeds in BULK_WARDS:
        if name in wards:
            continue
        w = Ward(name=name, department_id=depts[dept].id, specialty=spec, daily_rate=rate)
        db.session.add(w)
        db.session.flush()
        tag = "".join(x[0] for x in name.split())
        for ri in range(1, (nbeds + 1) // 2 + 1):
            room = Room(ward_id=w.id, label=f"{tag}{ri}")
            db.session.add(room)
            db.session.flush()
            for bi in (1, 2):
                if (ri - 1) * 2 + bi <= nbeds:
                    db.session.add(Bed(room_id=room.id, ward_id=w.id, label=f"Bed {bi}", code=f"{name.replace(' ', '')}-{room.label}-{bi}"))
        wards[name] = w
    db.session.flush()

    meds = {m.name: m for m in db.session.execute(select(Medicine)).scalars()}
    for name, gen, st, form, stock, rl, price in EXTRA_MEDS:
        if name not in meds:
            meds[name] = Medicine(name=name, generic_name=gen, strength=st, form=form, stock=stock, reorder_level=rl, unit_price=price, expiry_date=(today + timedelta(days=360)).isoformat(), batch_no="B-2026")
            db.session.add(meds[name])
    db.session.flush()

    doctors = list(db.session.execute(select(Doctor)).scalars())
    duser = {u.doctor_id: u for u in db.session.execute(select(AppUser).where(AppUser.role == C.DOCTOR)).scalars()}
    nurses = {}
    for u in db.session.execute(select(AppUser).where(AppUser.role == C.NURSE)).scalars():
        nurses.setdefault(u.ward_id, u)
    ward_for = {"General Medicine": ["Ward C", "Ward D"], "Cardiology": ["Ward D", "High Dependency Unit"], "Surgery": ["Orthopaedic Ward", "Ward C"],
                "Maternity": ["Maternity Ward"], "Paediatrics": ["Paediatric Ward"]}
    slots = {(a.doctor_id, a.appointment_date, a.appointment_time) for a in db.session.execute(select(Appointment)).scalars()}
    stats = {"patients": 0, "admitted": 0, "discharged": 0, "labs": 0, "imaging": 0, "bills": 0, "appointments": 0}

    for _ in range(count):
        cond, (amin, amax), dept, test_idx, img_idx, rxname = rng.choice(CONDITIONS)
        sex = "Female" if dept == "Maternity" else rng.choice(["Female", "Male"])
        age = rng.randint(amin, amax)
        dob = (today - timedelta(days=age * 365 + rng.randint(0, 364))).isoformat()
        name = _person(rng, sex)
        area, city, pin = rng.choice(AREAS)
        rel = rng.choice(RELATIONS if age >= 18 else ["Father", "Mother"])
        ec_sex = "Male" if rel in ("Father", "Son", "Brother") else "Female" if rel in ("Mother", "Daughter", "Sister") else ("Male" if sex == "Female" else "Female")
        ins = rng.choice(INSURERS)
        p = Patient(patient_code=next_patient_code(), name=name, dob=dob, gender=sex, blood_group=rng.choice(["A+", "A+", "B+", "B+", "O+", "O+", "AB+", "A-", "B-", "O-", "AB-"]),
                    phone=_phone(rng), email=f"{name.lower().replace(' ', '.').replace(chr(39), '')}{rng.randint(1, 99)}@example.com",
                    address=f"{rng.randint(1, 240)}, {rng.choice(['Gandhi Road', 'Temple Street', 'Lake View Road', 'Park Avenue', 'Main Road', 'Nehru Street'])}, {area}, {city} {pin}",
                    emergency_contact=_person(rng, ec_sex), emergency_contact_relation=rel, emergency_contact_phone=_phone(rng),
                    insurance_provider=ins, insurance_policy_no=f"POL-{rng.randint(10000000, 99999999)}" if ins else "",
                    identifier_label="Aadhaar" if age >= 18 else "", identifier_last4=f"{rng.randint(0, 9999):04d}" if age >= 18 else "",
                    medical_history=rng.choice(["No significant past history.", "Previous hospital admission two years ago.", "Family history of diabetes.",
                                                "Family history of heart disease.", "Past surgery: appendicectomy.", "Known drug allergy recorded.", "Non-smoker, occasional alcohol.",
                                                "Regular exercise, vegetarian diet."]),
                    data_origin="demo", consent_data_sharing=rng.random() < 0.3, allergies="")
        db.session.add(p)
        db.session.flush()
        stats["patients"] += 1
        pool = [d for d in doctors if d.department == dept] or doctors
        doc = rng.choice(pool)
        du = duser.get(doc.id) or admin
        if rng.random() < 0.25:
            db.session.add(Allergy(patient_id=p.id, substance=rng.choice(["Penicillin", "Sulfonamides", "Peanuts", "Latex", "Aspirin", "Dust mites", "Shellfish"]),
                                   reaction=rng.choice(["Rash", "Hives", "Swelling", "Wheeze"]), severity=rng.choice(["Mild", "Moderate"]), recorded_by_id=du.id))
        db.session.add(Problem(patient_id=p.id, description=cond, status="Active", onset_on=(today - timedelta(days=rng.randint(3, 900))).isoformat(), recorded_by_id=du.id))
        if duser.get(doc.id):
            db.session.add(PatientAssignment(patient_id=p.id, user_id=du.id, relation="primary", created_by_id=admin.id))
        # appointments (1-2)
        for _a in range(rng.randint(1, 2)):
            for _try in range(30):
                day = (today + timedelta(days=rng.randint(-45, 21))).isoformat()
                tm = f"{rng.randint(9, 16):02d}:{rng.choice(['00', '15', '30', '45'])}"
                if (doc.id, day, tm) not in slots:
                    slots.add((doc.id, day, tm))
                    past = day < today.isoformat()
                    db.session.add(Appointment(patient_id=p.id, doctor_id=doc.id, appointment_date=day, appointment_time=tm, reason=cond,
                                               status=(rng.choice(["Completed", "Completed", "Completed", "Cancelled", "No-show"]) if past else "Scheduled"),
                                               visit_type=rng.choice(["Consultation", "Follow-up", "Review"]), created_by_id=admin.id))
                    stats["appointments"] += 1
                    break
        # admission: ~45 percent; of those most are later discharged
        adm, room_cost = None, 0.0
        if rng.random() < 0.45:
            for wn in ward_for.get(dept, ["Ward C"]):
                bed = db.session.execute(select(Bed).where(Bed.ward_id == wards[wn].id, Bed.status == "Available").order_by(Bed.code)).scalars().first()
                if bed:
                    days_ago = rng.randint(1, 12)
                    adm = bedsvc.admit(p, user=du, bed_id=bed.id, doctor_id=doc.id, reason=cond, admitted_on=(today - timedelta(days=days_ago)).isoformat())
                    db.session.add(ClinicalNote(patient_id=p.id, admission_id=adm.id, encounter_id=adm.encounter_id, author_id=du.id, note_type="Admission",
                                                body=f"Admitted with {cond.lower()}. Investigations and treatment started.", status="Final"))
                    for code, val in (("heart_rate", rng.randint(62, 108)), ("spo2", rng.randint(94, 99)), ("temperature", round(rng.uniform(36.4, 38.4), 1)),
                                      ("bp_systolic", rng.randint(104, 150)), ("bp_diastolic", rng.randint(64, 94))):
                        monitoring.record_observation(p, code, val, source="simulated", observed_at=now - timedelta(minutes=rng.randint(5, 120)), note="")
                    stats["admitted"] += 1
                    room_cost = wards[wn].daily_rate * days_ago
                    if days_ago >= 3 and rng.random() < 0.6:
                        bedsvc.plan_discharge(adm, du, "Home with follow-up in one week", (today).isoformat())
                        bedsvc.authorize_discharge(adm, du, f"{cond}: treated, improved, discharged with medicines and follow-up advice.")
                        bedsvc.complete_discharge(adm, du)
                        adm.discharged_on = (today - timedelta(days=rng.randint(0, days_ago - 1))).isoformat()
                        b2 = db.session.get(Bed, bed.id)
                        b2.status = "Available"
                        stats["admitted"] -= 1
                        stats["discharged"] += 1
                    break
        # labs
        lab_total = 0.0
        for ti in test_idx:
            test, analytes = TESTS[ti]
            pending = rng.random() < 0.18
            rep = LabReport(patient_id=p.id, test_name=test, sample_date=(today - timedelta(days=rng.randint(0, 10))).isoformat(), status="Ordered" if pending else "Released",
                            ordered_by=du.name, ordered_by_id=du.id, accession_no=osvc.next_accession(), ordered_at=now - timedelta(hours=rng.randint(2, 200)))
            db.session.add(rep)
            db.session.flush()
            lab_total += 30.0
            stats["labs"] += 1
            if pending:
                continue
            summary = []
            for analyte, unit, lo, hi, cl, ch in analytes:
                val = round(rng.uniform(lo * 0.8 if lo else 0, hi * 1.3), 1)
                flag, is_crit = osvc.compute_flag(val, lo, hi, cl, ch)
                db.session.add(LabResult(lab_report_id=rep.id, analyte=analyte, value_num=val, unit=unit, ref_low=lo, ref_high=hi, critical_low=cl, critical_high=ch, flag=flag,
                                         is_critical=is_crit, status="Final", entered_by_id=lab_u.id))
                summary.append(f"{analyte}: {val:g} {unit}")
            rep.resulted_at = rep.verified_at = rep.released_at = now - timedelta(hours=rng.randint(1, 96))
            rep.resulted_by_id = rep.verified_by_id = rep.released_by_id = lab_u.id
            rep.result = "; ".join(summary)
            db.session.flush()
            dsvc.ensure(p.id, "Laboratory report", f"{rep.test_name} ({rep.sample_date})", "lab", rep.id, digital=True, created_by_id=lab_u.id).physical_status = rng.choice(["Ready for collection", "Requested", "Handed over", "Not requested"])
        # imaging
        if img_idx is not None and rng.random() < 0.7:
            mod, desc, findings, impression = IMAGING[img_idx]
            rr = RadiologyRecord(patient_id=p.id, modality=mod, study_date=(today - timedelta(days=rng.randint(0, 8))).isoformat(), study_description=desc, indication=cond,
                                 ordered_by_id=du.id, order_status="Final", report_status="Final", findings=findings, impression=impression, performed_at=now - timedelta(hours=30),
                                 performed_by_id=rad_u.id, reported_at=now - timedelta(hours=26), reported_by_id=rad_u.id, authorized_at=now - timedelta(hours=26), authorized_by_id=rad_u.id)
            db.session.add(rr)
            db.session.flush()
            db.session.add(RadiologyReportVersion(radiology_id=rr.id, version=1, findings=findings, impression=impression, status="Final", author_id=rad_u.id))
            dsvc.ensure(p.id, "Radiology report", f"{mod} {desc}", "radiology", rr.id, digital=True, created_by_id=rad_u.id)
            lab_total += 60.0
            stats["imaging"] += 1
        # prescription
        rx = next((r for r in RX if r[0] == rxname), None)
        m = meds.get(rxname)
        if m:
            _, dose, freq, qty, days = rx or (rxname, m.strength, "Twice daily", 20, 10)
            db.session.add(Prescription(patient_id=p.id, doctor_name=du.name, medicine=m.name, medicine_id=m.id, dosage=dose, route="Inhaled" if m.form == "Inhaler" else "Oral",
                                        frequency=freq, status="Ordered", ordered_by_id=du.id, quantity=qty, duration_days=days))
        # billing
        cons = float(rng.choice([150, 200, 250, 300, 400]))
        b = Bill(patient_id=p.id, description="Inpatient bill" if adm else "Outpatient bill", consultation=cons, laboratory=lab_total, pharmacy=round(rng.uniform(15, 180), 2),
                 room=round(room_cost, 2), insurance_provider=ins, insurance_status=("Approved" if ins and rng.random() < 0.5 else "Not submitted"),
                 status="Issued", created_by_id=bill_u.id, admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None)
        db.session.add(b)
        db.session.flush()
        total = cons + lab_total + b.pharmacy + b.room
        r = rng.random()
        if r < 0.5:
            db.session.add(Payment(bill_id=b.id, kind="Payment", amount=round(total, 2), method=rng.choice(["Cash", "Card", "UPI", "Insurance"]), reference=f"RCPT-{b.id:05d}", received_by_id=bill_u.id))
        elif r < 0.8:
            db.session.add(Payment(bill_id=b.id, kind="Payment", amount=round(total * rng.uniform(0.3, 0.7), 2), method=rng.choice(["Cash", "Card", "UPI"]), reference=f"RCPT-{b.id:05d}", received_by_id=bill_u.id))
        db.session.flush()
        osvc.refresh_bill_status(b)
        dsvc.ensure(p.id, "Invoice / receipt", b.description, "bill", b.id, digital=True, created_by_id=bill_u.id)
        stats["bills"] += 1
        db.session.flush()
    audit("seed.bulk_patients", category="admin", details=f"{stats['patients']} bulk sample patients loaded", user=admin)
    db.session.commit()
    stats["enriched_existing"] = enriched
    return stats
