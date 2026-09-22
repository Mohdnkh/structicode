# P11 Product Acceptance Report

## AUTOMATED TEST EVIDENCE

The P11 acceptance test compares `docs/PRODUCT_CAPABILITY_MATRIX.md` and release-scope markers with the P6 registry and `GET /api/v1/capabilities`. It checks all twelve family IDs, metadata confidence, structure status fields, seismic v1 routing, ACI and AISC source-blocked targets, ACI legacy element paths, IS steel unavailability, generic-steel steel-only behavior, and the five release taxonomy labels.

Observed results on this branch: P11 acceptance checks 4 passed; complete backend suite 416 passed; protected P3/P4/P5/P6/P7 regression command 266 passed; P9 enterprise suite 7 passed; P10 security/CI suite 26 passed; frontend tests 14 passed; Vite build passed with 1,711 modules transformed; backend import passed; repository hygiene passed with 172 tracked files inspected; committed-whitespace check passed for `main...HEAD`. The acceptance test does not duplicate the registry; the registry remains the source of truth.

## MANUAL / BROWSER ACCEPTANCE

Manual acceptance was performed against the local FastAPI and Vite stack using an isolated SQLite database and dedicated local auth secret. Home rendered with skip navigation and capability-boundary copy. Element Analysis rendered all seven form choices, disabled unsupported generic-steel concrete routes, displayed `LEGACY_UNVERIFIED`, showed canonical units, completed an ACI beam run, returned run ID `5462fb43-df32-42a1-9a32-0fc0332cb7d6`, and downloaded a traceable PDF. A generic-steel steel-beam run returned run ID `e6035559-2f34-4356-9f7b-29387bd3f6a4` with the same unverified boundary. The acceptance record distinguishes transport success from engineering verification.

Representative legacy concrete and steel runs retained `UNVERIFIED` semantics, exposed capability context, showed canonical input units, returned a server-generated run ID, and used the traceable report action. Structure analysis rendered canonical combination mechanics with separate analysis/design/load/seismic capability states; slab transfer was rejected as not implemented. Invalid, incomplete, and unstable models surfaced structured validation or solver errors without a raw traceback in the user response.

Anonymous runs displayed `EPHEMERAL` and were process-local. Authenticated project runs displayed `PROJECT_PERSISTED`, remained retrievable after the in-memory store was cleared, and generated protected traceable PDFs. A second tenant could not view, update, list, retrieve, or report on the first tenant's project records. The compatibility `/generate-pdf` route remained labeled legacy/client-supplied/unverified and was not the primary UI action.

The local browser session observed the primary workflow at the default desktop viewport and reviewed responsive CSS/source behavior for approximately 1440px, 1024px, 768px, and 390px breakpoints. Navigation, labels, disabled controls, status text, engineering tables, and report actions remained usable; the SVG model editor is intentionally simplified on mobile. Keyboard focus, skip navigation, form labels, disabled semantics, live status text, and Arabic RTL direction were reviewed. This is not a WCAG certification.

## DOCUMENTATION REVIEW

The root README, local-development guide, API and unit contracts, structural solver, analysis-run schema, report traceability, design-code registry, engineering workspace, enterprise data, security/reliability, known limitations, P0-P10 audits, release scope, capability matrix, architecture, release checklist, blocker register, and P12 decision input were reconciled with the merged P10 implementation.

P8's pre-P9 statements about no identity and process-local-only runs were corrected. P9's handoff now records the P10 review of CORS, limits, auth secret handling, rate limiting, tenant isolation, fail-closed persistence, and CI. CI documentation preserves the actual merge-base behavior and does not claim a silent fallback when a merge-base cannot be resolved.

## KNOWN LIMITATIONS

- P4 and P5 remain `DEFERRED — SOURCE BLOCKED`; no concrete or steel design capability is `VERIFIED`.
- Raw compatibility calculation routes retain historical `safe`/`unsafe` or `Overall_OK` fields in their legacy payloads. They are outside the primary v1 UI, remain explicitly unverified, and are not used as authoritative release conclusions.
- Seismic is not an active verified v1 workflow and slab transfer is not implemented.
- SQLite, process-local rate limiting, local JWT identity, regenerated PDFs, missing production backups, missing production HTTPS/secret manager/observability, and dependency advisories remain release risks.
- Manual browser observations are local acceptance evidence, not hosted production evidence. Hosted CI is reported separately and must be observed on the exact P11 commit.

## P12 RELEASE DECISION INPUT

P12 must decide hosting, database, durable report/blob storage, secrets, TLS, backups, migrations, logs/metrics, distributed rate limiting, multi-instance behavior, rollback, costs, and operational ownership. P11 does not choose a provider or deploy anything.
