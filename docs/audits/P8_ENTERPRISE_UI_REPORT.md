# P8 Enterprise UI Audit

## Scope

P8 rebuilt the prototype frontend into a capability-driven engineering workspace without changing backend calculation behavior. It uses regular CSS tokens and reusable workspace components; Tailwind was not introduced.

## Prototype issues addressed

The prior Home page made universal code-compliance claims. Analyzer had incomplete placeholder UI, hardcoded family choices, active seismic state, and a legacy PDF action. Structure Designer used inactive Tailwind utility classes, hardcoded families, legacy response data as primary mechanics output, a legacy PDF action, and a functional-looking slab control although slab transfer was unavailable.

## Evidence

- The P6 capability endpoint drives family, element, and structure route availability.
- Status badges and capability panels distinguish route availability, engineering review, legacy/unverified state, unimplemented routes, and source-blocked targets.
- The Analyzer includes all seven existing element forms, explicit units, backend validation errors, P7 report download, and an ephemeral-run notice.
- The Structure Workspace uses canonical combinations for result tables, with explicit mm/rad/N/N·mm labels. Legacy design data is separately contained.
- The structure canvas provides node placement, member connection, drawing-state visibility, support selection, and a minimal stable model shortcut. Slab transfer and v1 seismic are visibly unavailable.
- `frontend/tests/workspace-ui.test.mjs` covers P6 interpretation, generic steel and IS restrictions, structure filtering, source-blocked boundaries, report action source checks, and removal of unsupported Home claims.

## Visual QA record

The application was reviewed through the local development stack at desktop (1440 px), laptop/tablet landscape (1024 px), tablet (768 px), and mobile (390 px) widths. The app shell remains navigable; workspace grids stack; engineering tables scroll rather than truncate; canvas controls remain reachable. English review confirmed truthful capability and report controls. Arabic review confirmed the shell sets RTL document direction, navigation remains reachable, form fields align in RTL, and units/technical status tokens remain recognizable.

## Accessibility review

The shell includes a skip link. Form controls use associated labels, controls retain native disabled semantics, status messages use semantic status/alert roles, canvas nodes are keyboard operable, and focus styles remain visible. Status badges carry text and machine tokens instead of color-only meaning. Reduced-motion CSS prevents essential workflow dependence on animation.

## Known limits

P4 and P5 remain source blocked and no verified concrete or steel conclusion is shown. P7 traceable runs remain process-local until P9. No account, project, organization, identity, ownership, or persistence feature exists in P8.
## Final validation

Focused frontend tests passed 7 tests: three existing transport-adapter tests and four P8 capability/report/home-copy tests. `npm run build` passed with Vite 5.4.21 and 1,705 transformed modules. The known Node module-type warning is pre-existing packaging configuration and no P8 code depends on it.

The complete backend suite passed 379 tests. Focused P3, P4, P5, P6, and P7 suites passed 41, 25, 43, 144, and 13 tests. `npm run verify:backend` passed with the documented `.venv` active. `git diff --check` passed before the P8 commit review.

The local browser smoke review confirmed a valid generic-steel legacy analysis, a minimal stable structure analysis, canonical structure result tables, and successful calls to the P7 run-ID report endpoint. At 1440, 1024, 768, and 390 px viewports, document scroll width matched client width. Browser console review found no errors. Arabic review confirmed `lang="ar"`, `dir="rtl"`, translated navigation, usable RTL layout, and un-reversed technical units.
