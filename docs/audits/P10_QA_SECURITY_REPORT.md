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

The backend regression suite passes 412 tests. The focused P10 security and CI-range suites pass 26 tests. The frontend suite passes 14 tests, the production build transforms 1,711 modules, the clean migration reaches the Alembic head, the backend import passes with the project virtual environment, and the repository hygiene check inspects 171 tracked files.

HTTP smoke results record transport and authorization safety separately from engineering verification: health/CORS, 413 body rejection, 429 rate limiting, strong and weak-secret behavior, anonymous and project-persisted runs, cross-tenant denial, persistent run/report authorization, database-failure fail-closed behavior, and sanitized legacy errors are covered. Legacy calculation responses remain explicitly `UNVERIFIED`.

## Dependency audits

### Python runtime findings (`pip-audit -r backend/requirements.txt`)

The tool reports advisory identifiers and fixed versions, but does not provide a normalized severity field. Compatibility below means compatibility with the current exact pins was not established, not that a finding is unreachable.

| Package | Installed | Advisory | Reported fix | Compatible fix established |
| --- | --- | --- | --- | --- |
| anyio | 4.9.0 | GHSA-82r6-8w77-94w6 | 4.14.2 | No; review required |
| anyio | 4.9.0 | GHSA-5p39-cfhj-2xmp | 4.14.2 | No; review required |
| click | 8.2.1 | PYSEC-2026-2132 | 8.3.3 | No; review required |
| starlette | 0.47.2 | PYSEC-2026-161 | 1.0.1 | No compatible fix established |
| starlette | 0.47.2 | PYSEC-2026-249 | 1.3.1 | No compatible fix established |
| starlette | 0.47.2 | PYSEC-2026-248 | 1.3.0 | No compatible fix established |
| starlette | 0.47.2 | PYSEC-2026-1942 | 0.49.1 | No; review required |
| starlette | 0.47.2 | PYSEC-2026-2281 | 1.1.0 | No compatible fix established |
| starlette | 0.47.2 | PYSEC-2026-2280 | 1.1.0 | No compatible fix established |
| idna | 3.10 | PYSEC-2026-215 | 3.15 | No; review required |
| requests | 2.32.4 | PYSEC-2026-2275 | 2.33.0 | No; review required |
| urllib3 | 2.5.0 | PYSEC-2026-141 | 2.7.0 | No; review required |
| urllib3 | 2.5.0 | PYSEC-2026-1998 | 2.6.0 | No; review required |
| urllib3 | 2.5.0 | PYSEC-2026-1994 | 2.6.0 | No; review required |
| urllib3 | 2.5.0 | PYSEC-2026-1996 | 2.6.3 | No; review required |
| ecdsa | 0.19.2 | PYSEC-2026-1325 | none reported | No fix reported |

### Python development findings

`pip-audit -r backend/requirements-dev.txt` reports the same runtime findings plus one additional development dependency finding in `pytest` 8.4.2 (`PYSEC-2026-1845`, reported fix 9.0.3). The audit also includes the pinned audit tooling dependency graph. Advisory severity is not inferred from this output.

### NPM runtime findings (`npm audit --omit=dev`)

| Package | Severity reported by npm | Advisory | Fix availability |
| --- | --- | --- | --- |
| react-router | moderate | GHSA-wrjc-x8rr-h8h6; GHSA-337j-9hxr-rhxg | `react-router-dom` 7.18.4, semver-major breaking upgrade |
| react-router-dom | moderate (transitive react-router) | GHSA-wrjc-x8rr-h8h6; GHSA-337j-9hxr-rhxg | `react-router-dom` 7.18.4, semver-major breaking upgrade |

### NPM development findings (`npm audit`)

The full audit additionally reports `esbuild` moderate (GHSA-67mh-4wv8-2f99, fixed through Vite 8.3.0) and `vite` high (GHSA-4w7w-66w2-5vf9, GHSA-v6wh-96g9-6wx3, GHSA-fx2h-pf6j-xcff, fixed through Vite 8.3.0). Both fixes are breaking major upgrades. No dependency was upgraded without a separate compatibility review.

## Repository hygiene and residual risk

The hygiene script rejects tracked dependency directories, build output, Python caches, local databases, generated reports, and secret environment files, including nested `.env*` basenames. Process-local rate limiting, SQLite persistence, missing production secret management, and the deferred engineering verification phases remain material release limitations.

## CI

`.github/workflows/ci.yml` runs the deterministic checks on push and pull request using Python 3.12 and Node.js 20. It does not deploy. The hosted CI result must be reported separately from local execution and must not be described as production certification.

## Engineering integrity

No concrete design equation, steel design equation, load-factor value, seismic equation, section-property value, or P3 structural-solver equation was modified.
