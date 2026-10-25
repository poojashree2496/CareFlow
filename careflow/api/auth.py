from flask import Blueprint, current_app, g, jsonify, request, session
from sqlalchemy import or_, select

from ..access import ROLE_PERMS, workspaces_for
from ..audit import audit
from ..constants import ROLE_LABELS
from ..extensions import db
from ..models import AppUser, Notification, utcnow
from ..security import attempt_login, csrf_token, hash_password, logout, validate_password_strength
from ..utils import ApiError, commit, iso, ok, payload
from werkzeug.security import check_password_hash

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
DEMO_PASSWORD_ENV = "DEMO_PASSWORD"


def demo_password() -> str:
    import os
    return os.environ.get(DEMO_PASSWORD_ENV, "CareFlow-Demo-2026!")


def user_payload(u: AppUser) -> dict:
    return {
        "id": u.id, "name": u.name, "email": u.email, "role": u.role, "role_label": ROLE_LABELS[u.role],
        "doctor_id": u.doctor_id, "patient_id": u.patient_id, "ward_id": u.ward_id, "ward": u.ward.name if u.ward else None,
        "is_demo": u.is_demo, "must_change_password": u.must_change_password,
        "workspaces": workspaces_for(u), "permissions": sorted(ROLE_PERMS.get(u.role, [])),
    }


@bp.get("/csrf")
def get_csrf():
    return jsonify(ok=True, csrf=csrf_token())


@bp.post("/login")
def login():
    d = payload()
    user = attempt_login(current_app, d.get("email", ""), d.get("password", ""))
    return jsonify(ok=True, user=user_payload(user), csrf=csrf_token())


@bp.post("/logout")
def do_logout():
    logout()
    return ok("Signed out")


@bp.get("/me")
def me():
    return jsonify(ok=True, user=user_payload(g.user), demo_mode=current_app.config["DEMO_MODE"],
                   environment=current_app.config["CAREFLOW_ENV"], csrf=csrf_token(),
                   simulator_enabled=current_app.config["SIMULATOR_ENABLED"])


def _ensure_demo_patient_login():
    """Databases seeded before the patient portal existed have no demo patient login; create one for a demo patient."""
    from ..models import Patient
    from .. import constants as C
    if db.session.execute(select(AppUser.id).where(AppUser.role == C.PATIENT, AppUser.is_demo.is_(True))).first():
        return
    p = db.session.execute(select(Patient).where(Patient.data_origin == "demo").order_by(Patient.id)).scalars().first()
    if p is None:
        return
    if db.session.execute(select(AppUser.id).where(AppUser.patient_id == p.id)).first():
        return
    db.session.add(AppUser(email="patient1@careflow.demo.example", name=p.name, role=C.PATIENT, patient_id=p.id, password_hash=hash_password(demo_password()),
                           is_demo=True, must_change_password=False, password_changed_at=utcnow()))
    commit()


@bp.get("/demo-accounts")
def demo_accounts():
    """Only exists in explicit demonstration mode. Accounts are real, server-side-authenticated, demo users."""
    if not current_app.config["DEMO_MODE"]:
        return jsonify(ok=True, demo=False, accounts=[])
    _ensure_demo_patient_login()
    rows = db.session.execute(select(AppUser).where(AppUser.is_demo.is_(True), AppUser.is_active.is_(True)).order_by(AppUser.role, AppUser.name)).scalars()
    return jsonify(ok=True, demo=True, password=demo_password(),
                   accounts=[{"email": u.email, "name": u.name, "role": u.role, "role_label": ROLE_LABELS[u.role]} for u in rows])


@bp.post("/password")
def change_password():
    d = payload()
    u = g.user
    if not check_password_hash(u.password_hash, d.get("current", "")):
        audit("auth.password_change_failed", category="security", outcome="denied", commit=True)
        raise ApiError("Current password is incorrect", 403)
    new = d.get("new", "")
    validate_password_strength(new, email=u.email, name=u.name)
    if check_password_hash(u.password_hash, new):
        raise ApiError("New password must differ from the current one")
    u.password_hash = hash_password(new)
    u.password_changed_at = utcnow()
    u.must_change_password = False
    u.session_epoch += 1  # invalidates every other session of this user
    audit("auth.password_changed", category="security")
    commit()
    session["epoch"] = u.session_epoch
    return ok("Password updated")


# ---- notifications ----------------------------------------------------------
@bp.get("/notifications")
def notifications():
    u = g.user
    rows = db.session.execute(
        select(Notification).where(or_(Notification.user_id == u.id, Notification.role == u.role)).order_by(Notification.created_at.desc()).limit(50)
    ).scalars().all()
    # role broadcasts are only shown for patients this user is allowed to see (least privilege)
    from ..access import bulk_scopes
    visible = bulk_scopes(u, {n.patient_id for n in rows if n.patient_id and n.user_id is None})
    rows = [n for n in rows if n.user_id == u.id or n.patient_id is None or n.patient_id in visible]
    return jsonify(ok=True, unread=sum(1 for n in rows if n.read_at is None and n.user_id == u.id),
                   items=[{"id": n.id, "kind": n.kind, "severity": n.severity, "title": n.title, "body": n.body, "patient_id": n.patient_id,
                           "ref_type": n.ref_type, "ref_id": n.ref_id, "created_at": iso(n.created_at), "read": n.read_at is not None, "broadcast": n.user_id is None}
                          for n in rows])


@bp.post("/notifications/read")
def notifications_read():
    u = g.user
    for n in db.session.execute(select(Notification).where(Notification.user_id == u.id, Notification.read_at.is_(None))).scalars():
        n.read_at = utcnow()
    commit()
    return ok("Marked as read")
