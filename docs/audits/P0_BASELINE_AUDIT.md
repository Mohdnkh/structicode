# P0 Baseline Audit

## Scope and evidence

Repository: Mohdnkh/structicode. Baseline commit: b3801df62fdf1ba0ce61515e1ec5c29d28cacc32. Working branch: codex/48h-enterprise-remediation. Paths below are repository-relative with one-based line numbers. Dynamic probes used in-memory inputs and Python with bytecode writing disabled. P0 did not alter calculations or install dependencies.

No design module has repository evidence sufficient to call it VERIFIED: there are no first-party benchmark tests or traceable code-clause references. Several incomplete paths nevertheless emit safe, unsafe, or Overall_OK. The capability inventory below records those paths for later phases.

## Reproduced cases

| Severity | Input or action | Observed behavior | Source |
| --- | --- | --- | --- |
| Critical | Steel I beam: fy=250 MPa, span=5 m, w=100 kN/m, h=300 mm, b=200 mm, tf=10 mm, tw=6 mm, simply supported. | Mp=145000 kN m, Mu=312.5 kN m, status=safe. Current flange-only expression produces 58000 cm3; dimensional conversion of its 580000 mm3 term is 580 cm3. Its two conversion errors inflate that term's moment capacity by 1000 times. | Dynamic and dimensional; backend/api/engine/steel/steel_beam.py:34-51. |
| Critical | ACI structure-level check: Mmax=10000 kN m, Vmax=0, Nmax=0, bw=0.3 m, h=0.6 m, cover=0.04 m, fc=25 MPa, fy=420 MPa. | As_required=48990.79, fabricated As_provided=58788.95, Overall_OK=True. | Dynamic; backend/api/codes/aci.py:115-133. |
| Critical | Rectangular column: 30 by 30 cm, four 16 mm bars, fc=25 MPa, fy=420 MPa, axial=100 kN; compare moment=0 with moment=10000 kN m. | Both return Pn=22.33 kN and identical status. Supplied moment has no effect. | Dynamic; backend/api/engine/concrete/column.py:37-57. |
| High | Supported two-node ACI structure request with one member. | HTTP 500: string indices must be integers, not 'str'. | Dynamic; backend/api/engine/structure_router.py:87-90. |
| High | Same structure request using Eurocode. | HTTP 500 wrapping 400: Unsupported code: EUROCODE. | Dynamic; backend/api/engine/structure_router.py:73-99 and code_router.py:14-29. |
| High | 1.4D combination, 4 m supported member, D=10 kN/m; then add L=20 kN/m without changing the combination. | Reported Mmax changes from 18.6667 to 45.3333, proving omitted live load is included. | Dynamic; backend/api/engine/structure_analyzer.py:144. |
| High | Connected frame with all supports free. | NumPy raises LinAlgError: Singular matrix. Structure Designer creates nodes as free and offers no support editor. | Dynamic and static; StructureDesigner.jsx:44; structure_analyzer.py:70-76. |
| High | Hollow block height 10 versus 20 cm; waffle rib width/spacing 10/50 versus 30/100 cm; other data fixed. | Each pair produces identical design output. Changed geometry appears only in reported metadata. | Dynamic; concrete/slab_hollow.py:15-21,65-80 and slab_waffle.py:15-23,65-80. |

## A. Unit-system defects

Structure Designer sends length=m, force=kN, section width/depth in m, and E=25000 (frontend/src/pages/StructureDesigner.jsx:78-85). The solver computes A in m2 and I in m4 and uses E directly in EA/L and EI/L (backend/api/engine/structure_analyzer.py:105-120). If E=25000 is MPa, as its magnitude and adjacent fc/fy MPa inputs imply, E must be 25,000,000 kN/m2 for this geometry/force system. The resulting stiffness and displacements differ by a factor of 1000. The API declares force and length but no stress, area, inertia, moment, distributed-load, or E unit (structure_router.py:38-64).

