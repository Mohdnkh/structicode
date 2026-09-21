"""Independent closed-form frame benchmarks and solver safety regressions."""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from backend.api.engine.load_combination import combine_loads, parse_combination
from backend.api.engine.structure_analyzer import (
    SolverInputError, StructureAnalyzer, StructureUnstableError, UnsupportedSlabError,
)
from backend.api.main import app


E = 25_000_000.0  # kN/m2
B, H = 0.3, 0.5
A, I = B*H, B*H**3/12
W = 10.0  # kN/m, local negative-y
CLIENT = TestClient(app)


def model(nodes, members, expression="1.0D"):
    return {
        "units": {"length": "m", "force": "kN", "modulus": "kN/m2"},
        "nodes": nodes,
        "sections": [{"id": "S", "shape": "rectRC", "params": {"bw": B, "h": H}}],
        "materials": [{"id": "M", "E": E}],
        "members": members,
        "slabs": [],
        "loads": {"combinations": [{"id": "LC", "name": expression, "expr": expression}]},
    }


def member(member_id, n1, n2, loads=None):
    return {"id": member_id, "n1": n1, "n2": n2, "sectionId": "S",
            "materialId": "M", "loads": loads if loads is not None else [{"type": "D", "w": W}]}


def cantilever():
    return model([{"id": "A", "x": 0, "y": 0, "support": "fix"},
                  {"id": "B", "x": 4, "y": 0, "support": "free"}],
                 [member("AB", "A", "B")])


def simply_supported():
    return model([{"id": "A", "x": 0, "y": 0, "support": "pin"},
                  {"id": "B", "x": 6, "y": 0, "support": "roller"}],
                 [member("AB", "A", "B")])


def rigid_frame():
    return model([{"id": "base", "x": 0, "y": 0, "support": "fix"},
                  {"id": "joint", "x": 0, "y": 3, "support": "free"},
                  {"id": "tip", "x": 4, "y": 3, "support": "free"}],
                 [member("column", "base", "joint", []),
                  member("beam", "joint", "tip")])


def analyze(structure):
    return StructureAnalyzer(structure).analyze_combinations()["LC"]


def test_cantilever_uniform_load_closed_form():
    length = 4
    result = analyze(cantilever())
    reaction = result["reactions"]["A"]
    tip = result["displacements"]["B"]
    beam = result["member_forces"]["AB"]
    assert reaction["rx"] == pytest.approx(0, abs=1e-9)
    assert reaction["ry"] == pytest.approx(W*length, rel=1e-11)
    assert reaction["mz"] == pytest.approx(W*length**2/2, rel=1e-11)
    assert tip["uy"] == pytest.approx(-W*length**4/(8*E*I), rel=1e-11)
    assert tip["rz"] == pytest.approx(-W*length**3/(6*E*I), rel=1e-11)
    assert beam["Mmax"] == pytest.approx(-W*length**2/2, rel=1e-11)
    assert beam["Mmax_x"] == 0
    assert beam["end_1"]["shear"] == pytest.approx(W*length, rel=1e-11)
    assert beam["end_1"]["moment"] == pytest.approx(W*length**2/2, rel=1e-11)
    assert beam["end_2"]["shear"] == pytest.approx(0, abs=1e-9)
    assert beam["end_2"]["moment"] == pytest.approx(0, abs=1e-9)
    assert reaction["ry"]-W*length == pytest.approx(0, abs=1e-9)
    assert reaction["mz"]-W*length**2/2 == pytest.approx(0, abs=1e-9)


def test_simply_supported_uniform_load_closed_form():
    length = 6
    result = analyze(simply_supported())
    left, right = result["reactions"]["A"], result["reactions"]["B"]
    beam = result["member_forces"]["AB"]
    assert left["ry"] == pytest.approx(W*length/2, rel=1e-11)
    assert right["ry"] == pytest.approx(W*length/2, rel=1e-11)
    assert left["mz"] == right["mz"] == 0
    assert beam["Mmax"] == pytest.approx(W*length**2/8, rel=1e-11)
    assert beam["Mmax_x"] == pytest.approx(length/2, rel=1e-11)
    assert beam["midspan_local_y_displacement"] == pytest.approx(
        -5*W*length**4/(384*E*I), rel=1e-11)
    assert beam["end_1"]["moment"] == pytest.approx(0, abs=1e-9)
    assert beam["end_2"]["moment"] == pytest.approx(0, abs=1e-9)
    assert left["ry"]+right["ry"]-W*length == pytest.approx(0, abs=1e-9)
    assert right["ry"]*length-W*length**2/2 == pytest.approx(0, abs=1e-9)


