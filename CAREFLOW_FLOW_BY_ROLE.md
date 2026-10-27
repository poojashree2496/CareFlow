# CareFlow: how every role works, feature by feature

Written from the actual code in your CareFlow folder (the version after the audit-chain / QR changes were reverted).
Every function, route, permission and rule below is something I read in the source. Where something is *not* built, I say so.

Contents
1. The big picture: how a click travels through the system
2. Shared foundations (login, sessions, permissions, scopes, audit, notifications)
3. Roles at a glance
4. Role-by-role flows
   - Super Administrator
   - Hospital Administrator
   - Doctor
   - Nurse
   - Laboratory Staff
   - Radiology Staff
   - Pharmacist
   - Billing & Insurance
   - Patient
5. Cross-role end-to-end journeys
6. State machines (allowed status changes)
7. Alerts, critical results and escalation timers
8. The AI assistant pipeline
9. Documents, OCR and storage
10. Honest limits and things that are not built

---------------------------------------------------------------------------------------------------

## 1. The big picture: how a click travels through the system

```
Browser (static/js/*.js)
   |  api.js: fetch(url, {method, headers: X-CSRF-Token, JSON body, cookies})
   v
Flask app (careflow/__init__.py: create_app)
   |
   |-- security.py  @before_request  (runs on EVERY request, in this order)
   |      1. new request id
   |      2. load_user_from_session  (idle 30 min / absolute 12 h / session_epoch / active / demo-mode check)
   |      3. rate limit: 600 API calls per minute per user (or per IP if not signed in)
   |      4. CSRF check on every POST/PUT/PATCH/DELETE under /api/ (except /api/integrations/ = devices)
   |      5. "not signed in -> 401" unless the path is public (login, csrf, health, demo-accounts)
   |      6. patient accounts may ONLY call /api/auth, /api/portal, /api/ai, /api/workspaces
   |      7. must_change_password -> only the password / me / logout / csrf endpoints work
   v
Route function in careflow/api/<module>.py
   |-- @require_perm("x.y")   -> does the ROLE hold this permission?  (access.py ROLE_PERMS)
   |-- get_authorized_patient(pid, "scope")  -> does THIS USER have a care relationship with THIS
   |        PATIENT and the right data scope?  (404 = no relationship, 403 = missing scope)
   |-- validation helpers (utils.py: need, s, to_int, valid_date ...)
   v
Service layer (careflow/services/*.py)  business rules and state machines
   |     e.g. beds.admit, orders.dispense, monitoring.record_observation
   v
SQLAlchemy models (careflow/models.py)  ->  PostgreSQL (Supabase) / SQLite
   |
   |-- audit(...)   queued into the SAME transaction as the change
   |-- Notification rows (for people / roles) when something needs attention
   v
commit()  ->  JSON {ok: true/false, ...}  ->  api.js  ->  UI re-render
```

Key idea: **the browser is never trusted**. Role, patient id and workspace name sent by the browser are re-checked on the server every single time.

Front end shell (static/js/app.js, boot()):
1. `GET /api/auth/me` returns the user, role, permissions and workspace list.
2. Patients get `renderPortal` only. Staff get `GET /api/workspaces`, then one tab per workspace.
3. Each tab calls its own endpoint (`/api/workspaces/doctor`, `/nurse`, `/lab`, `/radiology`, `/pharmacy`, `/billing`, `/admin`) or a view module (bedboard, patients, appointments, AI).
4. `openPatient(id)` opens the patient drawer (patient.js) which calls `/api/patients/<id>/journey` and the per-section endpoints.
5. Notifications are polled every 60 seconds (`/api/auth/notifications`). The UI polls; nothing is pushed.

---------------------------------------------------------------------------------------------------

## 2. Shared foundations

### 2.1 Login and sessions (security.py, api/auth.py)

`POST /api/auth/login` -> `attempt_login(app, email, password)`:
- Rate limit: 10 attempts per minute per IP and per e-mail. Too many -> 429 and an audit row.
- Unknown e-mail: it still hashes a dummy password (same timing) and answers "Incorrect e-mail or password". It never says which part was wrong.
- Locked account (5 wrong passwords -> locked 15 minutes): 423.
- Wrong password: `failed_logins += 1`, at 5 the account locks.
- Suspended account (`is_active = false`): 403.
- Demo account while `DEMO_MODE` is off (production): rejected with the same generic message. This is why your Vercel logins failed until `is_demo` was set to false.
- Success: counters reset, `last_login_at` set, session cleared first (stops session fixation), then `uid`, `epoch`, `login_at`, `last_seen`, `csrf` stored in the signed cookie.

Session validity on every request: idle > 30 min, or older than 12 h, or the user's `session_epoch` changed, or the user is inactive, or a demo user in non-demo mode -> signed out.
`session_epoch` is bumped by: password change, password reset, role change, ward change, suspend/activate, "revoke sessions". That instantly kills every existing session for that user.

Password rules (`validate_password_strength`): 12+ characters, not a common word, not containing the e-mail name or the person's name, at least 5 distinct characters.

### 2.2 Two layers of authorisation (access.py)

**Layer 1: permissions per role** (`ROLE_PERMS`). Example: `lab.order`, `rx.dispense`, `billing.refund`. Checked by `@require_perm`. A failure writes an `access.denied` audit row and returns 403.

**Layer 2: scopes per patient.** A scope is a slice of one patient's record. The scopes are:
`identity, contact, allergies, clinical, observations, labs, radiology, meds, billing, documents`.

How a user earns scopes on a patient (`bulk_scopes`):

| Role | Gets scopes on a patient when... | Scopes granted |
|---|---|---|
| Super admin | always | all 10 (every clinical access is audited as `privileged.clinical_access`) |
| Hospital admin | always | identity, contact, billing, labs, radiology, documents |
| Billing staff | always | identity, contact, billing, documents |
| Doctor | active assignment, OR responsible doctor of a current admission, OR a non-cancelled appointment with them, OR an encounter with them | identity, contact, allergies, clinical, observations, labs, radiology, meds, documents |
| Nurse | active assignment, OR the patient's current bed is in the nurse's ward | identity, contact, allergies, clinical, observations, labs, meds, documents |
| Lab staff | the patient has at least one lab order | identity, labs, documents |
| Pharmacist | the patient has at least one prescription | identity, allergies, meds, documents |
| Radiology staff | the patient has at least one radiology order | identity, radiology, documents |
| Patient | it is their own linked record | everything of their own, but staff-internal material is filtered out where it is served |

`get_authorized_patient(pid, *scopes)`:
- No relationship at all -> **404** "Patient not found" (so the system does not reveal that the patient exists).
- Relationship but missing a scope -> **403** plus an audit row.
- Super admin touching clinical scopes -> extra audit row.

`visible_patient_filter(user)` builds the same rule as a SQL condition so patient lists only return allowed rows.

`patient_view(user, patient, scopes)` strips fields: contact fields need `contact`, allergies need `allergies`, medical history needs `clinical`, insurance needs `billing`. A lab technician looking at a patient sees name/age/sex and lab data, and nothing else.

### 2.3 Audit trail (audit.py)

`audit(action, category, entity_type, entity_id, patient_id, details, outcome)` adds an `AuditLog` row **inside the same database transaction** as the change. If the change rolls back, so does the log line. Passwords, tokens, connection strings and JWTs are scrubbed by regex before saving. Stored: user, role, IP, request id, patient id.
Categories: `security, access, clinical, admin, ai, export, system`.
Viewing: `GET /api/admin/audit` (perm `audit.view`: super admin and hospital admin), filterable by category/outcome/action/patient/user. Doctors can read one patient's non-security audit history via `/api/patients/<id>/audit`.

### 2.4 Notifications (models.Notification, api/auth.py)

Rows addressed to a specific user (`user_id`) or broadcast to a role (`role`). `GET /api/auth/notifications` returns the last 50 for you, **but role broadcasts are only shown for patients you can see** (it re-runs `bulk_scopes`). Kinds in use: `alert`, `alert-escalation`, `critical-result`, `critical-result-escalation`, `specimen-rejected`, `result-released`, `result-amended`, `report-final`, `report-amended`.

