# Production Operations

- Topology: one same-origin container replica and one Uvicorn worker.
- Database: managed PostgreSQL; SQLite remains the local-development default.
- Migration: run `python -m alembic upgrade head` once as a release step before activation.
- Reports: persistent run and report metadata; PDF bytes regenerated on request; no durable PDF blob archive.
- Anonymous state: process-local and ephemeral; do not scale beyond one replica.
- Rate limiting: process-local; distributed coordination is future work.
- Secrets: provider-managed environment/secret storage only.
- HTTPS: provider TLS termination is mandatory for public traffic.
- Logs: stdout/stderr collection with exception context but no credentials, tokens, or secret values.
- Monitoring: `/health` liveness, `/ready` database readiness, restart/crash visibility, database availability alerts, and application error logs.
- Recovery: pre-migration backup, provider restore-to-new-database drill, integrity smoke tests, and application rollback to an immutable image.

No item above is operationally active until an owner selects a provider and authorizes deployment.
