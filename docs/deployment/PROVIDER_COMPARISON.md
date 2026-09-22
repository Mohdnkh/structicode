# Provider Comparison

Accessed 2026-09-22. Only current official provider documentation was used. No provider account, project, database, domain, secret, or deployment was created.

| Capability | Railway | Render | Fly.io |
| --- | --- | --- | --- |
| Container deployment | Dockerfile-based deployments are supported. | Docker services and multi-stage Docker builds are supported. | Docker images and Machines are supported. |
| Managed PostgreSQL | Railway PostgreSQL service is documented. | Render Postgres is documented as managed PostgreSQL. | Fly Managed Postgres is documented; volumes and managed service choices differ. |
| Backups / recovery | Railway documents volume backups, PITR, logical dumps, and restore drills. | Render documents PITR and logical exports with plan-dependent recovery windows. | Fly documents managed Postgres backups and snapshot restore workflows. |
| Secrets | Railway variables and sealed variables. | Provider environment variables and secret files are documented for Docker services. | Fly encrypted application secrets are documented. |
| HTTPS / custom domain | Railway healthcheck and public service flow support HTTPS; exact domain setup remains owner work. | Render documents custom domains and managed TLS for services. | Fly service configuration and certificates require provider configuration. |
| Health checks | Configurable healthcheck path; checked before activation, not continuous monitoring. | Health checks participate in deploy readiness. | Service-level checks can gate routing and deployment. |
| One-replica control | Replica scaling exists and must be explicitly held at one. | Instance count can be held at one. | Machine count and deployment strategy are configurable. |
| Migration / release command | Docker command and deployment lifecycle support a separate migration step, but exact project configuration remains to be created. | Docker `CMD` plus release workflow can run a separate migration step. | Machine release configuration supports explicit commands, but operational wiring remains owner work. |
| Logs / monitoring | Provider logs and healthcheck visibility are available; continuous health monitoring needs explicit setup. | Provider logs, health checks, and monitoring features are documented. | Health checks and logs are documented; alerting configuration remains owner work. |
| Persistent disk | Not required for the recommended PostgreSQL/report design. | Not required for the recommended PostgreSQL/report design. | Volumes are available but should not be used for application state in this package. |
| Pricing | Current plan and usage pricing must be checked by the owner. | Current plan and usage pricing must be checked by the owner. | Current plan and usage pricing must be checked by the owner. |
| Operational complexity | Lower initial setup, but backup and monitoring policy still require explicit configuration. | Clear managed database and service separation, with plan-dependent recovery. | More infrastructure control and more operational responsibility. |

## Official sources

### Railway

- [Deployments reference](https://docs.railway.com/deployments/reference) — Dockerfile builds and healthcheck activation behavior.
- [PostgreSQL](https://docs.railway.com/databases/postgresql) — PostgreSQL service, backups, and observability guidance.
- [Using Variables](https://docs.railway.com/variables) — environment variables and sealed variables.
- [Healthchecks](https://docs.railway.com/deployments/healthchecks) — healthcheck path and `PORT` behavior.
- [Back Up and Restore Postgres](https://docs.railway.com/guides/postgres-backups-restores) — volume, PITR, and logical backup workflows.

### Render

- [Docker](https://render.com/docs/docker) — Docker services and multi-stage builds.
- [Render Postgres](https://render.com/docs/postgresql) — managed PostgreSQL capabilities.
- [Postgres Recovery and Backups](https://render.com/docs/postgresql-backups) — PITR and logical backup behavior.
- [Troubleshooting deploys](https://render.com/docs/troubleshooting-deploys) — Docker command, `PORT`, and health checks.
- [Environment variables](https://render.com/docs/environment-variables) — runtime environment handling.

### Fly.io

- [Databases and storage](https://fly.io/docs/database-storage-guides/) — Managed Postgres and storage choices.
- [Health checks](https://fly.io/docs/reference/health-checks/) — service and machine health checks.
- [Secrets and Fly Apps](https://fly.io/docs/apps/secrets/) — encrypted runtime secrets.
- [Backup and restore](https://fly.io/docs/postgres/managing/backup-and-restore/) — PostgreSQL snapshot restore.
- [App configuration](https://fly.io/docs/reference/configuration/) — deployment strategy and health-check configuration.

No exact prices are recorded because pricing depends on region, plan, storage, traffic, and current provider billing terms.
