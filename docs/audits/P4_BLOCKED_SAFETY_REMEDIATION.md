# P4 Blocked Safety Remediation

## Scope and blocker

This safety correction starts from `main` at `c36db9fb279d126e3dea804c9c4dbd16bb272c45` on `codex/p4-concrete-core`. The verified concrete core remains **BLOCKED** because an authorized copy of ACI CODE-318-25 in SI units, or authorized ACI 318 PLUS access to that edition, is unavailable. No ACI 318-25 provision was inferred or implemented. The source is still needed to verify the applicable beam flexure provisions, reinforcement limits and detailing, sectional strength assumptions, strength-reduction factors, and the corresponding clauses, equations, and tables before verified engineering work can resume.

The roadmap retains P0-P3 as PUSHED, P4 as BLOCKED, and P5-P12 as HOLD. This correction does not start P5 or authorize deployment.

## Confirmed fabricated reinforcement

Each structure-level concrete handler computed a required steel area but had no actual member bar/reinforcement input. It nonetheless reported `As_provided` as a multiple of `As_required` and set `Overall_OK` to `shear_ok and axial_ok`, omitting flexural adequacy. A static inspection found these eleven occurrences:

| Handler source | Fabricated `As_provided` expression |
| --- | --- |
| `backend/api/codes/aci.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/as_code.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/bs.py` | `round(As_req * 1.15, 2)` |
| `backend/api/codes/csa.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/egypt.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/eurocode.py` | `round(As_req * 1.15, 2)` |
| `backend/api/codes/is_code.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/jordan.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/saudi.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/turkey.py` | `round(As_req * 1.2, 2)` |
| `backend/api/codes/uae.py` | `round(As_req * 1.2, 2)` |

Before the correction, a member with `Mmax = 100 kN·m`, `Vmax = 0`, `Nmax = 0`, and no provided reinforcement returned a numeric `As_provided` and `Overall_OK = True` under every handler. This is a defect reproduction, not validation of the legacy `As_required` calculation.

## Corrected status and compatibility

All eleven handlers preserve the existing result keys. They now return `As_provided: null`, `Flexure_Check: NOT_EVALUATED`, `Overall_OK: null`, and `Overall_Check: NOT_EVALUATED`. The existing `Shear_OK` and `Axial_OK` fields remain as legacy calculation outputs; they are not verified code checks. The Structure Designer displays `Overall_Check` rather than a Boolean or the string `null`.

The v1 structure response continues to place legacy design data under `legacy_unverified` with `verification_status: UNVERIFIED`. It does not promote a legacy design verdict into the normalized response. The legacy v1 element beam response also remains UNVERIFIED.

The legacy PDF previously converted a client-supplied `Overall_OK` into `SAFE` or `NOT SAFE`. It now prints `Overall: NOT EVALUATED (legacy, unverified)` for every legacy design entry, including when the caller supplies `Overall_OK: true`. This is a narrow trust-label correction. The report still accepts client-supplied analysis data, and its storage, Unicode handling, and traceability require the later report phase.

## Engineering integrity and tests

No concrete capacity equation, material coefficient, strength-reduction equation, load equation, steel equation, or P3 solver equation was modified. The existing `As_required` outputs for the reproduction fixture are retained as behavioral snapshots, not engineering reference values.

`backend/tests/test_legacy_concrete_safety.py` has 25 focused cases. They cover all eleven direct handlers, all eleven v1 structure responses, the v1 element UNVERIFIED boundary, PDF output even with a forged true verdict, and an AST assertion over the eleven applicable engineering source files to reject numeric `As_provided` assignments. Full regression command results are recorded in the PR and final task report after execution.

## Remaining limits

The retained concrete capacity calculations and code-family implementations are unverified. `Shear_OK`, `Axial_OK`, and `As_required` are legacy outputs; callers must not interpret them as verified design acceptance. Other legacy element and seismic paths still emit their existing `safe`/`unsafe` or `safe`/`review` values. Their v1 wrappers remain unverified where applicable, but raw legacy endpoints can still expose those labels. Those paths were outside this targeted structure-design correction. The generic PDF path remains client-supplied and requires the planned report architecture work. No verified concrete calculation report was created because `docs/audits/P4_CONCRETE_CORE_REPORT.md` does not exist and the verified work remains blocked.
