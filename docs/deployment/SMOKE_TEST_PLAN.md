# Production Smoke Test Plan

Run only after explicit deployment approval. Transport success must remain separate from engineering verification.

- `GET /health` returns the minimal liveness response.
- `GET /ready` returns ready with a live database and 503 without leaking dependency details when unavailable.
- Home serves compiled frontend assets; `/analyze`, `/structure-designer`, `/sign-in`, and `/projects` fall back through FastAPI.
- `/api/v1/capabilities` exposes registry truth and no verified P4/P5 capability.
- Anonymous element analysis and its traceable report work during one process lifetime.
- Registration, login, project creation, and project-persisted element analysis work.
- Project run retrieval and protected report generation work after in-memory state is cleared.
- Project-persisted structure analysis works within the supported bounded route.
- A second tenant receives denial for the first tenant's project, run, and report.
- Project optimistic version conflict returns the structured conflict response.
- Arabic/RTL Home, Analyzer, Structure Workspace, Sign in, and responsive layouts render without overflow.
- Restart persistence is verified for project-owned records; anonymous restart loss is documented and expected.

No smoke test was run against a deployed environment in P12.
