# P11 Product Acceptance Report

## AUTOMATED TEST EVIDENCE

The P11 acceptance tests compare `docs/PRODUCT_CAPABILITY_MATRIX.md` and release-scope markers with the P6 registry and `GET /api/v1/capabilities`. The tests validate every registry family row, per-element aggregate status, source-blocked verification targets, seismic v1 routing, legacy element paths, generic-steel steel-only behavior, and the five release taxonomy labels. The registry remains the source of truth; the test derives its expected row values from the registry instead of maintaining a second capability table.

The focused suite was expanded during the independent-review rework to validate every matrix row and every element-level aggregate. Observed results were: focused P11 checks 5 passed; complete backend suite 417 passed; protected P3/P4/P5/P6/P7 regression 266 passed; P9 enterprise regression 7 passed; P10 security/CI regression 26 passed; frontend tests 14 passed; Vite build passed with 1,711 modules transformed; backend import passed; repository hygiene passed with 181 tracked files inspected; and committed-whitespace plus `git diff --check` passed.

The JavaScript toolchain reported Node.js `v24.11.1` and npm `11.14.1`, using `https://registry.npmjs.org/`, `package-lock=true`, and `omit-lockfile-registry-resolved=false`. The previously reviewed clean-cache `npm ci --no-audit --no-fund --prefer-online --cache <empty-temporary-cache>` completed successfully from the root lockfile; no dependency manifest was changed during this rework.

## INDEPENDENT REVIEW REWORK — ACCEPTANCE EVIDENCE

### Row-level capability validation

`backend/tests/test_p11_product_acceptance.py` now parses each row in `docs/PRODUCT_CAPABILITY_MATRIX.md` and compares it with the corresponding P6 registry record. It checks family ID, display name, jurisdiction, metadata confidence, concrete aggregate status, steel aggregate status, structure analysis/design status, load-combination status, the exact seismic cell derived as either `N/I` or `<status> (v1 false)`, and the source-blocked target. Separate assertions derive each element status from the registry's element records, including the explicit `STATUS_PRESENTATION` mapping used by the product matrix. This closes the previous broad phrase-only coverage gap.

### Documentation consistency

The same focused suite scans current-facing documentation for the stale release statements identified by review, including the old claims that Structure Workspace lacked editing controls, that the primary report path was legacy, that reports used a shared file, that P9 owned identity capabilities, and that P10 still needed review. The README now uses the verified PowerShell activation path `.\\.venv\\Scripts\\Activate.ps1` and the local-development guide no longer repeats the runtime requirements install already included by `requirements-dev.txt`.

### Clean Python environment

Using Python 3.12, a temporary virtual environment outside the repository was created with `py -3.12 -m venv <temporary-path>`. It ran `python -m pip install --upgrade pip`, `python -m pip install -r backend/requirements-dev.txt`, and `python -m pip check`; the result was `No broken requirements found.` The temporary environment was removed after the check. This is dependency evidence from a clean environment, separate from the repository's existing `.venv`.

### Report traceability correction

`docs/engineering/REPORT_TRACEABILITY.md` now documents the actual legacy `/generate-pdf` behavior: a server-generated unique temporary filename, `FileResponse`, and deterministic background cleanup. It does not create or reuse `report.pdf`. The route remains client-supplied, legacy, and unverified; `/api/v1/reports/{run_id}.pdf` remains the primary traceable report path.

## ACTUAL BROWSER OBSERVATION

The local FastAPI and Vite stack was started with an isolated SQLite database and a dedicated local auth secret. Actual browser navigation used the visible application links for Element Analysis (rather than relying on a direct route load) and then inspected rendered DOM state. The tested responsive viewports were exactly 1440x900, 1024x800, 768x900, and 390x844.

At each viewport, Home rendered capability-boundary copy; Element Analysis rendered its selectors and capability-backed workflow; Structure Workspace rendered the SVG model editor; Sign in rendered labeled controls; and unauthenticated Projects redirected to Sign in. `document.documentElement.scrollWidth` did not exceed the client width at any tested viewport. The 390px viewport reported a 375px layout client width and 375px scroll width, with no horizontal overflow.

## SOURCE/CSS REVIEW

