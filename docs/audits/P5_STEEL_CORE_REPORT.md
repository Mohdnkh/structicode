# P5 Steel Core Source Gate Report — BLOCKED

## Decision

P5 started from synchronized `main` at `1df722d6785c64fd401f6a3f8ab9bd698c6801a1` on `codex/p5-steel-core`. The working tree was clean and that branch was absent locally and remotely before creation. P5 is **BLOCKED** at the authoritative-source gate. No verified steel equation, engine, API, section catalog, benchmark, or trust status was implemented. No P5 commit, push, or pull request was created. P4 remains `DEFERRED — SOURCE BLOCKED`; P6-P12 remain HOLD.

## Source access evidence

| Required source | Evidence available in this environment | Gate result |
| --- | --- | --- |
| [ANSI/AISC 360-22 official page](https://www.aisc.org/aisc/publications/current-standards/aisc-360/) | The AISC page was visible in a browser and identified the dual-unit Specification. Its rendered page did not expose the required provision text or a working download. The `aisc.org/2022spec` shortcut led to the same page. Direct requests for the [official PDF path](https://www.aisc.org/globalassets/product-files-not-searched/publications/standards/a360-22w.pdf) returned HTTP 403 from the command environment; the browser could not open the PDF. | Exact provisions unavailable; verified implementation stopped. |
| [AISC revisions and errata](https://www.aisc.org/aisc/publications/revisions-and-errata/) | The official index identifies *Errata to ANSI/AISC 360-22, 1st Printing (Issued January 2025)*. The linked [January 23, 2025 PDF](https://www.aisc.org/media/qonm4cxk/errata_360-22_1st-printing_01232025.pdf) opened a browser tab, but its contents could not be inspected in the available viewer. | Errata identified, not applied or checked against a specification printing. |
| [AISC Shapes Database v16.0](https://www.aisc.org/aisc/publications/steel-construction-manual/aisc-shapes-database-v160/) | The official AISC listing identifies a versioned spreadsheet with U.S. customary and metric properties. The actual property file was not obtained or validated. | No authoritative section data available to the verified path. |
| [AISC Manual Companion, 16th Edition](https://www.aisc.org/aisc/publications/steel-construction-manual/manual-companion-for-16th-edition/) | The official listing identifies published design examples. No applicable beam or column example was accessed and checked as a benchmark. | Independent benchmark evidence unavailable. |

No local file named for AISC 360-22 was found in the repository or the user's Downloads directory. The source-access problem is specific to this environment and does not establish that the public standard is unavailable elsewhere. Unofficial reposts, old editions, legacy Structicode outputs, and remembered equations were not substituted.

The exact official 360-22 text still needed includes the applicable width-thickness classification and limits for rolled W-shapes in flexure and compression; the continuously braced major-axis flexural nominal-strength rule and its LRFD resistance factor; the concentric compression and principal-axis buckling rules and their LRFD resistance factor; and all applicability limits or additional governing checks for the proposed bounded domains. These are categories of missing provisions, not invented clause citations. The first-printing errata must be reviewed against the actual source printing before any rule is marked VERIFIED.

## Legacy steel audit

| Legacy path | Unit contract and observed behavior | Known defect or evidence gap | Status after P5 | Verified source of truth |
| --- | --- | --- | --- | --- |
| `backend/api/engine/steel/steel_beam.py` | Accepts span in m after the v1 adapter converts the UI's mm; returns raw `safe`/`unsafe`. | Section-modulus and moment conversions are dimensionally wrong; the geometry expression is also an approximation, not an authoritative section property. | LEGACY / UNVERIFIED, unchanged. | None. |
| `backend/api/engine/steel/steel_column.py` | Accepts length in mm and load in kN; looks up one `A` and `r` in the local JSON dataset; returns raw `safe`/`unsafe`. | One radius and K cannot establish both principal-axis checks. Dataset provenance and units are not recorded in the file; E and resistance factors are embedded. | LEGACY / UNVERIFIED, unchanged. | None. |
| `backend/api/codes/steel.py` | Alternate `SteelCode` accepts span in mm and load in kN/m through the v1 adapter; returns nested `safe`/`unsafe`. | Beam conversion from N·m to N·mm uses `1e6` rather than the dimensionally required `1e3`; its section modulus is a rectangle approximation. Column capacity is area-only `phi × Fy × A`, without buckling. | LEGACY / UNVERIFIED, unchanged. | None. |
| `backend/api/codes/{aci,as_code,bs,csa,egypt,eurocode,jordan,saudi,turkey,uae}.py` | Code-family wrappers call the direct legacy steel beam/column functions with different code labels. | Shared formulas do not establish independent compliance with those standards. `is_code.py` is not advertised as a steel path in the v1 capability map. | LEGACY / UNVERIFIED, unchanged. | None. |
| `backend/api/main.py` `/analyze` | Raw legacy route resolves a code handler and may expose nested legacy `safe`/`unsafe`. | No verified steel status boundary on that raw route. | LEGACY / UNVERIFIED, unchanged. | None. |
| `backend/api/v1.py` `/api/v1/analysis/element` | Normalizes input units, then nests legacy results under `legacy_unverified` and reports `verification_status: UNVERIFIED`. | This is a compatibility wrapper, not a verified steel calculation. | UNVERIFIED, unchanged. | None. |

The backend and frontend copies of `steel_sections_data.json` are byte-identical (each 3,056 bytes, SHA-256 `488DC0C36D56FA03C88A302AE94547024645DFD08F05C729A6184239ADA831E0`). They contain mixed shape families and just one `W` entry, `W200x21`. The files do not record an AISC v16.0 source, version, property definitions, or units. Their data was not used as authoritative evidence and was not changed.

## Reproduced dimensional defect

For a legacy beam example with `b = 150 mm`, `tf = 10 mm`, `h = 300 mm`, `fy = 250 MPa`, `span = 5 m`, and `w = 10 kN/m`, the direct legacy function reported `Zx = 43,500 cm³`, `Mp = 108,750 kN·m`, `Mu = 31.25 kN·m`, and `status = safe`. Its own geometric numerator is `435,000 mm³`, which converts to `435 cm³`; multiplying that numerator by `250 MPa` gives `108.75 kN·m`. Thus the reported capacity is 1,000 times the dimensionally consistent value of the *same approximate expression*. This is defect evidence only; neither expression is accepted as a verified AISC section modulus or capacity. No verified engine exists yet, so the required regression proving isolation from it could not be written.

The verified beam and column endpoints do not exist. A local HTTP smoke request returned `GET /health` = 200, generic v1 legacy steel beam = HTTP 200 with `UNVERIFIED`, and `POST /api/v1/design/steel/beam` = HTTP 405 with `NOT_EVALUATED`. The latter reflects the absent POST route, not a verified design rejection.

## Regression baseline and remaining work

- `.venv\Scripts\python.exe -m pytest backend/tests -q`: 179 passed, 0 failed.
- P3 solver module: 41 passed; P4 safety module: 25 passed.
- `node --test frontend/tests/api-adapters.test.mjs`: 3 passed, 0 failed.
- `npm run build`: passed with Vite 5.4.21 and 469 transformed modules.
- `npm run verify:backend` with the repository virtual environment on `PATH`: passed.

No P5 equation, source-reference matrix, AISC property comparison, published beam/column benchmark, boundary test, dimensional regression for a verified engine, or valid verified HTTP smoke test exists. The planned `docs/engineering/AISC_360_22_STEEL_CORE.md` and `docs/engineering/AISC_SHAPES_V16_SOURCE.md` were not created because doing so would imply a verified source chain that was not established. Resume P5 only when the exact official specification provisions and applicable errata can be inspected, authoritative section properties can be obtained and checked, and independent AISC design examples can be used for the selected scope.

No backend, frontend, calculation, API, test, dependency, P3 solver, P4 concrete, P6 registry, or deployment file was modified during this blocked gate review.

## Subsequent source-blocked safety recovery

After this source-gate report, a separately scoped P5 safety remediation contained legacy steel trust outputs without implementing AISC 360-22. The historical `safe`/`unsafe` descriptions and “unchanged” statements above record the state **at the initial blocked gate**; they are superseded for current runtime trust labels by [P5_BLOCKED_SAFETY_REMEDIATION.md](P5_BLOCKED_SAFETY_REMEDIATION.md). The verified P5 core remains incomplete and source blocked. The roadmap now records `P5 = DEFERRED — SOURCE BLOCKED`, while `P4 = DEFERRED — SOURCE BLOCKED` and `P6-P12 = HOLD`.

Safety recovery checks: focused steel tests 43 passed; complete backend suite 222 passed; frontend adapter tests 3 passed; Vite build passed with 469 transformed modules; backend import verification passed. The dimensional fixture remains defect evidence, not an AISC benchmark. No engineering formula was changed. The independent review and merge decision belongs to the pull request; this audit does not mark the verified core complete.
