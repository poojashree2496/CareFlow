"""Tamper-evident audit trail and QR-verifiable report copies."""
import re

import pytest
from sqlalchemy import select, text

from careflow import audit_chain
from careflow.audit import audit
from careflow.extensions import db
from careflow.models import AuditLog, Bill, Deliverable, LabReport, Payment


def _code(html: str) -> str:
    return re.search(r"<code>([^<]+)</code>", html).group(1)


def _public(app, code: str) -> str:
    return app.test_client().get("/verify", query_string={"code": code}).get_data(as_text=True)


def Api_anon(app):
    from conftest import Api
    return Api(app)


def _released_items(pat):
    return {i["kind"]: i for i in pat.get("/api/portal/overview").json["deliverables"] if i["copy_url"]}


# ------------------------------------------------------------------ audit chain
def test_chain_is_intact_after_normal_use(app, as_user):
    as_user("doctor1").get("/api/patients")
    as_user("admin").get("/api/admin/audit")
    res = audit_chain.verify()
    assert res["ok"] and res["checked"] >= 5 and res["issue_count"] == 0 and len(res["head_hash"]) == 64


def test_many_entries_in_one_transaction_keep_their_order(app):
    for i in range(6):
        audit("test.bulk", details=f"n={i}")
    db.session.commit()
    assert audit_chain.verify()["ok"]
    rows = db.session.execute(select(AuditLog).where(AuditLog.action == "test.bulk").order_by(AuditLog.id)).scalars().all()
    assert [r.details for r in rows] == [f"n={i}" for i in range(6)]


def test_editing_an_entry_is_detected_and_located(app, as_user):
    as_user("doctor1").get("/api/patients")
    target = db.session.execute(select(AuditLog).order_by(AuditLog.id.desc())).scalars().first()
    db.session.execute(text("UPDATE audit_log SET details = 'nothing happened here' WHERE id = :i"), {"i": target.id})
    db.session.commit()
    res = audit_chain.verify()
    assert not res["ok"] and [i["id"] for i in res["issues"]] == [target.id] and "modified" in res["issues"][0]["problem"]


def test_removing_an_entry_is_detected(app, as_user):
    as_user("doctor1").get("/api/patients")
    rows = db.session.execute(select(AuditLog).order_by(AuditLog.id)).scalars().all()
    victim, after = rows[2], rows[3]
    db.session.execute(text("DELETE FROM audit_log WHERE id = :i"), {"i": victim.id})
    db.session.commit()
    res = audit_chain.verify()
    assert not res["ok"] and res["issues"][0]["id"] == after.id and "broken" in res["issues"][0]["problem"]


def test_admin_endpoint_and_permission(app, as_user):
    assert as_user("admin").get("/api/admin/audit/verify").json["chain_ok"] is True
    assert as_user("doctor1").get("/api/admin/audit/verify").status_code == 403
    assert as_user("patient1").get("/api/admin/audit/verify").status_code == 403
    db.session.execute(text("UPDATE audit_log SET outcome = 'success', details = 'x' WHERE id = 2"))
    db.session.commit()
    r = as_user("super").get("/api/admin/audit/verify").json
    assert r["chain_ok"] is False and r["issues"][0]["id"] == 2


# ------------------------------------------------------------------ QR-verifiable copies
def test_printed_copy_carries_qr_and_code_that_verify_publicly(app, as_user):
    pat = as_user("patient1")
    items = _released_items(pat)
    assert {"Laboratory report", "Radiology report", "Invoice / receipt"} <= set(items)
    for item in items.values():
        html = pat.get(item["copy_url"]).get_data(as_text=True)
        assert "<svg" in html and "Check that this copy is genuine" in html
        page = _public(app, _code(html))
        assert "Genuine" in page and "M. R." in page
        assert "Maya" not in page and "Rao" not in page and "Haemoglobin" not in page   # nothing clinical, no name
    assert audit_chain.verify()["ok"]


def test_wrong_or_malformed_codes_are_rejected(app, as_user):
    pat = as_user("patient1")
    code = _code(pat.get(_released_items(pat)["Laboratory report"]["copy_url"]).get_data(as_text=True))
    flipped = code[:-1] + ("0" if code[-1] != "0" else "1")
    for bad in (flipped, "L1-0000 0000 0000 0000 0000", "X9-1234", "L99999-AAAA AAAA AAAA AAAA AAAA", "'; drop table patient; --", ""):
        page = _public(app, bad)
        assert "Genuine" not in page
    assert "does not match" in _public(app, flipped)
    assert db.session.execute(text("SELECT count(*) FROM patient")).scalar() > 0


def test_correcting_a_report_invalidates_old_copies_but_payments_do_not_invalidate_invoices(app, as_user, ids):
    pat = as_user("patient1")
    items = _released_items(pat)
    lab_code = _code(pat.get(items["Laboratory report"]["copy_url"]).get_data(as_text=True))
    bill_code = _code(pat.get(items["Invoice / receipt"]["copy_url"]).get_data(as_text=True))
    assert "Genuine" in _public(app, lab_code) and "Genuine" in _public(app, bill_code)
    lab = db.session.execute(select(LabReport).where(LabReport.patient_id == ids.patient["Maya Rao"], LabReport.status == "Released")).scalars().first()
    lab.result = (lab.result or "") + " (changed after printing)"
    bill = db.session.execute(select(Bill).where(Bill.patient_id == ids.patient["Maya Rao"])).scalars().first()
    db.session.add(Payment(bill_id=bill.id, kind="Payment", amount=10.0, method="Cash", reference="T1", received_by_id=ids.user["billing"]))
    db.session.commit()
    assert "does not match" in _public(app, lab_code)
    assert "Genuine" in _public(app, bill_code)


def test_public_checks_are_audited_without_breaking_the_chain(app, as_user):
    before = db.session.execute(select(AuditLog).where(AuditLog.action == "verify.public_check")).scalars().all()
    _public(app, "L1-0000 0000 0000 0000 0000")
    rows = db.session.execute(select(AuditLog).where(AuditLog.action == "verify.public_check")).scalars().all()
    assert len(rows) == len(before) + 1 and rows[-1].outcome == "denied"
    assert audit_chain.verify()["ok"]


def test_public_check_is_rate_limited(app):
    app.config["RATE_LIMIT_ENABLED"] = True
    codes = [_public(app, f"L{i}-0000 0000 0000 0000 0000") for i in range(35)]
    assert any("Too many checks" in c for c in codes)


def test_staff_can_print_released_copies_and_patients_cannot_use_that_route(app, as_user, ids):
    adm = as_user("admin")
    d = db.session.execute(select(Deliverable).where(Deliverable.patient_id == ids.patient["Maya Rao"], Deliverable.ref_type == "lab")).scalars().first()
    r = adm.get(f"/api/deliverables/{d.id}/print")
    assert r.status_code == 200 and b"<svg" in r.data
    code = _code(r.get_data(as_text=True))
    assert "Genuine" in _public(app, code)
    assert as_user("patient1").get(f"/api/deliverables/{d.id}/print").status_code == 403
    assert Api_anon(app).get(f"/api/deliverables/{d.id}/print").status_code == 401


def test_unreleased_reports_cannot_be_printed(app, as_user, ids):
    adm = as_user("admin")
    d = db.session.execute(select(Deliverable).where(Deliverable.patient_id == ids.patient["Maya Rao"], Deliverable.ref_type == "lab")).scalars().first()
    lab = db.session.get(LabReport, d.ref_id)
    lab.status = "Ordered"
    db.session.commit()
    assert adm.get(f"/api/deliverables/{d.id}/print").status_code == 404