### 2.5 The sweep (services/monitoring.run_sweeps)

There is **no background scheduler**. The sweep runs when someone loads a dashboard, the bedboard, the alert list or the critical list (throttled to once a minute), or via `POST /api/monitoring/sweep` / `flask monitor-sweep`. It does three things:
1. "Missing observation" rules: admitted patients with no reading for longer than the rule window raise an alert.
2. Critical alerts still `Open` after 15 minutes -> escalated to `hospital_admin`.
3. Critical lab/radiology results still `Pending` after 30 minutes -> `Escalated`, broadcast to `hospital_admin`.

Because of this, escalation only happens while at least one person is using the app.

### 2.6 Deliverables (services/deliverables.py)

A "deliverable" tracks something the hospital hands the patient: lab report, radiology report, discharge summary, medicine label, invoice. Each has a digital side (`digital_available`) and a physical lifecycle: `Not requested -> Requested -> Ready for collection -> Handed over`. Created automatically at: lab release, radiology authorisation, dispensing, bill creation, discharge completion. Staff update it (`PATCH /api/deliverables/<id>`); "Handed over" requires the name of the person who received it and stamps who handed it over and when. A handed-over item cannot move back.

---------------------------------------------------------------------------------------------------

## 3. Roles at a glance

| Role | Workspaces (tabs) | Can create | Cannot do |
|---|---|---|---|
| Super admin | Operations, Doctor, Bedboard, Nurse, Lab, Pharmacy, Radiology, Billing, Patients, Appointments, AI (+ Users & audit) | patients, users (incl. admins), beds/wards, alert rules, devices, bills, adjustments, refunds | order labs, prescribe, enter lab results, write notes (no `lab.order`, `rx.prescribe`, `lab.process`, `note.write`) |
| Hospital admin | Operations, Bedboard, Lab, Radiology, Patients, Appointments, Billing (+ Users & audit) | patients, appointments, admissions, beds, users (non-admin), billing incl. refunds, exports, reports | clinical writing, processing results, managing other admins |
| Doctor | Doctor (command center), Bedboard, Patients, Appointments, AI | notes, orders, prescriptions, tasks, discharge authorisation | billing, user management, dispensing, processing lab/radiology |
| Nurse | Nurse (workbench), Bedboard, Patients, AI | observations, I/O, medication administration, nursing notes, tasks | prescribe, order tests, discharge authorisation |
| Lab staff | Lab, AI | results, verification, release, amendments | order tests, see non-lab data |
| Radiology staff | Radiology, AI | perform, report, authorise, amend | order studies |
| Pharmacist | Pharmacy, AI | verify, dispense, inventory, reconciliation | prescribe |
| Billing staff | Billing, Patients, AI | bills, payments, claims, small adjustments | refunds, voiding bills |
| Patient | My Care (portal), AI | nothing | everything else (read-only) |

---------------------------------------------------------------------------------------------------

## 4. Role-by-role flows

Format for each feature: **Route** -> **function** -> *what it checks* -> *what it writes* -> *who gets told*.

---

### 4.1 SUPER ADMINISTRATOR

Permissions: everything administrative plus `user.manage_privileged`, `security.view`, `alert.configure`, `sim.run`, `workspace.admin`. Scopes: all, always.

**A. User management** (api/admin.py)
- `GET /api/admin/users` -> `users()` (perm `user.manage`): a hospital admin does not see admin accounts; a super admin sees all.
- `POST /api/admin/users` -> `create_user()`: validates e-mail, role, `_guard_target` (only a super admin may create admin roles), `_check_links` (a doctor account MUST be linked to a Doctor profile; a patient account MUST be linked to an existing patient and a patient can have only one login; only doctors link to doctor profiles), password strength. Account is created with `must_change_password = true`. Audit `user.created`.
- `PATCH /api/admin/users/<id>` -> `update_user()`: change name, role, doctor link, ward, active flag. You cannot change your own role or suspend yourself. A patient login cannot be converted to or from staff. Role/ward/active changes bump `session_epoch` (instant sign-out).
- `DELETE /api/admin/users/<id>`: tries to delete; if the user already appears in clinical rows or audit (foreign key error), it **disables instead** and says so. History stays attributable.
- `POST .../reset-password`: sets temp password, forces change, ends all sessions, clears lock.
- `POST .../revoke-sessions`, `POST .../unlock`.

**B. Audit and security** (api/admin.py)
- `GET /api/admin/audit` (perm `audit.view`), itself audited as `audit.viewed`.
- `GET /api/admin/security` (perm `security.view`, super admin only): 7-day counts of security events, currently locked accounts, and posture (demo mode, environment, session lengths, rate limiting, secure cookies).

**C. Operations console** (`GET /api/workspaces/admin` -> `admin()`): users by role, bed counts by status, security events in the last 24 h (total and denied), system block (environment, database backend, schema state vs migration head, demo mode, storage backend, AI provider status), open alert count.

**D. Facility set-up** (api/beds.py, perm `bed.configure`): `POST /departments`, `/wards`, `PATCH /wards/<id>`, `POST /rooms`, `/beds`, `PATCH /beds/<id>`. Wards carry a `daily_rate` that billing uses.

**E. Alert rules and devices** (api/monitoring.py)
- `POST/PATCH /api/alert-rules` (perm `alert.configure`; super admin only): threshold rules (`type_code operator threshold severity`) or "missing data" rules (`window_minutes`). Each edit increments `version`; alerts snapshot the rule at raise time. `POST /alert-rules/<id>/review` marks a threshold as clinically reviewed.
- `POST /api/devices` (perm `config.manage`): returns a device API key **once** (`cfd_...`); only its SHA-256 is stored. `POST /devices/<id>/revoke`.

**F. Patient deletion** (`DELETE /api/patients/<id>`): only super admin, and only if the patient has no appointments, admissions, labs, prescriptions, radiology, bills, notes, observations, documents or encounters. Otherwise: "archive instead".

**G. Simulator** (`POST /api/patients/<id>/simulate`, perm `sim.run`): generates vitals marked `source = simulated` (stable / deteriorating / recovering) so alerts can be demonstrated. Alerts raised from them are tagged `[SIMULATED DATA]`.

**H. AI purge** (`POST /api/ai/purge`, perm `config.manage`): deletes AI conversations older than the retention days.

---

### 4.2 HOSPITAL ADMINISTRATOR

Permissions include `patient.register/update/registry`, `appointment.manage`, `admission.manage`, `bed.operate/configure`, all billing incl. `billing.adjust` and `billing.refund`, `report.view`, `audit.view`, `user.manage`, `config.manage`, `assign.manage`, `export.run`, `inventory.manage`, `patient.verify_identity`, plus read of released lab/radiology reports and documents.

**A. Registry** (api/patients.py)
- `POST /api/patients` -> `create_patient()`: `_clean_patient_fields` validates name (2+ chars), DOB (not future), gender, blood group, e-mail. **Duplicate check**: same name (case-insensitive) + DOB returns 409 with possible duplicates unless `confirm_duplicate` is sent. Code `P-YYMMDD-XXXX` from `next_patient_code()` (random, collision-checked). If the creator is a doctor/nurse, a primary `PatientAssignment` is created so they keep access.
- `PATCH /api/patients/<id>` -> `update_patient()`: **field-level permissions** (identity fields need `patient.update`; contact needs `patient.update` + `contact` scope; allergies need `allergy.write`; medical history needs `note.write` + `clinical`; insurance needs `billing` scope + `patient.update` or `patient.update_insurance`). Changing name or DOB un-verifies identity.
- `POST /api/patients/<id>/verify-identity` (perm `patient.verify_identity`): stores ID label and **last 4 characters only** ("the full number is never stored"), records who verified and when.
- `POST /api/patients/<id>/archive`: admins only; refused if currently admitted.

