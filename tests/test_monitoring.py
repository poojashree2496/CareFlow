from datetime import timedelta

from sqlalchemy import select

from careflow.extensions import db
from careflow.models import Admission, Alert, CriticalAck, MonitoringDevice, Observation, utcnow
from careflow.services import monitoring


def open_alerts(pid):
    return db.session.execute(select(Alert).where(Alert.patient_id == pid, Alert.status != "Resolved")).scalars().all()


def test_manual_vitals_recorded_with_provenance(as_user, ids):
    n = as_user("nurse")
    maya = ids.patient["Maya Rao"]
    r = n.post(f"/api/patients/{maya}/observations", {"values": {"heart_rate": 82, "temperature": 37.2}})
    assert r.status_code == 200 and len(r.json["ids"]) == 2
    o = db.session.get(Observation, r.json["ids"][0])
    assert o.source == "manual" and o.recorded_by_id == ids.user["nurse"] and o.validation_status == "Valid"


def test_implausible_or_future_or_nonnumeric_values_are_rejected(as_user, ids):
    n = as_user("nurse")
    maya = ids.patient["Maya Rao"]
    for bad in ({"heart_rate": 5000}, {"spo2": 140}, {"temperature": "hot"}, {"heart_rate": "nan"}, {"unknown_type": 1}, {}):
        assert n.post(f"/api/patients/{maya}/observations", {"values": bad}).status_code == 400, bad
    future = (utcnow() + timedelta(hours=2)).isoformat()
    assert n.post(f"/api/patients/{maya}/observations", {"values": {"heart_rate": 80}, "observed_at": future}).status_code == 400


def test_alert_raised_deduplicated_acknowledged_and_resolved(as_user, ids):
    n, d1 = as_user("nurse"), as_user("doctor1")
    maya = ids.patient["Maya Rao"]
    assert n.post(f"/api/patients/{maya}/observations", {"values": {"spo2": 85}}).status_code == 200
    a = open_alerts(maya)
    assert len(a) == 1 and a[0].severity == "Critical" and a[0].rule_snapshot["review_status"] == "Unreviewed"
    assert a[0].from_simulated_data is False
    n.post(f"/api/patients/{maya}/observations", {"values": {"spo2": 84}})
    a = open_alerts(maya)
    assert len(a) == 1 and a[0].occurrences == 2            # one live alert per patient+rule
    aid = a[0].id
    assert n.post(f"/api/alerts/{aid}/resolve", {}).status_code == 400                     # note required
    assert n.post(f"/api/alerts/{aid}/acknowledge").status_code == 200
    assert as_user("billing").post(f"/api/alerts/{aid}/acknowledge").status_code in (403, 404)
    assert as_user("doctor2").post(f"/api/alerts/{aid}/acknowledge").status_code in (403, 404)
    assert d1.post(f"/api/alerts/{aid}/resolve", {"note": "Probe repositioned, repeat reading 97%"}).status_code == 200
    assert d1.post(f"/api/alerts/{aid}/resolve", {"note": "again"}).status_code == 409


def test_seeded_demo_alert_is_labelled_simulated(as_user, ids):
    items = as_user("doctor2").get("/api/alerts").json["items"]
    ravi = [a for a in items if a["patient_id"] == ids.patient["Ravi Menon"]]
    assert ravi and all(a["simulated"] for a in ravi)


def test_alert_listing_respects_patient_access(as_user, ids):
    seen = {a["patient_id"] for a in as_user("nurse").get("/api/alerts?status=all").json["items"]}
    assert ids.patient["Ravi Menon"] not in seen


def test_correction_and_withdrawal_keep_history(as_user, ids):
    n = as_user("nurse")
    maya = ids.patient["Maya Rao"]
    oid = n.post(f"/api/patients/{maya}/observations", {"values": {"heart_rate": 190}}).json["ids"][0]
    assert n.post(f"/api/observations/{oid}/correct", {"value": 90}).status_code == 400
    r = n.post(f"/api/observations/{oid}/correct", {"value": 90, "reason": "Transposed digits"})
    assert r.status_code == 200
    assert db.session.get(Observation, oid).validation_status == "Corrected"
    new = db.session.execute(select(Observation).where(Observation.supersedes_id == oid)).scalar_one()
    assert new.value_num == 90 and new.correction_reason == "Transposed digits"
    assert n.post(f"/api/observations/{oid}/correct", {"value": 91, "reason": "again"}).status_code == 409
    oid2 = n.post(f"/api/patients/{maya}/observations", {"values": {"resp_rate": 20}}).json["ids"][0]
    assert n.post(f"/api/observations/{oid2}/withdraw", {}).status_code == 400
    assert n.post(f"/api/observations/{oid2}/withdraw", {"reason": "Wrong patient"}).status_code == 200
    series = n.get(f"/api/patients/{maya}/observations?hours=1").json["series"]
    assert all(p["id"] != oid2 for p in series.get("resp_rate", {"points": []})["points"])