SteelBeamForm labels span in mm and submits the raw value (frontend/src/components/SteelBeamForm.jsx:47,103-104); the direct steel engine interprets span in m (backend/api/engine/steel/steel_beam.py:10-19). Entering 5000 for 5 m gives Mu=312500000 kN m in the probe instead of 312.5. An alternate engine in backend/api/codes/steel.py:53-70 interprets span as mm. Other unit inconsistencies occur in column area/stress, footing mixed m/mm dimensions, and copied concrete structure checks.

## B. Steel beam calculation

The direct steel engine divides an mm3 section expression by 10 while labeling it cm3; conversion requires division by 1000. It divides fy times cm3 by 100 while labeling kN m; conversion requires division by 1000 (backend/api/engine/steel/steel_beam.py:22-37). For the same flange term and example above, the dimensionally converted estimate is 145 kN m before including web contribution and any other checks, whereas the code reports 145000 kN m. The expression itself omits the web and is not a validated catalog property. The inflated value controls its safe verdict (line 51).

## C. Concrete structure verdict

ACI structure-level code derives As_required from Mu, invents As_provided=1.2 times As_required, and sets Overall_OK from shear_ok and axial_ok only (backend/api/codes/aci.py:115-133). No actual provided reinforcement or flexural adequacy participates. The very large moment probe still returned True. Similar copied patterns appear in other handlers, including backend/api/codes/jordan.py:123-143 and bs.py:114-138. The normal structure route currently fails before this code; direct handler invocation proves the latent defect.

## D. Concrete column

ColumnForm sends both axial and moment loads (frontend/src/components/ColumnForm.jsx:39-46). The rectangular engine reads axial only, with no axial-moment interaction, slenderness, or moment amplification (backend/api/engine/concrete/column.py:37-57). It multiplies cm2 areas by MPa, which is N/mm2, then divides by 1000 for kN; this misses the cm2-to-mm2 factor of 100. Circular and composite choices are placeholders returning not_implemented (lines 87-105).

## E. Footing assumptions

The footing engine selects allowable pressure only from clay/sand/rock labels or a generic default, assumes a 0.4 m square column and 75 mm cover, and checks simplified bearing/punching under axial load (backend/api/engine/concrete/footing.py:22-63). It has no actual geotechnical capacity, column dimensions, eccentricity, settlement, or full reinforcement design inputs. Rebar diameter and spacing are echoed but do not affect safe (lines 77-93). FootingForm offers isolated, combined, strip, and raft choices, but backend logic does not branch on type (frontend/src/components/FootingForm.jsx:59-63). Safe can therefore rely on hidden assumptions.

## F. Slabs and staircase

Solid, hollow, and waffle slabs use the same hardcoded D/L/W/S factors 1.2/1.6/1.0/1.0 regardless of selected code, a simple wL2/8 demand, and an assumed lever arm (backend/api/engine/concrete/slab_solid.py:22-65; slab_hollow.py:27-80; slab_waffle.py:27-80). Unknown code identifiers silently fall back to generic phi/fy. The solid slab calls its reinforcement mm2/m without defining bar spacing per meter; zero bottom bars triggers division by zero at slab_solid.py:66. The safe verdict does not include all relevant system and serviceability checks.

Hollow block height and waffle rib width/spacing are accepted and displayed but do not affect design output, as the probes confirm. Staircase assumes four bars and 25 mm cover, sums dead/live/wind without design factors, assumes simple-span wL2/8, then emits safe/unsafe from one flexural comparison (backend/api/engine/concrete/staircase.py:17-50). The main API does not pass the selected code to that function, leaving its ACI default (backend/api/main.py:73-74).

## G. Design-code integrity

The UI advertises ACI, BS, Eurocode, AS, CSA, IS, Jordan, Egypt, Saudi, UAE, and Turkey (frontend/src/pages/StructureDesigner.jsx:6-19; Analyzer.jsx:28). All eleven handler classes exist. Their element methods mostly wrap the same shared simplified concrete and steel functions with a different code string (for example backend/api/codes/aci.py:61-89, bs.py:58-83, eurocode.py:57-82). Jordan, Saudi, and UAE inherit ACI and add local wrappers (jordan.py:12-43, saudi.py:12-41, uae.py:12-41). Structure checks are duplicated with different constants. None has adequate benchmark or authoritative edition/clause evidence.

