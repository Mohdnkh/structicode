# Production Topology

## Recommended shape

Use a single-origin application container:

- compiled React assets served by FastAPI;
- one FastAPI ASGI process;
- managed PostgreSQL for project-owned identity, project, run, and report metadata;
- provider-managed HTTPS termination;
- provider secret storage;
- regenerated PDF bytes from stored run records, without durable PDF blobs.

The package intentionally does not select a provider. The topology is a release target, not a deployed environment.

## Constraints

The first release must use exactly one application replica and one Uvicorn worker. Anonymous run storage and rate-limit counters are process-local. Multiple independent processes would make anonymous lookup/report behavior inconsistent and would create independent rate-limit counters. Project-owned runs remain database-persistent, but that does not distribute anonymous state.

Do not enable autoscaling above one replica until distributed run state and rate limiting are implemented and tested. This is an initial release constraint, not a permanent architecture decision.

## Alternatives considered

Split frontend/API hosting would require an exact HTTPS CORS origin, coordinated API URL configuration, and independent release coordination. It adds failure modes without a current product need. A multi-replica service would require distributed state that is not implemented. The single-origin, single-replica shape therefore minimizes operational risk for a future owner-approved release.
