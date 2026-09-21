# P2 API Contracts and Units Audit

## Scope and branch

- Canonical workspace: `C:\Users\MOHAMMED\Desktop\structicode-main`.
- Integration base: `origin/codex/48h-enterprise-remediation` at `0e52159635d3135a9f97801c2380ef7fe35a5d62`.
- Isolated phase branch: `codex/p2-api-units`, created from that exact remote commit.
- Work is limited to API contracts, unit normalization, frontend transport, contract tests, and documentation. No engineering formula, deployment file, integration branch, or `main` change is part of P2.

## Architecture decisions

1. `backend/api/domain/units.py` is the sole conversion authority for normalized engineering dimensions. It uses a small auditable factor table and rejects non-finite or unsupported conversions.
2. Transport inputs carry their source units in field names. `backend/api/domain/schemas.py` contains strict, typed Pydantic requests and canonical domain models; the latter carry canonical unit suffixes.
3. `backend/api/domain/identifiers.py` defines stable family, element, load-case, and support IDs. A family ID is a legacy routing key, not a verified code edition.
4. `backend/api/domain/legacy_adapters.py` is the temporary mixed-unit boundary. It converts form-display inputs to canonical models, and canonical models to the exact historical engine inputs. It does not repair calculations.
5. `backend/api/v1.py` exposes one versioned element route and one versioned structure route. Responses distinguish software success from engineering verification and keep raw calculation output under `legacy_unverified`.
6. `frontend/src/api/client.js` centralizes API paths, error extraction, and PDF compatibility. `frontend/src/api/adapters.js` deterministically maps existing form and Structure Designer data into explicit v1 request fields. The frontend retains its existing displayed units during P2.

## Canonical unit and schema inventory

Canonical dimensions are length mm, force N, stress/modulus MPa, moment N·mm, line load N/mm, area load/pressure N/mm², section area mm², section modulus mm³, inertia mm⁴, and rotation rad. The required ten conversion identities and round trips are covered by unit tests. See `docs/UNIT_SYSTEM.md` for factors and dimensional reasoning.

The v1 element request is a discriminated union of beam, column, slab, footing, staircase, steel-beam, and steel-column inputs. The structure request has typed materials, sections, nodes, supports, members, member loads, and slabs. Responses have typed envelopes, canonical input/output fields, unverified legacy output, warnings, and structured errors. The schema rejects unknown fields, invalid finite/positive values, duplicate IDs within collections, invalid references, zero-length members, and all-free models. An explicit inertia input is rejected as unsupported because the old solver does not use it.

## Endpoints and compatibility

| Route | Status | Contract |
| --- | --- | --- |
| `GET /health` | Existing | Process health only |
| `POST /api/v1/analysis/element` | New | Typed input, canonical normalization, `UNVERIFIED` legacy output |
| `POST /api/v1/analysis/structure` | New | Typed graph, canonical normalization, `UNVERIFIED` solver/design output |
| `POST /analyze` | Legacy compatibility | Historical generic body and historical trust limitations |
| `POST /api/structure/analyze` | Legacy compatibility | Historical body, with the combination routing shape corrected |
| `POST /generate-pdf` | Legacy compatibility | Historical report generation, still outside P7 trust controls |

The frontend analysis pages now use `/api/v1` through the shared client; Structure Designer no longer sends to the nonexistent `/structure/analyze` path. PDF remains a separate legacy route.

## Legacy adapters and routing defects

- Existing element engines still use historical cm/m/kN inputs, and the direct steel-beam engine expects m although its UI labels span in mm. The v1 boundary accepts `span_mm`, then the adapter supplies m to the direct engine or mm to the alternate SteelCode path. Steel formulas remain unverified.
- The frame solver uses m geometry, kN force, kN/m line load, and stiffness requiring E in kN/m². The old Structure Designer supplied E in MPa without conversion. The P2 adapter explicitly supplies the converted modulus. This can change numerical results compared with the old route; frame equations remain unmodified and unverified.
- The legacy structure router previously called each handler once per single combination, while handlers expected the entire combination mapping. It now passes the complete mapping in one call. A regression test exercises the historical route, and a v1 test checks the same mapping shape.
- The old code router used exact mixed-case keys. It now normalizes all supported family IDs before lookup, including Eurocode and national families. This is a routing correction, not code-edition verification.
- Unsupported seismic analysis, prestressed beams, non-rectangular legacy columns, non-isolated footings, non-straight stairs, and ignored nonzero element load categories receive `NOT_IMPLEMENTED` errors. The staircase width is accepted because the current form supplies it, but the response warns that the legacy engine ignores it.

## Result safety

Successful v1 calculations have `request_status=success` and `verification_status=UNVERIFIED`. `legacy_unverified` contains historical verdicts such as `safe` and `Overall_OK`, without promoting them to a normalized PASS. Validation failures use `NOT_EVALUATED`, and unsupported capabilities use `NOT_IMPLEMENTED`. `VERIFIED` and normalized PASS/FAIL are reserved for future validated modules. The frontend structure labels and warnings identify the output as legacy and unverified. No P2 test asserts engineering correctness.

## Validation evidence

Run commands from the repository root, with `.venv` active for Python-backed npm scripts.

