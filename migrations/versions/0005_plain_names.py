"""plain names: drop the " (demo)" suffix from stored names

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-25 20:00:00

Data-only: removes the " (demo)" / " (synthetic)" suffix from names (users, doctors and copies of those names stored on orders), plus the old wording of a few seeded sentences, in every text column and renames the
placeholder registration numbers DEMO-001/DEMO-002. Only exact matches change. Re-running is harmless.
"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


PHRASES = ((" (demo)", ""), (" (synthetic)", ""), ("Synthetic report:", "Report:"), ("Synthetic admission note:", "Admission note:"), ("Synthetic inpatient bill", "Inpatient bill"))


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    for table in insp.get_table_names():
        if table == "alembic_version":
            continue
        for col in insp.get_columns(table):
            if isinstance(col["type"], (sa.String, sa.Text)):
                c = col["name"]
                for old, new in PHRASES:
                    bind.execute(sa.text(f'UPDATE "{table}" SET "{c}" = REPLACE("{c}", :old, :new) WHERE "{c}" LIKE :pat'), {"old": old, "new": new, "pat": f"%{old}%"})
    if "doctor" in insp.get_table_names():
        for old, new in (("DEMO-001", "REG-001"), ("DEMO-002", "REG-002")):
            bind.execute(sa.text("UPDATE doctor SET registration_no = :n WHERE registration_no = :o"), {"o": old, "n": new})


def downgrade():
    raise RuntimeError("Downgrades are not supported. Restore from a backup instead.")