**B. Appointments** (api/scheduling.py)
- `POST /api/appointments` -> `create_appointment()`: `_validate_slot`: not in the past, within 08:00-20:00, doctor available, and the doctor does not already have an active appointment at that time (also enforced by a partial unique index, so two simultaneous bookings produce a 409).
- `PATCH /api/appointments/<id>`: reschedule (needs `appointment.manage`; only Scheduled/Checked-in ones) or status change following `APPOINTMENT_TRANSITIONS`; cancelling requires a reason.
- Doctors: `POST /api/doctors` (`config.manage`), `PATCH /api/doctors/<id>` (`assign.manage`), `GET /api/doctors/<id>/slots`.

**C. Admissions and beds** (api/beds.py + services/beds.py): see 5.3 (full flow).

**D. Billing**: see 4.8, plus refunds, large adjustments, voiding.

**E. Reports** (api/reports.py): `GET /api/reports` lists which reports your permissions allow, `GET /api/reports/<name>?days=30`. Names: occupancy, admissions, appointments, lab-turnaround, alerts, billing, prescriptions, radiology. `?format=csv` needs `export.run`, is audited as `report.exported`, and neutralises spreadsheet formula injection (a leading `= + - @` gets a `'` prefix).

**F. Care-team assignment**: `POST /api/patients/<id>/assignments` (perm `assign.manage`, or a doctor with clinical scope adding *consulting/covering* only), `DELETE /api/assignments/<id>` (admins). Assignee must be an active doctor or nurse. This is what grants doctors/nurses access to a patient.

**G. Escalation target**: unacknowledged critical alerts and critical results land in this role's notifications (see section 7).

**H. Released-result visibility**: hospital admin sees lab/radiology only when `Released` / `Final` (`_can_see_results`, `_rad_visible_report`). Draft or in-progress results are hidden from them.

**I. Users**: same as super admin but cannot create or manage admin accounts (`PRIVILEGED = {super_admin, hospital_admin}` need `user.manage_privileged`).

---

### 4.3 DOCTOR

Doctor account must be linked to a `Doctor` profile (`doctor_id`). That profile id drives scheduling and access.

**Landing: Clinical Command Center** (`GET /api/workspaces/doctor` -> `doctor()`)
1. `run_sweeps()` (throttled).
2. `_my_patients()` = patients passing `visible_patient_filter`.
3. `_attention_list()` -> `_attention()` builds a **ranked worklist** from stored records only: open alerts (weight 30 + 10 x severity + 15 if still Open), overdue observations for admitted patients (25), unacknowledged critical results (60, or 70 if escalated), new lab releases in 24 h (8), overdue tasks (18), discharge authorised but not completed (10). Score = sum of top 4 reasons. The page states plainly that this is a worklist aid, not a clinical risk score.
4. Also today's appointments, count of pending critical results.

**A. Consultation** (api/scheduling.py)
- `POST /api/appointments/<id>/start` -> `start_encounter()` (perm `encounter.manage`): only the appointment's own doctor; needs `clinical` scope; creates an `Encounter` (Outpatient), sets appointment `Checked-in`. Repeating the call returns the existing encounter.
- `POST /api/appointments/<id>/complete` -> `complete_encounter()`: closes the encounter, appointment `Completed`.

**B. Clinical record** (api/patients.py)
- Notes: `POST /patients/<id>/notes` (perm `note.write`, scope `clinical`). Doctor types: Progress, Consult, Procedure, Discharge, Admission. Linked to the active admission/encounter automatically. **Amend** (`POST /notes/<id>/amend`): only the author; creates a *new* note pointing to the old one, marks the old `Superseded`; a reason is required; the original text is never overwritten.
- Allergies (`allergy.write`), problems (`problem.write`, can be updated), care plans (`care.plan`), follow-ups (`followup.write`), tasks (`task.write`, categories Observation/Medication/Wound care/Mobility/Intake-Output/Assessment/Discharge/Other, priority Routine or Urgent, assigned to a role, default nurse).
- Handover (SBAR): `GET /patients/<id>/handover-draft` compiles Situation/Background/Assessment/Recommendation **deterministically from structured records** (no AI, no external call). `POST /patients/<id>/handovers` saves it (kind Medical for doctors, Nursing for nurses). `POST /handovers/<id>/review`: reviewer must be a **different person** than the author.

**C. Ordering**
- Lab: `POST /api/labs` (perm `lab.order`; needs `labs` scope). Priority Routine/Urgent/STAT. Any `result` sent by the doctor is **ignored** (results come only from lab staff). Status starts `Ordered`; linked to the active admission/encounter. Audit `lab.ordered`.
- Radiology: `POST /api/radiology` (perm `rad.order`): modality must be in the allowed list; findings ignored; status `Ordered`.
- Prescription: `POST /api/prescriptions` (perm `rx.prescribe`, scope `meds`):
  1. Resolve catalogue medicine (must be active and not expired).
  2. `medication_warnings(patient, name, generic)`: **allergy** match against structured allergies AND the free-text allergy field (blocking), **duplicate** active order for the same medicine (blocking), **interaction** from a 4-pair demo list (warning only: warfarin+ibuprofen, sildenafil+nitroglycerin, sertraline+tramadol, lisinopril+potassium chloride). The code states this is not a real drug-interaction database.
  3. If any blocking warning exists, an `override_reason` of at least 10 characters is required, otherwise 409 with the warnings.
  4. Row saved as `Ordered` with the warnings and override reason stored.
  - `POST /prescriptions/check` previews warnings without saving. `POST /prescriptions/<id>/discontinue` (reason required). Cancel is allowed for prescriber or verifier while still Ordered/Verified.

**D. Results**
- Lab and radiology results appear to the doctor only once Released/Final.
- **Critical acknowledgment**: `POST /api/critical/<id>/ack` -> `ack_critical()`: **only role doctor** (not admins, not nurses). Stores who/when/note. Audit `critical_result.acknowledged`.
- `GET /api/patients/<id>/lab-trend` for charts.

**E. Monitoring**
- `POST /patients/<id>/observations` (perm `obs.record`) -> `monitoring.record_vitals`: see 4.4 and section 7.
- Alerts: `POST /alerts/<id>/acknowledge | escalate | resolve` (perm `alert.act`). Resolve requires a note.

**F. Admission and discharge**
- `POST /api/admissions`, discharge plan (`admission.manage`), **`POST /admissions/<id>/discharge/authorize`** (perm `discharge.authorize`, doctor only): requires a non-empty discharge summary; stores who authorised and when.

**G. Documents**: upload (`doc.upload`), review/correct OCR text (`doc.review`) - see section 9.

**H. Care team**: may add *consulting* or *covering* colleagues for patients they can see clinically.

**I. AI assistant**: clinical mode; see section 8.

**J. Per-patient audit** (`GET /patients/<id>/audit`): allowed with clinical scope; excludes security-category rows.

---

### 4.4 NURSE

**Landing: Nursing Workbench** (`GET /api/workspaces/nurse` -> `nurse()`):
- Admitted patients the nurse can see (assignment or own ward), each with observation **freshness** (`fresh / due / overdue / none`, based on `OBS_EXPECTED_INTERVAL_MIN` = 240 min: fresh <= 240, due <= 480, then overdue), open alerts, and attention reasons.
- Pending care tasks sorted by due time, flagged overdue.
- Scheduled medication administrations due (with overdue flag).

**A. Vitals / observations** (api/monitoring.py, services/monitoring.py)
`POST /api/patients/<id>/observations` body `{values: {heart_rate: 80, ...}, observed_at?, note?}` -> `record_vitals()`:
1. For each value, `record_observation()`: known active type; number and finite; inside the **plausible entry range** (typo guard only, e.g. HR 10-300, SpO2 30-100, temp 25-45); not more than 5 minutes in the future.
2. Row stored with provenance `source = manual`, recorder, admission/encounter link, a shared `group_id` for the set.
3. `evaluate_observation()` immediately checks every active threshold rule for that type. Matching rules call `raise_alert()` (section 7).
4. Response includes the patient's currently open alerts so the UI can show them.
- **Correct** (`POST /observations/<id>/correct`): needs value + reason; creates a new reading with `supersedes_id`, old one marked `Corrected` (kept). **Withdraw** (`/withdraw`): marks `Entered in error` with reason. Neither deletes anything.