| Check | Result |
| --- | --- |
| `npm ci` | Passed; 132 packages installed; audit reports four advisories |
| `npm run build` | Passed; Vite 5.4.21, 469 modules transformed, output `frontend/dist` |
| `npm run verify:backend` with `.venv` on PATH | Passed |
| `.\.venv\Scripts\python.exe -m pytest backend/tests -q` | Passed; 113 tests after targeted capability rework |
| `node --test frontend/tests/api-adapters.test.mjs` | Passed; 3 tests |
| Live `GET http://127.0.0.1:8000/health` | HTTP 200, `{"status":"ok"}` |
| Live valid `POST /api/v1/analysis/element` | HTTP 200, success/UNVERIFIED, canonical input and `legacy_unverified` |
| Live invalid element width | HTTP 422, error/NOT_EVALUATED, `VALIDATION_ERROR` |
| Live valid `POST /api/v1/analysis/structure` | HTTP 200, success/UNVERIFIED, combinations and `legacy_unverified` |
| Live unsupported family ID | HTTP 422, error/NOT_EVALUATED, `VALIDATION_ERROR` |
| Live unsupported structure family path (`steel`) | HTTP 400, error/NOT_IMPLEMENTED |
| Live finite-input normalization overflow | HTTP 422, error/NOT_EVALUATED, `NORMALIZATION_ERROR` |
| Vite proxy `POST http://localhost:5173/api/v1/analysis/element` | HTTP 200, success/UNVERIFIED |

`npm run verify:backend` initially failed when the shell used the machine-wide Python, which lacks the project's `fpdf` package. Rerunning with the existing `.venv` activated passed; the P1 local development guide already requires this environment. Vite emitted its existing CommonJS Node API deprecation warning. The standalone Node adapter tests emitted a package module-type warning; neither warning failed a check. `frontend/dist` remains ignored and untracked.

`npm audit --json` reported four existing dependency advisories: three moderate (`esbuild`, `react-router`, `react-router-dom`) and one high (`vite`, including a Windows file-deny bypass advisory). npm identifies major-version dependency upgrades as the available fixes. P2 made no package or lockfile change; assess and upgrade these dependencies under a later security/reliability gate, with build and UI regression checks.

## Deferred engineering and product limits

- **P3:** Frame stability, singular matrices, fixed-end/member-force recovery, load combinations, slab distribution, reactions, and numerical verification. P2 only repairs the handler call shape and the explicit E boundary conversion.
- **P4:** Concrete beam, column, slab, footing, and staircase design assumptions and verification. Legacy column moment is not evaluated; footing geometry/soil values are assumed; staircase width is ignored; slab factors and reinforcement mechanics remain unverified.
- **P5:** Steel beam section modulus/capacity consistency, steel column interaction and stability, and verified section properties.
- **P6:** Formal code-edition registry, capabilities, and standard-specific evidence. P2 IDs denote only old families.
- **P7:** Server-side report traceability, report trust, generated filenames, and Unicode output. The legacy PDF route still accepts client-supplied results.
- **P8:** Analyzer form visibility and results usability, Structure Designer support/load editing, and broader UI workflow. The current designer creates free nodes and cannot produce a supported model solely through its current controls.

Legacy `/analyze` and `/api/structure/analyze` retain historical response shapes. They are documented compatibility paths; v1 is the new analysis contract. No structural calculation should be treated as engineering-verified from this phase's transport tests.

## Independent Review Rework — Legacy Capability Routing

Independent review found that valid typed `is` steel-beam/column requests reached an explicit concrete-only refusal but were reported as HTTP 500 `ENGINE_FAILURE`. The AS handler advertised steel paths but lacked imports for its existing steel engine functions, also producing HTTP 500. The pre-correction 12-family × 3-element matrix had four such HTTP 500 cells.

The temporary `backend/api/legacy_capabilities.py` map now gates the existing software paths: ten mixed families have concrete and steel element paths plus structure analysis; `is` has concrete elements and structure analysis but no steel elements; `steel` has steel elements only. This routing inventory is not a design-code edition registry or a verification claim. Unsupported paths return HTTP 400 `NOT_IMPLEMENTED`. The v1 adapter also recognizes explicit legacy unsupported-element results; other calculation errors remain HTTP 500 `ENGINE_FAILURE` with `NOT_EVALUATED`.

`backend/api/codes/as_code.py` gained only the two missing steel function imports. The existing AS steel paths now execute and remain `UNVERIFIED`; no steel equation or coefficient changed. `ISCode` remains concrete-only and was not modified. `steel + structure` remains HTTP 400 `NOT_IMPLEMENTED`.

The parameterized element matrix covers all 12 current family IDs against concrete beam, steel beam, and steel column: **36 requests, 33 HTTP 200/UNVERIFIED and 3 HTTP 400/NOT_IMPLEMENTED; no HTTP 500**. A second 12-family structure matrix confirms 11 HTTP 200/UNVERIFIED paths and one HTTP 400/NOT_IMPLEMENTED steel path. The full backend suite has **113 passing tests**, including the original seven element schemas, explicit AS and IS regressions, steel structure rejection, and checks that a legacy refusal is distinct from a genuine engine error. The optional input-sign review found intentional nonnegative axial-force magnitude fields for concrete columns, footings, and steel columns; P2 does not define a compression/tension sign convention. Structure member line loads and concrete-column moment are finite signed fields.
