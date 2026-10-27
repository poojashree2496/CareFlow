"""tamper-evident audit trail: hash chain over audit_log

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-27 20:00:00

Adds prev_hash / entry_hash to audit_log and chains every existing row in id order. The hash function below is a frozen copy
of careflow.audit_chain.compute_hash at the time of this revision (migrations must not depend on application code).
"""
import hashlib
import json
from datetime import timezone

from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None

GENESIS = "0" * 64


def _s(v):
    return "" if v is None else str(v)


def _ts(dt):
    if dt is None:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")


def _hash(prev, r):
    data = [prev, _s(r.action), _s(r.details), _s(r.category), _s(r.entity_type), _s(r.entity_id), _s(r.patient_id),
            _s(r.outcome), _s(r.user_id), _s(r.user_role), _s(r.ip), _s(r.request_id), _ts(r.created_at)]
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def upgrade():
    bind = op.get_bind()
    cols = {c["name"] for c in sa.inspect(bind).get_columns("audit_log")}
    with op.batch_alter_table("audit_log") as b:
        if "prev_hash" not in cols:
            b.add_column(sa.Column("prev_hash", sa.String(64), nullable=True))
        if "entry_hash" not in cols:
            b.add_column(sa.Column("entry_hash", sa.String(64), nullable=True))
    t = sa.table("audit_log", sa.column("id", sa.Integer), sa.column("action"), sa.column("details"), sa.column("category"), sa.column("entity_type"),
                 sa.column("entity_id"), sa.column("patient_id"), sa.column("outcome"), sa.column("user_id"), sa.column("user_role"), sa.column("ip"),
                 sa.column("request_id"), sa.column("created_at", sa.DateTime(timezone=True)), sa.column("prev_hash"), sa.column("entry_hash"))
    prev = GENESIS
    rows = bind.execute(sa.select(t).where(t.c.entry_hash.is_(None)).order_by(t.c.id)).fetchall()
    for r in rows:
        h = _hash(prev, r)
        bind.execute(t.update().where(t.c.id == r.id).values(prev_hash=prev, entry_hash=h))
        prev = h


def downgrade():
    raise RuntimeError("Downgrades are not supported. Restore from a backup instead.")
