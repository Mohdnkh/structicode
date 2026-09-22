# P5 Source-Blocked Decision

## Decision

P5 verified steel core remains **DEFERRED — SOURCE BLOCKED** after the legacy safety containment is reviewed and merged. The P5 exit gate is unmet: there is no single unit-consistent, authoritative, benchmarked steel beam/column engine, and no steel capability is VERIFIED. The source-access audit documents the missing evidence; the safety remediation documents the contained compatibility outputs.

This is a deferral of verified engineering scope, not approval of the existing formulas. Known legacy `safe`/`unsafe` comparisons are retained only as explicitly named `legacy_status` beneath an `UNVERIFIED` / `NOT_EVALUATED` trust boundary. The known beam dimensional defect and section-data provenance gap remain unresolved engineering work.

## Later-phase eligibility

P6 stays **HOLD** in this task. After independent review and merge of the safety recovery PR, P6 may begin because design-code registry architecture can be built without implementing or relying on the missing AISC rules. P6 must not register legacy steel as verified. P4 separately remains **DEFERRED — SOURCE BLOCKED** for missing authorized ACI CODE-318-25 access.

## Release gate

Before P11/P12 completion, P5 must be completed and verified with authoritative evidence, intentionally excluded from the release scope, or consistently represented as `UNVERIFIED` / `NOT IMPLEMENTED` across API, UI, and reports. Product acceptance and deployment must not count this deferred core as complete. No deployment is authorized by this decision.

## Exact restart evidence

Verified P5 can resume only after access to the applicable ANSI/AISC 360-22 provisions and scope limits, applicable AISC 360-22 errata text checked against the source printing, authoritative section properties such as AISC Shapes Database v16.0 with property definitions and units, and published/reference examples adequate for independent beam and column benchmarks. The source set must be inspected before clause/equation mappings or VERIFIED outcomes are created.
