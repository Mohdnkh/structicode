# Release Scope

This document freezes the local release candidate against the P6 capability registry. Status terms are registry terms; they are not substitutes for engineering judgment.

## SUPPORTED RELEASE SCOPE

- Typed v1 transport and canonical unit normalization.
- Bounded P3 2D linear-elastic frame mechanics with explicit benchmark limits.
- Read-only P6 capability discovery.
- P7 server-owned traceable analysis records and regenerated reports.
- P8 English/Arabic engineering workspace with explicit capability warnings.
- P9 local identity, organization membership, projects, and tenant-scoped project records.
- P10 local request limits, CORS, security headers, rate limiting, and regression gates.

## LIMITED / ENGINEERING REVIEW REQUIRED

- Structure analysis for registry families with a route: P3 mechanics are bounded and reported as `ENGINEERING_REVIEW_REQUIRED`; complete design, load combinations, and seismic are separate statuses.
- Project persistence and report generation describe storage and traceability only. They do not verify a calculation.

## LEGACY / UNVERIFIED

- Concrete beam, column, slab, footing, and staircase compatibility paths where the registry exposes `LEGACY_UNVERIFIED`.
- Steel beam and column compatibility paths where the registry exposes `LEGACY_UNVERIFIED`.
- Legacy structure design and load-combination handlers.
- Legacy seismic handlers; seismic is not an active v1 workflow.

Legacy output may complete for compatibility, but it does not produce an authoritative SAFE, UNSAFE, PASS, or VERIFIED design conclusion.
Raw compatibility endpoints may retain historical lowercase `safe`/`unsafe` or `Overall_OK` fields for existing clients; those fields are not release trust signals and the primary v1 UI does not promote them.

## NOT IMPLEMENTED

- Registry combinations marked `NOT_IMPLEMENTED`, including IS steel elements and generic-steel structure analysis/design/load/seismic routes.
- Slab load transfer into the P3 frame solver.
- Production identity, billing, SSO, MFA, cloud backups, durable PDF blobs, and multi-instance coordination.

## SOURCE BLOCKED

- ACI verified target `aci_318_25` requires authorized ACI CODE-318-25 SI provisions and independent benchmarks.
- AISC verified target `aisc_360_22` requires the exact provisions and errata, authoritative section properties, and independent beam/column examples.

P4 and P5 remain `DEFERRED — SOURCE BLOCKED`. No source-blocked target is exposed as a verified implementation.