**B. Alerts**: acknowledge / escalate (default to `doctor`) / resolve (note required).

**C. Medication administration (MAR)** (`POST /api/prescriptions/<id>/administer`, perm `rx.administer`):
- Order must be `Verified`, `Dispensed` or `Partially Dispensed`.
- Status Given / Held / Refused / Missed. **Given requires both `identity_verified` and `allergies_checked` to be true.** Held/Refused/Missed require a note.
- Writes a `MedicationAdministration` row (dose, who, when) and audit `mar.recorded`.

**D. Intake/output** (`POST /patients/<id>/intake-output`, perm `io.record`), **care tasks** (create/complete), **nursing notes** (note type `Nursing` only), **allergies**, **handover** drafts/saves/reviews.

**E. Admission/bed operations**: `bed.operate` (assign bed, transfer, change bed status Cleaning -> Available), `admission.manage` (admit, plan/complete discharge). Nurses cannot authorise discharge.

**F. Appointment check-in**: `PATCH /api/appointments/<id>` with status `Checked-in` (perm `appointment.checkin`).

**G. Identity verification** (`patient.verify_identity`) and registration of walk-in patients.

---

### 4.5 LABORATORY STAFF

Perms: `lab.read, lab.process, lab.verify`, document upload/review/read, `report.view`, `ai.use`, `alert.view`. Scope: only patients with a lab order, and only `identity + labs + documents`.

**Landing**: `GET /api/workspaces/lab`: counts by status, the open queue sorted by priority then order time (statuses Ordered..Verified), and unacknowledged critical lab results.

**State machine** (`LAB_TRANSITIONS`, enforced by `services/orders.lab_transition`):
`Ordered -> Collected -> Received -> Resulted -> Verified -> Released`; `Rejected` can go back to `Ordered`; Cancelled is final. Anything else returns 409 "cannot move from X to Y".

**Step by step** (api/orders.py)
1. **Collect** `POST /labs/<id>/collect`: stamps collector/time, sample type, and generates an **accession number** `ACC-YYMMDD-NNNNN-XX`.
2. **Receive** `POST /labs/<id>/receive`.
3. **Reject** `POST /labs/<id>/reject`: reason required; notifies the ordering doctor ("Specimen rejected"). **Re-order** `POST /labs/<id>/reorder` re-opens it for recollection (clears timestamps).
4. **Enter results** `PUT /labs/<id>/results` with `results: [{analyte, value, unit, ref_low, ref_high, critical_low, critical_high, flag?}]`:
   - `_parse_result_items`: numeric value or text value; ranges optional.
   - `_store_results` -> `compute_flag`: **flags are derived only from ranges the lab supplies**: critical_low/high -> `Critical Low/High`, below ref_low -> `Low`, above ref_high -> `High`, inside -> `Normal`, no ranges -> manual flag or `Not assessed`. The system never invents reference ranges.
   - Re-entering results while still `Resulted` replaces the previous *entered* values.
5. **Verify** `POST /labs/<id>/verify`: moves to `Verified`. A "second person must verify" check exists in code (`LAB_DUAL_VERIFY`) but that setting is not defined in config, so it is **off** unless you add it.
6. **Release** `POST /labs/<id>/release` -> `_do_release()`:
   - status `Released`, results marked `Final`, a text summary stored on the report (`summarize_results`);
   - if any result is critical -> `notify_critical()` creates a `CriticalAck` (Pending) plus notifications to the ordering user and the whole `doctor` role;
   - otherwise a "Lab result released" info notification to the orderer;
   - attached files become **patient-visible** (`share_documents_with_patient`);
   - a Deliverable "Laboratory report" is created.
7. **One-step submit** `POST /labs/<id>/submit` (UI button "attach report and mark complete"): refuses if there is neither an attached file nor entered results; then walks the legal states itself (collect -> receive -> result -> verify -> release), recording each step in the audit detail. With dual-verify on, it stops at Resulted.
8. **Amend a released result** `POST /labs/<id>/amend`: reason required; the old value is marked `Superseded`, the new row gets `version + 1` and `supersedes_id` (full history kept); orderer gets a "CORRECTED" warning notification; if the corrected value is critical, the acknowledgment resets to Pending.
9. **Attach the actual report file**: `POST /api/patients/<id>/documents` with `lab_report_id` (doc type must be "Laboratory report" for this role) - section 9.
- Legacy `PATCH /labs/<id>` maps an old single-line result onto the structured flow.

Lab staff **cannot order tests** (only doctors hold `lab.order`).

---

### 4.6 RADIOLOGY STAFF

Perms: `rad.read, rad.perform, rad.report, rad.authorize`, documents, reports, AI. Scope: patients with a radiology order, `identity + radiology + documents`.

**Landing**: `GET /api/workspaces/radiology`: queue of orders not Final/Cancelled by priority, status counts, urgent-finding flags.

**State machine** (`RAD_TRANSITIONS`): `Ordered -> Scheduled -> Performed -> Reported -> Final`; `Reported -> Reported` (redraft); Final changes only through amendment.

**Steps** (api/orders.py)
1. **Schedule** `POST /radiology/<id>/schedule` with `scheduled_at`.
2. **Perform** `POST /radiology/<id>/perform` (stamps performer/time).
3. **Draft report** `PUT /radiology/<id>/report`: findings required; study must be Performed; saves findings/impression/recommendations/`urgent_finding`; each save writes a **`RadiologyReportVersion`** row (v1, v2...).
4. **Authorise** `POST /radiology/<id>/authorize` (perm `rad.authorize`) -> `_do_authorize()`: status `Final`, version stamped "Authorized"; if `urgent_finding` -> `notify_critical("radiology", ...)` (acknowledgment workflow), else "Imaging report available" notification; attached files shared with the patient; Deliverable created.
5. **One-step submit** `POST /radiology/<id>/submit`: needs findings; performs -> reports -> authorises in one call, each step recorded.
6. **Amend** `POST /radiology/<id>/amend` (Final only): `findings` + `reason` required; new version stored, `amendment_count` incremented, orderer notified "AMENDED"; earlier versions preserved.
Non-radiology users see only `Final` reports.

---

### 4.7 PHARMACIST

Perms: `rx.read, rx.dispense, rx.verify, inventory.manage`, documents, reports, AI. Scope: patients who have at least one prescription; `identity + allergies + meds + documents`.

**Landing**: `GET /api/workspaces/pharmacy`: queue of orders in Ordered/Verified/Partially Dispensed with their stored warnings; **low stock** (stock <= reorder level); **expiring within 60 days** (and stock > 0).

**A. Verify** `POST /prescriptions/<id>/verify`: only from `Ordered`; **re-runs `medication_warnings` at verification time** (allergies may have changed since ordering) and stores them; status `Verified`, records pharmacist and time.

**B. Dispense** `POST /prescriptions/<id>/dispense` body `{quantity, medicine_id, acknowledged_warnings[], note}` -> `services/orders.dispense()`:
1. Order must be Ordered / Verified / Partially Dispensed; quantity > 0; not above (ordered quantity - already dispensed).
2. Medicine must be active and **not expired**.
3. Fresh **allergy** check. If an allergy warning exists and there is neither a prescriber override nor an acknowledgment from the pharmacist, dispensing is refused with the warnings.
4. **Atomic stock decrement**: `UPDATE medicine SET stock = stock - q WHERE id = ? AND stock >= q`. If 0 rows change -> "Insufficient stock" (safe against two pharmacists dispensing at once).
5. A `StockMovement` row (delta, balance after, reason `dispense`, link to prescription, user) and a `DispenseEvent` row (what was acknowledged).
6. Order becomes `Dispensed` (fully) or `Partially Dispensed`; if nobody had verified it, the dispenser is recorded as verifier.
7. Deliverable "Prescription / medicine label" created and set to **Ready for collection**.
Dispensed != administered: giving the dose is a nursing MAR record (4.4).

