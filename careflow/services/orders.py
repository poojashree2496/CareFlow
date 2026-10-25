"""Laboratory, radiology critical-result, pharmacy and billing business rules."""
from __future__ import annotations

import re
from datetime import date

from sqlalchemy import func, select, update

from ..audit import audit
from ..constants import LAB_FLAGS, LAB_TRANSITIONS, LEGACY_INSURANCE_STATUS
from ..extensions import db
from ..models import (Allergy, AppUser, Bill, CriticalAck, DispenseEvent, InsuranceClaim, LabReport, LabResult, Medicine,
                      Notification, Patient, Prescription, StockMovement, utcnow)
from ..utils import ApiError

# --------------------------------------------------------------------------- #
# Laboratory
# --------------------------------------------------------------------------- #
CRITICAL_FLAGS = {"Critical High", "Critical Low"}


def compute_flag(value_num, ref_low, ref_high, crit_low, crit_high, manual_flag=None):
    """Derive a flag only from ranges supplied by the laboratory - never invented here."""
    if value_num is None:
        flag = manual_flag if manual_flag in LAB_FLAGS else "Not assessed"
        return flag, flag in CRITICAL_FLAGS
    if crit_low is not None and value_num <= crit_low:
        return "Critical Low", True
    if crit_high is not None and value_num >= crit_high:
        return "Critical High", True
    if ref_low is not None and value_num < ref_low:
        return "Low", False
    if ref_high is not None and value_num > ref_high:
        return "High", False
    if ref_low is None and ref_high is None:
        return (manual_flag if manual_flag in LAB_FLAGS else "Not assessed"), manual_flag in CRITICAL_FLAGS
    return "Normal", False


def lab_transition(report: LabReport, new_status: str):
    cur = report.status
    # legacy values
    if cur == "Pending":
        cur = "Ordered"
    if cur == "Completed":
        cur = "Released"
    if new_status not in LAB_TRANSITIONS.get(cur, set()):
        raise ApiError(f"Lab order cannot move from {cur} to {new_status}", 409)
    report.status = new_status


def next_accession() -> str:
    n = db.session.execute(select(func.count(LabReport.id))).scalar() or 0
    return f"ACC-{date.today():%y%m%d}-{n + 1:05d}-{__import__('os').urandom(1).hex().upper()}"


def summarize_results(report: LabReport) -> str:
    live = [r for r in report.results if r.status != "Superseded"]
    parts = []
    for r in live:
        val = f"{r.value_num:g}" if r.value_num is not None else (r.value_text or "-")
        parts.append(f"{r.analyte}: {val} {r.unit}".strip() + (f" [{r.flag}]" if r.flag not in ("Normal", "Not assessed") else ""))
    return "; ".join(parts)[:4000]


def notify_critical(source_type: str, source_id: int, patient_id: int, summary: str, ordering_user_id=None):
    existing = db.session.execute(select(CriticalAck).where(CriticalAck.source_type == source_type, CriticalAck.source_id == source_id)).scalar_one_or_none()
    if existing:
        return existing
    ack = CriticalAck(source_type=source_type, source_id=source_id, patient_id=patient_id, summary=summary[:300], notify_user_id=ordering_user_id)
    db.session.add(ack)
    db.session.flush()
    patient = db.session.get(Patient, patient_id)
    title = f"CRITICAL {source_type} result - acknowledgment required"
    body = f"{patient.patient_code} - {summary}"
    if ordering_user_id:
        db.session.add(Notification(user_id=ordering_user_id, kind="critical-result", severity="Critical", title=title, body=body[:400],
                                    patient_id=patient_id, ref_type=source_type, ref_id=source_id))
    db.session.add(Notification(role="doctor", kind="critical-result", severity="Critical", title=title, body=body[:400],
                                patient_id=patient_id, ref_type=source_type, ref_id=source_id))
    audit("critical_result.notified", category="clinical", entity_type=source_type, entity_id=source_id, patient_id=patient_id, user=None)
    return ack


