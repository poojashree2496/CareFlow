"""Observations, alerts, alert rules, devices, the simulator and the device ingestion boundary."""
from __future__ import annotations

from datetime import timedelta

from flask import Blueprint, current_app, g, jsonify, request
from sqlalchemy import select

from .. import constants as C
from ..access import bulk_scopes, get_authorized_patient, has_perm, patient_scopes, require_perm
from ..audit import audit
from ..extensions import db
from ..models import Alert, AlertRule, AppUser, MonitoringDevice, Observation, ObservationType, Patient, utcnow
from ..services import journey, monitoring
from ..utils import ApiError, commit, iso, need, ok, parse_dt, payload, s, to_float, to_int

bp = Blueprint("monitoring", __name__, url_prefix="/api")


def _obs_row(o: Observation, names=None):
    return {"id": o.id, "type": o.type_code, "label": o.type.label if o.type else o.type_code, "value": o.value_num, "unit": o.unit, "observed_at": iso(o.observed_at),
            "recorded_at": iso(o.recorded_at), "source": o.source, "validation_status": o.validation_status, "recorded_by": (names or {}).get(o.recorded_by_id, ""),
            "supersedes_id": o.supersedes_id, "correction_reason": o.correction_reason, "device_id": o.device_id, "note": o.note}


@bp.get("/observation-types")
def observation_types():
    rows = db.session.execute(select(ObservationType).where(ObservationType.is_active.is_(True)).order_by(ObservationType.code)).scalars()
    return jsonify(ok=True, items=[{"code": t.code, "label": t.label, "unit": t.unit, "decimals": t.decimals, "plausible_min": t.plausible_min, "plausible_max": t.plausible_max} for t in rows])


@bp.get("/patients/<int:pid>/observations")
def list_observations(pid):
    get_authorized_patient(pid, "observations")
    hours = min(24 * 30, max(1, request.args.get("hours", 24, type=int)))
    since = utcnow() - timedelta(hours=hours)
    q = select(Observation).where(Observation.patient_id == pid, Observation.observed_at >= since)
    if request.args.get("type"):
        q = q.where(Observation.type_code == request.args["type"])
    rows = db.session.execute(q.order_by(Observation.observed_at)).scalars().all()
    names = {u.id: u.name for u in db.session.execute(select(AppUser).where(AppUser.id.in_({o.recorded_by_id for o in rows if o.recorded_by_id}))).scalars()} if rows else {}
    series: dict = {}
    for o in rows:
        if o.validation_status in ("Entered in error", "Corrected"):
            continue
        series.setdefault(o.type_code, {"label": o.type.label if o.type else o.type_code, "unit": o.unit, "points": []})["points"].append(
            {"t": iso(o.observed_at), "v": o.value_num, "source": o.source, "id": o.id})
    sources = sorted({o.source for o in rows})
    devices = db.session.execute(select(MonitoringDevice).where(MonitoringDevice.patient_id == pid, MonitoringDevice.is_active.is_(True))).scalars().all()
    return jsonify(ok=True, window_hours=hours, series=series, readings=[_obs_row(o, names) for o in reversed(rows)][:300], latest=journey.latest_vitals(pid),
                   freshness=monitoring.freshness([pid]).get(pid), sources_in_window=sources, contains_simulated="simulated" in sources,
                   mechanism="Values appear when recorded. The screen polls the server; it is not a push/streaming connection.",
                   devices=[{"id": d.id, "name": d.name, "kind": d.kind, "simulated": d.is_simulated, "last_seen_at": iso(d.last_seen_at),
                             "status": ("Simulated feed" if d.is_simulated else ("Connected" if d.last_seen_at and utcnow() - d.last_seen_at < timedelta(minutes=10) else "No recent data"))} for d in devices])


@bp.post("/patients/<int:pid>/observations")
@require_perm("obs.record")
def add_observations(pid):
    p = get_authorized_patient(pid, "observations")
    d = payload()
    values = d.get("values")
    if not isinstance(values, dict) or not values:
        raise ApiError("values must be an object such as {\"heart_rate\": 80}")
    when = parse_dt(d.get("observed_at"), "observed_at")
    obs = monitoring.record_vitals(p, values, user=g.user, observed_at=when, note=s(d, "note", 300))
    commit()
    open_alerts = db.session.execute(select(Alert).where(Alert.patient_id == pid, Alert.status != "Resolved")).scalars().all()
    return jsonify(ok=True, message=f"{len(obs)} reading(s) recorded", ids=[o.id for o in obs], alerts=[journey.alert_row(a) for a in open_alerts])


@bp.post("/observations/<int:oid>/correct")
@require_perm("obs.record")
def correct_obs(oid):
    o = db.session.get(Observation, oid)
    if not o:
        raise ApiError("Observation not found", 404)
    get_authorized_patient(o.patient_id, "observations")
    d = payload()
    need(d, "value", "reason")
    new = monitoring.correct_observation(o, new_value=d["value"], reason=s(d, "reason", 300), user=g.user)
    commit()
    return ok("Correction recorded; the original reading is preserved", id=new.id)


