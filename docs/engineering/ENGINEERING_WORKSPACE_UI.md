# Engineering Workspace UI

## Information architecture

P8 provides three application destinations: Home, Element Analysis, and Structure Workspace. The shared application shell provides navigation, a language control, document language/direction handling, and a skip link. It does not present project, organization, account, billing, or authentication features.

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

Both primary workflows download reports only with `analysis_run_id` through the P7 server-owned report endpoint. The browser helper creates and revokes object URLs. The legacy PDF endpoint remains compatibility-only and is not visible in the P8 workflows. The UI discloses that P7 runs are process-local and are lost after API restart.

## Language, responsive behavior, and accessibility

The shell persists only the language preference. It applies `lang` and `dir` at the document element, including Arabic RTL. CSS uses semantic tokens, regular CSS classes, responsive grids, scrollable engineering tables, semantic labels, keyboard-accessible canvas nodes, visible focus rings, text-bearing status badges, status live regions, disabled controls, and reduced-motion support.

## P9 handoff

P8 keeps model state in the current page session. It adds no identity, ownership, database, project, or durable engineering-record persistence. P9 owns those capabilities.