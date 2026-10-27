"""Administration: users, security events, audit log, system status."""
from __future__ import annotations

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import func, or_, select

from .. import constants as C
from ..access import has_perm, require_perm
from ..audit import audit
from ..extensions import db
from ..models import AppUser, AuditLog, Doctor, Patient, Ward, utcnow
from ..security import hash_password, validate_password_strength
from ..utils import ApiError, commit, iso, ok, page_args, payload, s, to_int

bp = Blueprint("admin", __name__, url_prefix="/api/admin")
PRIVILEGED = {C.SUPER_ADMIN, C.HOSPITAL_ADMIN}


def _u(u: AppUser) -> dict:
    return {"id": u.id, "email": u.email, "name": u.name, "role": u.role, "role_label": C.ROLE_LABELS[u.role], "is_active": u.is_active, "is_demo": u.is_demo, "doctor_id": u.doctor_id, "patient_id": u.patient_id, "patient_name": u.patient.name if u.patient else None,
            "ward_id": u.ward_id, "ward": u.ward.name if u.ward else None, "must_change_password": u.must_change_password, "locked": bool(u.locked_until and u.locked_until > utcnow()),
            "last_login_at": iso(u.last_login_at), "created_at": iso(u.created_at)}


def _guard_target(target_role: str):
    if target_role in PRIVILEGED and not has_perm(g.user, "user.manage_privileged"):
        audit("access.denied", category="security", outcome="denied", details=f"privileged role management role={target_role}", commit=True)
        raise ApiError("Only a super administrator can manage administrator accounts", 403)


def _check_links(role, doctor_id, ward_id, patient_id=None, exclude_user_id=None):
    if role == C.PATIENT:
        if not patient_id or not db.session.get(Patient, patient_id):
            raise ApiError("A patient account must be linked to an existing patient record")
        taken = db.session.execute(select(AppUser.id).where(AppUser.patient_id == patient_id)).scalars().all()
        if any(t != exclude_user_id for t in taken):
            raise ApiError("That patient already has a portal login", 409)
        if doctor_id or ward_id:
            raise ApiError("A patient account cannot be linked to a doctor profile or ward")
    elif patient_id:
        raise ApiError("Only patient accounts can be linked to a patient record")
    if doctor_id:
        if not db.session.get(Doctor, doctor_id):
            raise ApiError("Unknown doctor profile")
        if role != C.DOCTOR:
            raise ApiError("Only doctor accounts can be linked to a doctor profile")
    if role == C.DOCTOR and not doctor_id:
        raise ApiError("A doctor account must be linked to a doctor profile (required for assignments and scheduling)")
    if ward_id and not db.session.get(Ward, ward_id):
        raise ApiError("Unknown ward")


@bp.get("/users")
@require_perm("user.manage")
def users():
    q = (request.args.get("q") or "").strip().lower()
    stmt = select(AppUser).order_by(AppUser.name)
    if not has_perm(g.user, "user.manage_privileged"):
        stmt = stmt.where(AppUser.role.notin_(tuple(PRIVILEGED)))
    if q:
        stmt = stmt.where(or_(func.lower(AppUser.name).like(f"%{q}%"), func.lower(AppUser.email).like(f"%{q}%")))
    return jsonify(ok=True, items=[_u(u) for u in db.session.execute(stmt.limit(300)).scalars()], roles=[{"id": r, "label": C.ROLE_LABELS[r]} for r in C.ROLES])


