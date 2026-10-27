# CareFlow: the DBMS view (schema, constraints, transactions, and how data travels)

This guide covers only the database side of the project: the files that define and use the database, what each module/function does to the data, and the path data takes between browser, application and tables.
Everything here was read from the code in your CareFlow folder. Line numbers point at the class/function line.

Contents
1. The database stack and the files that matter
2. How data travels (the general path)
3. The schema: 48 tables, keys and relationships
4. Integrity rules the database enforces itself
5. Indexes
6. Normalization, and the places that are deliberately denormalized
7. Transactions, locking and concurrency (the ACID part)
8. Data-flow walkthroughs of the important operations
9. How queries are written (joins, subqueries, aggregates)
10. Migrations, schema files, seed data and CLI
11. File and function map
12. What this project does NOT use (be ready for this in a viva)

---------------------------------------------------------------------------------------------------

## 1. The database stack and the files that matter

| Layer | Technology |
|---|---|
| DBMS | PostgreSQL 16 on Supabase (production), SQLite file `hospital.db` (local fallback), same schema on both |
| Driver | psycopg 3 (PostgreSQL), built-in sqlite3 |
| ORM | Flask-SQLAlchemy / SQLAlchemy 2.x (models are Python classes, one per table) |
| Migrations | Alembic via Flask-Migrate, revisions 0001 to 0005 |
| App | Flask (the application layer between browser and database) |

Files ranked by how relevant they are to a DBMS project:

| # | File | Why it matters |
|---|---|---|
| 1 | `careflow/models.py` | The whole schema: every table, column, key, check, unique and partial index |
| 2 | `database/schema_postgresql.sql` | The same schema as plain SQL DDL (48 `CREATE TABLE`, indexes) |
| 3 | `database/supabase/*.sql` | Schema + data + constraints as scripts for the Supabase SQL editor |
| 4 | `database/careflow_mysql.sql` | The same schema and data in MySQL syntax |
| 5 | `migrations/versions/0001..0005` | Version history of the schema (Alembic) |
| 6 | `careflow/services/beds.py` | Row locking, bed allocation, admit/transfer/discharge transactions |
| 7 | `careflow/services/orders.py` | Atomic stock update, bill balance math, lab status rules |
| 8 | `careflow/services/monitoring.py` | Observation inserts, alert rule evaluation, de-duplication |
| 9 | `careflow/api/orders.py` | Lab / radiology / pharmacy / billing SQL through the ORM |
| 10 | `careflow/access.py` | Access control as SQL (`EXISTS` subqueries, `IN` lists) |
| 11 | `careflow/api/reports.py`, `api/workspaces.py` | Aggregate queries (`GROUP BY`, `COUNT`, `SUM`) |
| 12 | `careflow/config.py`, `extensions.py`, `utils.py` | Connection settings, naming convention, `commit()` error mapping |
| 13 | `careflow/audit.py` | The audit table writer |
| 14 | `careflow/seed*.py`, `cli.py` | Loading sample data, health checks |

---------------------------------------------------------------------------------------------------

## 2. How data travels (the general path)

```
 Browser form / button
   |  fetch() JSON  (static/js/api.js)  ----------------------------------->  HTTP request
   v
 Flask route  (careflow/api/*.py)
   |  1. security checks (session, CSRF, permission, patient access)
   |  2. validate input (utils.py: need, s, to_int, valid_date)
   v
 Service function  (careflow/services/*.py)   business rules
   |
   v
 SQLAlchemy Session  (db.session)      <-- the "unit of work": changes are collected in memory
   |   db.session.add(obj)            -> INSERT
   |   obj.field = value              -> UPDATE (tracked automatically)
   |   db.session.execute(select(...))-> SELECT
   |   db.session.flush()             -> sends pending INSERT/UPDATE inside the open transaction
   v
 Database transaction  (BEGIN ... COMMIT)
   |   audit_log INSERT is part of the SAME transaction as the change
   v
 utils.commit()  ->  COMMIT
   |   IntegrityError   -> ROLLBACK, API answers 409 "conflicts with existing data"
   |   OperationalError "locked" (SQLite) -> ROLLBACK, 409 "database busy"
   v
 JSON response  ->  browser re-renders
```

Rules worth quoting:
- **One request = one transaction.** Nothing is saved until `commit()` (`utils.py:150`). If any step raises an error, `security.py`'s error handler does `db.session.rollback()`, so a half-finished operation never reaches the tables.
- **The audit row and the business change succeed or fail together** (`audit.py` adds the `AuditLog` object to the same session).
- **The database is the last line of defence.** The application checks rules first (nice error messages), but unique indexes and CHECK constraints reject bad data even if two requests race or someone bypasses the app.

