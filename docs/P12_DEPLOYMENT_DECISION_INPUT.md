# P12 Deployment Decision Input

P12 must make the deployment decision; no provider is selected here.

Decide the frontend hosting model and API hosting model, database engine and managed-service topology, persistent report/PDF blob strategy, secret manager, TLS/HTTPS termination, backup and restore policy, migration and rollback process, logs and metrics, distributed rate limiting, multi-instance/session behavior, operational ownership, expected traffic, cost ceiling, and support model.

The decision must also account for the explicit release boundary: P4/P5 are source blocked, legacy calculations are unverified, anonymous runs are ephemeral, project records are local SQLite in the current candidate, and generated PDFs are not durable blobs. A deployment is not authorized by P11.
