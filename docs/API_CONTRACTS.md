# Versioned Analysis API Contracts (P2)

The local FastAPI server exposes `POST /api/v1/analysis/element` and `POST /api/v1/analysis/structure`. `GET /health` remains a process-health check. All v1 engineering quantities use explicit unit-bearing field names; request parsing rejects unknown fields and invalid geometry. OpenAPI at `/openapi.json` is generated from the Pydantic v1 models.

## Stable identifiers

| Kind | Identifiers |
| --- | --- |
| Legacy design-code families | `aci`, `bs`, `eurocode`, `as`, `csa`, `is`, `jordan`, `egypt`, `saudi`, `uae`, `turkey`, `steel` |
| Elements | `beam`, `column`, `slab`, `footing`, `staircase`, `steel_beam`, `steel_column` |
| Load cases | `dead`, `live`, `wind`, `snow`, `earthquake` |
| Supports | `free`, `pin`, `roller`, `fixed` |

Code-family input is case insensitive, and the historical support spelling `fix` maps to `fixed`. The family identifiers name legacy routing choices, not verified design-code editions. P6 owns the formal edition and capability registry. Unsupported family/element combinations and variants return structured errors instead of a fabricated calculation.

### Temporary legacy routing capability

`backend/api/legacy_capabilities.py` records only whether a software dispatch path exists for the current v1 adapter. It is not the P6 design-code registry and does not establish engineering validity.

| Legacy family IDs | Concrete elements | Steel elements | Structure analysis |
| --- | --- | --- | --- |
| `aci`, `bs`, `eurocode`, `as`, `csa`, `jordan`, `egypt`, `saudi`, `uae`, `turkey` | Beam, column, slab, footing, staircase | Steel beam, steel column | Legacy path exists |
| `is` | Beam, column, slab, footing, staircase | Not implemented | Legacy path exists |
| `steel` | Not implemented | Steel beam, steel column | Not implemented |

Unsupported family/element combinations return HTTP 400 with `NOT_IMPLEMENTED` before invoking a legacy engine. An explicit legacy handler refusal is also mapped to that outcome. A genuine calculation or runtime failure remains HTTP 500 with `ENGINE_FAILURE` and `NOT_EVALUATED`. A successful legacy path always remains `UNVERIFIED`. The AS steel handler's missing imports were repaired without changing its calculations; IS continues to expose concrete paths only.

## Element request

The body has a normalized `code_id`, a discriminated `input` object, and optional `seismic`. Seismic input is rejected as `NOT_IMPLEMENTED` until a verified path exists.

```json
{
  "code_id": "aci",
  "input": {
    "kind": "beam",
    "beam_type": "normal",
    "width_cm": 30,
    "depth_cm": 60,
    "span_m": 5,
    "cover_cm": 3,
    "fc_mpa": 25,
    "fy_mpa": 420,
    "bar_count": 4,
    "bar_diameter_mm": 16,
    "line_loads_kn_per_m": {"dead": 5, "live": 3}
  }
}
```

The `kind` discriminator selects a concrete beam, concrete column, slab, footing, staircase, steel beam, or steel column schema. Variant fields are explicit: for example `slab_type`, `block_height_cm`, `rib_width_cm`, and `rib_spacing_cm`. Steel beam span is **`span_mm`**, matching its current form label. Column forces use `axial_force_kn` and `moment_kn_m`. Each model and its optional/default fields are specified in `backend/api/domain/schemas.py` and the generated OpenAPI schema.

Element-only `axial_force_kn` fields for concrete columns, footings, and steel columns are nonnegative **magnitudes** under the current legacy form/engine convention. P2 defines no compression/tension sign convention for those paths. Structure member line loads and the concrete-column moment field accept finite signed values. Engineering sign semantics belong to the applicable later calculation phase.

Successful element response shape:

```json
{
  "request_status": "success",
  "verification_status": "UNVERIFIED",
  "code_id": "aci",
  "element_id": "beam",
  "canonical_input": {"kind": "beam", "width_mm": 300, "span_mm": 5000},
  "legacy_unverified": {"result": {}},
  "warnings": ["Legacy calculation output has not been independently verified."]
}
```

