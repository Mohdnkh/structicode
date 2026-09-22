# Engineering Workspace UI

## Information architecture

The application shell provides Home, Element Analysis, Structure Workspace, Sign In, and Projects destinations. It provides navigation, language and direction handling, a skip link, and explicit project/authentication boundaries. Billing and production identity are not implemented.

## Capability-driven controls

The frontend loads `GET /api/v1/capabilities` when an engineering workspace opens. Family and element controls use the returned stable IDs and capability records. An unavailable route remains disabled and visibly names its `NOT_IMPLEMENTED` state. The frontend does not maintain a code-family capability matrix. A request cannot be made until a selected route has a v1 capability.

## Verification presentation

Capability badges always include text and machine status. The workspace distinguishes `ENGINEERING_REVIEW_REQUIRED`, `LEGACY_UNVERIFIED`, `NOT_IMPLEMENTED`, and `SOURCE_BLOCKED`. Source-blocked ACI/AISC targets appear only as future verification targets. They are never described as current standards used by a result.

## Element workflow

The element flow is family selection, element selection, capability review, contract-unit input, v1 analysis, result review, and traceable report download. All seven existing forms remain available where the registry exposes the associated route. The result view presents server response status, family, element, run ID, warnings, canonical input, and a separately contained legacy/unverified output. Seismic controls are excluded because v1 seismic analysis is unavailable.

## Structure workflow

The workspace supports a bounded 2D frame model: canvas node creation, member connection, visible drawing state, support editing, model inventory, and an optional minimal stable example. The UI provides only local completeness checks. The backend remains authoritative for validation and solver/stability behavior. Slab transfer is visibly unavailable because P3 structure analysis does not implement it.

Canonical `response.combinations` results are primary. Displacements use mm/rad, reactions use N/N·mm, and member forces use N/N·mm/mm. Legacy structure-design output remains separate and unverified. Structure mechanics, complete design, load combinations, and seismic are shown as separate capability states.

## P7 reports

Both primary workflows download reports only with `analysis_run_id` through the P7 server-owned report endpoint. Anonymous runs are `EPHEMERAL`, process-local, and lost after API restart. Runs submitted with an authorized project are `PROJECT_PERSISTED`, tenant-scoped, and retrievable after restart. PDFs are regenerated from the stored run; PDF bytes are not durable blobs. The legacy PDF endpoint remains compatibility-only and is not visible in the primary workflows.

## Language, responsive behavior, and accessibility

The shell persists only the language preference. It applies `lang` and `dir` at the document element, including Arabic RTL. CSS uses semantic tokens, regular CSS classes, responsive grids, scrollable engineering tables, semantic labels, keyboard-accessible canvas nodes, visible focus rings, text-bearing status badges, status live regions, disabled controls, and reduced-motion support.

## P9 and P10 integration

The UI keeps unsaved model state in the current page session, while P9 supplies local identity, organization membership, project selection, and project-owned run persistence. Project and report requests are authorized by current database membership, not by a client-selected role. P10 adds request limits, CORS, rate limiting, security headers, fail-closed persistence behavior, and regression gates. These controls do not promote any calculation to VERIFIED.
## P8 independent-review rework

The Structure Workspace now renders a dedicated capability summary from the P6 family record. It consumes `family.structure_analysis`, `family.structure_design`, `family.load_combination`, and `family.seismic` directly; it does not infer those states from a code-family name or a frontend matrix.

Analyzer and Structure Workspace use the existing `react-i18next` catalog for their primary engineering copy. All seven element forms and the P7 traceable-report action are localized in English and Arabic. Technical IDs, machine-status tokens, numeric values, and unit notation remain isolated for left-to-right reading when Arabic RTL is active.

A report download failure is independent from analysis success in both workflows. The successful run and its results stay visible while a nearby retryable error panel reports the failed download.
