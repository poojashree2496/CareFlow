"""tidy demonstration labels

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-25 19:30:00

Data-only clean-up of the demonstration records created by earlier versions: drops the " (synthetic)" suffix from patient
names, renames the data_origin value to 'demo' and simplifies a few seeded sentences. Rows the user created are untouched
(only exact matches of the old wording change). Re-running is harmless.
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

# (table, column, old, new) - plain substring replacement
REPLACEMENTS = [
    ("patient", "name", " (synthetic)", ""),
    ("app_user", "name", " (synthetic)", ""),
    ("allergy", "reaction", "Rash (synthetic example)", "Rash"),
    ("clinical_note", "body", "Synthetic admission note:", "Admission note:"),
    ("radiology_record", "findings", "Synthetic report:", "Report:"),
    ("bill", "description", "Synthetic inpatient bill", "Inpatient bill"),
    ("patient_deliverable", "title", "Synthetic inpatient bill", "Inpatient bill"),
    ("observation", "note", "synthetic demo data", "demo data"),
    ("observation", "note", "SYNTHETIC", "SIMULATED"),
    ("audit_log", "details", "synthetic demonstration data loaded", "demonstration data loaded"),
    ("audit_log", "details", "SYNTHETIC", "SIMULATED"),
]


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    for table, col, old, new in REPLACEMENTS:
        if table not in tables or col not in {c["name"] for c in insp.get_columns(table)}:
            continue
        bind.execute(sa.text(f'UPDATE "{table}" SET "{col}" = REPLACE("{col}", :old, :new) WHERE "{col}" LIKE :pat'),
                     {"old": old, "new": new, "pat": f"%{old}%"})
    if "patient" in tables:
        bind.execute(sa.text("UPDATE patient SET data_origin = 'demo' WHERE data_origin = 'synthetic'"))


def downgrade():
    raise RuntimeError("Downgrades are not supported. Restore from a backup instead.")