def test_rigid_frame_closed_form_joint_and_end_actions():
    column_height, beam_length = 3, 4
    result = analyze(rigid_frame())
    base = result["reactions"]["base"]
    joint, tip = result["displacements"]["joint"], result["displacements"]["tip"]
    beam, column = result["member_forces"]["beam"], result["member_forces"]["column"]
    moment = W*beam_length**2/2
    expected_rotation = -moment*column_height/(E*I)
    expected_joint_ux = moment*column_height**2/(2*E*I)
    expected_joint_uy = -W*beam_length*column_height/(E*A)
    expected_tip_uy = expected_joint_uy+expected_rotation*beam_length-W*beam_length**4/(8*E*I)
    assert base["ry"] == pytest.approx(W*beam_length, rel=1e-11)
    assert base["mz"] == pytest.approx(moment, rel=1e-11)
    assert base["rx"] == pytest.approx(0, abs=1e-9)
    assert joint["rz"] == pytest.approx(expected_rotation, rel=1e-11)
    assert joint["ux"] == pytest.approx(expected_joint_ux, rel=1e-11)
    assert joint["uy"] == pytest.approx(expected_joint_uy, rel=1e-11)
    assert tip["uy"] == pytest.approx(expected_tip_uy, rel=1e-11)
    assert beam["end_1"]["shear"] == pytest.approx(W*beam_length, rel=1e-11)
    assert beam["end_1"]["moment"] == pytest.approx(moment, rel=1e-11)
    assert column["end_2"]["moment"] == pytest.approx(-moment, rel=1e-11)
    assert base["ry"]-W*beam_length == pytest.approx(0, abs=1e-9)
    assert base["mz"]-W*beam_length**2/2 == pytest.approx(0, abs=1e-9)


@pytest.mark.parametrize(("expression", "expected"), [
    ("1.4D", {"D": 1.4}),
    ("1.2D+1.6L", {"D": 1.2, "L": 1.6}),
    ("0.9D+1.0E", {"D": 0.9, "E": 1.0}),
    (" 1.2 D + 1.6 L - 0.5 W ", {"D": 1.2, "L": 1.6, "W": -0.5}),
    ("-0.9D+1.0S", {"D": -0.9, "S": 1.0}),
    ("1D+0.5D", {"D": 1.5}),
])
def test_combination_parser(expression, expected):
    assert parse_combination(expression) == expected


@pytest.mark.parametrize("expression", ["", "D", "1.2", "1.2X", "1.2D+", "1.2D 1.6L",
                                         "1.2D++1.6L", "1.2D*1.6L", "1e3D"])
def test_combination_parser_rejects_malformed(expression):
    with pytest.raises(ValueError):
        parse_combination(expression)


def test_missing_combination_factor_excludes_live_load():
    structure = cantilever()
    structure["members"][0]["loads"].append({"type": "L", "w": 100})
    structure["loads"]["combinations"][0].update(name="1.4D", expr="1.4D")
    result = analyze(structure)
    assert result["member_forces"]["AB"]["applied_uniform_load"] == pytest.approx(14)
    assert result["reactions"]["A"]["ry"] == pytest.approx(56)
    assert combine_loads({"dead": 10, "live": 100}, {"dead": 1.4}) == pytest.approx(14)


def test_consistent_nodal_load_vector_equilibrium():
    beam = StructureAnalyzer(cantilever()).member_states[0]
    vector = beam.equivalent_load(W)
    length = beam.length
    assert vector[1]+vector[4] == pytest.approx(-W*length)
    assert vector[2]+vector[5]+vector[4]*length == pytest.approx(-W*length**2/2)
    assert vector[0]+vector[3] == 0


def test_fixed_fixed_beam_recovers_fixed_end_load_effects_with_zero_displacements():
    structure = cantilever()
    structure["nodes"][1]["support"] = "fixed"
    result = analyze(structure)
    beam = result["member_forces"]["AB"]
    assert all(abs(value) < 1e-12 for node in result["displacements"].values() for value in node.values())
    assert result["reactions"]["A"]["ry"] == pytest.approx(W*4/2)
    assert result["reactions"]["B"]["ry"] == pytest.approx(W*4/2)
    assert beam["end_1"]["moment"] == pytest.approx(W*4**2/12)
    assert beam["end_2"]["moment"] == pytest.approx(-W*4**2/12)
    assert beam["end_1"]["shear"] == pytest.approx(W*4/2)
    assert beam["end_2"]["shear"] == pytest.approx(W*4/2)


def test_positive_member_load_follows_rotated_local_negative_y():
    structure = cantilever()
    structure["nodes"][1].update(x=0, y=4)
    result = analyze(structure)
    assert result["reactions"]["A"]["rx"] == pytest.approx(-W*4)
    assert result["reactions"]["A"]["ry"] == pytest.approx(0, abs=1e-9)
    assert result["displacements"]["B"]["ux"] == pytest.approx(W*4**4/(8*E*I))