@bp.post("/users")
@require_perm("user.manage")
def create_user():
    d = payload()
    email, name, role = s(d, "email", 200).lower(), s(d, "name", 120), s(d, "role", 30)
    if "@" not in email or len(name) < 2:
        raise ApiError("A valid e-mail and name are required")
    if role not in C.ROLES:
        raise ApiError("Unknown role")
    _guard_target(role)
    doctor_id = to_int(d["doctor_id"], "doctor_id") if d.get("doctor_id") else None
    ward_id = to_int(d["ward_id"], "ward_id") if d.get("ward_id") else None
    patient_id = to_int(d["patient_id"], "patient_id") if d.get("patient_id") else None
    _check_links(role, doctor_id, ward_id, patient_id)
    pw = d.get("password") or ""
    validate_password_strength(pw, email=email, name=name)
    if db.session.execute(select(AppUser.id).where(AppUser.email == email)).first():
        raise ApiError("An account with this e-mail already exists", 409)
    u = AppUser(email=email, name=name, role=role, doctor_id=doctor_id, ward_id=ward_id, patient_id=patient_id, password_hash=hash_password(pw), must_change_password=True, created_by_id=g.user.id, password_changed_at=utcnow())
    db.session.add(u)
    db.session.flush()
    audit("user.created", category="admin", entity_type="app_user", entity_id=u.id, details=f"role={role}")
    commit()
    return ok("Account created. The user must change the temporary password at first sign-in.", user=_u(u))


def _target(uid: int) -> AppUser:
    u = db.session.get(AppUser, uid)
    if u is None:
        raise ApiError("User not found", 404)
    _guard_target(u.role)
    return u


@bp.patch("/users/<int:uid>")
@require_perm("user.manage")
def update_user(uid):
    u = _target(uid)
    d = payload()
    role = s(d, "role", 30) or u.role
    if role not in C.ROLES:
        raise ApiError("Unknown role")
    _guard_target(role)
    if u.id == g.user.id and (role != u.role or d.get("is_active") is False):
        raise ApiError("You cannot change your own role or suspend yourself", 409)
    doctor_id = (to_int(d["doctor_id"], "doctor_id") if d.get("doctor_id") else None) if "doctor_id" in d else u.doctor_id
    ward_id = (to_int(d["ward_id"], "ward_id") if d.get("ward_id") else None) if "ward_id" in d else u.ward_id
    if role != C.DOCTOR:
        doctor_id = None
    if role != u.role and C.PATIENT in (role, u.role):
        raise ApiError("A patient login cannot be converted to or from a staff role. Disable it and create a new account instead.", 409)
    _check_links(role, doctor_id, ward_id, u.patient_id, exclude_user_id=u.id)
    changed = []
    if "name" in d and s(d, "name", 120):
        u.name = s(d, "name", 120); changed.append("name")
    if role != u.role:
        changed.append(f"role {u.role}->{role}"); u.role = role; u.session_epoch += 1
    if doctor_id != u.doctor_id:
        u.doctor_id = doctor_id; changed.append("doctor link")
    if ward_id != u.ward_id:
        u.ward_id = ward_id; changed.append("ward"); u.session_epoch += 1
    if "is_active" in d and bool(d["is_active"]) != u.is_active:
        u.is_active = bool(d["is_active"]); u.session_epoch += 1; changed.append("active" if u.is_active else "suspended")
    audit("user.updated", category="admin", entity_type="app_user", entity_id=u.id, details=", ".join(changed) or "no change")
    commit()
    return ok("User updated", user=_u(u))


@bp.delete("/users/<int:uid>")
@require_perm("user.manage")
def delete_user(uid):
    """Remove an account. Accounts that already appear in clinical records or the audit trail cannot be erased
    (that history must stay attributable), so they are disabled and signed out instead."""
    from sqlalchemy.exc import IntegrityError
    u = _target(uid)
    _guard_target(u.role)
    if u.id == g.user.id:
        raise ApiError("You cannot delete your own account", 409)
    email, role = u.email, u.role
    try:
        with db.session.begin_nested():
            db.session.delete(u)
            db.session.flush()
    except IntegrityError:
        db.session.expire_all()
        u = _target(uid)
        u.is_active = False
        u.session_epoch += 1
        audit("user.disabled_instead_of_deleted", category="admin", entity_type="app_user", entity_id=uid, details=f"role={role}")
        commit()
        return ok("This account appears in clinical records or the audit trail, so it can't be erased. It was disabled and signed out instead.", deleted=False, disabled=True)
    audit("user.deleted", category="admin", entity_type="app_user", entity_id=uid, details=f"role={role}")
    commit()
    return ok("Account deleted", deleted=True)