**C. Inventory**: `POST /medicines` (starting stock goes through `adjust_stock` so it is logged), `PATCH /medicines/<id>` (stock edits become logged adjustments; price, expiry, reorder level, active flag), `POST /medicines/<id>/restock` (quantity 1..1,000,000, optional batch/expiry), `GET /medicines/<id>/movements` (last 100 movements = the stock ledger). `adjust_stock` blocks anything that would take stock below zero.

**D. Medication reconciliation**: `GET /patients/<id>/med-reconciliation` (active orders, **duplicate active medicines**, allergy text, history) and `POST` (each item: Continue/Stop/Modify/Add + note) saved with the pharmacist id.

**E. Cancel** (Ordered/Verified only, reason required).

---

### 4.8 BILLING & INSURANCE STAFF

Perms: `billing.read, billing.write, billing.adjust`, `patient.registry`, `patient.update_insurance`, documents, reports, AI. Scope on every patient: `identity + contact + billing + documents`.
**Not allowed:** refunds and voiding (those need `billing.refund`, held only by admins).

**Landing**: `GET /api/workspaces/billing`: counts of bills, unpaid bills and unpaid total, claims by status, list of unpaid bills.

**Money model** (`services/orders.bill_figures`):
`balance = bill.total - sum(adjustments) - (sum(Payment rows of kind Payment) - sum(rows of kind Refund))`.
A bill is `paid` when `total > 0` and balance <= 0.005. `refresh_bill_status` recomputes `paid` and mirrors the latest claim status into the legacy `insurance_status`/`insurance_provider` columns after every money or claim change. `Bill.total` is the sum of consultation + laboratory + pharmacy + room + other charges.

**Steps** (api/orders.py)
1. **Create bill** `POST /bills`: charges must be >= 0 and < 100,000,000; insurance provider defaults from the patient; creates the "Invoice / receipt" deliverable. Audit `bill.created`.
2. **From admission** `POST /bills/from-admission/<admission_id>`: finds the ward by name, takes its `daily_rate`, days = (discharge or today) - admit date (+1 day if still admitted, minimum 1), `room = days x rate`.
3. **Payment** `POST /bills/<id>/payments`: amount > 0 and **cannot exceed the outstanding balance** (409). Method/reference recorded. Recomputes status.
4. **Adjustment** `POST /bills/<id>/adjustments`: kind Discount / Write-off / Correction, reason mandatory, cannot exceed balance. **Billing staff may only adjust up to 10% of the bill total** (`BILLING_ADJUST_LIMIT_PCT`, default 10); above that, only hospital/super admin (who are recorded as `approved_by`).
5. **Refund** `POST /bills/<id>/refunds` (admins only): reason mandatory, cannot exceed the amount paid; stored as a Payment row of kind Refund with approver.
6. **Void** `POST /bills/<id>/void` (admins only): refused if any payment exists ("refund first"); reason required. Voided bills reject further changes.
7. **Insurance claim** `POST /bills/<id>/claims` (provider needed; defaults amount claimed = bill total, status `Draft`) then `PATCH /claims/<id>`: status through Draft -> Submitted (stamps `submitted_at`) -> Approved / Partially approved / Rejected -> Paid, plus `amount_approved`, claim number, notes.
8. Legacy `PATCH /bills/<id>`: `paid: true` records a "Marked paid" payment for the remaining balance; un-paying is refused ("use a refund").
- Every view of a bill writes `bill.viewed`.

---

### 4.9 PATIENT (portal)

An admin creates the account (role `patient`, linked to exactly one patient). All requests are restricted by security.py to `/api/auth`, `/api/portal`, `/api/ai`, `/api/workspaces`; anything else -> 403 plus an `access.denied` audit row.

**`GET /api/portal/overview`** -> `overview()` assembles, for the linked patient only:
- profile (name, code, DOB, contact, insurance), current stay (ward, bed, doctor, expected discharge; the discharge summary is hidden until discharge is complete), past admissions (discharge summary only if discharged; plan only if authorised/completed), care team (names, role labels);
- appointments, active allergies and problems, follow-ups;
- **medicines**: ordered vs dispensed vs last dose are shown as separate facts;
- **vitals**: latest per type with provenance and freshness; flags if any are simulated;
- **lab results only if `Released`**; **radiology only if `Final`**; files only if `patient_visible`;
- bills (total, paid, adjustments, balance, insurance status, payment history; voided bills hidden);
- hand-over items with `copy_url`.
Audit `portal.viewed`. The page is explicitly labelled read-only.

**Downloads**
- `GET /api/portal/documents/<id>/download`: only own, only `patient_visible`. Missing, someone else's and not-shared all return the *same* 404, so IDs cannot be probed. Served with a sandbox CSP and `no-store`. Audit `portal.document_downloaded`.
- `GET /api/portal/deliverables/<id>/copy`: if an attached visible file exists it redirects to the download; otherwise builds a printable HTML page for a released lab report (results table), a final radiology report, or a bill (total/paid/balance). Unreleased -> 404.

**AI** (`/api/ai/*`): see section 8; always "simple" mode with extra patient-safe rules.

---------------------------------------------------------------------------------------------------

## 5. Cross-role end-to-end journeys

### 5.1 Outpatient visit
1. **Admin/doctor/nurse** `POST /patients` registers (duplicate guard, code `P-...`).
2. **Scheduler** `POST /appointments` (slot validation + unique index).
3. **Nurse/scheduler** check-in: status `Checked-in`.
4. **Doctor** `start` -> Encounter created; gains access via appointment relationship; writes a Progress note; orders a lab; prescribes.
5. **Lab/pharmacy** flows (5.2, 4.7). **Doctor** `complete` -> encounter Closed, appointment Completed.
6. **Billing** creates the bill; payment recorded.
7. **Patient** sees released results, medicines and bill in the portal.

### 5.2 A lab order, whole round trip
```
Doctor  POST /labs            -> LabReport(status=Ordered, ordered_by_id, admission/encounter link)   audit lab.ordered
Lab     POST /labs/N/collect  -> Collected + accession no.
Lab     POST /labs/N/receive  -> Received
Lab     PUT  /labs/N/results  -> Resulted, LabResult rows with flags from lab-supplied ranges
Lab     POST /labs/N/verify   -> Verified
Lab     POST /labs/N/release  -> Released
          |- normal  -> Notification(user = orderer, "Lab result released")
          |- critical-> CriticalAck(Pending) + Notification(orderer) + Notification(role=doctor)
          |- files attached to the order become patient_visible
          |- Deliverable "Laboratory report"
Doctor  POST /critical/C/ack  -> Acknowledged (only doctors)
          (if nobody acknowledges within 30 min and someone loads a dashboard: Escalated -> hospital_admin)
Patient GET  /portal/overview -> sees it (Released only)
Lab     POST /labs/N/amend    -> new version, old Superseded, orderer notified, critical re-acknowledgment if needed
```

