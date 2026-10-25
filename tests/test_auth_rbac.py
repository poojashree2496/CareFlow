from sqlalchemy import select

from careflow.extensions import db
from careflow.models import AppUser, AuditLog
from careflow.security import limiter

from conftest import DEMO_PW, DOMAIN


def test_unauthenticated_api_is_rejected(anon):
    for url in ("/api/patients", "/api/bedboard", "/api/labs", "/api/ai/status", "/api/workspaces/doctor", "/api/admin/users"):
        assert anon.get(url).status_code == 401, url


def test_health_is_public_and_real(anon):
    r = anon.get("/health")
    assert r.status_code == 200 and r.json["database"] == "connected"


def test_login_success_and_generic_failure(anon):
    assert anon.login("doctor1").status_code == 200
    a2 = type(anon)(anon.c.application)
    bad_pw = a2.login("doctor1", "wrong-password-1")
    unknown = a2.login("nobody@example.org", "wrong-password-1")
    assert bad_pw.status_code == unknown.status_code == 401
    assert bad_pw.json["error"] == unknown.json["error"]  # no account enumeration


def test_csrf_required_for_state_changes(as_user):
    a = as_user("doctor1")
    r = a.c.post("/api/patients/1/allergies", json={"substance": "x"})  # no token header
    assert r.status_code == 403 and "CSRF" in r.json["error"]


def test_lockout_after_repeated_failures(app, anon):
    for _ in range(app.config["LOGIN_MAX_FAILURES"]):
        anon.login("nurse", "bad-password-123")
    assert anon.login("nurse").status_code == 423  # correct password still refused while locked
    audit_actions = {a.action for a in db.session.execute(select(AuditLog)).scalars()}
    assert "auth.account_locked" in audit_actions


def test_rate_limit_on_login(app, anon):
    app.config["RATE_LIMIT_ENABLED"] = True
    limiter.reset()
    codes = [anon.login("lab", "bad-password-123").status_code for _ in range(app.config["LOGIN_RATE_PER_MINUTE"] + 3)]
    assert 429 in codes


def test_demo_accounts_cannot_sign_in_when_demo_mode_off(app, anon):
    app.config["DEMO_MODE"] = False
    assert anon.login("doctor1").status_code == 401
    assert anon.get("/api/auth/demo-accounts").json["accounts"] == []


def test_existing_demo_session_dies_when_demo_mode_is_switched_off(app, as_user):
    a = as_user("doctor1")
    assert a.get("/api/auth/me").status_code == 200
    app.config["DEMO_MODE"] = False
    assert a.get("/api/auth/me").status_code == 401


def test_session_revocation_by_admin(as_user):
    victim = as_user("nurse")
    admin = as_user("super")
    uid = victim.get("/api/auth/me").json["user"]["id"]
    assert admin.post(f"/api/admin/users/{uid}/revoke-sessions").status_code == 200
    assert victim.get("/api/auth/me").status_code == 401


def test_suspended_user_loses_access_immediately(as_user):
    victim = as_user("lab")
    admin = as_user("super")
    uid = victim.get("/api/auth/me").json["user"]["id"]
    assert admin.patch(f"/api/admin/users/{uid}", {"is_active": False}).status_code == 200
    assert victim.get("/api/labs").status_code == 401


def test_role_permissions_are_enforced_server_side(as_user):
    nurse = as_user("nurse")
    assert nurse.get("/api/admin/users").status_code == 403
    assert nurse.post("/api/admin/users", {"email": "x@y.org", "name": "Xx", "role": "super_admin", "password": "Long-Enough-Pass-1"}).status_code == 403
    assert nurse.get("/api/workspaces/admin").status_code == 403
    assert nurse.get("/api/audit").status_code in (403, 404)
    billing = as_user("billing")
    assert billing.post("/api/labs", {"patient_id": 1, "test_name": "CBC"}).status_code == 403
    pharm = as_user("pharmacist")
    assert pharm.post("/api/prescriptions", {"patient_id": 1, "medicine": "Aspirin 75 mg"}).status_code == 403


def test_workspace_list_only_contains_authorised_workspaces(as_user):
    lab = as_user("lab")
    ids = [w["id"] for w in lab.get("/api/workspaces").json["items"]]
    assert "lab" in ids and "admin" not in ids and "billing" not in ids
    assert lab.get("/api/workspaces/billing").status_code == 403
    assert lab.get("/api/workspaces/lab").status_code == 200


def test_hospital_admin_cannot_create_or_modify_super_admin(as_user):
    admin = as_user("admin")
    r = admin.post("/api/admin/users", {"email": f"evil@{DOMAIN}", "name": "Evil Admin", "role": "super_admin", "password": "Long-Enough-Pass-1"})
    assert r.status_code == 403
    sup_id = db.session.execute(select(AppUser.id).where(AppUser.role == "super_admin")).scalar()
    assert admin.patch(f"/api/admin/users/{sup_id}", {"is_active": False}).status_code == 403


def test_cannot_demote_or_suspend_self(as_user):
    sup = as_user("super")
    me = sup.get("/api/auth/me").json["user"]["id"]
    assert sup.patch(f"/api/admin/users/{me}", {"is_active": False}).status_code == 409
    assert sup.patch(f"/api/admin/users/{me}", {"role": "nurse"}).status_code == 409


def test_new_user_must_change_password_before_anything_else(app, as_user):
    sup = as_user("super")
    r = sup.post("/api/admin/users", {"email": f"newdoc@{DOMAIN}", "name": "New Nurse", "role": "nurse", "password": "Temporary-Pass-77x"})
    assert r.status_code == 200, r.json
    from conftest import Api
    n = Api(app)
    assert n.login(f"newdoc@{DOMAIN}", "Temporary-Pass-77x").status_code == 200
    blocked = n.get("/api/patients")
    assert blocked.status_code == 403 and blocked.json.get("must_change_password")
    assert n.post("/api/auth/password", {"current": "Temporary-Pass-77x", "new": "short"}).status_code == 400
    assert n.post("/api/auth/password", {"current": "Temporary-Pass-77x", "new": "A-Much-Better-Passphrase-9"}).status_code == 200
    assert n.get("/api/patients").status_code == 200


def test_password_policy():
    from careflow.security import validate_password_strength
    from careflow.utils import ApiError
    import pytest
    for bad in ("short", "aaaaaaaaaaaaaaaa", "password1234"[:12], "careflow123"):
        with pytest.raises(ApiError):
            validate_password_strength(bad)
    with pytest.raises(ApiError):
        validate_password_strength("jonathan-smith-1", email="jonathan@x.org")
    validate_password_strength("correct horse battery staple")


def test_security_headers_present(anon):
    r = anon.get("/health/live")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
    assert r.headers.get("X-Request-ID")
