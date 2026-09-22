# Structicode

Structicode is a local-first structural engineering analysis workspace with explicit capability and verification states, traceable server-owned analysis records, and bounded 2D frame mechanics.

It is a release candidate for local engineering review. It is not globally code compliant, a certified design platform, a production SaaS, or a substitute for an independent engineer. Concrete and steel design paths remain legacy and unverified; seismic design is not an active verified v1 workflow.

## Quick start

Requirements: Python 3.12, Node.js 20 LTS or newer, npm, and Git.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m pip install -r backend/requirements-dev.txt
npm ci
export STRUCTICODE_DATABASE_URL=sqlite:///./structicode-local.sqlite3
export STRUCTICODE_AUTH_SECRET=replace-with-a-local-secret-at-least-32-bytes
python -m alembic upgrade head
npm run dev
```

On Windows PowerShell use `\.venv\Scripts\Activate.ps1` and `$env:NAME = "value"`. The combined command serves FastAPI at `http://127.0.0.1:8000` and Vite at `http://localhost:5173`. See [local development](docs/LOCAL_DEVELOPMENT.md) for the complete workflow.

## Product boundaries

- P2 typed contracts normalize inputs to canonical mm, N, MPa, N·mm, N/mm, N/mm², mm², mm⁴, and rad units.
- P3 provides bounded, benchmarked 2D linear-elastic frame mechanics. Complete code-specific design remains unverified.
- P6 is the source of capability truth. Legacy routes are labeled `LEGACY_UNVERIFIED`; structure mechanics are `ENGINEERING_REVIEW_REQUIRED`.
- P7 reports are server-owned and traceable. Anonymous records are `EPHEMERAL`; authorized project records are `PROJECT_PERSISTED`.
- P9 provides local identity, organizations, projects, and tenant-scoped persistence. It is not production identity.
- P10 provides local QA and security controls. Distributed rate limiting, backups, HTTPS, secret management, and production observability remain open decisions.
- P4 and P5 are `DEFERRED — SOURCE BLOCKED` and excluded from verified release scope.

## Main routes and APIs

UI routes: `/`, `/analyze`, `/structure-designer`, `/sign-in`, and `/projects`.

API entry points include `/health`, `/api/v1/capabilities`, `/api/v1/analysis/element`, `/api/v1/analysis/structure`, `/api/v1/analysis-runs/{id}`, `/api/v1/reports/{id}.pdf`, `/api/v1/auth/*`, and `/api/v1/projects`.

## Testing

```sh
python -m pytest backend/tests -q
node --test frontend/tests/*.test.mjs
npm run build
npm run verify:backend
python scripts/check_repository_hygiene.py
```

## Documentation

- [Local development](docs/LOCAL_DEVELOPMENT.md)
- [API contracts](docs/API_CONTRACTS.md)
- [Canonical units](docs/UNIT_SYSTEM.md)
- [Structural solver](docs/STRUCTURAL_SOLVER.md)
- [Design-code registry](docs/engineering/DESIGN_CODE_REGISTRY.md)
- [Report traceability](docs/engineering/REPORT_TRACEABILITY.md)
- [Enterprise data foundation](docs/engineering/ENTERPRISE_DATA_FOUNDATION.md)
- [Security and reliability](docs/engineering/SECURITY_AND_RELIABILITY.md)
- [Known limitations](docs/engineering/KNOWN_LIMITATIONS.md)
- [Release scope](docs/RELEASE_SCOPE.md)
- [Capability matrix](docs/PRODUCT_CAPABILITY_MATRIX.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [P12 decision inputs](docs/P12_DEPLOYMENT_DECISION_INPUT.md)

## Release status

P0 through P3 and P6 through P10 are pushed. P4 and P5 remain source blocked. P11 is the current product-acceptance and documentation review. P12 deployment decisions have not started; no deployment is configured or performed.