Connection settings (`config.py`):
- `parse_postgres_url` (119) accepts the `DATABASE_URL`; adds `sslmode=require` for non-local hosts; detects Supabase direct / session pooler (5432) / transaction pooler (6543); on 6543 it sets `prepare_threshold=None` (pooler cannot keep prepared statements).
- Engine options: `pool_pre_ping=True` (test a connection before using it), `pool_recycle=270` s, `pool_size=5`, `pool_timeout=10` s.
- `resolve_database` (216) picks PostgreSQL if `DATABASE_URL` is set, otherwise SQLite. `diagnose_connectivity` (350) is the engine behind `flask db-doctor` (TCP, TLS, login checks).
- SQLite gets `PRAGMA foreign_keys=ON`, WAL journal mode and `busy_timeout=15000` (`careflow/__init__.py`, the `_sqlite_pragmas` listener) so foreign keys are really enforced there too.
- `extensions.py` sets a **naming convention** so every constraint gets a predictable name (`pk_<table>`, `fk_<table>_<col>_<reftable>`, `uq_...`, `ck_...`, `ix_...`). This is what makes migrations reproducible on both databases.

---------------------------------------------------------------------------------------------------

## 3. The schema: 48 tables, keys and relationships

Every table has a surrogate integer primary key `id` (SERIAL in PostgreSQL), except `observation_type` (natural key `code`) and `ai_conversation` (UUID string key). Timestamps use a custom `UTCDateTime` type (`models.py:24`) that stores timezone-aware UTC on PostgreSQL and naive UTC on SQLite.

### 3.1 Tables by domain (class : line in `models.py`)

**Facilities / structure**
`Department` 57, `Ward` 64, `Room` 76, `Bed` 85, `Doctor` 107

**Users and settings**
`AppUser` 118 (login accounts), `SystemSetting` 147

**Patient core**
`Patient` 158, `PatientAssignment` 190 (care relationship), `Allergy` 209, `Problem` 222

**Visits and stays**
`Appointment` 241, `Encounter` 270, `Admission` 286, `BedAssignment` 317

**Clinical documentation**
`ClinicalNote` 343, `CarePlan` 360, `CareTask` 372, `Handover` 394, `IntakeOutput` 415, `FollowUp` 428

**Monitoring and alerts**
`ObservationType` 445, `MonitoringDevice` 456, `Observation` 471, `AlertRule` 498, `Alert` 523, `Notification` 557, `CriticalAck` 575

**Laboratory and radiology**
`LabReport` 601, `LabResult` 635, `RadiologyRecord` 662, `RadiologyReportVersion` 694

**Pharmacy**
`Medicine` 711, `Prescription` 729, `DispenseEvent` 760, `MedicationAdministration` 773, `StockMovement` 791, `MedReconciliation` 804

**Billing**
`Bill` 818, `Payment` 845, `BillAdjustment` 861, `InsuranceClaim` 875

**Documents and hand-over**
`MedicalDocument` 896, `DocumentPage` 960, `Deliverable` 933 (table `patient_deliverable`)

**AI and audit**
`AiConversation` 978, `AiMessage` 990, `AuditLog` 1008

### 3.2 Relationships (the ER diagram in words)

One-to-many (parent -> child):
- `department` 1 - N `ward` 1 - N `room` 1 - N `bed`; `ward` also 1 - N `bed` directly.
- `patient` 1 - N each of: `appointment`, `encounter`, `admission`, `allergy`, `problem`, `clinical_note`, `care_plan`, `care_task`, `handover`, `intake_output`, `follow_up`, `observation`, `alert`, `lab_report`, `radiology_record`, `prescription`, `bill`, `medical_document`, `patient_deliverable`, `audit_log`.
- `doctor` 1 - N `appointment`; `doctor` 1 - N `admission` (responsible doctor).
- `admission` 1 - N `bed_assignment`; `bed` 1 - N `bed_assignment`.
- `lab_report` 1 - N `lab_result`; `radiology_record` 1 - N `radiology_report_version`.
- `prescription` 1 - N `dispense_event`; `prescription` 1 - N `medication_administration`; `medicine` 1 - N `dispense_event`, `stock_movement`, `prescription`.
- `bill` 1 - N `payment`, `bill_adjustment`, `insurance_claim`.
- `medical_document` 1 - N `document_page` (unique on `document_id, page_no`).
- `alert_rule` 1 - N `alert`; `observation_type` 1 - N `observation`, `alert_rule`.
- `ai_conversation` 1 - N `ai_message`.

One-to-one (enforced with UNIQUE on the foreign key):
- `app_user.doctor_id` UNIQUE -> a doctor profile has at most one login.
- `app_user.patient_id` UNIQUE -> a patient has at most one portal login.