# --------------------------------------------------------------------------- #
# Pharmacy
# --------------------------------------------------------------------------- #
ACTIVE_RX = ("Ordered", "Verified", "Dispensed", "Partially Dispensed")
# Small illustrative list carried over from the original prototype. NOT a drug-safety database.
DEMO_INTERACTIONS = [
    ({"warfarin", "ibuprofen"}, "Potentially increased bleeding risk"),
    ({"sildenafil", "nitroglycerin"}, "Potentially dangerous blood-pressure drop"),
    ({"sertraline", "tramadol"}, "Potential serotonin toxicity risk"),
    ({"lisinopril", "potassium chloride"}, "Potentially elevated potassium"),
]
INTERACTION_NOTICE = ("Illustrative demonstration rules only (4 pairs). Not a validated or comprehensive drug-interaction database; "
                      "absence of an alert does not mean a combination is safe.")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def medication_warnings(patient: Patient, medicine_name: str, generic_name: str = "", *, exclude_rx_id: int | None = None) -> list[dict]:
    names = {n for n in (_norm(medicine_name), _norm(generic_name)) if n}
    warnings: list[dict] = []
    # allergies: structured + legacy free text
    substances = [(a.substance, a.reaction) for a in db.session.execute(select(Allergy).where(Allergy.patient_id == patient.id, Allergy.status == "Active")).scalars()]
    for token in re.split(r"[,;\n]", patient.allergies or ""):
        t = token.strip()
        if t and _norm(t) not in {"none", "none reported", "nka", "nkda", "not recorded", "no known allergies"}:
            substances.append((t, ""))
    for sub, reaction in substances:
        sn = _norm(sub)
        if len(sn) >= 3 and any(sn in n or n in sn for n in names if len(n) >= 3):
            warnings.append({"type": "allergy", "blocking": True, "message": f"Recorded allergy to '{sub}'" + (f" ({reaction})" if reaction else "") + f" may match {medicine_name}"})
    # duplicates & demo interactions against active orders
    active = db.session.execute(select(Prescription).where(Prescription.patient_id == patient.id, Prescription.status.in_(ACTIVE_RX))).scalars().all()
    active_names = []
    for rx in active:
        if exclude_rx_id and rx.id == exclude_rx_id:
            continue
        rn = _norm(rx.medicine)
        active_names.append(rn)
        if rn in names:
            warnings.append({"type": "duplicate", "blocking": True, "message": f"An active order for {rx.medicine} already exists (order #{rx.id}, {rx.status})"})
    def _has(pool, token):
        return any(token in n for n in pool)

    for pair, msg in DEMO_INTERACTIONS:
        a, b = sorted(pair)
        if (_has(names, a) and _has(active_names, b)) or (_has(names, b) and _has(active_names, a)):
            warnings.append({"type": "interaction", "blocking": False, "message": f"{msg} ({a} + {b}). {INTERACTION_NOTICE}"})
    return warnings