Responsive CSS, keyboard focus, skip navigation, form labels, disabled semantics, live status text, and the simplified mobile SVG editor were reviewed separately from the DOM observations above. This review is not a WCAG certification. The browser observations are actual local acceptance evidence; source/CSS review is a separate evidence type.

## ENGLISH ACCEPTANCE

At 1440x900 and 390x844, English Home, Element Analysis, Structure Workspace, Sign in, and Projects flows rendered with `lang="en"` and `dir="ltr"`. Element Analysis exposed two selectors and no horizontal overflow. Structure Workspace rendered ten SVG/canvas elements and no horizontal overflow. Sign in rendered one form. Projects redirected to `/sign-in` without overflow.

## ARABIC / RTL ACCEPTANCE

At 1440x900 and 390x844, the same flows were exercised after using the visible language switch. Home, Element Analysis, Structure Workspace, Sign in, and the Projects redirect rendered with `lang="ar"` and `dir="rtl"`, Arabic navigation/content, and no horizontal overflow. Element Analysis exposed two selectors; Structure Workspace rendered ten SVG/canvas elements; Sign in rendered one form.

## PRIOR PRODUCT WORKFLOW EVIDENCE

Home rendered skip navigation and capability-boundary copy. Element Analysis rendered all seven form choices, disabled unsupported generic-steel concrete routes, displayed `LEGACY_UNVERIFIED`, showed canonical units, completed an ACI beam run, returned run ID `5462fb43-df32-42a1-9a32-0fc0332cb7d6`, and downloaded a traceable PDF. A generic-steel steel-beam run returned run ID `e6035559-2f34-4356-9f7b-29387bd3f6a4` with the same unverified boundary. The acceptance record distinguishes transport success from engineering verification.

Representative legacy concrete and steel runs retained `UNVERIFIED` semantics, exposed capability context, showed canonical input units, returned a server-generated run ID, and used the traceable report action. Structure analysis rendered canonical combination mechanics with separate analysis/design/load/seismic capability states; slab transfer was rejected as not implemented. Invalid, incomplete, and unstable models surfaced structured validation or solver errors without a raw traceback in the user response.

Anonymous runs displayed `EPHEMERAL` and were process-local. Authenticated project runs displayed `PROJECT_PERSISTED`, remained retrievable after the in-memory store was cleared, and generated protected traceable PDFs. A second tenant could not view, update, list, retrieve, or report on the first tenant's project records. The compatibility `/generate-pdf` route remained labeled legacy/client-supplied/unverified and was not the primary UI action.

## DOCUMENTATION REVIEW

The root README, local-development guide, API and unit contracts, structural solver, analysis-run schema, report traceability, design-code registry, engineering workspace, enterprise data, security/reliability, known limitations, P0-P10 audits, release scope, capability matrix, architecture, release checklist, blocker register, and P12 decision input were reconciled with the merged P10 implementation.

P8's pre-P9 statements about no identity and process-local-only runs were corrected. P9's handoff records the P10 review of CORS, limits, auth secret handling, rate limiting, tenant isolation, fail-closed persistence, and CI. CI documentation preserves the actual merge-base behavior and does not claim a silent fallback when a merge-base cannot be resolved.

## KNOWN LIMITATIONS

- P4 and P5 remain `DEFERRED — SOURCE BLOCKED`; no concrete or steel design capability is `VERIFIED`.
- Raw compatibility calculation routes retain historical `safe`/`unsafe` or `Overall_OK` fields in their legacy payloads. They are outside the primary v1 UI, remain explicitly unverified, and are not used as authoritative release conclusions.
- Seismic is not an active verified v1 workflow and slab transfer is not implemented.
- SQLite, process-local rate limiting, local JWT identity, regenerated PDFs, missing production backups, missing production HTTPS/secret manager/observability, and dependency advisories remain release risks.
- Manual browser observations are local acceptance evidence, not hosted production evidence. Hosted CI must be observed on the exact rework commit.

## P12 RELEASE DECISION INPUT

P12 must decide hosting, database, durable report/blob storage, secrets, TLS, backups, migrations, logs/metrics, distributed rate limiting, multi-instance behavior, rollback, costs, and operational ownership. P11 does not choose a provider or deploy anything.
