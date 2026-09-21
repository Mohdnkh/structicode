from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from backend.api.domain.identifiers import DesignCode
from backend.api.domain.legacy_adapters import (
    element_to_legacy, normalize_element, normalize_structure, structure_to_legacy,
)
from backend.api.domain.schemas import ElementRequest, StructureRequest
from backend.api.engine.code_router import get_code_handler
from backend.api.main import app


client = TestClient(app)
STEEL_DIMS = {
    "depth_mm": 100, "width_mm": 55,
    "flange_thickness_mm": 7.1, "web_thickness_mm": 4.1,
}


ELEMENT_INPUTS = [
    ("beam", {
        "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
        "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
        "bar_count": 4, "bar_diameter_mm": 16,
        "line_loads_kn_per_m": {"dead": 5, "live": 3},
    }),
    ("column", {
        "kind": "column", "width_cm": 30, "depth_cm": 40, "height_m": 3,
        "bar_diameter_mm": 16, "bar_count": 4, "tie_spacing_cm": 20,
        "fc_mpa": 25, "fy_mpa": 420, "axial_force_kn": 100,
        "moment_kn_m": 120,
    }),
    ("slab", {
        "kind": "slab", "slab_type": "solid", "thickness_cm": 20,
        "length_m": 5, "width_m": 4, "fc_mpa": 25, "fy_mpa": 420,
        "bar_diameter_mm": 12, "top_bar_count": 5, "bottom_bar_count": 5,
        "area_loads_kn_per_m2": {"dead": 3, "live": 2},
    }),
    ("footing", {
        "kind": "footing", "length_m": 2, "width_m": 2,
        "thickness_cm": 50, "axial_force_kn": 500,
        "bar_diameter_mm": 12, "bar_spacing_cm": 20,
        "fc_mpa": 25, "fy_mpa": 420, "soil_type": "sand",
    }),
    ("staircase", {
        "kind": "staircase", "width_cm": 100, "riser_cm": 17,
        "tread_cm": 30, "steps": 10, "thickness_cm": 15,
        "bar_diameter_mm": 12, "fc_mpa": 25, "fy_mpa": 420,
        "area_loads_kn_per_m2": {"dead": 3, "live": 2},
    }),
    ("steel_beam", {
        "kind": "steel_beam", "section_type": "IPE", "section_size": "IPE100",
        "dimensions": STEEL_DIMS, "fy_mpa": 235, "span_mm": 5000,
        "uniform_load_kn_per_m": 5, "support_type": "simply_supported",
    }),
    ("steel_column", {
        "kind": "steel_column", "section_type": "IPE", "section_size": "IPE100",
        "dimensions": STEEL_DIMS, "fy_mpa": 235, "axial_force_kn": 100,
        "length_mm": 3000, "k_factor": 1, "boundary_condition": "Pinned-Pinned",
    }),
]


def structure_payload(code="ACI"):
    return {
        "code_id": code,
        "materials": [{
            "id": "M1", "name": "C25", "fc_mpa": 25, "fy_mpa": 420,
            "elastic_modulus_mpa": 25000,
        }],
        "sections": [{
            "id": "S1", "name": "Rect", "shape": "rectRC",
            "width_m": 0.3, "depth_m": 0.6, "cover_m": 0.04,
        }],
        "nodes": [
            {"id": "N1", "x_m": 0, "y_m": 0, "support_id": "fixed"},
            {"id": "N2", "x_m": 5, "y_m": 0, "support_id": "free"},
        ],
        "members": [{
            "id": "B1", "n1": "N1", "n2": "N2", "member_type": "beam",
            "section_id": "S1", "material_id": "M1",
            "loads": [{"case_id": "dead", "line_load_kn_per_m": 5}],
        }],
        "slabs": [],
    }


@pytest.mark.parametrize("element,form", ELEMENT_INPUTS, ids=[item[0] for item in ELEMENT_INPUTS])
def test_each_element_has_typed_v1_contract_and_unverified_output(element, form):
    response = client.post("/api/v1/analysis/element", json={"code_id": "ACI", "input": form})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["request_status"] == "success"
    assert body["verification_status"] == "UNVERIFIED"
    assert body["element_id"] == element
    assert body["canonical_input"]["kind"] == element
    assert isinstance(body["legacy_unverified"]["result"], dict)
    assert body["verification_status"] != "VERIFIED"


def test_element_adapters_preserve_form_inputs_and_steel_span_units():
    form = deepcopy(dict(ELEMENT_INPUTS)["steel_beam"])
    original = deepcopy(form)
    request = ElementRequest.model_validate({"code_id": "aCi", "input": form})
    canonical = normalize_element(request.input)
    assert canonical.span_mm == 5000
    assert element_to_legacy(canonical, DesignCode.ACI)["span"] == 5
    assert element_to_legacy(canonical, DesignCode.STEEL)["span"] == 5000
    assert form == original


def test_beam_and_column_normalize_display_units():
    beam = normalize_element(ElementRequest.model_validate({
        "code_id": "aci", "input": dict(ELEMENT_INPUTS)["beam"],
    }).input)
    assert beam.width_mm == 300
    assert beam.span_mm == 5000
    assert beam.line_loads_n_per_mm.dead == 5
    column = normalize_element(ElementRequest.model_validate({
        "code_id": "aci", "input": dict(ELEMENT_INPUTS)["column"],
    }).input)
    assert column.axial_force_n == 100_000
    assert column.moment_n_mm == 120_000_000