def dispense(rx: Prescription, medicine: Medicine, quantity: int, pharmacist: AppUser, acknowledged: list[str], note: str = "") -> DispenseEvent:
    if rx.status not in ("Ordered", "Verified", "Partially Dispensed"):
        raise ApiError(f"Order #{rx.id} is {rx.status} and cannot be dispensed", 409)
    if quantity <= 0:
        raise ApiError("Quantity must be positive")
    if rx.quantity is not None and rx.dispensed_quantity + quantity > rx.quantity:
        raise ApiError(f"Quantity exceeds the ordered amount (ordered {rx.quantity}, already dispensed {rx.dispensed_quantity})", 409)
    if not medicine.is_active:
        raise ApiError("Medicine is not active in the catalogue", 409)
    if medicine.expiry_date and medicine.expiry_date < date.today().isoformat():
        raise ApiError(f"{medicine.name} is expired ({medicine.expiry_date}) and cannot be dispensed", 409)
    patient = db.session.get(Patient, rx.patient_id)
    fresh = [w for w in medication_warnings(patient, rx.medicine, medicine.generic_name, exclude_rx_id=rx.id) if w["type"] == "allergy"]
    if fresh and not (rx.allergy_override_reason or "").strip() and not acknowledged:
        raise ApiError("Allergy warning(s) must be reviewed and acknowledged before dispensing", 409, warnings=fresh)
    res = db.session.execute(update(Medicine).where(Medicine.id == medicine.id, Medicine.stock >= quantity).values(stock=Medicine.stock - quantity))
    if res.rowcount != 1:
        raise ApiError(f"Insufficient stock for {medicine.name}", 409)
    db.session.refresh(medicine)
    db.session.add(StockMovement(medicine_id=medicine.id, delta=-quantity, balance_after=medicine.stock, reason="dispense", ref_type="prescription", ref_id=rx.id, user_id=pharmacist.id))
    ev = DispenseEvent(prescription_id=rx.id, medicine_id=medicine.id, quantity=quantity, dispensed_by_id=pharmacist.id,
                       warnings_acknowledged=acknowledged or [], note=note[:300])
    db.session.add(ev)
    rx.medicine_id = rx.medicine_id or medicine.id
    if rx.verified_by_id is None:  # dispensing is a pharmacist review: record who verified the order
        rx.verified_by_id, rx.verified_at = pharmacist.id, utcnow()
    rx.dispensed_quantity = (rx.dispensed_quantity or 0) + quantity
    rx.status = "Dispensed" if (rx.quantity is None or rx.dispensed_quantity >= rx.quantity) else "Partially Dispensed"
    db.session.flush()
    from . import deliverables as dsvc
    item = dsvc.ensure(rx.patient_id, "Prescription / medicine label", f"{medicine.name} {rx.dosage or ''}".strip(), "prescription", rx.id, digital=True, created_by_id=pharmacist.id)
    if item.physical_status == "Not requested":
        item.physical_status = "Ready for collection"      # the dispensed medicine and its label are physical items to hand over
    audit("rx.dispensed", category="clinical", entity_type="prescription", entity_id=rx.id, patient_id=rx.patient_id, details=f"{medicine.name} x{quantity}")
    return ev


def adjust_stock(medicine: Medicine, delta: int, reason: str, user: AppUser, ref: str = ""):
    if delta == 0:
        raise ApiError("Adjustment cannot be zero")
    res = db.session.execute(update(Medicine).where(Medicine.id == medicine.id, Medicine.stock + delta >= 0).values(stock=Medicine.stock + delta))
    if res.rowcount != 1:
        raise ApiError("Stock cannot go below zero", 409)
    db.session.refresh(medicine)
    db.session.add(StockMovement(medicine_id=medicine.id, delta=delta, balance_after=medicine.stock, reason=reason, ref_type=ref[:30], user_id=user.id))
    audit("inventory.adjusted", category="clinical", entity_type="medicine", entity_id=medicine.id, details=f"{medicine.name} {delta:+d} ({reason})")


# --------------------------------------------------------------------------- #
# Billing
# --------------------------------------------------------------------------- #
def bill_figures(bill: Bill) -> dict:
    adj = round(sum(a.amount for a in bill.adjustments), 2)
    paid = round(sum(p.amount for p in bill.payments if p.kind == "Payment") - sum(p.amount for p in bill.payments if p.kind == "Refund"), 2)
    balance = round(bill.total - adj - paid, 2)
    claims = sorted(bill.claims, key=lambda c: c.id)
    return {"total": bill.total, "adjustments": adj, "paid": paid, "balance": balance,
            "claim_status": claims[-1].status if claims else None,
            "claim_approved": round(sum((c.amount_approved or 0) for c in claims), 2)}


def refresh_bill_status(bill: Bill):
    f = bill_figures(bill)
    bill.paid = bool(bill.total > 0 and f["balance"] <= 0.005)
    claims = sorted(bill.claims, key=lambda c: c.id)
    if claims:
        bill.insurance_status = LEGACY_INSURANCE_STATUS.get(claims[-1].status, bill.insurance_status)
        bill.insurance_provider = claims[-1].provider
