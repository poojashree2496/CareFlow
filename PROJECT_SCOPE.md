# CareFlow — scope and known limits

CareFlow turns the original single-file hospital prototype into a role-based, auditable clinical workspace.
**It is a demonstration/teaching system. It is not a certified medical device or a validated EHR and must not guide real patient care.**

## What is implemented
* Server-side authentication, 8 roles, least-privilege scopes, resource-level authorisation (care relationships), CSRF, session timeouts, lockout, audit.
* Patient journey, admissions/beds/transfers/discharge, orders (lab, radiology, pharmacy with dispense ≠ administer), billing/claims, notes with amendments, tasks, handover.
* Monitoring: observations with provenance (manual/device/simulated), freshness, configurable alert rules that need clinical review, device ingestion endpoint, labelled simulator.
* Role-based editing (each role edits only what it owns; one-step lab/radiology *Complete & submit* with attached report), a read-only **patient portal** (own released records, reports, documents, bills, assistant) and digital/physical **hand-over tracking**.
* Patient-aware AI assistant (server-side RAG, citations, safety checks) with an honest "configuration required" state.
* Documents: private storage, validation, OCR/extraction quality, review and correction.
* PostgreSQL/Supabase with Alembic migrations; safe diagnostics; automated tests.

## Known limits (be honest with your users)
* **Not verified against a live Supabase project, live OCR (Tesseract), or a live external AI provider** from the build environment. Tests use local PostgreSQL 16 / SQLite, mocked HTTP for AI, and simulated data.
* The login/API **rate limiter is per-process, in memory**. Behind several workers it is per worker; use a shared store or a reverse proxy for real deployments.
* There is **no background scheduler**. Monitoring sweeps run on dashboard load, via the API, and with `flask monitor-sweep` (run it from cron/Task Scheduler).
* **Allergy matching is substring-based**: "Amoxicillin" is *not* matched to a "Penicillin" allergy. The drug-interaction list is a 4-pair illustration, not a drug database.
* Alert rule defaults are examples marked *Unreviewed*; a clinician must review thresholds before use.
* Legacy patients imported from the prototype are visible **only to administrators** until care-team assignments are made (least privilege by design).
* The AI assistant cannot analyse images; it uses extracted report text only and says so. It never diagnoses or prescribes.
* The simulator produces simulated readings, always labelled "simulated".
* Data-protection compliance (HIPAA/GDPR etc.), backups, TLS termination, key management and monitoring are the deployer's responsibility.


## Patient portal limits
* Read-only by design; the assistant is the only interactive feature and runs in plain-language mode on the patient's own released data.
* Patients never see unreleased results, drafts, clinical notes, alerts or unshared documents.
* Physical copies are tracked (requested / ready / handed over, with recipient), not printed by CareFlow.
* Patient logins are created by an administrator with a temporary password; there is no self-registration.