The example abbreviates `canonical_input` and `legacy_unverified.result`; live responses contain the full model and historical calculation output. The raw legacy result may contain old `safe`, `unsafe`, or similar values, which remain unverified.

## Structure request

The structure body has `code_id`, `materials`, `sections`, `nodes`, `members`, and optional `slabs`. Required material fields include `fc_mpa`, `fy_mpa`, and `elastic_modulus_mpa`. Rectangular section dimensions use `width_m`, `depth_m`, and `cover_m`, with optional `area_m2` and `inertia_mm4`. Node coordinates use `x_m` and `y_m` plus `support_id`. Members reference existing node, section, and material IDs; loads use `case_id` and `line_load_kn_per_m`. Slab geometry dimensions use `_m` fields. Duplicate IDs within each collection, missing references, zero-length members, and wholly unsupported models are rejected at the contract boundary. Explicit section inertia is rejected as `NOT_IMPLEMENTED` because the current frame solver does not consume it.

```json
{
  "code_id": "eurocode",
  "materials": [{"id": "M1", "name": "C25", "fc_mpa": 25, "fy_mpa": 420, "elastic_modulus_mpa": 25000}],
  "sections": [{"id": "S1", "name": "Rect", "shape": "rectRC", "width_m": 0.3, "depth_m": 0.6, "cover_m": 0.04}],
  "nodes": [
    {"id": "N1", "x_m": 0, "y_m": 0, "support_id": "fixed"},
    {"id": "N2", "x_m": 5, "y_m": 0, "support_id": "free"}
  ],
  "members": [{"id": "B1", "n1": "N1", "n2": "N2", "member_type": "beam", "section_id": "S1", "material_id": "M1", "loads": [{"case_id": "dead", "line_load_kn_per_m": 5}]}],
  "slabs": []
}
```

A successful structure response has `request_status: "success"`, `verification_status: "UNVERIFIED"`, `code_id`, `canonical_input`, `combinations`, `legacy_unverified.results`, and `warnings`. Canonical combinations expose `ux_mm`, `uy_mm`, `rz_rad`, `nmax_n`, `vmax_n`, and `mmax_n_mm`. These normalized values are unit-consistent representations of *unverified* solver output. Historical design checks stay under `legacy_unverified.results`.

## Errors and result meaning

Validation errors return HTTP 422. Unsupported analysis paths return HTTP 400 with `NOT_IMPLEMENTED`. Legacy engine failures return HTTP 500 with a generic message; internal exception details are logged server-side and are not sent in the v1 response. Unknown v1 routes return a structured HTTP 404.
Finite inputs that overflow during unit normalization also return a structured HTTP 422 `NORMALIZATION_ERROR`.

```json
{
  "request_status": "error",
  "verification_status": "NOT_EVALUATED",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [{"field": "body.input.width_cm", "message": "Input should be greater than 0"}]
  }
}
```

`request_status` describes software handling (`success` or `error`). `verification_status` separately describes engineering trust: `VERIFIED` is reserved for a later validated capability; current legacy output is `UNVERIFIED`; rejected or unevaluated requests use `NOT_EVALUATED`; and an unsupported capability uses `NOT_IMPLEMENTED`. The typed `CheckState` reserves `PASS`, `FAIL`, `NOT_EVALUATED`, and `NOT_VERIFIED`; P2 emits no authoritative normalized PASS/FAIL engineering check.

## Migration and local checks

The frontend API client is `frontend/src/api/client.js`, and its form-to-request mapping is `frontend/src/api/adapters.js`. The pages now call v1 through that client. Existing `/analyze`, `/api/structure/analyze`, and `/generate-pdf` remain compatibility routes, retaining their old contract and trust limitations. PDF report architecture and trust belong to P7. Structure Designer controls and Analyzer layout remain incomplete and belong to P8.

From the repository root with the documented virtual environment and npm dependencies installed, run `python -m pytest backend/tests -q` for the backend unit/contract suite and `node --test frontend/tests/api-adapters.test.mjs` for frontend mapping tests. These tests check contract behavior and transport units; they do not certify structural calculations.
