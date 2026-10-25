"""Small shared helpers: API errors, validation and serialisation."""
from __future__ import annotations

import re
from datetime import date, datetime, timezone

from flask import jsonify, request

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ApiError(Exception):
    def __init__(self, message: str, status: int = 400, **extra):
        super().__init__(message)
        self.message, self.status, self.extra = message, status, extra


def payload() -> dict:
    data = request.get_json(silent=True)
    if isinstance(data, dict):
        return data
    return request.form.to_dict() if request.form else {}


def ok(message: str = "", **extra):
    return jsonify(ok=True, message=message, **extra)


def need(data, *keys):
    missing = [k for k in keys if data.get(k) in (None, "") or not str(data.get(k, "")).strip()]
    if missing:
        raise ApiError("Required fields: " + ", ".join(missing))


def s(data, key, maxlen=200, default="") -> str:
    v = data.get(key, default)
    v = "" if v is None else str(v).strip()
    if len(v) > maxlen:
        raise ApiError(f"{key} is too long (max {maxlen} characters)")
    return v


def to_int(v, name="value", minimum=None, maximum=None):
    try:
        i = int(str(v).strip())
    except (TypeError, ValueError):
        raise ApiError(f"{name} must be a whole number")
    if minimum is not None and i < minimum:
        raise ApiError(f"{name} must be at least {minimum}")
    if maximum is not None and i > maximum:
        raise ApiError(f"{name} must be at most {maximum}")
    return i


def to_float(v, name="value", minimum=None, maximum=None):
    try:
        f = float(str(v).strip())
    except (TypeError, ValueError):
        raise ApiError(f"{name} must be a number")
    if f != f or f in (float("inf"), float("-inf")):
        raise ApiError(f"{name} must be a finite number")
    if minimum is not None and f < minimum:
        raise ApiError(f"{name} must be at least {minimum}")
    if maximum is not None and f > maximum:
        raise ApiError(f"{name} must be at most {maximum}")
    return f


def valid_date(v: str, name="date", allow_empty=True) -> str:
    v = (v or "").strip()
    if not v:
        if allow_empty:
            return ""
        raise ApiError(f"{name} is required")
    if not DATE_RE.match(v):
        raise ApiError(f"{name} must be YYYY-MM-DD")
    try:
        date.fromisoformat(v)
    except ValueError:
        raise ApiError(f"{name} is not a real calendar date")
    return v


def valid_time(v: str, name="time") -> str:
    v = (v or "").strip()
    if not TIME_RE.match(v):
        raise ApiError(f"{name} must be HH:MM (24h)")
    return v


def parse_dt(v, name="datetime", allow_empty=True):
    """Parse ISO-8601 text into an aware UTC datetime (naive values are treated as UTC)."""
    if v in (None, ""):
        if allow_empty:
            return None
        raise ApiError(f"{name} is required")
    try:
        dt = datetime.fromisoformat(str(v).strip().replace("Z", "+00:00"))
    except ValueError:
        raise ApiError(f"{name} must be an ISO-8601 date-time")
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)


def iso(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def row(obj, *fields, **renamed):
    """Serialise selected attributes; datetimes become ISO-8601 UTC strings."""
    out = {}
    for f in fields:
        v = getattr(obj, f)
        out[f] = iso(v) if isinstance(v, datetime) else v
    for key, attr in renamed.items():
        v = getattr(obj, attr)
        out[key] = iso(v) if isinstance(v, datetime) else v
    return out


def page_args(default=25, maximum=100):
    try:
        page = max(1, int(request.args.get("page", 1)))
        per = min(maximum, max(1, int(request.args.get("per_page", default))))
    except ValueError:
        raise ApiError("page and per_page must be integers")
    return page, per


def paginate(query, serializer, default=25):
    page, per = page_args(default)
    total = query.order_by(None).count() if hasattr(query, "order_by") else 0
    items = query.limit(per).offset((page - 1) * per).all()
    return {"items": [serializer(i) for i in items], "page": page, "per_page": per, "total": total}


def age_from_dob(dob: str):
    try:
        d = date.fromisoformat(dob)
    except (TypeError, ValueError):
        return None
    t = date.today()
    return t.year - d.year - ((t.month, t.day) < (d.month, d.day))


def commit():
    """Commit; translate constraint violations into a clean 409."""
    from sqlalchemy.exc import IntegrityError, OperationalError

    from .extensions import db
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ApiError("The change conflicts with existing data (duplicate or in-use record).", 409)
    except OperationalError as exc:
        db.session.rollback()
        if "locked" in str(exc).lower():
            raise ApiError("The database is busy with a competing update. Please retry.", 409)
        raise