@bp.post("/observations/<int:oid>/withdraw")
@require_perm("obs.record")
def withdraw_obs(oid):
    o = db.session.get(Observation, oid)
    if not o:
        raise ApiError("Observation not found", 404)
    get_authorized_patient(o.patient_id, "observations")
    monitoring.withdraw_observation(o, reason=s(payload(), "reason", 300), user=g.user)
    commit()
    return ok("Reading marked as entered in error")


# ---- alerts ---------------------------------------------------------------
@bp.get("/alerts")
@require_perm("alert.view")
def list_alerts():
    monitoring.run_sweeps()
    q = select(Alert, Patient).join(Patient, Patient.id == Alert.patient_id)
    status = request.args.get("status", "open")
    if status == "open":
        q = q.where(Alert.status != "Resolved")
    elif status != "all":
        q = q.where(Alert.status == status)
    if request.args.get("patient_id"):
        q = q.where(Alert.patient_id == to_int(request.args["patient_id"], "patient_id"))
    rows = db.session.execute(q.order_by(Alert.triggered_at.desc()).limit(300)).all()
    sc = bulk_scopes(g.user, {p.id for _, p in rows})
    out = []
    for a, p in rows:
        if "observations" in sc.get(p.id, ()):
            r = journey.alert_row(a)
            r.update(patient_name=p.name, patient_code=p.patient_code)
            out.append(r)
    order = {"Critical": 0, "Warning": 1, "Info": 2}
    out.sort(key=lambda r: (order[r["severity"]], r["triggered_at"]), reverse=False)
    return jsonify(ok=True, items=out)


def _alert_or_404(aid) -> Alert:
    a = db.session.get(Alert, aid)
    if not a:
        raise ApiError("Alert not found", 404)
    get_authorized_patient(a.patient_id, "observations")
    return a


@bp.post("/alerts/<int:aid>/acknowledge")
@require_perm("alert.act")
def ack_alert(aid):
    monitoring.acknowledge_alert(_alert_or_404(aid), g.user)
    commit()
    return ok("Alert acknowledged")


@bp.post("/alerts/<int:aid>/escalate")
@require_perm("alert.act")
def esc_alert(aid):
    a = _alert_or_404(aid)
    monitoring.escalate_alert(a, g.user, s(payload(), "to_role", 30) or "doctor")
    commit()
    return ok("Alert escalated")


@bp.post("/alerts/<int:aid>/resolve")
@require_perm("alert.act")
def res_alert(aid):
    monitoring.resolve_alert(_alert_or_404(aid), g.user, s(payload(), "note", 300))
    commit()
    return ok("Alert resolved")


@bp.post("/monitoring/sweep")
def sweep():
    if not (has_perm(g.user, "alert.act") or has_perm(g.user, "config.manage")):
        raise ApiError("Not permitted", 403)
    return jsonify(ok=True, **monitoring.run_sweeps(force=True))


# ---- rules ----------------------------------------------------------------
def _rule_row(r: AlertRule):
    return {"id": r.id, "name": r.name, "description": r.description, "rule_kind": r.rule_kind, "type_code": r.type_code, "operator": r.operator, "threshold": r.threshold,
            "severity": r.severity, "window_minutes": r.window_minutes, "cooldown_minutes": r.cooldown_minutes, "active": r.active, "version": r.version,
            "review_status": r.review_status, "reviewed_by": r.reviewed_by, "reviewed_at": iso(r.reviewed_at)}


@bp.get("/alert-rules")
@require_perm("alert.view")
def list_rules():
    rows = db.session.execute(select(AlertRule).order_by(AlertRule.id)).scalars()
    items = [_rule_row(r) for r in rows]
    return jsonify(ok=True, items=items, unreviewed_active=sum(1 for r in items if r["active"] and r["review_status"] != "Reviewed"),
                   notice="Thresholds are configuration, not clinical guidance. They must be set and reviewed by qualified clinical stakeholders before use.")


def _apply_rule(r: AlertRule, d: dict):
    kind = s(d, "rule_kind", 12) or r.rule_kind or "threshold"
    if kind not in ("threshold", "missing"):
        raise ApiError("rule_kind must be threshold or missing")
    r.rule_kind = kind
    if "name" in d:
        r.name = s(d, "name", 120)
    if "description" in d:
        r.description = s(d, "description", 300)
    type_code = s(d, "type_code", 30) if "type_code" in d else r.type_code
    if type_code and not db.session.get(ObservationType, type_code):
        raise ApiError("Unknown observation type")
    r.type_code = type_code or None
    sev = s(d, "severity", 10) or r.severity or "Warning"
    if sev not in C.ALERT_SEVERITIES:
        raise ApiError("severity must be Info, Warning or Critical")
    r.severity = sev
    if kind == "threshold":
        op = s(d, "operator", 3) if "operator" in d else r.operator
        if op not in monitoring.OPS:
            raise ApiError("operator must be one of >, >=, <, <=")
        r.operator = op
        if "threshold" in d:
            r.threshold = to_float(d["threshold"], "threshold")
        if r.threshold is None or not r.type_code:
            raise ApiError("A threshold rule needs an observation type and a threshold")
    else:
        if "window_minutes" in d:
            r.window_minutes = to_int(d["window_minutes"], "window_minutes", 5, 7 * 24 * 60)
        if not r.window_minutes:
            raise ApiError("A missing-data rule needs window_minutes")
    if "cooldown_minutes" in d:
        r.cooldown_minutes = to_int(d["cooldown_minutes"], "cooldown_minutes", 0, 24 * 60)
    if "active" in d:
        r.active = str(d["active"]).lower() in ("1", "true", "yes")