### 5.3 Inpatient: admission to discharge
1. **Admit** `POST /admissions` -> `beds.admit()`: blocks if the patient already has an active admission; creates an **Inpatient Encounter** and the `Admission`; if a bed is given, `_lock_bed` (SELECT ... FOR UPDATE) then `_occupy`: bed must be Available/Reserved, no open assignment on that bed, creates `BedAssignment`, bed -> `Occupied`. Responsible doctor gets a primary assignment automatically (so they can see the patient).
2. **Bed later** `POST /admissions/<id>/assign-bed` (only when no bed yet).
3. **Transfer** `POST /admissions/<id>/transfer`: locks both beds in id order (avoids deadlocks), closes the old assignment (end reason "Transfer"), old bed -> `Cleaning`, new bed occupied. Partial unique indexes in the database also stop two patients ending up in one bed.
4. **Bed status** `POST /beds/<id>/status`: only manual transitions allowed (Available <-> Reserved/Maintenance, Cleaning -> Available/Maintenance, Maintenance -> Available/Cleaning). Occupied beds cannot be changed by hand.
5. **Bedboard** `GET /api/bedboard`: beds with occupant, **filtered per viewer**: someone without `identity` scope sees "restricted"; observation freshness and alert badge need `observations`; tasks and doctor need `clinical`. Also lists admitted patients still waiting for a bed.
6. **Care**: nurses record vitals/tasks/MAR; doctors order; alerts as in section 7.
7. **Discharge** is a 3-step gate:
   - `discharge/plan` (`admission.manage`): status `Planned`.
   - `discharge/authorize` (`discharge.authorize`, doctors): summary mandatory -> `Authorized`.
   - `discharge/complete` (`admission.manage`): refuses unless `Authorized`. Then: assignment ended, bed -> `Cleaning`, admission `Discharged`, encounter Closed, **pending tasks auto-cancelled**, **open alerts auto-resolved** ("Closed at discharge"), Deliverable "Discharge summary" set to Ready for collection.
8. **Billing**: `bills/from-admission/<id>` computes room charges from the ward rate.

### 5.4 Monitoring alert to resolution
See section 7.

---------------------------------------------------------------------------------------------------

## 6. State machines

| Object | States and allowed moves |
|---|---|
| Appointment | Scheduled -> Checked-in / Completed / Cancelled / No-show; Checked-in -> Completed / Cancelled / No-show; the rest are final |
| Lab order | Ordered -> Collected -> Received -> Resulted -> Verified -> Released; Rejected -> Ordered; Cancelled final; (Ordered/Collected can also go Rejected/Cancelled; Received/Resulted can go Rejected) |
| Radiology | Ordered -> Scheduled -> Performed -> Reported -> Final (Ordered can skip to Performed); Reported -> Reported; Final only via amendment |
| Prescription | Ordered -> Verified -> Dispensed / Partially Dispensed; Cancelled (while Ordered/Verified); Discontinued (any active) |
| Dose (MAR) | Given / Held / Refused / Missed |
| Bed | Available <-> Reserved, Maintenance; Occupied only through admission/transfer; Cleaning -> Available / Maintenance |
| Discharge | None -> Planned -> Authorized -> Completed |
| Alert | Open -> Acknowledged / Escalated -> Resolved |
| Critical result | Pending -> Acknowledged (doctor) or Escalated (timer) |
| Claim | Draft -> Submitted -> Approved / Partially approved / Rejected -> Paid |
| Deliverable (physical) | Not requested -> Requested -> Ready for collection -> Handed over (no way back) |
| Document review | Unreviewed -> Reviewed / Needs correction |

---------------------------------------------------------------------------------------------------

## 7. Alerts, critical results and escalation timers

**Rule evaluation** (`evaluate_observation`, runs on every recorded reading, including device and simulator readings):
- Loads active threshold rules for the reading's type; if `value <op> threshold` is true -> `raise_alert()`.
- **De-duplication**: one live (non-resolved) alert per patient+rule. A repeat just increments `occurrences` and updates the message.
- **Cooldown**: for non-critical rules, after a clinician resolves an alert, the same rule stays quiet for `cooldown_minutes`.
- New alert stores a **snapshot of the rule** (name, threshold, version, review status) so later rule edits don't rewrite history. It records whether it came from simulated data.
- **Who is told**: nurse role broadcast always; the account of the admission's responsible doctor directly. Responder role = `doctor` for Critical, `nurse` otherwise.

**Human actions** (`alert.act`): acknowledge, escalate (to doctor by default, notifies the responder too), resolve (note mandatory).

**Timers** (see sweep in 2.5, defaults from config): critical alert still Open after **15 min** -> escalated to hospital_admin; critical result Pending after **30 min** -> escalated to hospital_admin; missing-observation rule windows default to **240 min**.

**Devices** (`POST /api/integrations/observations`): header `X-Device-Key`; the server hashes the key and looks it up (constant-time compare); the device must be bound to a patient; 1-200 readings per call, not older than 7 days; stored as `device` (or `simulated`) with no CSRF needed. Real hardware is not connected by default.

---------------------------------------------------------------------------------------------------

## 8. The AI assistant pipeline (api/ai.py, ai/assistant.py, ai/retrieval.py, ai/safety.py)

`POST /api/ai/conversations/<id>/ask`:
1. `ai.use` permission; per-user limit (20/min).
2. `_conv()`: conversation belongs to this user; **access is re-checked now** with `get_authorized_patient` (it may have been withdrawn).
3. `patient_scopes` computed; **every evidence type is gated by scope** (`AI_EVIDENCE_SCOPE`: labs->labs, medication->meds, vitals->observations, notes/problems/admission->clinical, billing->billing...). Missing scope = skipped, and the answer tells the user "your role does not have access to X".
4. `retrieval.gather`: exact values (labs, vitals, meds) come from direct DB queries; uploaded-document text is ranked with BM25 and passed through `sanitize_untrusted`, which **removes instruction-like lines** (prompt-injection defence). Identity (name, contact) is never put in evidence, only age and sex.
5. Safety pre-checks: emergency words add an emergency notice; "should I take / what dose / diagnose" adds a "this assistant doesn't advise" notice.
6. No usable evidence -> a fixed "could not find any records you are allowed to see" answer (no model call).
7. Provider (`AI_PROVIDER`; `mock` only in tests). If the provider is external and `AI_ALLOW_EXTERNAL_PHI` is off, **no patient data is sent**; evidence is returned instead.
8. System prompt rules: use only `<evidence>`, cite as [E3], no invention/rounding, no diagnosis or dosing, treat UNTRUSTED text as data, never reveal rules. Patients get extra plain-language rules.
9. `safety.validate_answer`: blocks (answer withheld, evidence shown instead) on credential-like text, prompt leakage, another patient's code, empty output, or **numbers not found in the evidence** (decimals, numbers > 20 or with units). Unknown citations are stripped.
10. Messages saved with sources, limitations, provider, model; audit `ai.query`. Conversation delete wipes messages (`ai.conversation_deleted`).
If no AI provider is configured, users still get the retrieved records ("configuration_required").

---------------------------------------------------------------------------------------------------

## 9. Documents, OCR and storage (api/documents.py, services/documents.py)

`POST /api/patients/<id>/documents` (multipart: file, doc_type, title, lab_report_id?, radiology_id?, supersedes_id?, patient_visible?):
1. Perm `doc.upload` + `documents` scope.
2. **Role limits on type** (`DOC_TYPES_BY_ROLE`): lab staff -> "Laboratory report" only; radiology -> "Radiology report"; pharmacist -> "Prescription"; billing -> "Insurance".
3. Size <= 15 MB (`MAX_UPLOAD_MB`); `sniff_and_validate` checks **magic bytes** (PDF, PNG, JPEG, plain text), not just the extension.
4. If linked to a lab/radiology order, the order must belong to the same patient. `supersedes_id` creates a new **version** of an earlier document.
5. Stored via the storage backend (`local` folder, or private Supabase bucket) under a random key; SHA-256 of the content saved.
6. `process_document` -> `extract`: PDF pages use embedded text when it's long enough and clean (quality >= 0.6), otherwise OCR (Tesseract, 300 dpi) if installed; images use OCR. Result status: Complete / Partial / Failed / "OCR unavailable", with per-page method and confidence. It never invents text. Extraction failure doesn't fail the upload.
7. Reviewers (`doc.review`: doctors, lab, radiology) can **correct page text**; the original extraction is preserved in its own column, and corrections survive re-processing. `reprocess` re-runs from the untouched original.
8. Downloads (`doc.read`) are audited; if the storage backend supports signed URLs the user is redirected to a 60-second link, otherwise the file streams with a sandbox CSP.
9. Visibility: lab/radiology attachments become patient-visible automatically at release/authorisation; others by `POST /documents/<id>/visibility`.
10. "Not allowed" and "doesn't exist" return the same 404.
On Vercel the disk is read-only, so uploads/OCR use `/tmp` and are not durable there (use the Supabase storage backend for real use).