Many-to-many (resolved with a junction/bridge table):
- **patient <-> app_user (clinicians)** through `patient_assignment` (extra attributes: `relation` primary/consulting/covering, `active`, `starts_at`, `ends_at`).
- **admission <-> bed over time** through `bed_assignment` (attributes: `started_at`, `ended_at`, `reason`, `end_reason`).

Self-referencing foreign keys (versioning / history):
- `lab_result.supersedes_id -> lab_result.id`, `observation.supersedes_id -> observation.id`, `clinical_note.amends_note_id -> clinical_note.id`, `medical_document.supersedes_id -> medical_document.id`, `app_user.created_by_id -> app_user.id`.

Polymorphic reference (no FK by design): `critical_ack(source_type, source_id)` points at a lab or radiology row, and `patient_deliverable(ref_type, ref_id)` points at a lab/radiology/bill/prescription/admission row. These are protected by a UNIQUE constraint instead of an FK.

Circular dependency: `app_user.patient_id -> patient.id` and `patient.identity_verified_by_id -> app_user.id`. The first FK is created with `use_alter=True` (added after both tables exist).

### 3.3 Two key tables in detail (so you can explain a table end to end)

**`patient`** (`models.py:158`): PK `id`; `patient_code` UNIQUE NOT NULL (format `P-YYMMDD-XXXX`); demographics; legacy free-text `allergies` and `medical_history`; `identifier_label` + `identifier_last4` (only the last 4 characters of an ID are ever stored); `identity_verified*`; consent fields; insurance fields; `data_origin`; `archived_at` (soft delete: archiving sets a timestamp, rows are not removed); `updated_at` auto-set by `onupdate`.

**`app_user`** (`models.py:118`, DDL in `database/schema_postgresql.sql:77`): PK `id`; `email` UNIQUE; `password_hash` (scrypt, never the password); `role` with a CHECK against the nine allowed roles; `doctor_id`, `ward_id`, `patient_id` FKs; security columns `failed_logins`, `locked_until`, `session_epoch`, `must_change_password`. The CHECK `(role = 'patient') = (patient_id IS NOT NULL)` means: a patient login must be linked to a patient, and a non-patient login must not be.

---------------------------------------------------------------------------------------------------

## 4. Integrity rules the database enforces itself

### 4.1 CHECK constraints (value rules)
| Table | Rule |
|---|---|
| `app_user` | `role` in the 9 roles; patient link matches role |
| `bed` | `status` in Available / Occupied / Cleaning / Reserved / Maintenance |
| `clinical_note` | `status` in Final / Superseded |
| `care_task` | `status` in Pending / Done / Cancelled |
| `intake_output` | `kind` in Intake / Output; `amount_ml >= 0` |
| `observation` | `source` in manual / device / simulated; `validation_status` in Valid / Unverified / Corrected / Entered in error |
| `alert_rule` | `rule_kind` in threshold / missing; `severity` in Info / Warning / Critical |
| `alert` | `status` in Open / Acknowledged / Escalated / Resolved |
| `critical_ack` | `status` in Pending / Acknowledged / Escalated |
| `medicine` | `stock >= 0` (stock can never go negative) |
| `dispense_event` | `quantity > 0` |
| `payment` | `amount > 0`; `kind` in Payment / Refund |
| `bill_adjustment` | `amount > 0` |
| `patient_deliverable` | `physical_status` in the four hand-over states |

### 4.2 UNIQUE constraints
`patient.patient_code`, `app_user.email`, `app_user.doctor_id`, `app_user.patient_id`, `lab_report.accession_no`, `medicine.name`, `room(ward_id, label)`, `bed(room_id, label)`, `critical_ack(source_type, source_id)`, `patient_deliverable(patient_id, ref_type, ref_id, kind)`, `document_page(document_id, page_no)`.

### 4.3 PARTIAL UNIQUE INDEXES (the most interesting part for a viva)
A partial unique index is "unique among only the rows that match a condition". They express business rules that a plain UNIQUE cannot.

| Index | SQL | Business rule it enforces |
|---|---|---|
| `uq_appointment_doctor_slot_active` | `UNIQUE (doctor_id, appointment_date, appointment_time) WHERE status IN ('Scheduled','Checked-in')` | A doctor cannot be double-booked, but cancelled/completed slots can be reused |
| `uq_admission_active_patient` | `UNIQUE (patient_id) WHERE status = 'Admitted'` | A patient has at most one current admission |
| `uq_bed_assignment_open_bed` | `UNIQUE (bed_id) WHERE ended_at IS NULL` | A bed holds at most one patient at a time |
| `uq_bed_assignment_open_admission` | `UNIQUE (admission_id) WHERE ended_at IS NULL` | An admission occupies at most one bed at a time |
| `uq_patient_assignment_active` | `UNIQUE (patient_id, user_id) WHERE active` | A clinician can't be on the same patient's team twice |
| `uq_alert_open_patient_rule` | `UNIQUE (patient_id, rule_id) WHERE status <> 'Resolved'` | At most one live alert per patient per rule (de-duplication) |