The structure router uppercases names before lookup, but code_router.py stores Eurocode, Jordan, Egypt, Saudi, Turkey, and Steel as mixed-case keys. generate_combinations defines ACI, BS, and EUROCODE only; other advertised codes fall back to 1.0D (backend/api/engine/load_combination.py:23-59). Egypt wrappers pass ECP and Turkey wrappers pass TS500 to generic functions that do not recognize those names and can silently take defaults. The separate SteelCode implementation duplicates the direct steel engine with different formula and unit assumptions. UI-advertised support must not be equated with verified engineering support.

## H. Seismic analysis

Eleven seismic classes use fixed 1000 multipliers and a common 2000 kN safe/review threshold (backend/api/codes_seismic.py:2-329). Jordan explicitly calls its base-shear input a dummy value (line 28). The calculations lack building seismic weight, period, a validated spectrum, structural-system factors, drift, and a structural model. Several handler analyze_seismic methods return demand=0, resistance=0, status=safe directly (for example backend/api/codes/bs.py:141-147 and eurocode.py:144-150). This is placeholder and potentially misleading behavior, not verified seismic design.

## I. Structural frame solver

A load type absent from a combination receives factor 1.0; slab dead load does too (backend/api/engine/structure_analyzer.py:140-159). A fixed-end equivalent load vector is assembled, but force recovery uses only k_local times local displacement and omits the load term (lines 140-150,176-216). Only the first local-end N, V, and M are returned, while fields are called Nmax, Vmax, Mmax; actual member maxima and reaction forces are unavailable. No force diagram is sampled.

Slab self-weight is distributed equally across all members, irrespective of geometry, orientation, or tributary width (lines 153-162). Slab and member loads also use inconsistent sign directions. There is no pre-solve validation for duplicate IDs, disconnected components, inadequate support, zero member length, or nonpositive properties. Zero length is divided into at lines 103-105. All-free structures reach NumPy and fail with a raw singular-matrix error. A nonrectangular section with A but no bw/h can fail because the default bw*h expression is evaluated eagerly (lines 110,199).

## J. API contracts

The backend prefixes structure routes with /api (backend/api/main.py:25), but StructureDesigner posts to /structure/analyze when no environment override is set (frontend/src/pages/StructureDesigner.jsx:88). Once addressed, structure_router.py:87-90 still passes one combo result to handlers expecting a mapping of combo IDs to results. Its broad exception handler changes an intended 400 into 500 and exposes text (lines 73-99). Code-name normalization is inconsistent.

The element analyzer and PDF endpoint paths themselves exist: /analyze and /generate-pdf (frontend/src/pages/Analyzer.jsx:68,86; backend/api/main.py:44,99). Their request fields are unrestricted dictionaries (main.py:34-42). Slab dispatch mutates payload.data with pop before the try block (lines 49-55). Inner error or not_implemented results can be wrapped in outer status=success; broad exceptions in /analyze return raw messages with HTTP 200 (lines 57-97). The frontend does not consistently check HTTP status before consuming responses.

## K. UI workflow

Analyzer.jsx declares code and element state, options, renderForm, submit, seismic options, and result state, but its JSX omits selectors, the renderForm call, and result details (frontend/src/pages/Analyzer.jsx:17-120,122-164). Its forms cannot be reached through the visible page.

StructureDesigner.jsx creates only free nodes, generic members without loads, and a fixed slab; materials and sections are hardcoded in the request. It offers no support or load assignment, property editing, deletion, or stability validation (lines 38-85,272-310). Empty or unstable models can be submitted. Result rendering assumes numeric values and a particular response shape (lines 194-250). Tailwind-like utility classes are used without a Tailwind dependency/configuration in frontend/package.json, vite.config.js, or src/index.css. Forms expose unsupported modes such as prestressed/Tee beam and multiple footing types.

## L. PDF/report trust

