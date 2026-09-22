# P12 Deployment Decision Report

## Decision

`NO-GO`

P12 prepares a provider-neutral release package and documents the exact owner gates. It does not provision or deploy anything. The unresolved runtime dependency advisories and missing owner/provider/database decisions prohibit a GO decision without owner risk acceptance.

## Repository facts

- Main base: `ceefb11a91fc64ab2c55ed9dd9dfb8dab4105918`.
- P11 was merged before this phase; the P12 branch starts from that main head.
- FastAPI can serve `frontend/dist` and React client routes through the fallback route.
- Local storage defaults to SQLite; PostgreSQL support uses `psycopg2-binary` and Alembic.
- Project-owned runs and report metadata are database-persistent; anonymous runs remain process-local and ephemeral.
- Trusted report bytes are regenerated from stored run records. Legacy `/generate-pdf` uses an operating-system or configured temporary directory and is explicitly unverified.
- Rate limiting remains process-local.
- No production infrastructure or public deployment exists.

## Packaging implementation

- Replaced the old single-stage development Dockerfile with a Node 20 / Python 3.12 multi-stage image.
- Added a non-root runtime user, compiled frontend-only runtime assets, one-worker production launcher, and a production `.dockerignore`.
- Added `/ready` with a minimal database `SELECT 1` check and safe 503 response behavior.
- Added `scripts/start_production.py` and `scripts/production_preflight.py`.
- Moved legacy temporary PDFs to `tempfile` storage.
- Added an opt-in PostgreSQL compatibility suite and separate GitHub Actions PostgreSQL 16 and container-build jobs.
- Added provider comparison, topology, environment, operations, runbooks, manifest, smoke plan, and decision documentation.

## PostgreSQL evidence

The deterministic CI gate uses PostgreSQL 16, runs Alembic `upgrade head`, executes registration/login, project creation, project-persisted analysis, retrieval, report generation, tenant isolation, and optimistic version conflict checks, then exercises `downgrade base` followed by `upgrade head`. Local evidence is recorded separately in the execution report; no production database was used.

## Provider evidence

Railway, Render, and Fly.io were compared using current official documentation accessed 2026-09-22. Sources and capability notes are in `docs/deployment/PROVIDER_COMPARISON.md`. No provider is selected because no owner supplied a provider, region, cost ceiling, or operational owner.

## Dependency risk evidence

- `python -m pip_audit -r backend/requirements.txt`: 16 known vulnerabilities in 7 packages.
- `python -m pip_audit -r backend/requirements-dev.txt`: 17 known vulnerabilities in 8 packages.
- `npm audit --omit=dev`: 2 moderate React Router vulnerabilities; the available fix is a breaking major upgrade.
- `npm audit`: 4 vulnerabilities total, including one high Vite advisory and three moderate advisories; available fixes include breaking upgrades.

These findings are not silently accepted. No owner acceptance is present, so they remain `UNRESOLVED — NO-GO`.

## Operational blockers

- Provider selection, account, region, budget, and ownership are unresolved.
- Managed PostgreSQL backup retention and a real restore drill are not operationally configured.
- Process-local anonymous state and rate limiting prohibit scale-out above one replica.
- Public HTTPS, provider secrets, monitoring, and production migration execution remain owner-controlled deployment steps.
- P4 and P5 remain source blocked and excluded from verified release scope.

## Owner-risk decisions required

The owner must select a provider, approve the one-replica topology, resolve or explicitly accept each material runtime dependency advisory, define backup retention and recovery objectives, assign operational ownership, and explicitly authorize any later deployment.

## Deployment safety

No provider CLI, cloud API, project, database, bucket, domain, secret, registry push, deployment, Git tag, or GitHub Release was used during P12.

## Local verification evidence

- Backend regression: `.venv\\Scripts\\python.exe -m pytest backend/tests -q` passed with `421 passed, 1 skipped`.
- Frontend regression: `node --test frontend/tests/*.test.mjs` passed with `14 passed, 0 failed`.
- Frontend build: `npm run build` passed with Vite `5.4.21` and `1,711 modules transformed`.
- Dependency tree: `npm ls --depth=0` completed without invalid, extraneous, unmet, or peer dependency errors.
- Import and whitespace checks: `npm run verify:backend` and `git diff --check` passed. The latter reports only Git's CRLF normalization warnings.
- Migration round trip: SQLite and PostgreSQL 16 both completed `upgrade head`, `downgrade base`, and `upgrade head`. Alembic now uses an explicit transaction context so the revision row is committed and repeatable.
- PostgreSQL compatibility: a temporary local PostgreSQL 16 container passed `backend/tests/test_postgres_compatibility.py` (`1 passed`). The container was removed after the test; no production database was used.
- Container package: `docker build --tag structicode:p12-local .` passed. A temporary local container smoke test returned HTTP 200 for `/health`, `/`, and `/api/v1/capabilities`; it was stopped and removed.

These local checks demonstrate package behavior only. They do not resolve the dependency advisories, provider ownership, production database backup, or restore-drill blockers that keep the release decision at `NO-GO`.