Models: `models.py` lines 260-266 (appointment), 311-314 (admission), 331-337 (bed_assignment), 203-206 (assignment), 550-553 (alert). SQL: `database/schema_postgresql.sql` lines 292, 403, 475, 516-517, 862.

### 4.4 Foreign keys
Every `*_id` column that references another table is a real FOREIGN KEY. Most "who did it" columns (`created_by_id`, `ordered_by_id`, `verified_by_id`...) point at `app_user.id`, so history stays attributable. A user who appears in clinical rows cannot be deleted: `api/admin.py delete_user` (134) catches the resulting `IntegrityError` inside a SAVEPOINT (`db.session.begin_nested()`) and disables the account instead.

### 4.5 NOT NULL and defaults
Patient identity, order types, link columns (`patient_id`, `bill_id`...) are NOT NULL. Status columns have defaults (`Ordered`, `Scheduled`, `Issued`...) so a new row always starts in a valid state.

---------------------------------------------------------------------------------------------------

## 5. Indexes

- Automatic: PK and UNIQUE constraints each create an index.
- FK-column indexes (`index=True`): e.g. `ix_allergy_patient_id`, `ix_lab_result_lab_report_id`, `ix_bed_assignment_bed_id`, `ix_payment_bill_id`, `ix_notification_user_id`. They speed up joins and "all rows of this parent" lookups.
- Composite indexes for common filters: `ix_appointment_doctor_day (doctor_id, appointment_date)`, `ix_lab_report_patient_status (patient_id, status)`, `ix_prescription_patient_status (patient_id, status)`, `ix_observation_patient_type_time (patient_id, type_code, observed_at)` (vitals charts), `ix_audit_log_created`, `ix_audit_log_patient`, `ix_care_task_due_at`.
- Partial unique indexes listed in 4.3.
- The whole index list is in `database/schema_postgresql.sql` (search `CREATE INDEX`) and in `database/supabase/9_indexes_and_constraints.sql`.

---------------------------------------------------------------------------------------------------

## 6. Normalization, and deliberate denormalization

**What is properly normalized**
- Repeating groups live in child tables: lab values in `lab_result` (not columns on `lab_report`), payments in `payment`, claims in `insurance_claim`, bed history in `bed_assignment`, stock history in `stock_movement`, report versions in `radiology_report_version`, OCR text in `document_page`.
- Reference data is separate: `observation_type` (code, label, unit, plausible range), `department`/`ward`/`room`/`bed` hierarchy.
- `Bill.total` is **not stored**: it is a computed Python property (`models.py:818` area) summing the five charge columns. The outstanding balance is also computed, from `payment` and `bill_adjustment` rows (`services/orders.bill_figures`, 188). Storing derived values would risk them going out of sync (a classic update anomaly).

**Deliberate denormalization / legacy duplicates (be honest about these)**
| Duplicate | Why it exists | How it is kept consistent |
|---|---|---|
| `admission.ward`, `admission.bed` text | Original prototype columns, kept for backward compatibility | `services/beds._sync_legacy` (47) copies the real bed's ward/code on every assign/transfer |
| `lab_report.ordered_by` (name) next to `ordered_by_id` | Legacy | Set together in `create_lab` |
| `prescription.doctor_name` next to `ordered_by_id` | Legacy | Set together in `create_prescription` |
| `lab_report.result` summary text | Legacy display text | Rebuilt from `lab_result` rows by `services/orders.summarize_results` (57) at release and amendment |
| `bill.paid`, `bill.insurance_status`, `bill.insurance_provider` | Legacy flags, fast filtering | Recomputed by `services/orders.refresh_bill_status` (198) after every payment/adjustment/claim change |
| `patient.allergies` free text next to the `allergy` table | Legacy | Both are checked by `medication_warnings` |

Dates: `patient.dob`, `appointment_date/time`, `lab_report.sample_date`, `medicine.expiry_date` are stored as ISO text (`YYYY-MM-DD`, `HH:MM`) because the original prototype did; ISO text sorts and compares correctly. Event timestamps use real timezone-aware `TIMESTAMP`.

Money uses `FLOAT` (`Bill`, `Payment`, `Medicine.unit_price`) and results are rounded to 2 decimals in code. A production system would use `NUMERIC(12,2)`; see section 12.