---------------------------------------------------------------------------------------------------

## 10. Honest limits and things that are not built

- **No background worker.** Escalations and "missing observation" alerts only fire while someone is using the app (or you run `flask monitor-sweep` on a cron).
- **Drug-interaction check is a 4-pair demo list**, explicitly labelled as not a real database. Allergy and duplicate checks are string matches on names.
- **Alert thresholds** are data you configure; the system ships no universal clinical limits (entry "plausible ranges" are typo guards only).
- **Lab dual verification** exists in code but is not switched on by any config setting.
- **Rate limiting is per process** (in-memory), so on serverless/multi-instance deployments it is not shared.
- **Pharmacist/lab/radiology scope is by existence of an order** for that patient, not by shift or assignment.
- **Nurse scope by ward** requires the nurse account to have a ward set; otherwise only explicit assignments grant access.
- **The patient portal is read-only**: patients can't book appointments, pay bills, or message staff.
- **Hand-over printing** is a generated HTML page; there is no QR/anti-forgery verification (the QR and audit hash-chain work you asked me to revert is not in this version).
- **Live monitors** are not connected; vitals are manual, simulated, or posted by a device key.
- **Uploaded-file durability on Vercel** needs the Supabase storage backend.

---------------------------------------------------------------------------------------------------

## 11. Code map: where each thing lives

All paths are inside the `careflow/` package unless they start with `static/` or `templates/`.
Line numbers point at the `def` line of the function (its `@bp.route` / `@require_perm` decorators sit 1-3 lines above). They match the current files and will drift if you edit them.

### 11.1 Request pipeline, security, access control
| What | File : line |
|---|---|
| App factory, health checks, page routes, schema check | `__init__.py` : create_app 31, schema_status 64, _register_pages 80 |
| Request security (before/after request, CSRF, rate limit, patient lock-down, must-change-password) | `security.py` : init_security 130, PATIENT_API_PREFIXES 127, _check_csrf 95 |
| Session loading (idle/absolute/epoch/demo) | `security.py` : load_user_from_session 105 |
| Login with lockout and rate limit | `security.py` : attempt_login 223 |
| Password strength rules | `security.py` : validate_password_strength 37 |
| Role -> permission table | `access.py` : ROLE_PERMS ~25-59 (deliverable.manage loop at 56, hospital-admin read extras at 59) |
| Role -> workspace tabs | `access.py` : ROLE_WORKSPACES (just below ROLE_PERMS) |
| Role -> patient scopes, document types per role, AI evidence scopes | `access.py` : ROLE_SCOPES, DOC_TYPES_BY_ROLE, AI_EVIDENCE_SCOPE |
| `@require_perm`, `login_required` | `access.py` : require_perm, login_required |
| Scope calculation | `access.py` : bulk_scopes, patient_scopes |
| Patient gate (404/403) | `access.py` : get_authorized_patient |
| SQL patient filter | `access.py` : visible_patient_filter |
| Field filtering of the patient record | `access.py` : patient_view |
| Audit writer and secret scrubbing | `audit.py` : audit, sanitize |
| Role names, status vocabularies, state-machine tables | `constants.py` : LAB_TRANSITIONS, RAD_TRANSITIONS, APPOINTMENT_TRANSITIONS, BED_MANUAL_TRANSITIONS, PHYSICAL_STATUSES, OBSERVATION_TYPES, DOC_TYPES |
| Timer and limit settings (idle, lockout, rate, escalation minutes, upload size) | `config.py` : build_config ~lines 289-330 |
| Database tables | `models.py` (AppUser, Patient, Admission, Bed, BedAssignment, LabReport, LabResult, RadiologyRecord, Prescription, Medicine, Bill, Payment, Alert, AlertRule, Observation, MedicalDocument, AuditLog, Notification, Deliverable ...) |

### 11.2 Login, account, notifications
| Feature | File : line |
|---|---|
| csrf / login / logout / me | `api/auth.py` : get_csrf 32, login 37, do_logout 44, me 50 |
| Demo accounts list | `api/auth.py` : demo_accounts 73 |
| Change own password | `api/auth.py` : change_password 84 |
| Notifications list / mark read | `api/auth.py` : notifications 106, notifications_read 122 |

### 11.3 Super admin / hospital admin
| Feature | File : line |
|---|---|
| Create / list / update / delete user | `api/admin.py` : create_user 67, users 55, update_user 101, delete_user 135 |
| Reset password, revoke sessions, unlock | `api/admin.py` : reset_password 163, revoke_sessions 179, unlock 189 |
| Link rules (doctor/ward/patient) and privileged-role guard | `api/admin.py` : _check_links 31, _guard_target 25, PRIVILEGED 16 |
| Audit viewer, security posture | `api/admin.py` : audit_log 199, security 221 |
| Operations console data | `api/workspaces.py` : admin 188 |
| Wards, rooms, beds, departments set-up | `api/beds.py` : add_department 39, add_ward 51, update_ward 64, add_room 86, add_bed 98, configure_bed 114 |
| Reports and CSV export | `api/reports.py` : _build 30, catalogue 80, report 86 |
| Care-team assignment | `api/patients.py` : add_assignment 635, end_assignment 658, list_assignments 629 |
| Doctors profiles | `api/scheduling.py` : create_doctor 31, update_doctor 43 |
| Alert rules | `api/monitoring.py` : create_rule 219, update_rule 232, review_rule 248 |
| Devices and device ingest | `api/monitoring.py` : create_device 271, revoke_device 284, device_ingest 295 |
| Simulator | `api/monitoring.py` : simulate 305 ; `services/monitoring.py` : simulate_tick 344 |
| AI purge | `api/ai.py` : purge 139 |

### 11.4 Patients, appointments, admissions (used by many roles)
| Feature | File : line |
|---|---|
| Patient code generator, field validation | `api/patients.py` : next_patient_code 28, _clean_patient_fields 36 |
| List / register / view / update patient | `api/patients.py` : list_patients 79, create_patient 98, get_patient 119, update_patient 129 |
| Verify identity, archive, delete | `api/patients.py` : verify_identity 162, archive_patient 178, delete_patient 191 |
| Patient journey (snapshot + timeline) | `api/patients.py` : patient_journey 212 ; `services/journey.py` : build_snapshot 47, build_timeline 108, current_stay 25, care_team 42 |
| Per-patient audit | `api/patients.py` : patient_audit 226 |
| Allergies / problems | `api/patients.py` : add_allergy 249, update_allergy 265, add_problem 288, update_problem 303 |
| Clinical notes + amend | `api/patients.py` : add_note 344, amend_note 363 (note types at line 321-322) |
| Care tasks | `api/patients.py` : add_task 405, update_task 426, list_tasks 445 |
| Care plans, intake/output | `api/patients.py` : add_care_plan 461, add_io 494 |
| Handover (draft, save, review) | `api/patients.py` : handover_draft 524, add_handover 573, review_handover 591 |
| Follow-ups | `api/patients.py` : add_followup 613 |
| Doctors list and slots | `api/scheduling.py` : list_doctors 24, doctor_slots 59 |
| Book / reschedule / status | `api/scheduling.py` : _validate_slot 96, create_appointment 115, update_appointment 133 |
| Start / complete consultation | `api/scheduling.py` : start_encounter 178, complete_encounter 201 |
| Bedboard | `api/beds.py` : bedboard 146 |
| Admit | `api/beds.py` : create_admission 263 ; `services/beds.py` : admit 68 |
| Assign bed / transfer | `api/beds.py` : assign_bed 288, transfer 300 ; `services/beds.py` : assign_bed 100, transfer 111, _occupy 55, _lock_bed 21 |
| Bed status | `api/beds.py` : bed_status 131 ; `services/beds.py` : set_bed_status 191 |
| Discharge plan / authorize / complete | `api/beds.py` : discharge_plan 312, discharge_authorize 324, discharge_complete 335 ; `services/beds.py` : plan_discharge 137, authorize_discharge 147, complete_discharge 159 |

