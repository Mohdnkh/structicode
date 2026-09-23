# Provider Comparison

Accessed 2026-09-23. Only current official provider documentation was used. No provider account, project, database, domain, secret, or deployment was created.

| Capability | Railway | Render | Fly.io |
| --- | --- | --- | --- |
| Container deployment | Dockerfile-based deployments are supported. | Docker services and multi-stage Docker builds are supported. | Docker images and Machines are supported. |
| PostgreSQL offering / operational model | Railway PostgreSQL templates are platform-provisioned but documented as unmanaged; backup/PITR capabilities require explicit configuration. Railway can still host the application with an external approved managed database. | Render Postgres is a fully managed PostgreSQL service. | Fly.io Managed Postgres (MPG) is a fully managed PostgreSQL service with HA, backups/recovery, monitoring, and scaling documented by Fly. Unmanaged Fly Postgres remains a separate legacy product. |
| Backups / recovery | Railway documents volume backups, PITR, logical dumps, and restore drills. | Render documents PITR and logical exports with plan-dependent recovery windows. | Fly documents managed Postgres backups and snapshot restore workflows. |
| Secrets | Railway variables and sealed variables. | Provider environment variables and secret files are documented for Docker services. | Fly encrypted application secrets are documented. |
| HTTPS / custom domain | Railway healthcheck and public service flow support HTTPS; exact domain setup remains owner work. | Render documents custom domains and managed TLS for services. | Fly service configuration and certificates require provider configuration. |
| Health checks | Configurable healthcheck path; checked before activation, not continuous monitoring. | Health checks participate in deploy readiness. | Service-level checks can gate routing and deployment. |
| One-replica control | Replica scaling exists and must be explicitly held at one. | Instance count can be held at one. | Machine count and deployment strategy are configurable. |
| Migration / release command | Railway Pre-Deploy Command can run migrations before deployment; project wiring is not configured. | Render `preDeployCommand` runs after build and before start; project wiring is not configured. | MPG/application release commands are configurable; project wiring is not configured. |
| Logs / monitoring | Provider logs and healthcheck visibility are available; continuous health monitoring needs explicit setup. | Provider logs, health checks, and monitoring features are documented. | Health checks and logs are documented; alerting configuration remains owner work. |
| Persistent disk | Not required for the recommended PostgreSQL/report design. | Not required for the recommended PostgreSQL/report design. | Volumes are available but should not be used for application state in this package. |
| Pricing | Current plan and usage pricing must be checked by the owner. | Current plan and usage pricing must be checked by the owner. | Current plan and usage pricing must be checked by the owner. |
| Operational complexity | Lower initial setup, but backup and monitoring policy still require explicit configuration. | Clear managed database and service separation, with plan-dependent recovery. | More infrastructure control and more operational responsibility. |

## Official sources

### Railway

- [Deployments reference](https://docs.railway.com/deployments/reference) — Dockerfile builds and healthcheck activation behavior.
- [PostgreSQL](https://docs.railway.com/databases/postgresql) — Railway PostgreSQL template and its unmanaged operational model.
- [Pre-Deploy Command](https://docs.railway.com/deployments/pre-deploy-command) — migration command lifecycle and failure behavior.
- [Using Variables](https://docs.railway.com/variables) — environment variables and sealed variables.
- [Healthchecks](https://docs.railway.com/deployments/healthchecks) — healthcheck path and `PORT` behavior.
- [Back Up and Restore Postgres](https://docs.railway.com/guides/postgres-backups-restores) — volume, PITR, and logical backup workflows.

### Render

- [Docker](https://render.com/docs/docker) — Docker services and multi-stage builds.
- [Render Postgres](https://render.com/docs/postgresql) — fully managed PostgreSQL capabilities.
- [Postgres Recovery and Backups](https://render.com/docs/postgresql-backups) — PITR and logical backup behavior.
- [Deploying on Render](https://render.com/docs/deploys) — build, pre-deploy, start, and deployment lifecycle commands.
- [Environment variables](https://render.com/docs/environment-variables) — runtime environment handling.

### Fly.io

- [Managed Postgres](https://fly.io/docs/mpg/) — fully managed service, HA, backups, recovery, and scaling.
- [Managed Postgres metrics](https://fly.io/docs/mpg/metrics/) — monitoring and metrics.
- [Health checks](https://fly.io/docs/reference/health-checks/) — service and machine health checks.
- [Secrets and Fly Apps](https://fly.io/docs/apps/secrets/) — encrypted runtime secrets.
- [Backup and restore](https://fly.io/docs/postgres/managing/backup-and-restore/) — retained only for the explicitly unmanaged legacy Fly Postgres product.
- [App configuration](https://fly.io/docs/reference/configuration/) — deployment strategy and health-check configuration.

No exact prices are recorded because pricing depends on region, plan, storage, traffic, and current provider billing terms.