---------------------------------------------------------------------------------------------------

## 7. Transactions, locking and concurrency (the ACID part)

| Property | Where it shows up in this project |
|---|---|
| **Atomicity** | A request is one transaction. Admission creates `encounter`, `admission`, `bed_assignment`, updates `bed`, inserts `audit_log`, maybe `patient_assignment`; all commit together or all roll back. |
| **Consistency** | CHECK, UNIQUE, partial unique and FK constraints (section 4) make invalid states impossible even under races. |
| **Isolation** | Default PostgreSQL isolation (READ COMMITTED; the code does not change it) plus explicit row locks and atomic updates below. |
| **Durability** | PostgreSQL write-ahead log; SQLite WAL mode. |

### 7.1 Pessimistic row lock: `SELECT ... FOR UPDATE`
`services/beds._lock_bed` (21): `select(Bed).where(Bed.id == bed_id).with_for_update()`. Used before allocating or changing a bed, so two staff members cannot take the same bed. (SQLite has no row locks; SQLAlchemy omits `FOR UPDATE` there, and the partial unique indexes still protect correctness.)

### 7.2 Deadlock avoidance
`services/beds.transfer` (111) locks the old and new bed **in ascending id order** (`sorted([old.bed_id, new_bed_id])`). Two simultaneous transfers (A->B and B->A) therefore lock in the same order and cannot deadlock.

### 7.3 Atomic conditional update (optimistic style)
`services/orders.dispense` (137) and `adjust_stock` (174):
```sql
UPDATE medicine SET stock = stock - :q WHERE id = :id AND stock >= :q;
-- rowcount must be 1, otherwise "Insufficient stock"
```
The check and the update are one statement, so two pharmacists dispensing the last box at once cannot both succeed (no lost update). The `CHECK (stock >= 0)` is the backstop.

### 7.4 Constraint-as-lock (let the database arbitrate)
Booking, bed allocation, active admission and alert de-duplication rely on partial unique indexes. Two racing inserts: one wins, the other raises `IntegrityError`; `_flush_or_conflict` (`services/beds.py:34`) or `utils.commit()` turns it into HTTP 409 with a friendly message.

### 7.5 Savepoint
`api/admin.py delete_user` (134): `with db.session.begin_nested():` (SQL `SAVEPOINT`) tries the DELETE; on `IntegrityError` it rolls back only to the savepoint, then disables the user and commits.

### 7.6 Append-only ledgers and versioning (no destructive updates)
- `stock_movement`: every stock change inserts a row with `delta` and `balance_after` (`models.py:791`).
- `payment`: refunds are new rows with `kind = 'Refund'`, not edits.
- Corrections create a new row and mark the old one: `lab_result.status = 'Superseded'` + `version`, `observation.validation_status = 'Corrected'`, `clinical_note.status = 'Superseded'`, `radiology_report_version` rows.
- `audit_log` is insert-only from the application.

---------------------------------------------------------------------------------------------------

## 8. Data-flow walkthroughs (browser -> route -> service -> SQL -> response)

Each shows the tables touched, in the order the operations happen. All inside one transaction unless stated.

### 8.1 Register a patient
`POST /api/patients` -> `api/patients.py create_patient` (98)
1. `SELECT ... FROM patient WHERE lower(name)=? AND dob=?` (duplicate warning).
2. `next_patient_code` (28): `SELECT id FROM patient WHERE patient_code=?` (collision check).
3. `INSERT INTO patient`.
4. If a doctor/nurse registered: `INSERT INTO patient_assignment` (this row is what later lets them see the patient).
5. `INSERT INTO audit_log`. 6. `COMMIT`. Response: id + code.

### 8.2 Book an appointment
`POST /api/appointments` -> `api/scheduling.py create_appointment` (115)
1. `SELECT patient` (access check), `SELECT doctor`.
2. `_validate_slot` (96): `SELECT appointment ... WHERE doctor_id, date, time, status IN ('Scheduled','Checked-in')`.
3. `INSERT INTO appointment`; `INSERT INTO audit_log`; `COMMIT`.
4. If another booking took the slot between steps 2 and 3, the unique partial index raises `IntegrityError` -> 409.

