"""Verifiable report copies.

Each printed/downloaded copy of a released lab report, imaging report or invoice carries a verification code and a QR code.
The code is an HMAC (keyed with the server secret) over the record's id and a fingerprint of its *current content*. Anyone can
open the public check page with the code and learn whether it still matches the hospital's record. If the record is
corrected or altered after the copy was issued, or the code is forged, the check fails. The public page never shows clinical
content or the patient's name.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import timezone

from flask import current_app, request
from sqlalchemy import select

from ..extensions import db
from ..models import AppUser, Bill, Deliverable, LabReport, LabResult, Patient, RadiologyRecord
from ..utils import ApiError

TYPES = {"lab": ("L", "Laboratory report"), "radiology": ("R", "Imaging report"), "bill": ("B", "Invoice / receipt")}
LETTER = {v[0]: k for k, v in TYPES.items()}


def _fmt_num(v):
    return "" if v is None else (f"{v:g}" if isinstance(v, (int, float)) else str(v))


def _ts(dt):
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _fp(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def _key() -> bytes:
    return hashlib.sha256(("careflow-verify|" + str(current_app.config["SECRET_KEY"])).encode()).digest()


def load_released(ref_type: str, ref_id: int, patient_id: int | None = None):
    """Return (record, sections, note, fingerprint, released_at, issuer_role) for a RELEASED record, or None."""
    if ref_type == "lab":
        l = db.session.get(LabReport, ref_id)
        if not l or (patient_id and l.patient_id != patient_id) or l.status not in ("Released", "Completed"):
            return None
        rows = db.session.execute(select(LabResult).where(LabResult.lab_report_id == l.id, LabResult.status != "Superseded").order_by(LabResult.id)).scalars().all()
        sections = []
        if rows:
            sections.append(("Results", [["Test", "Result", "Reference", "Flag"]] + [[r.analyte, f"{_fmt_num(r.value_num if r.value_num is not None else r.value_text)} {r.unit or ''}".strip(),
                            r.ref_text or (f"{r.ref_low:g}-{r.ref_high:g}" if r.ref_low is not None and r.ref_high is not None else ""), r.flag or ""] for r in rows]))
        if l.result:
            sections.append(("Report", l.result))
        fp = _fp({"t": "lab", "id": l.id, "p": l.patient_id, "test": l.test_name, "acc": l.accession_no, "sample": l.sample_date, "result": l.result,
                  "rows": [[r.analyte, r.value_num, r.value_text, r.unit, r.flag] for r in rows], "rel": _ts(l.released_at)})
        return l, sections, f"Laboratory report · sample {l.sample_date or ''}", fp, l.released_at or l.resulted_at, "Laboratory"
    if ref_type == "radiology":
        r = db.session.get(RadiologyRecord, ref_id)
        if not r or (patient_id and r.patient_id != patient_id) or not (r.order_status == "Final" or (r.order_status is None and r.report_status == "Final")):
            return None
        sections = [(h, v) for h, v in (("Findings", r.findings), ("Impression", r.impression), ("Recommendations", r.recommendations)) if v]
        fp = _fp({"t": "rad", "id": r.id, "p": r.patient_id, "mod": r.modality, "date": r.study_date, "desc": r.study_description, "f": r.findings, "i": r.impression,
                  "r": r.recommendations, "auth": _ts(r.authorized_at)})
        return r, sections, f"Imaging report · {r.modality or ''} · {r.study_date or ''}", fp, r.authorized_at or r.reported_at, "Radiology"
    if ref_type == "bill":
        from .orders import bill_figures
        b = db.session.get(Bill, ref_id)
        if not b or (patient_id and b.patient_id != patient_id) or b.status == "Void":
            return None
        f = bill_figures(b)
        sections = [(b.description or f"Bill #{b.id}", [["Item", "Amount"], ["Total", f"{b.total:.2f}"], ["Paid", f"{f['paid']:.2f}"], ["Balance", f"{f['balance']:.2f}"],
                                                       ["Insurance", f"{b.insurance_provider or '-'} · {b.insurance_status or '-'}"]])]
        # only the charges are fingerprinted: later payments must not invalidate an issued invoice
        fp = _fp({"t": "bill", "id": b.id, "p": b.patient_id, "desc": b.description, "c": [b.consultation, b.laboratory, b.pharmacy, b.room, b.other_charges], "at": _ts(b.created_at)})
        return b, sections, "Invoice / receipt", fp, b.created_at, "Billing"
    return None


def make_code(ref_type: str, ref_id: int, fingerprint: str) -> str:
    sig = hmac.new(_key(), f"{ref_type}|{ref_id}|{fingerprint}".encode(), hashlib.sha256).hexdigest()[:20].upper()
    return f"{TYPES[ref_type][0]}{ref_id}-{sig}"


def pretty(code: str) -> str:
    head, sig = code.split("-", 1)
    return head + "-" + " ".join(sig[i:i + 4] for i in range(0, len(sig), 4))


def parse(code: str):
    c = (code or "").strip().upper().replace(" ", "")
    if "-" not in c or len(c) > 40:
        return None
    head, sig = c.split("-", 1)
    if len(head) < 2 or head[0] not in LETTER or not head[1:].isdigit() or len(head) > 12 or len(sig) != 20 or any(ch not in "0123456789ABCDEF" for ch in sig):
        return None
    return LETTER[head[0]], int(head[1:]), sig


def check(code: str):
    """Return a dict describing a genuine match, or None. The caller must not reveal *why* a check failed."""
    parsed = parse(code)
    if not parsed:
        return None
    ref_type, ref_id, sig = parsed
    got = load_released(ref_type, ref_id)
    if not got:
        return None
    rec, _sections, _note, fp, released_at, issuer = got
    expected = make_code(ref_type, ref_id, fp).split("-", 1)[1]
    if not hmac.compare_digest(expected, sig):
        return None
    pt = db.session.get(Patient, rec.patient_id)
    initials = " ".join(w[0].upper() + "." for w in (pt.name or "").split()[:3] if w)
    codeval = pt.patient_code or ""
    return {"type": TYPES[ref_type][1], "released_at": released_at, "issuer": issuer, "patient_initials": initials,
            "patient_ref": ("…" + codeval[-4:]) if len(codeval) > 4 else codeval, "code": pretty(f"{TYPES[ref_type][0]}{ref_id}-{sig}")}


def base_url() -> str:
    cfg = (current_app.config.get("PUBLIC_BASE_URL") or "").rstrip("/")
    if cfg:
        return cfg
    root = request.url_root.rstrip("/")
    if request.headers.get("X-Forwarded-Proto", "").split(",")[0].strip() == "https" and root.startswith("http://"):
        root = "https://" + root[len("http://"):]
    return root


def qr_svg(text: str) -> str:
    import segno
    return segno.make(text, error="m").svg_inline(scale=4, border=2, dark="#000000", light="#ffffff")


def build_copy(d: Deliverable):
    """Everything the printable-copy page needs for one hand-over item. Raises ApiError when there is nothing releasable."""
    if d.ref_type not in TYPES:
        raise ApiError("No downloadable copy is available for this item yet. Ask the front desk.", 404)
    got = load_released(d.ref_type, d.ref_id, d.patient_id)
    if not got:
        raise ApiError("This report has not been released yet" if d.ref_type != "bill" else "Bill not found", 404)
    _rec, sections, note, fp, _rel, _issuer = got
    code = make_code(d.ref_type, d.ref_id, fp)
    url = f"{base_url()}/verify?code={code}"
    return {"title": d.title, "note": note, "sections": sections, "code": pretty(code), "verify_url": url, "qr": qr_svg(url)}