### 11.5 Doctor
| Feature | File : line |
|---|---|
| Command-center worklist | `api/workspaces.py` : doctor 96, _attention 48, _attention_list 77, _my_patients 73 |
| Order lab | `api/orders.py` : create_lab 116 |
| Order radiology | `api/orders.py` : create_radiology 540 |
| Prescribe, warning preview, discontinue | `api/orders.py` : create_prescription 848, check_prescription 883, discontinue_rx 924 ; warnings logic `services/orders.py` : medication_warnings 104, DEMO_INTERACTIONS ~85 |
| Acknowledge critical result | `api/orders.py` : ack_critical 462, list_critical 447 |
| Lab trend | `api/orders.py` : lab_trend 424 |
| Record / correct / withdraw vitals | `api/monitoring.py` : add_observations 59, correct_obs 74, withdraw_obs 88 |
| Alert actions | `api/monitoring.py` : ack_alert 134, esc_alert 142, res_alert 151 |

### 11.6 Nurse
| Feature | File : line |
|---|---|
| Nursing workbench | `api/workspaces.py` : nurse 116 |
| Vitals engine | `services/monitoring.py` : record_observation 47, record_vitals 78, correct_observation 92, withdraw_observation 106 |
| Alert engine | `services/monitoring.py` : evaluate_observation 166, raise_alert 133, acknowledge_alert 182, escalate_alert 191, resolve_alert 204 |
| Observation freshness | `services/monitoring.py` : freshness 268 |
| Give medication (MAR) | `api/orders.py` : administer_rx 958 |
| Observation list and types | `api/monitoring.py` : list_observations 33, observation_types 27 |

### 11.7 Laboratory
| Feature | File : line |
|---|---|
| Lab workspace | `api/workspaces.py` : lab 142 |
| List / view lab orders | `api/orders.py` : list_labs 84, get_lab 104 |
| Collect / receive / reject / reorder | `api/orders.py` : lab_collect 143, lab_receive 158, lab_reject 170, lab_reorder 186 |
| Enter results | `api/orders.py` : lab_enter_results 242 (helpers _parse_result_items 196, _store_results 225) |
| Verify / release / one-step submit / amend | `api/orders.py` : lab_verify 254, lab_release 344, lab_submit 287, lab_amend 355, _do_release 266 |
| Status transitions, accession number, flags | `services/orders.py` : lab_transition 40, next_accession 52, compute_flag 22, summarize_results 57 |
| Critical-result creation | `services/orders.py` : notify_critical 66 |

### 11.8 Radiology
| Feature | File : line |
|---|---|
| Radiology workspace | `api/workspaces.py` : radiology 155 |
| List / view studies | `api/orders.py` : list_radiology 512, get_radiology 528 |
| Schedule / perform | `api/orders.py` : rad_schedule 576, rad_perform 589 |
| Draft report (+ versions) | `api/orders.py` : rad_report 607, _rad_version 599 |
| Authorize / one-step submit / amend | `api/orders.py` : rad_authorize 682, rad_submit 642, rad_amend 695, _do_authorize 628 |
| Transition check | `api/orders.py` : _rad_move 567 |

### 11.9 Pharmacy
| Feature | File : line |
|---|---|
| Pharmacy workspace (queue, low stock, expiring) | `api/workspaces.py` : pharmacy 165 |
| Verify / cancel | `api/orders.py` : verify_rx 892, cancel_rx 906 |
| Dispense | `api/orders.py` : dispense_rx 940 ; logic `services/orders.py` : dispense 137 |
| Inventory | `api/orders.py` : create_medicine 745, update_medicine 768, restock 797, movements 815 ; `services/orders.py` : adjust_stock 174 |
| Reconciliation | `api/orders.py` : get_reconciliation 997, save_reconciliation 1012 |
| Patient medication history | `api/orders.py` : patient_medications 983 |

### 11.10 Billing
| Feature | File : line |
|---|---|
| Billing workspace | `api/workspaces.py` : billing 178 |
| List / view bills | `api/orders.py` : list_bills 1054, get_bill 1069 |
| Create bill / from admission | `api/orders.py` : create_bill 1090, bill_from_admission 1108 |
| Update (legacy paid toggle, insurance status) | `api/orders.py` : update_bill 1140 |
| Payment / refund / adjustment / void | `api/orders.py` : add_payment 1166, add_refund 1186, add_adjustment 1205, void_bill 1232 |
| Claims | `api/orders.py` : add_claim 1248, update_claim 1268 |
| Balance maths and status refresh | `services/orders.py` : bill_figures 188, refresh_bill_status 198 |

### 11.11 Patient portal
| Feature | File : line |
|---|---|
| Portal overview | `api/portal.py` : overview 41 (helper _me 25, _doc_card 34) |
| Document download | `api/portal.py` : download 136 |
| Printable copy of report/bill | `api/portal.py` : deliverable_copy 175 |
| Portal screen (browser) | `static/js/portal.js` |
| Hand-over tracking (staff side) | `api/deliverables.py` : list_deliverables 20, create_deliverable 28, update_deliverable 55 ; `services/deliverables.py` : ensure 10, share_documents_with_patient 23, row 30 |

### 11.12 AI assistant
| Feature | File : line |
|---|---|
| Endpoints | `api/ai.py` : status 37, create_conversation 51, list_conversations 64, get_conversation 81, delete_conversation 88, ask 102 |
| Orchestration and system prompt | `ai/assistant.py` : run (bottom), SYSTEM_PROMPT (top) |
| Evidence retrieval, BM25 | `ai/retrieval.py` : Builder class, bm25_rank, classify |
| Safety checks (injection, numbers, secrets) | `ai/safety.py` : sanitize_untrusted, is_emergency, is_decision_request, ungrounded_numbers, validate_answer |
| Provider selection and external-data block | `ai/providers.py` : get_provider 138, check_phi_allowed 161 |
| Browser side | `static/js/assistant.js`, `static/js/views.js` (renderAi) |

### 11.13 Documents and OCR
| Feature | File : line |
|---|---|
| Upload / list / view / download | `api/documents.py` : upload_document 60, list_documents 108, get_document 115, download_document 128 |
| Visibility, reprocess, review, correct page text | `api/documents.py` : set_visibility 147, reprocess_document 159, review_document 174, correct_page 187 |
| Extraction | `api/documents.py` : process_document 44 ; `services/documents.py` : extract 229 |
| File type check by magic bytes | `services/documents.py` : sniff_and_validate 29 |
| Storage backends | `services/documents.py` : LocalStorage 88, SupabaseStorage 121, get_storage 149 |

### 11.14 Command line and seed data
| What | File |
|---|---|
| Flask commands (db-doctor, seed-demo, add-sample-patients, add-bulk-patients, add-sample-staff, monitor-sweep) | `cli.py` |
| Base demo data | `seed.py`; extra data `seed_more.py`, `seed_bulk.py`, `seed_staff.py` |
| Migrations | `migrations/versions/0001` ... `0005` |
| Entry point | `app.py` (project root) |

### 11.15 Browser side (static/js)
| File | Role |
|---|---|
| `api.js` | fetch wrapper: JSON, CSRF header, 401 -> login redirect, error objects |
| `app.js` | boot: /api/auth/me, tab building, notification polling (60 s), forced password change |
| `dashboards.js` | the doctor / nurse / lab / radiology / pharmacy / billing / admin workspace screens |
| `bedboard.js`, `views.js` | bedboard, patients list, appointments, AI view |
| `patient.js` | the patient drawer (journey, notes, orders, results, documents, hand-over) |
| `actions.js` | forms/buttons that call the write endpoints |
| `portal.js` | patient "My Care" screen |
| `admin.js` | users and audit screen |
| `login.js`, `ui.js` | login page, small UI helpers |
| `templates/index.html`, `templates/login.html` | the two HTML shells |