### 8.3 Admit a patient with a bed
`POST /api/admissions` -> `api/beds.py create_admission` (263) -> `services/beds.admit` (68)
1. `SELECT admission WHERE patient_id AND status='Admitted'` (guard).
2. `SELECT bed WHERE id=? FOR UPDATE` (lock).
3. `INSERT encounter` (type Inpatient) -> flush to get its id.
4. `INSERT admission` (`discharge_status='None'`, status `Admitted`) -> flush (partial unique index checks one active admission).
5. `_occupy` (55): check bed status is Available/Reserved; `SELECT bed_assignment WHERE bed_id AND ended_at IS NULL`; `INSERT bed_assignment`; `UPDATE bed SET status='Occupied'`; `UPDATE admission SET ward, bed` (legacy sync); flush.
6. `INSERT audit_log`; `INSERT patient_assignment` for the responsible doctor's login; `COMMIT`.
Tables touched: encounter, admission, bed, bed_assignment, audit_log, patient_assignment.

### 8.4 Transfer a bed
`transfer` (111): lock both beds (ordered) -> `UPDATE bed_assignment SET ended_at, end_reason='Transfer'` on the old row -> `UPDATE bed SET status='Cleaning'` (old) -> `_occupy` new bed (`INSERT bed_assignment`, `UPDATE bed` Occupied) -> audit -> COMMIT. The history table keeps every move.

### 8.5 Discharge
`discharge/plan` -> `UPDATE admission` (plan, status Planned). `discharge/authorize` -> `UPDATE admission` (summary, Authorized, who/when). `discharge/complete` (`services/beds.complete_discharge` 159) -> end the open `bed_assignment`, `UPDATE bed` -> Cleaning, `UPDATE admission` -> Discharged, `UPDATE encounter` -> Closed, `UPDATE care_task` Pending -> Cancelled, `UPDATE alert` open -> Resolved, upsert `patient_deliverable`, audit, COMMIT. One transaction, so a discharge is never half-done.

### 8.6 Lab order to patient portal
1. Doctor `POST /api/labs` -> `INSERT lab_report` (`status='Ordered'`, `ordered_by_id`, admission link from `SELECT admission` active).
2. Lab `collect` -> `UPDATE lab_report` (status, collected_at, accession_no UNIQUE).
3. `receive` -> `UPDATE lab_report`.
4. `PUT results` -> `INSERT lab_result` rows (flag computed in Python from ranges the lab supplied; status Entered); `UPDATE lab_report` status Resulted.
5. `verify` -> `UPDATE lab_report` Verified.
6. `release` (`api/orders.py _do_release` 266) -> `UPDATE lab_report` Released; `UPDATE lab_result` Entered -> Final; `UPDATE lab_report.result` summary text; if critical: `INSERT critical_ack` (UNIQUE source_type+source_id) + 2 `INSERT notification`; `UPDATE medical_document SET patient_visible=true` for attached files; upsert `patient_deliverable`; audit; COMMIT.
7. Patient `GET /api/portal/overview` -> `SELECT lab_report WHERE patient_id=? AND status IN ('Released','Completed')` + `SELECT lab_result WHERE status<>'Superseded'`.
8. Amendment: `INSERT lab_result` (version+1, supersedes_id = old id), `UPDATE` old row to Superseded, `UPDATE critical_ack` back to Pending if still critical.

### 8.7 Prescription to dispense to administration
1. Order: `SELECT allergy`, `SELECT prescription` (active, for duplicate/interaction check) -> `INSERT prescription` (warnings stored as JSON, override reason).
2. Verify: re-run checks, `UPDATE prescription` Verified.
3. Dispense (`services/orders.dispense`): `SELECT` checks -> atomic `UPDATE medicine SET stock = stock - q WHERE stock >= q` -> `INSERT stock_movement` -> `INSERT dispense_event` -> `UPDATE prescription` (dispensed_quantity, status) -> upsert `patient_deliverable` -> audit -> COMMIT.
4. Nurse administers: `INSERT medication_administration` (identity and allergy-check booleans, dose, who, when).
Three different facts, three different tables: ordered (`prescription`), handed out (`dispense_event`), actually given (`medication_administration`).

