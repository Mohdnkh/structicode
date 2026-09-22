# P5 Source-Blocked Steel Safety Remediation

## Scope and source gate

This patch contains trust claims in retained steel compatibility calculations. It does not implement ANSI/AISC 360-22 or complete the verified P5 exit gate. The exact authoritative ANSI/AISC 360-22 provisions for the proposed beam and column scope, the applicable first-printing errata text, authoritative section properties such as AISC Shapes Database v16.0, and published beam/column examples suitable for independent benchmarks were not accessible for inspection. The preceding source-gate evidence remains in [P5_STEEL_CORE_REPORT.md](P5_STEEL_CORE_REPORT.md).

## Active path inventory

| Entry point | Calculation path | Trust-facing result after containment |
| --- | --- | --- |
| `backend/api/engine/steel/steel_beam.py` | Direct legacy beam function | `status: unverified`, `verification_status: UNVERIFIED`, `check_state: NOT_EVALUATED`; old comparison retained only as `legacy_status`. |
| `backend/api/engine/steel/steel_column.py` | Direct legacy column function using local section JSON | Same boundary. |
| `backend/api/codes/steel.py` | Alternate `SteelCode` beam and column functions | Outer `status: success` means request processing only; outer and nested trust fields are `UNVERIFIED` / `NOT_EVALUATED`; raw comparison is nested `legacy_status`. |
| `backend/api/codes/{aci,as_code,bs,csa,egypt,eurocode,jordan,saudi,turkey,uae}.py` | Family wrappers calling the direct functions | Inherit the direct unverified boundary. Jordan, Saudi, and UAE add local details without replacing it. |
| `backend/api/main.py` `/analyze` | Raw legacy API | Adds outer `verification_status: UNVERIFIED` and `check_state: NOT_EVALUATED` for steel beam and column. `status: success` remains a transport outcome. The nested engine result has the same trust boundary. |
| `backend/api/v1.py` `/api/v1/analysis/element` | Typed compatibility API | Preserves its `verification_status: UNVERIFIED` and `legacy_unverified` envelope. A nested legacy `safe` comparison cannot become a verified pass. |
| `backend/api/utils/pdf_generator.py` | Legacy PDF called with steel element input | Displays `Overall: NOT EVALUATED (legacy, unverified)` and does not print a supplied steel `safe` or `VERIFIED` claim. Detailed steel calculation reporting remains for P7. |
| `frontend/src/pages/Analyzer.jsx` | Current element UI | Already displays “Legacy calculation output is unverified” and does not render the raw steel verdict. No frontend change was necessary. |

`backend/api/codes/is_code.py` imports the direct steel functions but does not dispatch steel elements; v1 identifies IS steel as unsupported. No verified steel beam or column design endpoint exists.

## Known engineering defects retained as unverified history

For the direct legacy beam fixture (`b = 150 mm`, `tf = 10 mm`, `h = 300 mm`, `fy = 250 MPa`, `span = 5 m`, `w = 10 kN/m`), the unchanged function produces `Zx = 43,500 cm³`, `Mp = 108,750 kN·m`, and `Mu = 31.25 kN·m`. Its geometric numerator is 435,000 mm³, which is 435 cm³. Applying 250 MPa to that same approximate numerator produces 108.75 kN·m, a factor of 1,000 below the function's reported moment. This is **defect evidence, not an AISC benchmark or accepted design strength**. The approximate geometric expression itself is unverified.

The direct column uses a single section radius and local property row, with embedded modulus and resistance factor. The alternate `SteelCode` column comparison uses only section area and yield stress for its capacity; it does not perform a complete verified buckling or axial-moment interaction check. The alternate beam uses a rectangular section-modulus expression and a dimensionally wrong N·m to N·mm conversion. None of these rules changed in this patch.

The datasets at `backend/api/engine/data/steel_sections_data.json` and `frontend/src/data/steel_sections_data.json` are byte-identical copies. They lack a recorded authoritative source, edition/version, property definitions, and unit declarations. **LEGACY DATASET — PROVENANCE AND UNITS NOT VERIFIED.** They remain available to compatibility paths but are not accepted as an official AISC section catalog.

## Safety semantics and compatibility

Successful legacy engine calculations now carry `verification_status: UNVERIFIED`, `check_state: NOT_EVALUATED`, `status: unverified`, and a plain warning. The old comparison is preserved as `legacy_status` for compatibility and historical investigation. Numerical results, usage values, and recommendations remain legacy artifacts and must not be treated as verified capacities, utilization checks, or design advice. Error results retain `status: error`. The raw API and alternate handler retain `status: success` solely as request-processing status.

The report generator's steel branch intentionally emits only a trust label. This also prevents the previous scalar-field iteration error for direct steel outputs. It does not add a traceable server-side report engine or solve broader P7 report limitations.

## Changed files and checks

- Trust labels only: `backend/api/engine/steel/steel_beam.py`, `backend/api/engine/steel/steel_column.py`, `backend/api/codes/steel.py`, `backend/api/main.py`.
- Legacy steel report trust display: `backend/api/utils/pdf_generator.py`.
- Safety regressions: `backend/tests/test_legacy_steel_safety.py`.
- Roadmap and audit records: `docs/STRUCTICODE_48H_ENTERPRISE_ROADMAP.md`, `docs/audits/P5_STEEL_CORE_REPORT.md`, this file, and `docs/audits/P5_SOURCE_BLOCKED_DECISION.md`.

The focused tests cover both comparison outcomes in direct and alternate engines, all ten active family wrappers, raw and v1 APIs, absent verified endpoints, duplicated section data, the dimensional defect, PDF trust display, and a targeted source-level status guard. Full command results and final Git/PR state are recorded in the task's P5 completion report.

No steel capacity equation, resistance factor, buckling equation, section-property equation, load equation, concrete equation, or P3 solver equation was modified.

## Restart condition

Resume verified P5 only when the exact applicable ANSI/AISC 360-22 provision text and applicability limits can be inspected; the applicable AISC 360-22 errata can be checked against the source printing; authoritative section properties such as AISC Shapes Database v16.0 can be obtained with definitions and units; and published/reference beam and column examples can independently benchmark the selected bounded scope. No clause number or edition-specific design claim is inferred here.
