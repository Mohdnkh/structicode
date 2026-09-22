# CI and QA Gate

The GitHub Actions workflow at `.github/workflows/ci.yml` runs on pushes and pull requests. It is a deterministic local-development quality gate, not a production release pipeline.

It uses Python 3.12 and Node.js 20, installs the pinned development requirements and root npm workspace, checks tracked-artifact hygiene, applies migrations to an isolated SQLite database, imports the backend, runs the backend and frontend tests, builds the frontend, and checks patch whitespace.

Developers can reproduce the checks locally with:

```powershell
python scripts/check_repository_hygiene.py
python -m alembic upgrade head
python -m pytest backend/tests -q
node --test frontend/tests/*.test.mjs
npm run build
git diff --check
```

The workflow does not deploy, modify Railway, or perform production operations.