@bp.post("/users/<int:uid>/reset-password")
@require_perm("user.manage")
def reset_password(uid):
    u = _target(uid)
    if u.id == g.user.id:
        raise ApiError("Use the change-password screen for your own account", 409)
    pw = payload().get("password") or ""
    validate_password_strength(pw, email=u.email, name=u.name)
    u.password_hash, u.must_change_password, u.password_changed_at = hash_password(pw), True, utcnow()
    u.session_epoch += 1
    u.failed_logins, u.locked_until = 0, None
    audit("user.password_reset", category="admin", entity_type="app_user", entity_id=u.id)
    commit()
    return ok("Temporary password set. All of the user's sessions were ended.")


@bp.post("/users/<int:uid>/revoke-sessions")
@require_perm("user.manage")
def revoke_sessions(uid):
    u = _target(uid)
    u.session_epoch += 1
    audit("user.sessions_revoked", category="admin", entity_type="app_user", entity_id=u.id)
    commit()
    return ok("Sessions ended")


@bp.post("/users/<int:uid>/unlock")
@require_perm("user.manage")
def unlock(uid):
    u = _target(uid)
    u.failed_logins, u.locked_until = 0, None
    audit("user.unlocked", category="admin", entity_type="app_user", entity_id=u.id)
    commit()
    return ok("Account unlocked")


@bp.get("/audit")
@require_perm("audit.view")
def audit_log():
    page, per = page_args(50, 200)
    stmt = select(AuditLog).order_by(AuditLog.id.desc())
    for key, col in (("category", AuditLog.category), ("outcome", AuditLog.outcome), ("action", AuditLog.action)):
        v = request.args.get(key)
        if v:
            stmt = stmt.where(col == v)
    if request.args.get("patient_id", type=int):
        stmt = stmt.where(AuditLog.patient_id == request.args.get("patient_id", type=int))
    if request.args.get("user_id", type=int):
        stmt = stmt.where(AuditLog.user_id == request.args.get("user_id", type=int))
    total = db.session.execute(select(func.count()).select_from(stmt.subquery())).scalar()
    rows = db.session.execute(stmt.limit(per).offset((page - 1) * per)).scalars().all()
    names = {u.id: u.name for u in db.session.execute(select(AppUser).where(AppUser.id.in_({r.user_id for r in rows if r.user_id} or {0}))).scalars()}
    audit("audit.viewed", category="access", details=f"page={page}")
    commit()
    return jsonify(ok=True, total=total, page=page, per_page=per, items=[{"id": r.id, "at": iso(r.created_at), "action": r.action, "category": r.category, "outcome": r.outcome, "user": names.get(r.user_id, ""),
                                                                         "role": r.user_role, "patient_id": r.patient_id, "entity": f"{r.entity_type}:{r.entity_id}" if r.entity_type else "", "details": r.details, "ip": r.ip} for r in rows])


@bp.get("/security")
@require_perm("security.view")
def security():
    from datetime import timedelta
    since = utcnow() - timedelta(days=7)
    rows = db.session.execute(select(AuditLog.action, func.count(AuditLog.id)).where(AuditLog.category == "security", AuditLog.created_at > since).group_by(AuditLog.action)).all()
    locked = db.session.execute(select(AppUser).where(AppUser.locked_until > utcnow())).scalars().all()
    cfg = current_app.config
    return jsonify(ok=True, last_7_days=dict(rows), locked_accounts=[{"id": u.id, "email": u.email} for u in locked],
                   posture={"demo_mode": cfg["DEMO_MODE"], "environment": cfg["CAREFLOW_ENV"], "session_idle_minutes": cfg["SESSION_IDLE_MINUTES"], "session_absolute_hours": cfg["SESSION_ABSOLUTE_HOURS"],
                            "rate_limiting": cfg["RATE_LIMIT_ENABLED"], "secure_cookies": bool(cfg.get("SESSION_COOKIE_SECURE"))})