### 8.8 Vital signs to alert
`POST /api/patients/<id>/observations` -> `services/monitoring.record_vitals` (78)
1. For each value: `SELECT observation_type` (range check), `SELECT admission` (active), `INSERT observation` (source, recorder, group_id).
2. `evaluate_observation` (166): `SELECT alert_rule WHERE active AND rule_kind='threshold' AND type_code=?`; compare in Python.
3. `raise_alert` (133): `SELECT alert WHERE patient_id AND rule_id AND status<>'Resolved'`. If found: `UPDATE alert SET occurrences = occurrences+1`. Else `INSERT alert` (with a JSON snapshot of the rule) + `INSERT notification` (role nurse, and the responsible doctor's user) + `INSERT audit_log`. The partial unique index `uq_alert_open_patient_rule` guarantees one live alert even under a race.
4. `COMMIT`; response lists the open alerts.
Later: `run_sweeps` (216) does `SELECT MAX(observed_at) ... GROUP BY` style freshness checks and `UPDATE alert/critical_ack` escalations.

### 8.9 Billing: bill, payment, refund
- Create: `INSERT bill` (five charge columns), upsert `patient_deliverable`, audit.
- From admission: `SELECT admission`, `SELECT ward` (daily_rate) -> `INSERT bill` with `room = days x rate`.
- Payment: `SELECT payment`, `SELECT bill_adjustment` to compute balance (`bill_figures`) -> reject if amount > balance -> `INSERT payment (kind='Payment')` -> `UPDATE bill SET paid, insurance_status` (`refresh_bill_status`).
- Refund: `INSERT payment (kind='Refund')` after checking `amount <= paid`; admins only.
- Balance formula: `total - SUM(adjustment.amount) - (SUM(payment where kind=Payment) - SUM(payment where kind=Refund))`.

### 8.10 Audit write path
Any route -> `audit()` (`audit.py:32`) -> `db.session.add(AuditLog(...))` (secrets scrubbed first) -> flushed with the same `COMMIT`. If the operation fails, the audit row rolls back with it; denied attempts are written with `commit=True` in their own transaction so they survive.

### 8.11 Document upload
`POST /api/patients/<id>/documents` -> validate (magic bytes) -> file bytes go to storage (local folder or Supabase bucket, **not** the DB) -> `INSERT medical_document` (path, SHA-256, size, mime) -> `INSERT/UPDATE document_page` rows (extracted text per page) -> audit -> COMMIT. The database stores metadata and text; the file itself lives in object storage.

---------------------------------------------------------------------------------------------------

## 9. How queries are written

All queries are built with SQLAlchemy `select()`; the generated SQL uses parameter binding (no string concatenation), which prevents SQL injection.

**Joins**: e.g. `select(LabReport, Patient).join(Patient, Patient.id == LabReport.patient_id)` for work queues (`api/workspaces.py lab` 141); bedboard joins `bed_assignment -> admission -> patient` (`api/beds.py bedboard` 146).

**Correlated subqueries (`EXISTS`)**: access control as SQL. `access.visible_patient_filter` builds, for a doctor, `EXISTS(patient_assignment ...) OR EXISTS(admission where responsible_doctor_id ...) OR EXISTS(appointment ...) OR EXISTS(encounter ...)`, so a patient list returns only allowed rows. Similar for nurse (assignment OR current bed in her ward via a 3-table join) and lab/pharmacy/radiology staff (`EXISTS` an order for that patient).

**Batch lookups instead of N+1**: `access.bulk_scopes` (about line 120) takes a list of patient ids and runs a handful of `WHERE patient_id IN (...)` queries for the whole page rather than one query per patient. Lists then filter in Python with the resulting scope sets.

**Aggregates / GROUP BY** (`api/reports.py _build` 30): bed counts per ward (`SELECT status, COUNT(*) ... GROUP BY status`), admissions and appointments by status, billing totals (`SUM(amount) GROUP BY kind`), prescriptions and radiology by status, lab turnaround (released_at - ordered_at, median computed in Python). `api/workspaces.py` uses `COUNT ... GROUP BY` for the lab, radiology and admin dashboards.

**Pagination**: `LIMIT/OFFSET` via `page_args`.

**Search**: `ILIKE '%q%'` on name, patient_code, phone (`api/patients.py list_patients` 79).

**Time-window queries**: observation charts use `WHERE patient_id=? AND observed_at >= now - N hours` (uses `ix_observation_patient_type_time`).

---------------------------------------------------------------------------------------------------

## 10. Migrations, schema files, seed data and CLI

**Alembic revisions** (`migrations/versions/`)
| Revision | What it does |
|---|---|
| 0001 `legacy_baseline` | Recreates the ten tables of the original prototype; idempotent (skips tables that exist) |
| 0002 `careflow_core` | The big one: adds the rest of the 48 tables and the new columns/indexes/constraints (about 240 operations) |
| 0003 `patient_portal` | `app_user.patient_id` + patient role, `medical_document.patient_visible`, `patient_deliverable` table with back-fill |
| 0004 `demo_labels` | Data-only text clean-up |
| 0005 `plain_names` | Data-only name clean-up |

Downgrades are not supported (they raise an error) to avoid accidental data loss. Commands: `python -m flask --app app db upgrade`, `db current`, `db-status` (compare DB revision with script head, `cli.py:162`). The table `alembic_version` stores the current revision.

**Plain SQL files** (for submitting/inspecting the DDL)
- `database/schema_postgresql.sql`: 48 `CREATE TABLE` + indexes (PostgreSQL). `database/schema.sql`: same for SQLite. `database/careflow_mysql.sql`: schema + data in MySQL syntax (7,930 lines).
- `database/supabase/`: `1_schema.sql` (tables), `2_data_part1..4.sql` (INSERTs), `9_indexes_and_constraints.sql` (PKs, FKs, indexes), run in that order in the Supabase SQL editor. Result: 246 patients, 76 users, etc.

**Seed data**: `careflow/seed.py` (base demo), `seed_more.py`, `seed_bulk.py`, `seed_staff.py`; loaded by `flask seed-demo`, `add-sample-patients`, `add-bulk-patients`, `add-sample-staff` (`cli.py` 45-105). All demo patient rows carry `data_origin='demo'`.

**Operational commands**: `db-doctor` (connectivity), `db-status`, `init-reference-data` (loads `observation_type`), `monitor-sweep`, `purge-ai`, `create-admin`.

---------------------------------------------------------------------------------------------------

## 11. File and function map (DBMS-relevant only)

| Topic | File : line |
|---|---|
| All table definitions | `careflow/models.py` : classes listed in 3.1 |
| Timestamp type | `careflow/models.py` : UTCDateTime 24 |
| Constraint naming convention, `db`, `migrate` objects | `careflow/extensions.py` |
| DB URL parsing, SSL, pooler detection, pool options | `careflow/config.py` : parse_postgres_url 119, resolve_database 216, build_config 242, diagnose_connectivity 350 |
| SQLite pragmas | `careflow/__init__.py` : _sqlite_pragmas listener (top of file) ; schema revision check schema_status 62 |
| Commit + error mapping | `careflow/utils.py` : commit 150 |
| Audit insert | `careflow/audit.py` : audit 32 |
| Access filtering as SQL | `careflow/access.py` : visible_patient_filter, bulk_scopes, patient_scopes, get_authorized_patient |
| Bed lock, occupy, admit, transfer, discharge | `careflow/services/beds.py` : _lock_bed 21, _flush_or_conflict 34, _occupy 55, admit 68, assign_bed 100, transfer 111, plan_discharge 137, authorize_discharge 147, complete_discharge 159, set_bed_status 191 |
| Atomic stock, dispense, bill math | `careflow/services/orders.py` : dispense 137, adjust_stock 174, bill_figures 188, refresh_bill_status 198, lab_transition 40, compute_flag 22 |
| Observations and alerts | `careflow/services/monitoring.py` : record_observation 47, record_vitals 78, evaluate_observation 166, raise_alert 133, run_sweeps 216, freshness 268 |
| Lab / radiology / pharmacy / billing endpoints | `careflow/api/orders.py` : see `CAREFLOW_FLOW_BY_ROLE.md` section 11 |
| Patient, appointment, admission endpoints | `careflow/api/patients.py`, `api/scheduling.py`, `api/beds.py` |
| Aggregate reports | `careflow/api/reports.py` : _build 30 |
| Dashboard queries | `careflow/api/workspaces.py` |
| Savepoint example | `careflow/api/admin.py` : delete_user 134 |
| Schema as SQL | `database/schema_postgresql.sql` (app_user line 77, admission 446, bed_assignment 498, lab_report 658, prescription 751, bill 520, payment 1058, alert 826) |
| Migration history | `migrations/versions/0001_...py` to `0005_...py` |
| Loading data | `careflow/seed.py`, `seed_more.py`, `seed_bulk.py`, `seed_staff.py`, `cli.py` |

---------------------------------------------------------------------------------------------------

## 12. What this project does NOT use (know this before a viva)

I searched the SQL files and the code for these; none exist:
- **No triggers, no stored procedures, no database functions, no views.** All business logic lives in Python services. The "trigger-like" behaviour (status transitions, balance recalculation, legacy column sync) is done in application code inside the same transaction.
- **No separate `queries.sql`** with sample SELECTs for demonstration. The queries exist only as SQLAlchemy code (section 9). If your course expects raw SQL queries, views and triggers, those would have to be added.
- **No explicit isolation level setting** (PostgreSQL default READ COMMITTED is used) and no `SERIALIZABLE` retry loop.
- **Money stored as FLOAT**, not `NUMERIC(12,2)`. Rounding is done in code; `NUMERIC` would be the textbook-correct choice.
- **Dates such as `dob`, `appointment_date`, `sample_date` are text** (ISO strings), not `DATE` columns, inherited from the original prototype.
- **Some legacy duplicate columns** (section 6) trade strict normalization for backward compatibility.
- **No row-level security (RLS) policies** in the database; access control is enforced in the application layer (`access.py`). The Supabase service connects with one database user.
- **Files are not stored in the database**; only their metadata and extracted text are.
- **Polymorphic references** (`critical_ack`, `patient_deliverable`) have no foreign key because they point at several different tables.
