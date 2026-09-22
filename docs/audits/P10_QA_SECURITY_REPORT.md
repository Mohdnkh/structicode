# P10 QA, Security, and Reliability Report

## Scope and status

P10 is a QA/security gate for the local release candidate. It does not verify concrete or steel design equations and does not authorize P11 or P12. P4 and P5 remain deferred as source-blocked phases.

## Security controls implemented

- CORS uses `STRUCTICODE_CORS_ORIGINS`, defaults to `http://127.0.0.1:5173` and `http://localhost:5173`, ignores wildcard entries, and does not enable credentials.
- API request bodies are bounded by `STRUCTICODE_MAX_REQUEST_BYTES` (default 1 MiB, bounded to 1 KiB–16 MiB) using accumulated ASGI body bytes rather than `Content-Length` alone.
- Typed element and structure requests have model-count, member-load, and numeric-magnitude guards.
- Auth and analysis POST/PATCH routes use a bounded process-local rate limiter with configurable windows and limits. This is not distributed rate limiting.
- HS256 authentication requires a non-blank secret of at least 32 UTF-8 bytes. Login uses a dummy bcrypt hash for missing-user failures, and auth/report responses use `Cache-Control: no-store`.
- Persistent run lookup fails closed on database exceptions, and persistent rows take precedence over the ephemeral store for the same run ID.
- Project updates use a database version compare-and-swap boundary; engine-version identity creation handles unique races through a savepoint.
- Legacy errors are sanitized, temporary PDF names are unique and cleaned up, and unexpected API errors return generic envelopes without exception text.

## Commands and results

Required commands are:

```text
python scripts/check_repository_hygiene.py
python -m alembic upgrade head
python -m pytest backend/tests -q
node --test frontend/tests/*.test.mjs
npm run build
python -c "import backend.api.main"
cmd /c "set PATH=.venv\\Scripts;%PATH%&& npm run verify:backend"
python -m pip_audit -r backend/requirements.txt --format json
python -m pip_audit -r backend/requirements-dev.txt --format json
npm audit --omit=dev
npm audit
git diff --check
```

The backend regression suite passes 395 tests. The frontend suite passes 14 tests, the production build transforms 1,711 modules, the clean migration reaches the Alembic head, the backend import passes with the project virtual environment, and the repository hygiene check inspects 158 tracked files.

HTTP smoke results record transport and authorization safety separately from engineering verification: health/CORS, 413 body rejection, 429 rate limiting, strong and weak-secret behavior, anonymous and project-persisted runs, cross-tenant denial, persistent run/report authorization, database-failure fail-closed behavior, and sanitized legacy errors are covered. Legacy calculation responses remain explicitly `UNVERIFIED`.

## Dependency audits

`npm audit --omit=dev` reports 2 moderate runtime advisories in the current React Router line. Full `npm audit` reports 4 advisories (3 moderate and 1 high), including the Vite/esbuild development advisory. Remediation requires a breaking major upgrade, so no unreviewed dependency upgrade was made in P10.

`pip-audit` 2.9.0 reports 16 advisories across the runtime requirements and 17 across the development requirements. No critical severity was identified in the generated reports; each item remains a documented maintenance input rather than an unreviewed breaking upgrade.

## Repository hygiene and residual risk

The hygiene script rejects tracked dependency directories, build output, Python caches, local databases, generated reports, and secret environment files. Process-local rate limiting, SQLite persistence, missing production secret management, and the deferred engineering verification phases remain material release limitations.

## CI

`.github/workflows/ci.yml` runs the deterministic checks on push and pull request using Python 3.12 and Node.js 20. It does not deploy. The hosted CI result must be reported separately from local execution and must not be described as production certification.

## Engineering integrity

No concrete design equation, steel design equation, load-factor value, seismic equation, section-property value, or P3 structural-solver equation was modified.