def test_explicit_area_is_used_for_frame_axial_stiffness():
    structure = rigid_frame()
    structure["sections"][0]["params"]["A"] = A/2
    result = analyze(structure)
    assert result["displacements"]["joint"]["uy"] == pytest.approx(-W*4*3/(E*(A/2)))


def test_zero_factored_load_recovers_no_forces_or_displacements():
    structure = cantilever()
    structure["loads"]["combinations"][0].update(name="1.0L", expr="1.0L")
    result = analyze(structure)
    assert result["reactions"]["A"]["ry"] == pytest.approx(0, abs=1e-10)
    assert result["displacements"]["B"]["uy"] == pytest.approx(0, abs=1e-10)
    assert result["member_forces"]["AB"]["Mmax"] == pytest.approx(0, abs=1e-10)


def test_mechanism_is_structured_failure_direct_and_http():
    structure = simply_supported()
    structure["nodes"][0]["support"] = "roller"
    with pytest.raises(StructureUnstableError, match="unstable|mechanism"):
        analyze(structure)
    payload = public_cantilever()
    payload["nodes"][0]["support_id"] = "roller"
    payload["nodes"][1]["support_id"] = "roller"
    response = CLIENT.post("/api/v1/analysis/structure", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "STRUCTURE_UNSTABLE"
    assert response.json()["verification_status"] == "NOT_EVALUATED"


def test_slab_is_unsupported_direct_and_http():
    structure = cantilever()
    structure["slabs"] = [{"id": "slab"}]
    with pytest.raises(UnsupportedSlabError, match="not implemented"):
        StructureAnalyzer(structure)
    payload = public_cantilever()
    payload["slabs"] = [{"id": "SL", "x_m": 0, "y_m": 0, "width_m": 4,
                         "height_m": 3, "thickness_m": 0.2, "material_id": "M"}]
    response = CLIENT.post("/api/v1/analysis/structure", json=payload)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "NOT_IMPLEMENTED"
    assert response.json()["verification_status"] == "NOT_IMPLEMENTED"


@pytest.mark.parametrize("mutation", [
    lambda m: m["nodes"].append(deepcopy(m["nodes"][0])),
    lambda m: m["members"].append(deepcopy(m["members"][0])),
    lambda m: m["members"][0].update(n2="missing"),
    lambda m: m["members"][0].update(sectionId="missing"),
    lambda m: m["members"][0].update(materialId="missing"),
    lambda m: m["nodes"][1].update(x=0),
    lambda m: m["nodes"][0].update(support="hinge"),
    lambda m: m["materials"][0].update(E=0),
    lambda m: m["sections"][0]["params"].update(A=0),
    lambda m: m["sections"][0]["params"].update(I=10),
    lambda m: m["members"][0]["loads"][0].update(w=float("nan")),
    lambda m: m["members"][0]["loads"][0].pop("w"),
    lambda m: m["members"][0]["loads"][0].pop("type"),
    lambda m: m.update(units={"length": "mm", "force": "N", "modulus": "MPa"}),
])
def test_direct_solver_rejects_invalid_models(mutation):
    structure = cantilever()
    mutation(structure)
    with pytest.raises(SolverInputError):
        StructureAnalyzer(structure)


def public_cantilever():
    return {
        "code_id": "ACI",
        "materials": [{"id": "M", "name": "Concrete", "fc_mpa": 25,
                       "fy_mpa": 420, "elastic_modulus_mpa": 25000}],
        "sections": [{"id": "S", "name": "Rect", "shape": "rectRC",
                      "width_m": B, "depth_m": H, "cover_m": 0.04}],
        "nodes": [{"id": "A", "x_m": 0, "y_m": 0, "support_id": "fixed"},
                  {"id": "B", "x_m": 4, "y_m": 0, "support_id": "free"}],
        "members": [{"id": "AB", "n1": "A", "n2": "B", "member_type": "beam",
                     "section_id": "S", "material_id": "M",
                     "loads": [{"case_id": "dead", "line_load_kn_per_m": W}]}],
        "slabs": [],
    }


def test_health_and_stable_http_canonical_reactions_and_member_ends():
    assert CLIENT.get("/health").json() == {"status": "ok"}
    response = CLIENT.post("/api/v1/analysis/structure", json=public_cantilever())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["verification_status"] == "UNVERIFIED"
    combination = body["combinations"]["LC1"]
    assert combination["reactions"]["A"]["ry_n"] == pytest.approx(56_000)
    assert combination["reactions"]["A"]["mz_n_mm"] == pytest.approx(112_000_000)
    assert combination["displacements"]["B"]["uy_mm"] == pytest.approx(
        -1.4*W*4**4/(8*E*I)*1000)
    assert combination["member_forces"]["AB"]["end_1"]["shear_n"] == pytest.approx(56_000)
    assert combination["member_forces"]["AB"]["mmax_x_mm"] == 0
