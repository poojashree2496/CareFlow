"""Observations, alert rules/alerts, device ingestion boundary and a simulator.

Honesty rules:
  * every observation carries its provenance (manual / device / simulated);
  * simulated readings are never presented as device readings;
  * thresholds are configured data awaiting clinical review - nothing here is a
    universal medical threshold or a diagnosis.
"""
from __future__ import annotations

import hashlib
import hmac
import random
import secrets
import uuid
from datetime import timedelta

from flask import current_app
from sqlalchemy import func, select

from ..audit import audit
from ..constants import OBSERVATION_TYPES
from ..extensions import db
from ..models import (Admission, Alert, AlertRule, AppUser, CriticalAck, MonitoringDevice, Notification, Observation,
                      ObservationType, Patient, utcnow)
from ..utils import ApiError

OPS = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}


def ensure_reference_data():
    """Idempotently load observation types (reference data, not patient data)."""
    existing = {t.code for t in db.session.execute(select(ObservationType)).scalars()}
    for code, label, unit, lo, hi, dec in OBSERVATION_TYPES:
        if code not in existing:
            db.session.add(ObservationType(code=code, label=label, unit=unit, plausible_min=lo, plausible_max=hi, decimals=dec))
    db.session.flush()


def active_admission(patient_id: int):
    return db.session.execute(select(Admission).where(Admission.patient_id == patient_id, Admission.status == "Admitted")).scalar_one_or_none()


# --------------------------------------------------------------------------- #
# Recording
# --------------------------------------------------------------------------- #
def record_observation(patient: Patient, type_code: str, value, *, user=None, observed_at=None, source="manual",
                       device: MonitoringDevice | None = None, note: str = "", group_id: str = "", evaluate: bool = True,
                       validation_status: str | None = None) -> Observation:
    otype = db.session.get(ObservationType, type_code)
    if otype is None or not otype.is_active:
        raise ApiError(f"Unknown observation type '{type_code}'")
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ApiError(f"{otype.label}: value must be a number")
    if v != v or v in (float("inf"), float("-inf")):
        raise ApiError(f"{otype.label}: value must be finite")
    if otype.plausible_min is not None and not (otype.plausible_min <= v <= otype.plausible_max):
        raise ApiError(f"{otype.label}: {v:g} is outside the accepted entry range ({otype.plausible_min:g}-{otype.plausible_max:g} {otype.unit}). Check for a typing error.")
    now = utcnow()
    observed_at = observed_at or now
    if observed_at > now + timedelta(minutes=5):
        raise ApiError("Observation time cannot be in the future")
    adm = active_admission(patient.id)
    obs = Observation(patient_id=patient.id, admission_id=adm.id if adm else None, encounter_id=adm.encounter_id if adm else None,
                      type_code=type_code, value_num=round(v, otype.decimals or 0), unit=otype.unit,
                      observed_at=observed_at, recorded_at=now, source=source, device_id=device.id if device else None,
                      recorded_by_id=getattr(user, "id", None), note=note[:300], group_id=group_id or "",
                      validation_status=validation_status or ("Valid" if source == "manual" and user else "Unverified"))
    db.session.add(obs)
    db.session.flush()
    if evaluate:
        evaluate_observation(obs)
    return obs


def record_vitals(patient: Patient, values: dict, *, user=None, observed_at=None, note: str = "") -> list[Observation]:
    """Record several readings taken together (e.g. a full set of vitals)."""
    gid = str(uuid.uuid4())
    out = []
    for code, val in values.items():
        if val in (None, ""):
            continue
        out.append(record_observation(patient, code, val, user=user, observed_at=observed_at, note=note, group_id=gid))
    if not out:
        raise ApiError("Enter at least one measurement")
    audit("observation.recorded", category="clinical", entity_type="observation", entity_id=out[0].id, patient_id=patient.id, details=f"{len(out)} reading(s), source=manual")
    return out


