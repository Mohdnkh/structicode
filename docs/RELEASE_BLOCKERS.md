# Release Blockers and Risks

## MUST RESOLVE BEFORE PUBLIC PRODUCTION DEPLOYMENT

- Select and harden a production database, backups, migrations, restore testing, and rollback.
- Provide HTTPS, production secret management, observability, and distributed rate limiting.
- Decide durable report/blob storage and multi-instance run/report behavior.
- Resolve or explicitly accept Python and npm dependency advisories through P12 go/no-go review.
- Keep P4 concrete and P5 steel outside verified scope until their authoritative source gates are satisfied.

## ACCEPTABLE FOR LOCAL RELEASE CANDIDATE

- SQLite local persistence with isolated migration testing.
- Process-local rate limiting and local JWT identity for development.
- Regenerated in-memory/response PDF bytes with traceable server-owned run IDs.
- Engineering-review and legacy-unverified statuses where the registry exposes them.

## DEFERRED ENGINEERING VERIFICATION

- ACI CODE-318-25 concrete verification (`aci_318_25`) is source blocked.
- ANSI/AISC 360-22 steel verification (`aisc_360_22`) is source blocked.
- Seismic design remains legacy/unverified or not implemented according to the P6 registry.
- Slab transfer into P3 frame analysis is not implemented.

These classifications do not turn a local candidate into a production release approval.
