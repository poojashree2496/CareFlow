"""Patient-aware assistant API. Each request re-checks role permission and the patient-level scopes."""
from __future__ import annotations

from datetime import timedelta

from flask import Blueprint, current_app, g, jsonify
from sqlalchemy import select

from ..access import get_authorized_patient, patient_scopes, require_perm
from ..ai import assistant
from ..ai.providers import ProviderError, get_provider
from ..audit import audit
from ..extensions import db
from ..models import AiConversation, AiMessage, utcnow
from ..security import limiter
from ..utils import ApiError, commit, iso, ok, payload, s

bp = Blueprint("ai", __name__, url_prefix="/api/ai")


def _conv(cid: str) -> AiConversation:
    c = db.session.get(AiConversation, cid)
    if c is None or c.user_id != g.user.id or c.deleted_at is not None:
        raise ApiError("Conversation not found", 404)
    # access to the patient may have been withdrawn since the conversation began
    get_authorized_patient(c.patient_id)
    return c


def _msg(m: AiMessage) -> dict:
    return {"id": m.id, "role": m.role, "content": m.content, "mode": m.mode, "status": m.status, "sources": m.sources or [], "limitations": m.limitations or [],
            "provider": m.provider, "model": m.model, "at": iso(m.created_at)}


@bp.get("/status")
@require_perm("ai.use")
def status():
    cfg = current_app.config
    try:
        p = get_provider(cfg)
        d = p.describe()
        return jsonify(ok=True, configured=True, provider=d["provider"], model=d["model"], external=d["external"],
                       phi_allowed=(not d["external"]) or bool(cfg["AI_ALLOW_EXTERNAL_PHI"]),
                       image_analysis=False, message="" if (not d["external"] or cfg["AI_ALLOW_EXTERNAL_PHI"]) else "External AI is configured but patient data is blocked until AI_ALLOW_EXTERNAL_PHI is enabled by an administrator.")
    except ProviderError as e:
        return jsonify(ok=True, configured=False, provider="", model="", external=False, phi_allowed=False, image_analysis=False, message=e.message)


@bp.post("/conversations")
@require_perm("ai.use")
def create_conversation():
    d = payload()
    pid = int(d.get("patient_id") or 0)
    get_authorized_patient(pid)
    c = AiConversation(user_id=g.user.id, patient_id=pid, title=s(d, "title", 120))
    db.session.add(c)
    audit("ai.conversation_created", category="ai", patient_id=pid, entity_type="ai_conversation")
    commit()
    return ok(conversation_id=c.id)


@bp.get("/conversations")
@require_perm("ai.use")
def list_conversations():
    from flask import request
    pid = request.args.get("patient_id", type=int)
    q = select(AiConversation).where(AiConversation.user_id == g.user.id, AiConversation.deleted_at.is_(None))
    if pid:
        get_authorized_patient(pid)
        q = q.where(AiConversation.patient_id == pid)
    rows = db.session.execute(q.order_by(AiConversation.updated_at.desc()).limit(30)).scalars().all()
    out = []
    for c in rows:
        if "identity" in patient_scopes(g.user, c.patient_id):
            out.append({"id": c.id, "patient_id": c.patient_id, "title": c.title, "updated_at": iso(c.updated_at)})
    return jsonify(ok=True, items=out)


@bp.get("/conversations/<cid>")
@require_perm("ai.use")
def get_conversation(cid):
    c = _conv(cid)
    return jsonify(ok=True, id=c.id, patient_id=c.patient_id, messages=[_msg(m) for m in c.messages])


@bp.delete("/conversations/<cid>")
@require_perm("ai.use")
def delete_conversation(cid):
    c = db.session.get(AiConversation, cid)
    if c is None or c.user_id != g.user.id:
        raise ApiError("Conversation not found", 404)
    c.deleted_at = utcnow()
    for m in list(c.messages):
        db.session.delete(m)
    audit("ai.conversation_deleted", category="ai", patient_id=c.patient_id, entity_type="ai_conversation")
    commit()
    return ok("Conversation deleted")


@bp.post("/conversations/<cid>/ask")
@require_perm("ai.use")
def ask(cid):
    c = _conv(cid)
    d = payload()
    q = s(d, "question", 1500)
    if len(q) < 2:
        raise ApiError("Enter a question")
    mode = d.get("mode") if d.get("mode") in ("simple", "clinical") else "simple"
    if g.user.role == "patient":
        mode = "simple"
    cfg = current_app.config
    if cfg["RATE_LIMIT_ENABLED"] and not limiter.hit(f"ai:{g.user.id}", cfg["AI_RATE_PER_MINUTE"]):
        raise ApiError("You are asking too quickly. Wait a moment and try again.", 429)
    patient = get_authorized_patient(c.patient_id)
    scopes = patient_scopes(g.user, c.patient_id)
    doc_ids = {int(x) for x in (d.get("document_ids") or []) if str(x).isdigit()} or None
    history = [{"role": m.role, "content": m.content} for m in c.messages if m.status in ("ok",) or m.role == "user"]
    res = assistant.run(g.user, patient, scopes, q, mode=mode, history=history, doc_ids=doc_ids)
    audit("ai.query", category="ai", patient_id=c.patient_id, entity_type="ai_conversation", details=f"status={res['status']} mode={mode} sources={len(res['sources'])} provider={res['provider'] or '-'}")
    content = res["answer"] or res.get("evidence_text") or res.get("message") or ""
    if res["notices"]:
        content = "\n".join(res["notices"]) + ("\n\n" + content if content else "")
    c.title = c.title or q[:80]
    db.session.add(AiMessage(conversation_id=c.id, role="user", content=q, mode=mode))
    am = AiMessage(conversation_id=c.id, role="assistant", content=content, mode=mode, status=res["status"], sources=res["sources"], limitations=res["limitations"] + ([res["message"]] if res.get("message") else []),
                   provider=res["provider"], model=res["model"])
    db.session.add(am)
    c.updated_at = utcnow()
    commit()
    out = _msg(am)
    out["answer_is_model_generated"] = res["status"] == "ok"
    if res.get("retry_after"):
        out["retry_after"] = res["retry_after"]
    return jsonify(ok=True, message=out, status=res["status"])


@bp.post("/purge")
@require_perm("config.manage")
def purge():
    """Delete AI conversations older than AI_RETENTION_DAYS."""
    days = current_app.config["AI_RETENTION_DAYS"]
    cutoff = utcnow() - timedelta(days=days)
    old = db.session.execute(select(AiConversation).where(AiConversation.updated_at < cutoff)).scalars().all()
    for c in old:
        db.session.delete(c)
    audit("ai.purge", category="ai", details=f"removed={len(old)} older_than_days={days}")
    commit()
    return ok(f"Removed {len(old)} conversation(s)", removed=len(old))
