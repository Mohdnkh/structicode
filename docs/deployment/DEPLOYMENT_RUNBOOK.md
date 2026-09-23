# Deployment Runbook

This runbook is procedural only. It was not executed in P12.

1. Verify the approved P12 commit, green hosted CI, and the `NO-GO`/`GO` decision.
2. Obtain explicit owner approval immediately before any provider action.
3. Select the provider, region, cost ceiling, and operational owner.
4. Create the provider service and managed PostgreSQL instance.
5. Configure provider backups, retention, and restore policy.
6. Configure production secrets and environment variables from `PRODUCTION_ENVIRONMENT.md`.
7. Configure the exact HTTPS domain and provider TLS termination.
8. Configure the provider's migration lifecycle (Railway [Pre-Deploy Command](https://docs.railway.com/deployments/pre-deploy-command), Render [`preDeployCommand`](https://render.com/docs/deploys), or an explicitly reviewed Fly release command), then run `python -m alembic upgrade head` once against the release database. No provider wiring is configured by P12.
9. Build and deploy the immutable container artifact with one replica and one worker.
10. Verify `/health`, `/ready`, `/`, `/api/v1/capabilities`, and the smoke plan.
11. Verify project persistence, protected reports, tenant isolation, and Arabic/RTL behavior.
12. Record the release commit, migration head, provider deployment identifier, and monitoring links.
13. Stop or roll back if readiness, persistence, tenant isolation, report trust, or capability boundaries fail.

The owner-approval checkpoint precedes all irreversible or provider-side actions.