def correct_observation(obs: Observation, *, new_value, reason: str, user) -> Observation:
    if obs.validation_status in ("Corrected", "Entered in error"):
        raise ApiError("This reading has already been corrected or withdrawn", 409)
    if not reason.strip():
        raise ApiError("A reason is required to correct a recorded observation")
    patient = db.session.get(Patient, obs.patient_id)
    new = record_observation(patient, obs.type_code, new_value, user=user, observed_at=obs.observed_at, source=obs.source,
                             device=None, note="corrected value", group_id=obs.group_id, evaluate=True)
    new.supersedes_id, new.correction_reason = obs.id, reason[:300]
    obs.validation_status = "Corrected"
    audit("observation.corrected", category="clinical", entity_type="observation", entity_id=obs.id, patient_id=obs.patient_id, details=reason)
    return new


def withdraw_observation(obs: Observation, *, reason: str, user):
    if not reason.strip():
        raise ApiError("A reason is required")
    obs.validation_status, obs.correction_reason = "Entered in error", reason[:300]
    audit("observation.withdrawn", category="clinical", entity_type="observation", entity_id=obs.id, patient_id=obs.patient_id, details=reason)


# --------------------------------------------------------------------------- #
# Alerts
# --------------------------------------------------------------------------- #
def _responder(adm):
    if adm and adm.responsible_doctor_id:
        u = db.session.execute(select(AppUser).where(AppUser.doctor_id == adm.responsible_doctor_id, AppUser.is_active.is_(True))).scalar_one_or_none()
        return u
    return None


def _notify(role=None, user_id=None, *, kind, severity, title, body, patient_id=None, ref_type="", ref_id=None):
    db.session.add(Notification(user_id=user_id, role=role, kind=kind, severity=severity, title=title[:200], body=body[:400],
                                patient_id=patient_id, ref_type=ref_type, ref_id=ref_id))


def _snapshot(rule: AlertRule):
    return {"name": rule.name, "type_code": rule.type_code, "operator": rule.operator, "threshold": rule.threshold,
            "severity": rule.severity, "window_minutes": rule.window_minutes, "review_status": rule.review_status}


def raise_alert(rule: AlertRule, patient_id: int, obs: Observation | None, message: str) -> Alert | None:
    adm = active_admission(patient_id)
    existing = db.session.execute(select(Alert).where(Alert.patient_id == patient_id, Alert.rule_id == rule.id, Alert.status != "Resolved")).scalar_one_or_none()
    simulated = bool(obs and obs.source == "simulated")
    if existing:  # de-duplicate: one live alert per patient+rule
        existing.occurrences += 1
        existing.last_triggered_at = utcnow()
        if obs:
            existing.observation_id = obs.id
            existing.message = message[:300]
        return existing
    if rule.severity != "Critical" and rule.cooldown_minutes:
        last = db.session.execute(select(func.max(Alert.resolved_at)).where(Alert.patient_id == patient_id, Alert.rule_id == rule.id)).scalar()
        if last and utcnow() - last < timedelta(minutes=rule.cooldown_minutes):
            return None  # within cooldown after a clinician resolved the previous alert
    responder = _responder(adm)
    alert = Alert(rule_id=rule.id, rule_version=rule.version, rule_snapshot=_snapshot(rule), patient_id=patient_id,
                  admission_id=adm.id if adm else None, observation_id=obs.id if obs else None, severity=rule.severity,
                  message=message[:300], from_simulated_data=simulated, responder_user_id=responder.id if responder else None,
                  responder_role="doctor" if rule.severity == "Critical" else "nurse")
    db.session.add(alert)
    db.session.flush()
    patient = db.session.get(Patient, patient_id)
    tag = " [SIMULATED DATA]" if simulated else ""
    title = f"{rule.severity} alert{tag}: {rule.name}"
    body = f"{patient.patient_code} - {message}"
    _notify(role="nurse", kind="alert", severity=rule.severity, title=title, body=body, patient_id=patient_id, ref_type="alert", ref_id=alert.id)
    if responder:
        _notify(user_id=responder.id, kind="alert", severity=rule.severity, title=title, body=body, patient_id=patient_id, ref_type="alert", ref_id=alert.id)
    audit("alert.raised", category="clinical", entity_type="alert", entity_id=alert.id, patient_id=patient_id, details=f"rule={rule.id} v{rule.version} {rule.severity}", user=None)
    return alert


