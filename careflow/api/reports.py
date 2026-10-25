"""Operational reports. Counts are computed live from the database; CSV export is permission-gated and audited."""
from __future__ import annotations

import csv
import io
from datetime import date, timedelta

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy import func, select

from ..access import has_perm, require_perm
from ..audit import audit
from ..extensions import db
from ..models import Admission, Alert, Appointment, Bed, Bill, InsuranceClaim, LabReport, Payment, Prescription, RadiologyRecord, Ward, utcnow
from ..utils import ApiError, commit, iso

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _days():
    d = request.args.get("days", 30, type=int)
    return min(365, max(1, d))


def _csv_cell(v):
    v = "" if v is None else str(v)
    return "'" + v if v[:1] in ("=", "+", "-", "@", "\t", "\r") else v  # neutralise spreadsheet formula injection


def _build(name: str, days: int) -> dict:
    since_d = (date.today() - timedelta(days=days)).isoformat()
    since_t = utcnow() - timedelta(days=days)
    if name == "occupancy":
        rows = []
        for w in db.session.execute(select(Ward).where(Ward.is_active.is_(True)).order_by(Ward.name)).scalars():
            by = dict(db.session.execute(select(Bed.status, func.count(Bed.id)).where(Bed.ward_id == w.id, Bed.is_active.is_(True)).group_by(Bed.status)).all())
            tot = sum(by.values())
            rows.append({"ward": w.name, "total_beds": tot, "occupied": by.get("Occupied", 0), "available": by.get("Available", 0), "cleaning": by.get("Cleaning", 0), "reserved": by.get("Reserved", 0),
                         "maintenance": by.get("Maintenance", 0), "occupancy_pct": round(100 * by.get("Occupied", 0) / tot, 1) if tot else 0})
        return {"title": "Bed occupancy (current)", "rows": rows}
    if name == "admissions":
        rows = [{"status": s_, "count": n} for s_, n in db.session.execute(select(Admission.status, func.count(Admission.id)).where(Admission.admitted_on >= since_d).group_by(Admission.status))]
        return {"title": f"Admissions in the last {days} days", "rows": rows}
    if name == "appointments":
        rows = [{"status": s_, "count": n} for s_, n in db.session.execute(select(Appointment.status, func.count(Appointment.id)).where(Appointment.appointment_date >= since_d).group_by(Appointment.status))]
        return {"title": f"Appointments in the last {days} days", "rows": rows}
    if name == "lab-turnaround":
        reps = db.session.execute(select(LabReport).where(LabReport.released_at.is_not(None), LabReport.released_at >= since_t, LabReport.ordered_at.is_not(None))).scalars().all()
        agg: dict = {}
        for r in reps:
            agg.setdefault(r.test_name, []).append((r.released_at - r.ordered_at).total_seconds() / 60)
        rows = [{"test": k, "released": len(v), "median_minutes": round(sorted(v)[len(v) // 2]), "max_minutes": round(max(v))} for k, v in sorted(agg.items())]
        return {"title": f"Lab turnaround, order to release ({days} days)", "rows": rows}
    if name == "alerts":
        rows = [{"severity": a, "status": b, "count": n} for a, b, n in db.session.execute(select(Alert.severity, Alert.status, func.count(Alert.id)).where(Alert.triggered_at >= since_t).group_by(Alert.severity, Alert.status))]
        return {"title": f"Monitoring alerts ({days} days)", "rows": rows}
    if name == "billing":
        billed = db.session.execute(select(Bill).where(Bill.status != "Void", Bill.created_at >= since_t)).scalars().all()
        pay = db.session.execute(select(Payment.kind, func.coalesce(func.sum(Payment.amount), 0)).where(Payment.created_at >= since_t).group_by(Payment.kind)).all()
        paid = round(sum(float(v) * (1 if k == "Payment" else -1) for k, v in pay), 2)
        claims = [{"claim_status": s_, "count": n} for s_, n in db.session.execute(select(InsuranceClaim.status, func.count(InsuranceClaim.id)).group_by(InsuranceClaim.status))]
        rows = [{"metric": "Bills issued", "value": len(billed)}, {"metric": "Total billed", "value": round(sum(b.total for b in billed), 2)}, {"metric": "Bills marked paid", "value": sum(1 for b in billed if b.paid)}]
        rows.append({"metric": "Net payments received (payments minus refunds)", "value": paid})
        return {"title": f"Billing ({days} days)", "rows": rows + [{"metric": f"Claims {c['claim_status']}", "value": c["count"]} for c in claims]}
    if name == "prescriptions":
        rows = [{"status": s_, "count": n} for s_, n in db.session.execute(select(Prescription.status, func.count(Prescription.id)).where(Prescription.created_at >= since_t).group_by(Prescription.status))]
        return {"title": f"Medication orders ({days} days)", "rows": rows}
    if name == "radiology":
        rows = [{"status": s_, "count": n} for s_, n in db.session.execute(select(RadiologyRecord.order_status, func.count(RadiologyRecord.id)).where(RadiologyRecord.ordered_at >= since_t).group_by(RadiologyRecord.order_status))]
        return {"title": f"Radiology orders ({days} days)", "rows": rows}
    raise ApiError("Unknown report", 404)


REPORT_PERMS = {"billing": "billing.read", "alerts": "alert.view"}
NAMES = ("occupancy", "admissions", "appointments", "lab-turnaround", "alerts", "billing", "prescriptions", "radiology")


@bp.get("")
@require_perm("report.view")
def catalogue():
    return jsonify(ok=True, items=[n for n in NAMES if has_perm(g.user, REPORT_PERMS.get(n, "report.view"))])


@bp.get("/<name>")
@require_perm("report.view")
def report(name):
    if name not in NAMES or not has_perm(g.user, REPORT_PERMS.get(name, "report.view")):
        raise ApiError("Report not available", 404)
    out = _build(name, _days())
    if request.args.get("format") == "csv":
        if not has_perm(g.user, "export.run"):
            audit("export.denied", category="export", outcome="denied", details=name, commit=True)
            raise ApiError("You do not have permission to export data", 403)
        buf = io.StringIO()
        rows = out["rows"]
        w = csv.writer(buf)
        if rows:
            w.writerow(rows[0].keys())
            for r in rows:
                w.writerow([_csv_cell(v) for v in r.values()])
        audit("report.exported", category="export", details=f"{name} rows={len(rows)}")
        commit()
        return Response(buf.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename=careflow-{name}.csv"})
    return jsonify(ok=True, name=name, generated_at=iso(utcnow()), **out)