def test_device_ingestion_boundary(app, as_user, anon, ids):
    sup = as_user("super")
    maya = ids.patient["Maya Rao"]
    r = sup.post("/api/devices", {"name": "Bedside monitor 1", "patient_id": maya})
    assert r.status_code == 200
    key = r.json["api_key"]
    dev = db.session.get(MonitoringDevice, r.json["id"])
    assert dev.api_key_hash and key not in dev.api_key_hash and dev.api_key_prefix == key[:8]
    # device calls carry no browser session and no CSRF token
    c = app.test_client()
    ok = c.post("/api/integrations/observations", json={"readings": [{"type": "heart_rate", "value": 77}]}, headers={"X-Device-Key": key})
    assert ok.status_code == 200 and ok.json["accepted"] == 1
    o = db.session.execute(select(Observation).where(Observation.device_id == dev.id)).scalar_one()
    assert o.source == "device" and o.patient_id == maya
    for bad in ({}, {"X-Device-Key": "cfd_wrong"}, {"X-Device-Key": "nope"}):
        assert c.post("/api/integrations/observations", json={"readings": [{"type": "heart_rate", "value": 70}]}, headers=bad).status_code == 401
    assert c.post("/api/integrations/observations", json={"readings": []}, headers={"X-Device-Key": key}).status_code == 400
    assert c.post("/api/integrations/observations", json={"readings": [{"type": "heart_rate", "value": 9999}]}, headers={"X-Device-Key": key}).status_code == 400
    # a device can only ever write for its own patient (there is no patient_id in the payload)
    assert c.post("/api/integrations/observations", json={"patient_id": ids.patient["Tomas Ek"], "readings": [{"type": "heart_rate", "value": 71}]}, headers={"X-Device-Key": key}).status_code == 200
    assert db.session.execute(select(Observation).where(Observation.patient_id == ids.patient["Tomas Ek"], Observation.device_id == dev.id)).first() is None
    assert sup.post(f"/api/devices/{dev.id}/revoke").status_code == 200
    assert c.post("/api/integrations/observations", json={"readings": [{"type": "heart_rate", "value": 70}]}, headers={"X-Device-Key": key}).status_code == 401


def test_only_config_managers_register_devices(as_user, ids):
    assert as_user("nurse").post("/api/devices", {"name": "x", "patient_id": ids.patient["Maya Rao"]}).status_code == 403
    assert as_user("doctor1").post("/api/devices", {"name": "x", "patient_id": ids.patient["Maya Rao"]}).status_code == 403


def test_simulator_is_labelled_and_can_be_disabled(app, as_user, ids):
    d1 = as_user("doctor1")
    maya = ids.patient["Maya Rao"]
    app.config["SIMULATOR_ENABLED"] = True
    r = d1.post(f"/api/patients/{maya}/simulate", {"scenario": "deteriorating"})
    assert r.status_code == 200 and "SIMULATED" in r.json["message"]
    srcs = {o.source for o in db.session.execute(select(Observation).where(Observation.patient_id == maya, Observation.note != "demo data")).scalars()}
    assert srcs == {"simulated"}
    resp = d1.get(f"/api/patients/{maya}/observations").json
    assert resp["contains_simulated"] is True
    app.config["SIMULATOR_ENABLED"] = False
    assert d1.post(f"/api/patients/{maya}/simulate", {}).status_code == 403


def test_data_freshness_states(as_user, ids):
    maya, tomas = ids.patient["Maya Rao"], ids.patient["Tomas Ek"]
    fr = monitoring.freshness([maya, tomas])
    assert fr[maya]["state"] == "fresh" and fr[tomas]["state"] == "none"
    for o in db.session.execute(select(Observation).where(Observation.patient_id == maya)).scalars():
        o.observed_at = utcnow() - timedelta(hours=20)
    db.session.commit()
    assert monitoring.freshness([maya])[maya]["state"] == "overdue"


def test_missing_data_alert_and_escalations_via_sweep(app, as_user, ids):
    tomas = ids.patient["Tomas Ek"]
    adm = db.session.execute(select(Admission).where(Admission.patient_id == tomas)).scalar_one()
    adm.admitted_at = utcnow() - timedelta(hours=12)
    db.session.commit()
    stats = monitoring.run_sweeps(force=True)
    assert stats["missing_alerts"] >= 1
    assert monitoring.run_sweeps(force=True)["missing_alerts"] == 0               # deduplicated on the next sweep
    # unacknowledged critical alert escalates after the configured time
    ravi_alert = db.session.execute(select(Alert).where(Alert.patient_id == ids.patient["Ravi Menon"], Alert.severity == "Critical")).scalars().first()
    ravi_alert.triggered_at = utcnow() - timedelta(minutes=app.config["ALERT_ESCALATE_MINUTES"] + 5)
    # unacknowledged critical lab result escalates too
    ack = db.session.execute(select(CriticalAck).where(CriticalAck.status == "Pending")).scalars().first()
    ack.created_at = utcnow() - timedelta(minutes=app.config["CRITICAL_ACK_MINUTES"] + 5)
    db.session.commit()
    stats = monitoring.run_sweeps(force=True)
    assert stats["alerts_escalated"] >= 1 and stats["critical_results_escalated"] >= 1
    db.session.expire_all()
    assert db.session.get(Alert, ravi_alert.id).status == "Escalated"


def test_alert_rules_are_configuration_requiring_review(as_user):
    sup = as_user("super")
    rules = sup.get("/api/alert-rules").json
    assert rules["unreviewed_active"] >= 3 and "not clinical guidance" in rules["notice"]
    assert as_user("nurse").post("/api/alert-rules", {"name": "x", "type_code": "spo2", "operator": "<", "threshold": 90, "severity": "Warning"}).status_code == 403
    r = sup.post("/api/alert-rules", {"name": "Custom", "type_code": "spo2", "operator": "<", "threshold": 90, "severity": "Warning"})
    assert r.status_code == 200
    rid = r.json["id"]
    row = [x for x in sup.get("/api/alert-rules").json["items"] if x["id"] == rid][0]
    assert row["review_status"] == "Unreviewed" and row["version"] == 1
    assert sup.patch(f"/api/alert-rules/{rid}", {"threshold": 88}).status_code == 200
    row = [x for x in sup.get("/api/alert-rules").json["items"] if x["id"] == rid][0]
    assert row["version"] == 2 and row["review_status"] == "Unreviewed"     # edits invalidate any earlier review
