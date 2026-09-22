# Backup and Restore Runbook

1. Require managed PostgreSQL automated backups and a documented retention target before deployment.
2. Take a pre-migration snapshot or logical dump before every schema-changing release.
3. Restore into a new isolated PostgreSQL instance using the selected provider's documented restore process.
4. Rotate credentials after a restore when the provider or incident procedure requires it.
5. Run integrity smoke checks: migration head, user login, project ownership, run retrieval, report generation, version conflict, and cross-tenant denial.
6. Compare the restored tenant/project/run/report records with the incident acceptance window.
7. Switch the application connection only after validation and record the restore identifier.

No cloud backup or restore was performed in P12. A backup that has never been restored is not evidence of recoverability.
