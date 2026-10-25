# Connecting CareFlow to Supabase PostgreSQL

CareFlow talks to Supabase **only through PostgreSQL** (psycopg 3 + Alembic migrations). The application server is the only
component that holds credentials; the browser never receives a database or service-role key.

> **Status of this guide:** the connection logic, diagnostics and migrations are tested against a local PostgreSQL 16 server.
> They have **not** been verified against your Supabase project from the build environment (it has no route to Supabase).
> Run the doctor below on your own machine to verify.

## 1. Rotate the password first
A database password that was ever pasted into a chat, zip file or screenshot must be treated as exposed.
Supabase Dashboard → Project Settings → Database → *Reset database password*. Put the new one only in your local `.env`.

## 2. Get the exact connection string
Dashboard → **Connect** → **Session pooler** (port 5432). Copy it exactly. Do not guess hostnames. Notes:

| Option | Host looks like | Use when |
|---|---|---|
| Direct | `db.<ref>.supabase.co:5432` | Your network has IPv6. Many home/campus networks do not. |
| **Session pooler** | `aws-0-<region>.pooler.supabase.com:5432` | **Recommended** – IPv4 compatible, supports migrations. User is `postgres.<project-ref>`. |
| Transaction pooler | same host, port `6543` | App traffic only; run migrations through 5432. |

Replace `[YOUR-PASSWORD]` **without the brackets** and URL-encode special characters (`@`→`%40`, `#`→`%23`, `/`→`%2F`).

## 3. Configure and verify
**Windows PowerShell**
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env        # edit .env: DATABASE_URL, SECRET_KEY
flask --app app check-config
flask --app app db-doctor
```
**Linux / macOS**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # edit .env: DATABASE_URL, SECRET_KEY
flask --app app check-config
flask --app app db-doctor
```
`db-doctor` reports each stage separately: **config → DNS → TCP (5432 and 6543) → TLS+auth → session → schema → migrations**.

## 4. Reading the doctor's result
| Result | Meaning | Do this |
|---|---|---|
| `config` fails: placeholder / brackets / `@` | The URL itself is malformed | Re-copy from the dashboard; encode the password |
| `dns` fails | Stale or invented hostname | Re-copy the host from **Connect**; do not guess |
| `dns` ok, `tcp` fails on 5432 **and** 6543 | **Network/firewall block** (campus, hostel and corporate Wi‑Fi often block outbound PostgreSQL) | Try a mobile hotspot/another network, or deploy on a host that allows egress. **Not a password problem – do not reset the password for this.** |
| `tcp` fails on 5432 but 6543 works | Pooler port blocked | Use the transaction-pooler URI for the app; run migrations from a network where 5432 works |
| `tls+auth`: "Tenant or user not found" | Wrong pooler username | Username must be `postgres.<project-ref>` |
| `tls+auth`: authentication failed | Reachable, wrong credentials | Reset the password in Supabase; update `.env` |
| `schema` empty | Connected, tables not created | `flask --app app db upgrade` |

CareFlow never falls back to SQLite when `DATABASE_URL` is set (or `DB_BACKEND=postgres`): it stops with a clear error instead.
`GET /health` returns **503** whenever a real `SELECT 1` fails.

## 5. Create the schema and the first administrator
```bash
flask --app app db upgrade                  # same command in PowerShell
flask --app app init-reference-data         # observation types / default reference data (idempotent)
flask --app app create-admin --email you@example.org --name "Your Name"
```
Existing databases created by the original prototype are upgraded in place (rows are preserved; the migration aborts without
changes if existing data violates a new rule, e.g. two active admissions for one patient). **Back up before upgrading.**
Downgrades are intentionally refused; restore from a backup instead.

## 6. Private document storage (optional)
Default is a private local folder (`UPLOAD_DIR`). For Supabase Storage set `STORAGE_BACKEND=supabase`, `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, and create a **private** bucket named by `SUPABASE_BUCKET`. Files are served through authorised,
audited endpoints or short-lived signed URLs. The service-role key stays on the server.

## 7. Row Level Security
CareFlow enforces authorisation in the Flask server (role + care-relationship checks on every request). It connects with a
privileged database role, which bypasses RLS. If you also expose the Supabase Data API, enable RLS with no permissive policies on every
`public` table so the API keys cannot read clinical data: this is defence in depth and is **not** configured by the migrations.

## 6. Quick path: connect, create tables, load sample data
1. Supabase Dashboard → **Connect** → copy the **Session pooler** URI (port 5432), replace `[YOUR-PASSWORD]`, URL-encode special characters.
2. In `.env` set:
   ```
   DATABASE_URL=postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres
   DB_BACKEND=postgres
   DEMO_MODE=1
   DEMO_PASSWORD=CareFlow-Demo-2026!
   SECRET_KEY=<any long random string>
   ```
3. Run, in order:
   ```
   python -m flask --app app db-doctor
   python -m flask --app app db upgrade
   python -m flask --app app seed-demo
   python -m flask --app app add-sample-patients
   python app.py
   ```
   `add-sample-patients` adds 41 more patients (including Pooja Shree), five more doctors, three more nurses, three more wards, with
   admissions, lab and radiology reports, prescriptions, bills, payments, appointments and hand-over items. It is safe to run twice.
   Extra patient logins: `patient2@careflow.demo.example` (Pooja Shree), `patient3@…` (Ishita Sharma), `patient4@…` (Keerthi Nair).
4. Open **Table Editor** in Supabase to see all 48 tables filled in. You can also paste `database/schema_postgresql.sql`
   into the **SQL Editor** to create the empty tables without running migrations; if you do that, run
   `python -m flask --app app db stamp head` afterwards so migrations know the tables already exist.

### More sample data
```
python -m flask --app app add-bulk-patients --count 200
```
Adds 200 new patients, each with their own age, phone, e-mail, address, emergency contact, insurance and history, plus matching
admissions (some already discharged), lab and radiology reports, prescriptions, bills, payments and appointments. It also fills the
missing contact details on the earlier sample patients. Run it again to add more.

### Accounts for every role
```
python -m flask --app app add-sample-staff
```
Adds 2nd and further accounts for each role: `super2`, `admin2-3`, `doctor8-12`, `nurse5-10`, `lab2-4`, `pharmacist2-3`,
`radiology2-3`, `billing2-4` and patient logins `patient5` onward (30 per run, `--patient-logins N` to change), all at `@careflow.demo.example`
with the shared password.
