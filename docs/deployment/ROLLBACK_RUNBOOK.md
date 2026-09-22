# Rollback Runbook

## Application-only rollback

Deploy the previous immutable image identified in the release record. Keep the database unchanged when the schema is compatible. Verify `/health`, `/ready`, capabilities, authentication, project retrieval, and report generation.

## Schema-changing rollback

The current release has one initial migration, `20260922_p9_initial`, whose downgrade drops the P9 tables. Do not run that downgrade against production without a verified pre-migration backup and explicit owner approval. Prefer restoring a pre-migration PostgreSQL backup to a new database, validating it, and switching the application connection string.

## Verification and incident decisions

Stop traffic when readiness fails, tenant isolation fails, reports lose traceability, or a source-blocked capability is promoted. Record the failed release SHA, database migration head, provider events, and restore verification before reopening traffic. Production rollback was not executed in P12.
