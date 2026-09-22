# Design-Code Capability Registry

## Purpose and boundary

`backend/api/domain/design_code_registry.py` is the runtime source of truth for Structicode's **software capability** metadata. A family identifier means that Structicode recognizes a legacy family name; it does not establish compliance with a published standard, a particular edition, a national annex, or professional approval. The registry contains no engineering equations and does not turn a route into a verified design capability.

The twelve stable family identifiers remain `aci`, `bs`, `eurocode`, `as`, `csa`, `is`, `jordan`, `egypt`, `saudi`, `uae`, `turkey`, and `steel`. These are software routing identifiers. A future verified standard identifier must be separate and exact, for example a source-blocked `aci_318_25` target. A legacy handler label such as `ACI 318-19` is stored only as `legacy_claims`; it is not an authoritative edition claim by Structicode.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| `VERIFIED` | A bounded design capability has complete authoritative standard, engine, scope, canonical-contract, and independent benchmark evidence. No current concrete or steel design capability has this status. |
| `ENGINEERING_REVIEW_REQUIRED` | Mechanics have bounded test evidence but the complete engineering response still needs review. Currently used for P3 2D frame analysis mechanics on structure routes. |
| `LEGACY_UNVERIFIED` | A compatibility implementation runs but its engineering rules, factors, or provenance have not been independently verified. |
| `NOT_IMPLEMENTED` | No client-facing capability is implemented for this route/scope. |
| `SOURCE_BLOCKED` | A future verified target cannot proceed until named authoritative sources are inspected. This is a target state, not a claim that its design engine exists. |

Capability status is distinct from a request's transport status (`success`/`error`), a calculation check state (`PASS`/`FAIL`/`NOT_EVALUATED`), and a roadmap phase status (`PUSHED`, `HOLD`, or `DEFERRED — SOURCE BLOCKED`).

## Schema and runtime architecture

Each immutable typed `FamilyCapability` records `family_id`, display name, jurisdiction, legacy label and handler key, material scopes, seven independent element capabilities, structure-analysis mechanics, structure design, load combinations and their legacy profile, seismic behavior, standard metadata confidence, source requirements, warnings, notes, and optional source-blocked verification targets. Each `Capability` records status, v1 route availability, raw legacy route availability, an explanation, and optional verified evidence. The models reject contradictory route/status combinations.

`DesignCode` and `ElementId` remain stable transport identifiers. The former `LEGACY_CODE_NAMES` mapping was removed; adapters and v1 read the registry's `legacy_name`. The temporary capability matrix was removed; v1 uses registry-backed accessors. `code_router.py` retains only its necessary Python class factory table and validates that its keys and handler methods agree with the registry at import time. This keeps class imports outside the registry and avoids circular imports. Unknown families are never silently routed.

For an element, `v1_route: true` means the typed compatibility API can attempt that legacy path; it does not mean verified design. `legacy_route: true` means an existing implementation can be reached through the compatibility layer. Structure analysis and structure design are separate: P3 solver mechanics have bounded benchmark evidence, while the structure response still includes unverified combination factors and legacy design checks. The full structure design result is therefore `LEGACY_UNVERIFIED`.

The load-combination parser's P3 mechanical fixes do not validate each family's factors. ACI, BS, and Eurocode use distinct existing generated sets; all other structure families use the existing generic dead-load fallback. Every exposed factor set remains `LEGACY_UNVERIFIED`. The raw seismic handlers for the eleven non-generic-steel families remain legacy placeholders. V1 seismic remains unavailable (`v1_route: false`); no seismic capability is VERIFIED. The generic `steel` family has no seismic or structure route.

## Current compatibility matrix

`L` means `LEGACY_UNVERIFIED`; `N` means `NOT_IMPLEMENTED`. All listed concrete and steel design routes are unverified. The seven element columns are concrete beam, concrete column, slab, footing, staircase, steel beam, and steel column.

| Family | Beam | Column | Slab | Footing | Stair | Steel beam | Steel column | Structure design | Combinations | Raw seismic |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| aci | L | L | L | L | L | L | L | L | L | L |
| bs | L | L | L | L | L | L | L | L | L | L |
| eurocode | L | L | L | L | L | L | L | L | L | L |
| as | L | L | L | L | L | L | L | L | L | L |
| csa | L | L | L | L | L | L | L | L | L | L |
| is | L | L | L | L | L | N | N | L | L | L |
| jordan | L | L | L | L | L | L | L | L | L | L |
| egypt | L | L | L | L | L | L | L | L | L | L |
| saudi | L | L | L | L | L | L | L | L | L | L |
| uae | L | L | L | L | L | L | L | L | L | L |
| turkey | L | L | L | L | L | L | L | L | L | L |
| steel | N | N | N | N | N | L | L | N | N | N |

Structure **analysis mechanics** are `ENGINEERING_REVIEW_REQUIRED` for the eleven structure families and `NOT_IMPLEMENTED` for generic `steel`. V1 seismic remains unavailable for every family even where a raw placeholder exists.

## Verified invariant and source-blocked targets

A `VERIFIED` capability requires a `VerifiedEvidence` record with exact standard ID and edition, standard title, jurisdiction, material and implemented scope, canonical input/result contracts, engine ID/version, authoritative references, assumptions, applicability limits, independent benchmark IDs, and unsupported scope. Non-verified capabilities cannot carry that evidence. The family must also carry authoritative standard metadata. Validation checks evidence completeness and consistency; independent review must determine whether cited sources are genuinely authoritative and benchmarks are valid. Validation runs when the registry and router are imported, with negative tests for duplicate/missing families, bad statuses, unknown elements, contradictory routes, and missing evidence.

P4's ACI CODE-318-25 concrete target and P5's ANSI/AISC 360-22 steel target are explicitly `SOURCE_BLOCKED`; neither is a verified runtime capability. P4 and P5 remain deferred in the roadmap. Source-blocked status does not authorize guessing a clause or substituting a different edition.

## National annex and jurisdiction metadata

The schema has optional `national_annex`, `jurisdiction_variant`, `local_adoption`, and `governing_edition` fields. All remain unset without evidence. In particular, `eurocode` is a family label, not one universal national factor set; regional wrappers are not independently validated merely because their labels exist. Future verified modules must define the applicable adoption and annex before claiming jurisdiction-specific compliance.

## Read-only API

- `GET /api/v1/capabilities` returns a typed `CapabilityListResponse` containing all twelve families in stable `DesignCode` order. The fixed small list has no pagination, authentication, or write operation in P6.
- `GET /api/v1/capabilities/{family_id}` returns a typed `FamilyCapability`. Family IDs are case-insensitive. Unknown IDs return the existing structured v1 404 error envelope.

The API exposes capability statuses, warnings, route availability, and metadata confidence. It does not expose Python class names or internal import paths. P8 can use it to present truthful availability without relying on frontend hard-coded code lists.

## Known limitations

This registry reflects the inspected routes and known source gaps. It does not validate any legacy equation, factor, section property, seismic output, or standard edition. The raw API still has legacy compatibility behavior and can differ from the typed v1 surface; both are explicitly represented. Detailed client-facing capability presentation belongs to P8, and report traceability belongs to P7. Before P11/P12 acceptance, deferred P4/P5 capabilities must be verified, excluded from release scope, or consistently shown as unverified/not implemented across API, UI, and reports.