def evaluate_observation(obs: Observation):
    if obs.validation_status in ("Entered in error",):
        return []
    rules = db.session.execute(select(AlertRule).where(AlertRule.active.is_(True), AlertRule.rule_kind == "threshold", AlertRule.type_code == obs.type_code)).scalars().all()
    raised = []
    for r in rules:
        if r.threshold is None or r.operator not in OPS:
            continue
        if OPS[r.operator](obs.value_num, r.threshold):
            msg = f"{obs.type.label if obs.type else obs.type_code} {obs.value_num:g} {obs.unit} ({r.operator} {r.threshold:g}) [{obs.source}]"
            a = raise_alert(r, obs.patient_id, obs, msg)
            if a:
                raised.append(a)
    return raised


def acknowledge_alert(alert: Alert, user):
    if alert.status == "Resolved":
        raise ApiError("Alert is already resolved", 409)
    if alert.status == "Open" or alert.status == "Escalated":
        alert.status = "Acknowledged"
        alert.ack_by_id, alert.ack_at = user.id, utcnow()
    audit("alert.acknowledged", category="clinical", entity_type="alert", entity_id=alert.id, patient_id=alert.patient_id)


def escalate_alert(alert: Alert, user=None, to_role="doctor"):
    if alert.status == "Resolved":
        raise ApiError("Alert is already resolved", 409)
    alert.status, alert.escalated_at, alert.escalated_to_role = "Escalated", utcnow(), to_role
    patient = db.session.get(Patient, alert.patient_id)
    _notify(role=to_role, kind="alert-escalation", severity=alert.severity, title=f"ESCALATED {alert.severity} alert",
            body=f"{patient.patient_code} - {alert.message}", patient_id=alert.patient_id, ref_type="alert", ref_id=alert.id)
    if alert.responder_user_id:
        _notify(user_id=alert.responder_user_id, kind="alert-escalation", severity=alert.severity, title="Your patient's alert was escalated",
                body=f"{patient.patient_code} - {alert.message}", patient_id=alert.patient_id, ref_type="alert", ref_id=alert.id)
    audit("alert.escalated", category="clinical", entity_type="alert", entity_id=alert.id, patient_id=alert.patient_id, details=f"to={to_role}", user=user)


def resolve_alert(alert: Alert, user, note: str):
    if alert.status == "Resolved":
        raise ApiError("Alert is already resolved", 409)
    if not note.strip():
        raise ApiError("A resolution note is required")
    alert.status, alert.resolved_by_id, alert.resolved_at, alert.resolution_note = "Resolved", user.id, utcnow(), note[:300]
    audit("alert.resolved", category="clinical", entity_type="alert", entity_id=alert.id, patient_id=alert.patient_id, details=note)


_last_sweep = {"t": None}


