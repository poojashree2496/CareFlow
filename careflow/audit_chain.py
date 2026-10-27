"""Tamper-evident audit trail.

Every audit row stores `prev_hash` (the previous row's hash) and `entry_hash` = SHA-256 over the previous hash and the
row's own content. Editing a row changes its hash; deleting a row breaks the link of the row after it. `verify()` walks the
chain and reports exactly where it no longer holds.

Honest limits: someone with full database rights who rewrites *every* later row (or removes the newest rows) can hide a
change. To catch that, note the head hash and row count shown by the verify screen somewhere outside the database.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import event, inspect as sa_inspect, select, text
from sqlalchemy.orm import Session

from .extensions import db
from .models import AuditLog, utcnow

GENESIS = "0" * 64
_LOCK_KEY = 7600123  # PostgreSQL advisory lock id: serialises writers so two requests cannot fork the chain


def _ts(dt) -> str:
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")


def _s(v) -> str:
    return "" if v is None else str(v)


def compute_hash(prev_hash: str, row) -> str:
    """`row` is anything with the audit columns as attributes. NOTE: migration 0006 keeps its own copy of this function."""
    data = [prev_hash, _s(row.action), _s(row.details), _s(row.category), _s(row.entity_type), _s(row.entity_id), _s(row.patient_id),
            _s(row.outcome), _s(row.user_id), _s(row.user_role), _s(row.ip), _s(row.request_id), _ts(row.created_at)]
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _chain_new_rows(session, flush_context, instances):
    new = [o for o in session.new if isinstance(o, AuditLog)]
    if not new:
        return
    new.sort(key=lambda o: sa_inspect(o).insert_order or 0)  # the database assigns ids in this same order
    if session.get_bind().dialect.name == "postgresql":
        session.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": _LOCK_KEY})
    prev = session.execute(select(AuditLog.entry_hash).where(AuditLog.entry_hash.is_not(None)).order_by(AuditLog.id.desc()).limit(1)).scalar()
    prev = prev or GENESIS
    for o in new:
        if o.created_at is None:
            o.created_at = utcnow()
        o.prev_hash = prev
        o.entry_hash = prev = compute_hash(prev, o)


event.listen(Session, "before_flush", _chain_new_rows)


def verify(max_issues: int = 20) -> dict:
    """Walk the whole chain in id order."""
    issues, prev, checked, unprotected, first_id, last_id = [], None, 0, 0, None, None
    rows = db.session.execute(select(AuditLog).order_by(AuditLog.id).execution_options(yield_per=1000))
    for (r,) in rows:
        if r.entry_hash is None:
            if prev is not None:
                issues.append({"id": r.id, "problem": "Row has no hash although the chain had already started"})
            else:
                unprotected += 1
            continue
        if first_id is None:
            first_id = r.id
        expected_prev = GENESIS if prev is None else prev
        if r.prev_hash != expected_prev:
            issues.append({"id": r.id, "problem": "Link to the previous entry is broken: an earlier entry was removed or changed" if prev is not None else "The chain does not start at its first entry: earlier entries are missing"})
        if compute_hash(r.prev_hash or "", r) != r.entry_hash:
            issues.append({"id": r.id, "problem": "Content of this entry was modified after it was written"})
        prev, last_id = r.entry_hash, r.id
        checked += 1
    return {"ok": not issues, "checked": checked, "unprotected_before_chain": unprotected, "first_id": first_id, "last_id": last_id,
            "head_hash": prev or GENESIS, "issues": issues[:max_issues], "issue_count": len(issues)}
