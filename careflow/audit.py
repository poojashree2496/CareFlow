"""Audit trail. Never log passwords, tokens, connection URIs or clinical payloads."""
from __future__ import annotations

import re

from flask import g, has_request_context, request

from .extensions import db
from .models import AuditLog

_SECRET_PATTERNS = [
    (re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|authorization)\s*[=:]\s*\S+"), r"\1=***"),
    (re.compile(r"(?i)\b(postgres(?:ql)?(?:\+\w+)?|https?)://[^\s:@/]+:[^\s@/]+@"), r"\1://***:***@"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,}\b"), "***jwt***"),
]


def sanitize(text: str, limit: int = 500) -> str:
    text = re.sub(r"[\x00-\x1f\x7f]", " ", str(text or ""))
    for pat, rep in _SECRET_PATTERNS:
        text = pat.sub(rep, text)
    return text[:limit]


def audit(action, *, category="system", entity_type="", entity_id=None, patient_id=None,
          details="", outcome="success", user=None, commit=False):
    """Queue an audit record in the current transaction (or commit it immediately)."""
    u = user if user is not None else (getattr(g, "user", None) if has_request_context() else None)
    entry = AuditLog(
        action=sanitize(action, 120), details=sanitize(details), category=category,
        entity_type=entity_type or "", entity_id=entity_id, patient_id=patient_id, outcome=outcome,
        user_id=getattr(u, "id", None), user_role=getattr(u, "role", "") or "",
    )
    if has_request_context():
        entry.ip = (request.remote_addr or "")[:64]
        entry.request_id = getattr(g, "request_id", "")
    db.session.add(entry)
    if commit:
        db.session.commit()
    return entry


def log(action, details=""):
    """Backward-compatible helper from the original app.py."""
    return audit(action, details=details)