def test_invalid_element_request_has_structured_422():
    form = deepcopy(dict(ELEMENT_INPUTS)["beam"])
    form["width_cm"] = -1
    response = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": form})
    assert response.status_code == 422
    body = response.json()
    assert body["request_status"] == "error"
    assert body["verification_status"] == "NOT_EVALUATED"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"]


def test_beam_cover_cannot_exceed_depth():
    form = deepcopy(dict(ELEMENT_INPUTS)["beam"])
    form["cover_cm"] = form["depth_cm"]
    response = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": form})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_extreme_finite_input_has_structured_normalization_error():
    form = deepcopy(dict(ELEMENT_INPUTS)["beam"])
    form["span_m"] = 1e308
    response = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": form})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "NORMALIZATION_ERROR"


def test_ignored_legacy_load_is_rejected_instead_of_silently_dropped():
    form = deepcopy(dict(ELEMENT_INPUTS)["beam"])
    form["line_loads_kn_per_m"]["earthquake"] = 4
    response = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": form})
    assert response.status_code == 400
    assert response.json()["verification_status"] == "NOT_IMPLEMENTED"


def test_unsupported_family_and_variant_are_explicit_errors():
    beam = dict(ELEMENT_INPUTS)["beam"]
    invalid = client.post("/api/v1/analysis/element", json={"code_id": "mars", "input": beam})
    assert invalid.status_code == 422
    variant = deepcopy(beam)
    variant["beam_type"] = "prestressed"
    response = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": variant})
    assert response.status_code == 400
    assert response.json()["verification_status"] == "NOT_IMPLEMENTED"


def test_v1_does_not_leak_internal_exception(monkeypatch):
    def fail(*args):
        raise RuntimeError("private calculation trace")
    monkeypatch.setattr("backend.api.v1._legacy_element_result", fail)
    response = client.post("/api/v1/analysis/element", json={
        "code_id": "aci", "input": dict(ELEMENT_INPUTS)["beam"],
    })
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "ENGINE_FAILURE"
    assert "private calculation trace" not in response.text


def test_structure_unit_adapter_and_request_immutability():
    payload = structure_payload()
    original = deepcopy(payload)
    request = StructureRequest.model_validate(payload)
    canonical = normalize_structure(request)
    legacy = structure_to_legacy(canonical)
    assert canonical.nodes[1].x_mm == 5000
    assert canonical.sections[0].width_mm == 300
    assert canonical.materials[0].elastic_modulus_mpa == 25000
    assert legacy["materials"][0]["E"] == 25_000_000
    assert legacy["sections"][0]["params"]["bw"] == pytest.approx(0.3)
    assert request.model_dump(mode="json") == StructureRequest.model_validate(original).model_dump(mode="json")
    assert payload == original


def test_structure_section_area_is_normalized_and_explicit_inertia_is_rejected():
    payload = structure_payload()
    payload["sections"][0]["area_m2"] = 0.18
    canonical = normalize_structure(StructureRequest.model_validate(payload))
    assert canonical.sections[0].area_mm2 == pytest.approx(180_000)
    payload["sections"][0]["inertia_mm4"] = 1_000_000
    response = client.post("/api/v1/analysis/structure", json=payload)
    assert response.status_code == 400
    assert response.json()["verification_status"] == "NOT_IMPLEMENTED"


def test_structure_v1_receives_all_combinations_and_unverified_result():
    response = client.post("/api/v1/analysis/structure", json=structure_payload("eUrOcOdE"))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code_id"] == "eurocode"
    assert body["verification_status"] == "UNVERIFIED"
    assert set(body["combinations"]) == set(body["legacy_unverified"]["results"])
    assert all("design" in result for result in body["legacy_unverified"]["results"].values())
    assert body["canonical_input"]["nodes"][1]["x_mm"] == 5000


def test_legacy_structure_route_no_longer_passes_single_combination():
    payload = structure_payload("Eurocode")
    legacy = structure_to_legacy(normalize_structure(StructureRequest.model_validate(payload)))
    legacy["materials"][0]["E"] = 25000
    response = client.post("/api/structure/analyze", json=legacy)
    assert response.status_code == 200, response.text
    results = response.json()["results"]
    assert set(results) == {"LC1", "LC2", "LC3"}
    assert all("design" in value for value in results.values())


@pytest.mark.parametrize("change", ["duplicate", "unknown_support", "zero_length", "bad_load_case"])
def test_invalid_structure_identifiers_are_structured_422(change):
    payload = structure_payload()
    if change == "duplicate":
        payload["nodes"][1]["id"] = "N1"
    elif change == "unknown_support":
        payload["nodes"][0]["support_id"] = "hinge"
    elif change == "zero_length":
        payload["nodes"][1]["x_m"] = 0
    else:
        payload["members"][0]["loads"][0]["case_id"] = "seismic"
    response = client.post("/api/v1/analysis/structure", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_structure_unsupported_family_has_structured_400():
    response = client.post("/api/v1/analysis/structure", json=structure_payload("steel"))
    assert response.status_code == 400
    assert response.json()["verification_status"] == "NOT_IMPLEMENTED"


@pytest.mark.parametrize("code", list(DesignCode))
def test_code_family_lookup_is_case_independent(code):
    assert get_code_handler(code.value) is not None
    assert type(get_code_handler(code.value.upper())) is type(get_code_handler(code.value.title()))


def test_health_and_unknown_v1_path():
    assert client.get("/health").json() == {"status": "ok"}
    missing = client.get("/api/v1/no-such-route")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"