@bp.post("/alert-rules")
@require_perm("alert.configure")
def create_rule():
    d = payload()
    need(d, "name")
    r = AlertRule(created_by_id=g.user.id, review_status="Unreviewed", version=1)
    _apply_rule(r, d)
    db.session.add(r)
    audit("alert_rule.created", category="admin", entity_type="alert_rule", details=r.name)
    commit()
    return ok("Rule created (Unreviewed until a clinical reviewer signs it off)", id=r.id)


@bp.patch("/alert-rules/<int:rid>")
@require_perm("alert.configure")
def update_rule(rid):
    r = db.session.get(AlertRule, rid)
    if not r:
        raise ApiError("Rule not found", 404)
    before = (r.operator, r.threshold, r.type_code, r.severity, r.window_minutes)
    _apply_rule(r, payload())
    if (r.operator, r.threshold, r.type_code, r.severity, r.window_minutes) != before:
        r.version += 1  # any change to the clinical logic is a new version needing fresh review
        r.review_status, r.reviewed_by, r.reviewed_at = "Unreviewed", "", None
    audit("alert_rule.updated", category="admin", entity_type="alert_rule", entity_id=rid, details=f"v{r.version}")
    commit()
    return ok(f"Rule saved as version {r.version}")


@bp.post("/alert-rules/<int:rid>/review")
@require_perm("alert.configure")
def review_rule(rid):
    r = db.session.get(AlertRule, rid)
    if not r:
        raise ApiError("Rule not found", 404)
    d = payload()
    need(d, "reviewed_by")
    r.review_status, r.reviewed_by, r.reviewed_at = "Reviewed", s(d, "reviewed_by", 120), utcnow()
    audit("alert_rule.reviewed", category="admin", entity_type="alert_rule", entity_id=rid, details=f"v{r.version} by {r.reviewed_by}")
    commit()
    return ok("Clinical review recorded")


# ---- devices & simulator --------------------------------------------------
@bp.get("/devices")
@require_perm("config.manage")
def list_devices():
    rows = db.session.execute(select(MonitoringDevice).order_by(MonitoringDevice.id)).scalars()
    return jsonify(ok=True, items=[{"id": d.id, "name": d.name, "kind": d.kind, "patient_id": d.patient_id, "simulated": d.is_simulated, "active": d.is_active,
                                    "key_prefix": d.api_key_prefix, "last_seen_at": iso(d.last_seen_at)} for d in rows])


@bp.post("/devices")
@require_perm("config.manage")
def create_device():
    d = payload()
    need(d, "name", "patient_id")
    get_authorized_patient(to_int(d["patient_id"], "patient_id"), "identity")
    dev, key = monitoring.create_device(name=s(d, "name", 120), kind=s(d, "kind", 60) or "Bedside monitor", patient_id=to_int(d["patient_id"], "patient_id"), user=g.user)
    audit("device.registered", category="admin", entity_type="device", entity_id=dev.id, patient_id=dev.patient_id)
    commit()
    return jsonify(ok=True, message="Device registered. Copy the key now; it is shown only once.", id=dev.id, api_key=key,
                   endpoint="/api/integrations/observations", header="X-Device-Key")


@bp.post("/devices/<int:did>/revoke")
@require_perm("config.manage")
def revoke_device(did):
    dev = db.session.get(MonitoringDevice, did)
    if not dev:
        raise ApiError("Device not found", 404)
    dev.is_active, dev.api_key_hash = False, None
    audit("device.revoked", category="admin", entity_type="device", entity_id=did)
    commit()
    return ok("Device key revoked")


@bp.post("/integrations/observations")
def device_ingest():
    """Device boundary. Authenticated by X-Device-Key (no browser session). Real hardware is NOT connected by default."""
    dev = monitoring.authenticate_device(request.headers.get("X-Device-Key", ""))
    n = monitoring.ingest_from_device(dev, (payload() or {}).get("readings"))
    commit()
    return ok(f"{n} reading(s) accepted", accepted=n)


@bp.post("/patients/<int:pid>/simulate")
@require_perm("sim.run")
def simulate(pid):
    p = get_authorized_patient(pid, "observations")
    if not current_app.config["SIMULATOR_ENABLED"]:
        raise ApiError("The simulator is disabled on this deployment", 403)
    scenario = s(payload(), "scenario", 20) or "stable"
    obs = monitoring.simulate_tick(p, g.user, scenario)
    audit("simulator.tick", category="system", entity_type="patient", entity_id=pid, patient_id=pid, details=f"scenario={scenario} SIMULATED")
    commit()
    return ok(f"{len(obs)} SIMULATED reading(s) generated", scenario=scenario)
