# CareFlow — Smart Hospital Digital Ecosystem

CareFlow connects every step of a patient's stay — appointment, admission, bed, observations, orders, results, medicines, billing and
discharge — into one **Connected Patient Journey**, with a role-specific workspace for each member of staff.
It is built on the original single-file prototype (kept in `legacy/app_v1.py`); existing features and data are preserved.

> **Demonstration / teaching system.** Not a certified medical device and not validated for real patient care.
> Read [PROJECT_SCOPE.md](PROJECT_SCOPE.md) for the honest list of limits. Use demonstration data only.

## Highlights
* **Nine roles** with server-side authorisation: super admin, hospital admin, doctor, nurse, lab, pharmacist, radiology, billing, and **patient**.
  Clinical staff see only patients they have a care relationship with. CSRF protection, session timeouts, lockout, audit trail.
* **Every role edits what it owns and only views the rest** — each dashboard states which is which, and the server enforces it.
  Lab and radiology staff attach the report and press *Complete & submit*; the order is completed, audited step by step, and the
  report becomes viewable by doctors, administrators and the patient. Pharmacy verifies/dispenses, nurses record vitals and tasks,
  doctors write notes, billing records payments, admins manage accounts (and can read, not alter, clinical reports).
* **Patient dashboard (read-only)**: a patient signs in and sees only their own released record — stay, medicines, lab and scan
  reports with downloads, shared documents, bills, and digital vs physical copy hand-over status — plus the AI assistant, which
  is the only interactive part. Unreleased results, clinical notes and monitoring alerts are never shown to patients.
* **Hand-over tracking**: staff record whether each printed copy is requested, ready or handed over (and to whom). CareFlow tracks
  this; it does not print.
* **Workspaces**: Doctor Clinical Command Center (attention-ranked patients), live Bedboard, Nursing workbench, Lab, Pharmacy,
  Radiology, Billing & Insurance, Operations console, Patients, Appointments, CareFlow AI.
* **Monitoring you can trust**: every reading shows its source (manual / device / **simulated**) and freshness; alert rules must be
  clinically reviewed; stale data is shown as stale.
* **Patient-aware AI assistant**: authorises every request on the server, uses only the selected patient's permitted records,
  cites its sources, refuses to diagnose or prescribe, and says "configuration required" instead of faking an answer.
* **Documents**: private storage, type/size validation, OCR with an extraction-quality indicator, reviewer corrections.
* **PostgreSQL/Supabase** with Alembic migrations and a staged connectivity doctor. No silent SQLite fallback.

## Quick start (local demo, SQLite)
**Windows PowerShell**
```powershell
py -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DEMO_MODE = "1"; $env:DEMO_PASSWORD = "Choose-A-Long-Demo-Password-1"
flask --app app db upgrade
flask --app app seed-demo
flask --app app run
```
**Linux / macOS**
```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
export DEMO_MODE=1 DEMO_PASSWORD='Choose-A-Long-Demo-Password-1'
flask --app app db upgrade
flask --app app seed-demo
flask --app app run
```
Open <http://127.0.0.1:5000>. In demo mode the sign-in page lists the demo accounts (e.g. `doctor1@careflow.demo.example`);
they have exactly their role's permissions. Demo mode is refused in `CAREFLOW_ENV=production`.

## Real use (PostgreSQL / Supabase)
1. Follow [SUPABASE_SETUP.md](SUPABASE_SETUP.md) (rotate your password, copy the exact Session-pooler URI, run `flask --app app db-doctor`).
2. Copy `.env.example` to `.env` and set `DATABASE_URL`, `SECRET_KEY`, `CAREFLOW_ENV=production`.
3. `flask --app app db upgrade`, then `flask --app app create-admin --email you@example.org --name "Your Name"`.
4. Serve with a production server: `waitress-serve --listen=0.0.0.0:8000 app:app` (Windows) or `gunicorn app:app` (Linux), behind HTTPS.

Upgrading a database created by the original prototype is supported: `flask --app app db upgrade` (back up first; see the setup guide).

## Upgrading an existing install
This update adds migration `0003_patient_portal` (additive: a `patient` role, `app_user.patient_id`, `medical_document.patient_visible`, a `deliverable` table).
1. Stop the app and **back up your database** (for the demo: copy `hospital.db`).
2. `flask --app app db upgrade`
3. Patients need a login: sign in as an administrator -> *Users & audit* -> *Patient portal logins* -> choose the patient and set a temporary password (they must change it at first sign-in). The demo login is `patient1@careflow.demo.example`.

Limits: the portal is read-only; patients see released items only; physical copies are tracked, not produced; downgrades are refused.

## Command reference
| Command | Purpose |
|---|---|
| `flask --app app check-config` | Validate configuration without printing secrets |
| `flask --app app db-doctor` | Staged DB diagnosis: config, DNS, TCP, TLS+auth, schema, migrations |
| `flask --app app db upgrade` / `db-status` | Apply / inspect migrations |
| `flask --app app init-reference-data` | Load observation types (idempotent) |
| `flask --app app seed-demo` | Demo data (requires `DEMO_MODE=1`, never production) |
| `flask --app app create-admin` | Create an administrator (password prompted, or `CAREFLOW_ADMIN_PASSWORD`) |
| `flask --app app monitor-sweep` | Missing-data alerts and escalations: schedule it (cron / Task Scheduler) |
| `flask --app app purge-ai` | Delete AI conversations older than `AI_RETENTION_DAYS` |

## AI assistant configuration
Set `AI_PROVIDER` (`anthropic`, `openai`, or `local` for an OpenAI-compatible server), `AI_MODEL`, and `AI_API_KEY` **in `.env` only**.
Patient data is never sent to an external provider unless `AI_ALLOW_EXTERNAL_PHI=true`; with a `local` endpoint nothing leaves your network.
Without configuration the assistant shows the permitted evidence it found and states that no model answered.

## Tests
```bash
pip install -r requirements-dev.txt
pytest                                   # throw-away SQLite database
# Recommended: the same engine as production (a LOCAL empty PostgreSQL database whose name contains "test")
export TEST_DATABASE_URL='postgresql+psycopg://postgres:<password>@127.0.0.1:5432/careflow_test'
export TEST_MIGRATION_DATABASE_URL='postgresql+psycopg://postgres:<password>@127.0.0.1:5432/careflow_migrate_test'
pytest
```
PowerShell: `$env:TEST_DATABASE_URL = "postgresql+psycopg://..."`. Tests never read `.env` and refuse a non-test database.
The suite covers authentication/RBAC, resource-level authorisation, clinical workflows, monitoring, documents, AI safety, configuration
diagnostics and migrations (fresh install and upgrade of a legacy database with data preserved).

## Project layout
```
app.py                WSGI entry point            careflow/api/        REST blueprints
careflow/             application package         careflow/services/   business rules (beds, orders, monitoring…)
careflow/ai/          provider, retrieval, safety migrations/            Alembic revisions (0001 legacy baseline, 0002 core)
static/ templates/    vanilla JS/CSS UI (no CDN)  tests/  legacy/       tests and the original prototype
```
The UI uses system fonts and no external scripts (Content-Security-Policy `script-src 'self'`).
