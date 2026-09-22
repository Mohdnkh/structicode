# P9 Enterprise Data Report

## Scope

P9 adds a local-first SQLAlchemy and Alembic data foundation, local JWT authentication, organizations, memberships, projects, persistent P7 analysis records, report-generation records, engine provenance, and minimal frontend project association. No engineering formula or deployment configuration is changed.

## Execution evidence

- `npm run db:migrate` applied revision `20260922_p9_initial` to a clean default SQLite database and created `alembic_version`, `users`, `organizations`, `organization_memberships`, `projects`, `engine_versions`, `persistent_analysis_runs`, and `report_records`.
- `backend/tests/test_enterprise_data.py`: 5 passed. It covers registration, normalized duplicate email rejection, hashed password storage, generic credential failure, invalid/missing authentication, missing-secret safety, project versioning, membership removal, two-tenant isolation, anonymous analysis, project analysis, memory-store restart, report event recording, tamper rejection, and project structure persistence.
- Full backend suite: 384 passed.
- Focused regressions: P3 solver 41 passed; P4 concrete safety 25 passed; P5 steel safety 43 passed; P6 registry 144 passed; P7 reporting 13 passed.
- Frontend Node suite: 13 passed. `npm run build` passed with Vite 5.4.21 and transformed 1711 modules. `npm run verify:backend` passed using the documented local `.venv` runtime.
- Authenticated test-client HTTP coverage verifies anonymous health-compatible v1 behavior, unauthorized project creation/project analysis, authorized element and structure persistence, project history, restart retrieval, report creation, and foreign-user 404 behavior. No deployed service, Railway action, or production database was used.

## Safety boundaries

P4 and P5 remain `DEFERRED — SOURCE BLOCKED`. `PROJECT_PERSISTED` only describes storage; it does not change a design code capability or engineering verification status. PDFs are not stored as durable blobs. Production hardening and deployment remain P10 and P12 work.

## Independent-review rework

- Password hashing now uses Passlib `bcrypt_sha256` as the canonical scheme, with legacy raw bcrypt verification retained only for compatibility. Long ASCII and multi-byte Unicode regression tests prove suffix bytes affect authentication and are not silently truncated at bcrypt's 72-byte boundary.
- Registration, login, and `/auth/me` check `STRUCTICODE_AUTH_SECRET` before account lookup or mutation. Missing configuration returns `503 AUTH_NOT_CONFIGURED` for valid, invalid, duplicate, and missing-token auth operations without disclosing account state.
- The existing `structicode-auth-cleared` event now clears both the token and active project selection. Stale project IDs are replaced with the first accessible project or cleared; project 404 responses also clear selection. Traceable report 401 responses use the same clearing path.
- Root scripts are cross-platform: `verify:backend` uses `python -c "import backend.api.main"` and `db:migrate` uses `python -m alembic upgrade head`. With the repository virtual environment activated, a clean temporary SQLite migration and backend import both passed.
- SQLite timestamps are normalized to UTC at API serialization boundaries and are emitted with `Z` or `+00:00` offsets for projects and persistent run history.
- Rework validation: P9 focused backend tests 7 passed; full backend suite 386 passed; frontend tests 14 passed; build passed; protected engineering and deployment paths remained unchanged.