/generate-pdf accepts browser-supplied data and result dictionaries rather than a trusted server-side run (backend/api/main.py:40-42,99-108). Every request writes reports/report.pdf and returns a FileResponse for the same path, allowing concurrent requests to collide (main.py:102-106; backend/api/utils/pdf_generator.py:131-135). Analyzer sends result.result containing structural and seismic keys; the generator treats each value as a combination and calls res.get, including on seismic=None (frontend/src/pages/Analyzer.jsx:86-93; pdf_generator.py:74,93-105). This is a schema mismatch confirmed statically; a runtime PDF probe was unavailable because host Python lacks fpdf.

sanitize drops non-Latin-1 characters, while some direct PDF cells contain an unsanitized Unicode arrow or emoji (pdf_generator.py:21-25,62,118). Reports lack immutable run ID, code edition, engine version, sources, units, assumptions, warnings, and reproducible input snapshots. Line 118 can print SAFE from an incomplete Overall_OK verdict.

## M. Build and repository

Root backend/start scripts use a POSIX PYTHONPATH assignment after cd backend, while application imports use backend.api from the repository root (package.json:9-11; backend/api/main.py:9-21). On Windows, npm run backend fails before Python starts. Root npm run dev fails because concurrently is absent. Frontend dev/build fail on a missing tracked Vite chunk; npm ci dry-run reports an inconsistent lockfile. Root and frontend manifests duplicate dependencies, and both frontend npm and Yarn locks are present.

Dockerfile installs only Python requirements and copies the source; it does not build frontend assets. StaticFiles relies on frontend/dist/assets relative to process working directory; the catch-all serves index.html for public root image URLs (backend/api/main.py:112-117). .gitignore entries cannot untrack files already committed; frontend/dist is intentionally not ignored. .dockerignore excludes lockfiles and node_modules while leaving dist. Railway configuration was inspected, never changed or executed. Exact command results and artifact counts are in P0_COMMAND_BASELINE.md and P0_REPOSITORY_INVENTORY.md.

## Current capability and verdict paths

| Area | Baseline state | Authoritative-looking output |
| --- | --- | --- |
| Concrete beam | Partial; normal implemented, inverted/Tee reuse normal, prestressed not implemented | concrete/beam.py:71 emits safe/unsafe after one flexural check. |
| Concrete column | Partial rectangular axial expression; circular/composite placeholders | concrete/column.py:57 emits safe/unsafe without moment interaction. |
| Solid, hollow, waffle slabs | Partial simplified flexure | slab_solid.py:65, slab_hollow.py:80, slab_waffle.py:80 emit safe/unsafe despite incomplete mechanics. |
| Footing | Partial isolated axial/bearing/punching approximation | concrete/footing.py:56-63 emits safe based on generic soil and assumed column size. |
| Staircase | Partial simple-span flexure | concrete/staircase.py:50 emits safe/unsafe with assumed bars. |
| Direct steel beam | Partial and unit-inconsistent | engine/steel/steel_beam.py:51 emits safe/unsafe with inflated capacity. |
| Direct steel column | Partial catalog-based compression expression | engine/steel/steel_column.py:51 emits safe/unsafe without full limit-state evidence. |
| Alternate SteelCode | Partial duplicate formulas | codes/steel.py:39,71 emit nested safe/unsafe with different assumptions. |
| Frame and code handlers | Prototype; normal structure route broken | codes/aci.py:133 and peers emit Overall_OK; StructureDesigner.jsx:250 shows it as OK; pdf_generator.py:118 prints SAFE. |
| Seismic | Placeholder / potentially misleading | codes_seismic.py emits safe/review; several handlers emit safe with zero demand and resistance. |
| Report export | Implemented basic PDF path, trust/schema/Unicode defects | Client controls the result object and report verdict. |
| Authentication, projects, database, migrations, billing | Not implemented in application code | Listed dependencies do not establish these capabilities. |

## P0 disposition

The baseline has been documented without repairing it. P1 should address clean local startup, lockfile/package-manager choice, generated artifacts, frontend build, import paths, and local smoke commands. P2-P10 retain ownership of the related contracts, units, solver, verified calculations, registry, reports, UI, data, QA, and security work under the master roadmap. No later phase has started.

P0 through P11 are local-development phases. No Railway action, production or preview deployment, hosting change, production operation, commit, or push is part of P0. P12 alone handles deployment decision and requires explicit approval before deployment.