def run_sweeps(force: bool = False):
    """Missing-data alerts + escalation of unacknowledged critical items.

    There is no background scheduler: sweeps run when dashboards load (throttled to
    once per minute), via POST /api/monitoring/sweep, or from `flask monitor-sweep`
    (suitable for cron / Task Scheduler).
    """
    now = utcnow()
    if not force and _last_sweep["t"] and now - _last_sweep["t"] < timedelta(seconds=60):
        return {"skipped": True}
    _last_sweep["t"] = now
    cfg = current_app.config
    stats = {"missing_alerts": 0, "alerts_escalated": 0, "critical_results_escalated": 0}
    # 1) missing-data rules
    rules = db.session.execute(select(AlertRule).where(AlertRule.active.is_(True), AlertRule.rule_kind == "missing")).scalars().all()
    if rules:
        for adm in db.session.execute(select(Admission).where(Admission.status == "Admitted")).scalars():
            for r in rules:
                window = timedelta(minutes=r.window_minutes or cfg["OBS_EXPECTED_INTERVAL_MIN"])
                q = select(func.max(Observation.observed_at)).where(Observation.patient_id == adm.patient_id, Observation.validation_status.notin_(("Entered in error", "Corrected")))
                if r.type_code:
                    q = q.where(Observation.type_code == r.type_code)
                last = db.session.execute(q).scalar()
                reference = last or adm.admitted_at
                if reference and now - reference > window:
                    if db.session.execute(select(Alert.id).where(Alert.patient_id == adm.patient_id, Alert.rule_id == r.id, Alert.status != "Resolved")).first():
                        continue  # already alerting; a sweep is not a new occurrence
                    label = r.type_code or "any observation"
                    mins = int((now - reference).total_seconds() // 60)
                    if raise_alert(r, adm.patient_id, None, f"No {label} recorded for {mins} min (limit {int(window.total_seconds() // 60)} min)"):
                        stats["missing_alerts"] += 1
    # 2) unacknowledged critical alerts
    cutoff = now - timedelta(minutes=cfg["ALERT_ESCALATE_MINUTES"])
    for a in db.session.execute(select(Alert).where(Alert.severity == "Critical", Alert.status == "Open", Alert.triggered_at < cutoff)).scalars():
        escalate_alert(a, None, "hospital_admin")
        stats["alerts_escalated"] += 1
    # 3) unacknowledged critical results
    cut2 = now - timedelta(minutes=cfg["CRITICAL_ACK_MINUTES"])
    for c in db.session.execute(select(CriticalAck).where(CriticalAck.status == "Pending", CriticalAck.created_at < cut2)).scalars():
        c.status, c.escalated_at, c.escalated_to_role = "Escalated", now, "hospital_admin"
        patient = db.session.get(Patient, c.patient_id)
        _notify(role="hospital_admin", kind="critical-result-escalation", severity="Critical", title="Critical result not acknowledged",
                body=f"{patient.patient_code} - {c.summary}", patient_id=c.patient_id, ref_type=c.source_type, ref_id=c.source_id)
        audit("critical_result.escalated", category="clinical", entity_type=c.source_type, entity_id=c.source_id, patient_id=c.patient_id, user=None)
        stats["critical_results_escalated"] += 1
    db.session.commit()
    return stats


# --------------------------------------------------------------------------- #
# Freshness & trends
# --------------------------------------------------------------------------- #
def freshness(patient_ids) -> dict[int, dict]:
    if not patient_ids:
        return {}
    interval = current_app.config["OBS_EXPECTED_INTERVAL_MIN"]
    rows = db.session.execute(select(Observation.patient_id, func.max(Observation.observed_at)).where(
        Observation.patient_id.in_(list(patient_ids)), Observation.validation_status.notin_(("Entered in error", "Corrected"))
    ).group_by(Observation.patient_id)).all()
    last = {pid: t for pid, t in rows}
    now = utcnow()
    out = {}
    for pid in patient_ids:
        t = last.get(pid)
        if t is None:
            out[pid] = {"state": "none", "age_min": None, "last_at": None, "expected_interval_min": interval}
            continue
        age = int((now - t).total_seconds() // 60)
        state = "fresh" if age <= interval else ("due" if age <= 2 * interval else "overdue")
        out[pid] = {"state": state, "age_min": age, "last_at": t.isoformat().replace("+00:00", "Z"), "expected_interval_min": interval}
    return out


# --------------------------------------------------------------------------- #
# Device integration boundary
# --------------------------------------------------------------------------- #
def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def create_device(*, name, kind, patient_id, user, simulated=False):
    key = "cfd_" + secrets.token_urlsafe(32)
    dev = MonitoringDevice(name=name[:120], kind=kind[:60], patient_id=patient_id, is_simulated=simulated,
                           api_key_hash=hash_key(key), api_key_prefix=key[:8], created_by_id=getattr(user, "id", None))
    db.session.add(dev)
    db.session.flush()
    return dev, key


def authenticate_device(key: str) -> MonitoringDevice:
    if not key or not key.startswith("cfd_"):
        raise ApiError("Invalid device key", 401)
    h = hash_key(key)
    dev = db.session.execute(select(MonitoringDevice).where(MonitoringDevice.api_key_hash == h, MonitoringDevice.is_active.is_(True))).scalar_one_or_none()
    if dev is None or not hmac.compare_digest(dev.api_key_hash or "", h):
        raise ApiError("Invalid device key", 401)
    return dev


def ingest_from_device(dev: MonitoringDevice, readings: list[dict]) -> int:
    if not dev.patient_id:
        raise ApiError("Device is not bound to a patient", 409)
    patient = db.session.get(Patient, dev.patient_id)
    from ..utils import parse_dt
    if not isinstance(readings, list) or not readings or len(readings) > 200:
        raise ApiError("readings must be a list of 1-200 items")
    n = 0
    for r in readings:
        t = parse_dt(r.get("observed_at"), "observed_at") or utcnow()
        if t < utcnow() - timedelta(days=7):
            raise ApiError("observed_at is more than 7 days old")
        record_observation(patient, str(r.get("type", "")), r.get("value"), observed_at=t, source="simulated" if dev.is_simulated else "device",
                           device=dev, evaluate=True)
        n += 1
    dev.last_seen_at = utcnow()
    audit("device.ingest", category="system", entity_type="device", entity_id=dev.id, patient_id=dev.patient_id, details=f"{n} reading(s)", user=None)
    return n


# --------------------------------------------------------------------------- #
# Simulator (demonstration only)
# --------------------------------------------------------------------------- #
BASELINES = {"heart_rate": 78, "bp_systolic": 122, "bp_diastolic": 78, "resp_rate": 16, "spo2": 97, "temperature": 36.8}
DRIFT = {  # per tick for the 'deteriorating' scenario
    "heart_rate": +4, "bp_systolic": -4, "bp_diastolic": -2, "resp_rate": +1, "spo2": -1.2, "temperature": +0.15,
}


def simulate_tick(patient: Patient, user, scenario: str = "stable") -> list[Observation]:
    if not current_app.config["SIMULATOR_ENABLED"]:
        raise ApiError("The monitoring simulator is disabled on this deployment", 403)
    if scenario not in ("stable", "deteriorating", "recovering"):
        raise ApiError("scenario must be stable, deteriorating or recovering")
    dev = db.session.execute(select(MonitoringDevice).where(MonitoringDevice.patient_id == patient.id, MonitoringDevice.is_simulated.is_(True))).scalar_one_or_none()
    if dev is None:
        dev, _ = create_device(name="Simulator", kind="Simulated feed (not a real device)", patient_id=patient.id, user=user, simulated=True)
    rng = random.Random()
    gid = str(uuid.uuid4())
    out = []
    for code, base in BASELINES.items():
        last = db.session.execute(select(Observation.value_num).where(
            Observation.patient_id == patient.id, Observation.type_code == code, Observation.source == "simulated",
            Observation.validation_status != "Entered in error").order_by(Observation.observed_at.desc()).limit(1)).scalar()
        cur = last if last is not None else base
        noise = rng.uniform(-1, 1) * (0.6 if code == "temperature" else 2.0)
        if scenario == "deteriorating":
            cur += DRIFT[code] + noise * 0.3
        elif scenario == "recovering":
            cur += (base - cur) * 0.35 + noise * 0.3
        else:
            cur += (base - cur) * 0.2 + noise * 0.5
        otype = db.session.get(ObservationType, code)
        cur = max(otype.plausible_min, min(otype.plausible_max, cur))
        if code == "temperature":
            cur = round(cur, 1)
        out.append(record_observation(patient, code, cur, user=user, source="simulated", device=dev, group_id=gid, note="SIMULATED", evaluate=True))
    dev.last_seen_at = utcnow()
    return out
