# P6 Design-Code Registry Audit

## Baseline and migration

P6 began from synchronized `main` at `a02ee9aa12fc91136951af96bff7dff153e37bd5` on `codex/p6-design-code-registry`. The previous capability truth was fragmented among `domain/identifiers.py` (`DesignCode` and `LEGACY_CODE_NAMES`), `legacy_capabilities.py` (manual element/structure matrix), `engine/code_router.py` (handler classes), and legacy handler labels/versions. The new `domain/design_code_registry.py` owns metadata and route availability. `DesignCode` remains the stable identifier enum; Python handler classes remain only in the router factory. `legacy_capabilities.py` and its duplicate table were removed. V1 and adapters now use registry accessors.

## Registry entries and capability matrix

The twelve entries are `aci`, `bs`, `eurocode`, `as`, `csa`, `is`, `jordan`, `egypt`, `saudi`, `uae`, `turkey`, and `steel`. Display and jurisdiction metadata are returned by the capability API; they are labels, not approved standard editions. The first ten mixed families have legacy concrete and steel element routes. `is` has the five concrete element routes only. Generic `steel` has steel beam and column routes only. Eleven families have structure-level compatibility, legacy load combinations, and raw seismic placeholders; generic `steel` has none. The exact seven-element matrix and status vocabulary are in [DESIGN_CODE_REGISTRY.md](../engineering/DESIGN_CODE_REGISTRY.md).

Structure mechanics are `ENGINEERING_REVIEW_REQUIRED` for the bounded P3 solver scope. Complete structure design responses, all available element design paths, and all exposed load-factor sets remain `LEGACY_UNVERIFIED`. Raw seismic placeholders are `LEGACY_UNVERIFIED` and unavailable in v1. No current concrete or steel design capability is `VERIFIED`. The P4 ACI CODE-318-25 and P5 ANSI/AISC 360-22 verification targets are `SOURCE_BLOCKED`; both roadmap phases remain deferred.

The ACI, BS, and Eurocode legacy generators have separate existing factor sets. Other structure families use the generic dead-load fallback. These factors were not changed or independently verified in P6. Handler edition strings appear only as `LEGACY_CLAIM` metadata, with no authoritative standard ID or edition populated. National annex, jurisdiction variant, local adoption, and governing edition fields remain unset pending evidence.

## Router and API consistency

The router checks duplicate handler keys, then validates an exact one-to-one family/key match and required handler methods during import. Registry validation rejects duplicate/missing families, unknown element IDs or statuses, empty labels, contradictory route/status claims, and VERIFIED capabilities without evidence. Tests compare declared legacy seismic routes against the actual seismic router and combination profiles against the actual generator. Unknown families do not route.

The read-only endpoints are `GET /api/v1/capabilities` and `GET /api/v1/capabilities/{family_id}`. They use typed Pydantic response models, deterministic family order, and the existing structured v1 404 envelope. They expose no internal class path. V1 analysis continues to return the same transport and verification statuses for supported and unsupported legacy requests.

## Files and verification

Added: `backend/api/domain/design_code_registry.py`, `backend/api/capabilities_api.py`, `backend/tests/test_design_code_registry.py`, `docs/engineering/DESIGN_CODE_REGISTRY.md`, `docs/engineering/DESIGN_CODE_MODULE_ONBOARDING.md`, and this report.

Modified: `backend/api/domain/identifiers.py`, `backend/api/domain/legacy_adapters.py`, `backend/api/engine/code_router.py`, `backend/api/v1.py`, `backend/api/main.py`, and `docs/STRUCTICODE_48H_ENTERPRISE_ROADMAP.md`.

Deleted: `backend/api/legacy_capabilities.py` (independent temporary matrix).

Validation results: 144 P6 registry tests passed, including all seven v1 element requests across all twelve families; 366 complete backend tests passed; P3 solver 41, P4 concrete safety 25, and P5 steel safety 43 passed as targeted regressions. Frontend adapter tests 3 passed, `npm run build` passed with Vite 5.4.21 and 469 transformed modules, and backend import verification passed using the repository virtual environment. Local HTTP smoke checks returned 200 for `/health`, capability list, `aci` detail, and `steel` detail, and a structured 404 for an unknown family. V1 concrete and steel compatibility, IS steel rejection, and generic-steel concrete rejection are covered by P6 and existing API tests. `git diff --check` passed. Transport success remains distinct from engineering verification.

No concrete design equation, steel design equation, load-factor value, seismic equation, section-property value, or P3 structural-solver equation was modified. P7 and deployment work were not started.

## Limitations and later work

The registry is not an engineering verification of the legacy handlers. Evidence-field validation checks completeness and consistency, while independent engineering review must assess source authority and benchmark validity. Some wrappers share simplified formulas while advertising different regions, and the raw API remains a compatibility surface. P8 will need to consume the capability API to correct UI claims, and P7 will need report traceability. P4/P5 source access and independent benchmarks remain prerequisites for any VERIFIED design status. Before product acceptance or release, deferred capabilities must be verified, excluded, or consistently identified as unverified/not implemented.
