# Canonical Unit System (P2)

The v1 API normalizes engineering data to a single `N–mm–MPa` system before passing it through a named legacy adapter. API input field suffixes state the unit accepted at the transport boundary. Form values retain their displayed units until the backend normalizes them; neither a field name nor a code-family label implies engineering verification.

| Dimension | Canonical unit | Relationship |
| --- | --- | --- |
| Length | mm | member geometry, displacements, cover |
| Force | N | axial and shear forces |
| Stress and elastic modulus | MPa = N/mm² | material properties |
| Moment | N·mm | bending moment |
| Line load | N/mm | distributed member load |
| Area load and pressure | N/mm² | distributed surface load |
| Section area | mm² | axial stiffness input |
| Section modulus | mm³ | section property |
| Second moment of area | mm⁴ | flexural stiffness property |
| Rotation | rad | dimensionless angle |

In this system, `E [N/mm²]`, `A [mm²]`, `I [mm⁴]`, and `L [mm]` give `EA/L [N/mm]` and `EI/L³ [N/mm]`. This keeps stiffness, force, and moment dimensions explicit without hidden factors inside formulas.

## Authoritative conversions

`backend/api/domain/units.py` defines the dimensions, canonical units, factors, and finite-value validation. It rejects conversions across dimensions or unsupported units.

| Identity | Factor to canonical unit |
| --- | ---: |
| 1 m = 1000 mm | 1000 |
| 1 cm = 10 mm | 10 |
| 1 kN = 1000 N | 1000 |
| 1 kN·m = 1,000,000 N·mm | 1,000,000 |
| 1 kN/m = 1 N/mm | 1 |
| 1 kN/m² = 0.001 N/mm² | 0.001 |
| 1 cm² = 100 mm² | 100 |
| 1 cm³ = 1000 mm³ | 1000 |
| 1 cm⁴ = 10,000 mm⁴ | 10,000 |
| 1 GPa = 1000 MPa | 1000 |

Additional supported inputs include `m²`, `m⁴`, `kN/m²` as a stress unit, and `rad`. A beam width entered as 30 cm becomes 300 mm, a span of 5 m becomes 5000 mm, and a 120 kN·m moment becomes 120,000,000 N·mm. The frontend adapter sends `width_cm`, `span_m`, and `moment_kn_m` unchanged from form display values; the backend converts them to canonical fields.

## Boundary rules

1. New transport models use explicit suffixes such as `_cm`, `_m`, `_mm`, `_kn`, `_n`, `_mpa`, `_kn_m`, `_n_mm`, `_kn_per_m`, and `_n_per_mm`.
2. Canonical domain models use only canonical unit suffixes. Unit conversion is centralized in the domain unit module and called from the adapter, not embedded in calculation formulas.
3. `backend/api/domain/legacy_adapters.py` converts canonical data back to the historical mixed units required by existing engines. This temporary boundary is explicit and testable.
4. The old frame solver receives geometry in m, forces in kN, line loads in kN/m, and elastic modulus in kN/m². The adapter converts the user-entered MPa modulus before invoking it. This corrects a boundary mismatch and can change the numerical result relative to the old UI path; it does not verify the solver.
5. The direct legacy steel-beam engine expects span in m while the alternate SteelCode path expects mm. The adapter chooses the required representation explicitly from the canonical `span_mm` value. Neither steel formula is verified.
6. Raw legacy results retain their historical units and verdict fields only under `legacy_unverified`. Normalized frame displacements and forces in v1 use canonical units, with an overall `UNVERIFIED` verification status.

P3 owns frame solver mathematics and combinations. P4 owns concrete engineering checks. P5 owns steel engineering checks. These later phases must establish formula and design-code validity before any calculation may be called verified.
