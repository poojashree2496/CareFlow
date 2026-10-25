"""Extra sample accounts for every role, plus patient-portal logins for many patients. Idempotent (skips existing e-mails)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import select

from . import constants as C
from .api.auth import demo_password
from .audit import audit
from .extensions import db
from .models import AppUser, Doctor, Patient, Ward, utcnow
from .security import hash_password
from .seed import DOMAIN

DOCTORS = [("Dr. Vikram Chandran", "Neurology", "Neurology"), ("Dr. Lakshmi Narayan", "Pulmonology", "General Medicine"), ("Dr. Imran Qureshi", "Nephrology", "General Medicine"),
           ("Dr. Anjali Deshmukh", "Endocrinology", "General Medicine"), ("Dr. Suresh Pillai", "Emergency Medicine", "Critical Care")]
NAMES = {
    "super_admin": ["Ritu Sharma"],
    "hospital_admin": ["Karthik Raman", "Shalini Bose"],
    "nurse": ["Pushpa Devi", "Merlin Thomas", "Sunitha Reddy", "Jyothi Lakshmi", "Rosy Mathew", "Bindu Nair"],
    "lab": ["Naveen Kumar", "Rukmini Iyer", "Farhan Sheikh"], "pharmacist": ["Gayathri Menon", "Anwar Hussain"],
    "radiology": ["Dilip Varma", "Sheetal Kapoor"], "billing": ["Meghna Ghosh", "Harish Babu", "Zeenat Ali"],
}
PREFIX = {"super_admin": ("super", C.SUPER_ADMIN, 2), "hospital_admin": ("admin", C.HOSPITAL_ADMIN, 2), "nurse": ("nurse", C.NURSE, 5), "lab": ("lab", C.LAB_STAFF, 2),
          "pharmacist": ("pharmacist", C.PHARMACIST, 2), "radiology": ("radiology", C.RADIOLOGY_STAFF, 2), "billing": ("billing", C.BILLING_STAFF, 2)}


def run(patient_logins: int = 30) -> dict:
    now = utcnow()
    pw = hash_password(demo_password())
    have = {e for (e,) in db.session.execute(select(AppUser.email))}
    made = []

    def add(email, name, role, **kw):
        if email in have:
            return
        db.session.add(AppUser(email=email, name=name, role=role, password_hash=pw, is_demo=True, must_change_password=False, password_changed_at=now, **kw))
        have.add(email)
        made.append((role, email, name))

    for key, (prefix, role, start) in PREFIX.items():
        wards = list(db.session.execute(select(Ward).order_by(Ward.id)).scalars()) if role == C.NURSE else []
        for i, name in enumerate(NAMES[key]):
            kw = {"ward_id": wards[i % len(wards)].id} if wards else {}
            add(f"{prefix}{start + i}@{DOMAIN}", name, role, **kw)
    # more doctors (doctor8...)
    existing_regs = {r for (r,) in db.session.execute(select(Doctor.registration_no))}
    n = 8
    for i, (name, spec, dept) in enumerate(DOCTORS):
        reg = f"REG-{100 + i}"
        if reg in existing_regs:
            continue
        d = Doctor(name=name, specialty=spec, department=dept, registration_no=reg)
        db.session.add(d)
        db.session.flush()
        add(f"doctor{n + i}@{DOMAIN}", name, C.DOCTOR, doctor_id=d.id)
    # patient logins for patients that have none (prefer ones with records), numbered after the existing patientN
    taken = [int(e.split("@")[0][7:]) for e in have if e.startswith("patient") and e.split("@")[0][7:].isdigit()]
    nxt = (max(taken) if taken else 1) + 1
    has_login = {pid for (pid,) in db.session.execute(select(AppUser.patient_id).where(AppUser.patient_id.is_not(None)))}
    pts = db.session.execute(select(Patient).where(Patient.data_origin == "demo").order_by(Patient.id)).scalars().all()
    for p in pts:
        if patient_logins <= 0:
            break
        if p.id in has_login:
            continue
        add(f"patient{nxt}@{DOMAIN}", p.name, C.PATIENT, patient_id=p.id)
        nxt += 1
        patient_logins -= 1
    audit("seed.staff", category="admin", details=f"{len(made)} sample accounts added", user=None)
    db.session.commit()
    return {"accounts": made}
