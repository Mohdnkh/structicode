"""Safety regressions for unverified concrete structure results.

The retained As_required values are behavior snapshots, not code validation.
"""

import ast
from pathlib import Path
import re
import zlib

from fastapi.testclient import TestClient
import pytest

from backend.api.engine.code_router import get_code_handler
from backend.api.main import app
from backend.api.utils.pdf_generator import generate_pdf


LEGACY_CODES = {
    "aci": ("aci.py", 489.91),
    "as": ("as_code.py", 551.15),
    "bs": ("bs.py", 507.05),
    "csa": ("csa.py", 489.91),
    "egypt": ("egypt.py", 489.91),
    "eurocode": ("eurocode.py", 507.05),
    "is": ("is_code.py", 489.91),
    "jordan": ("jordan.py", 489.91),
    "saudi": ("saudi.py", 489.91),
    "turkey": ("turkey.py", 489.91),
    "uae": ("uae.py", 489.91),
}
CLIENT = TestClient(app)


def legacy_structure():
    return {
        "members": [{"id": "B1", "sectionId": "S1", "materialId": "M1"}],
        "sections": [{"id": "S1", "params": {"bw": 0.3, "h": 0.6, "cover": 0.04}}],
        "materials": [{"id": "M1", "fc": 25, "fy": 420}],
    }


def legacy_demand():
    # Shear and axial checks previously returned True, so Overall_OK was True
    # despite no provided reinforcement in the model.
    return {"LC1": {"member_forces": {
        "B1": {"Nmax": 0.0, "Vmax": 0.0, "Mmax": 100.0},
    }}}


@pytest.mark.parametrize("code", LEGACY_CODES)
def test_legacy_structure_never_fabricates_provided_steel_or_overall_pass(code):
    result = get_code_handler(code).analyze_structure(
        legacy_structure(), legacy_demand(),
    )["LC1"]["design"]["B1"]
    assert result["As_provided"] is None
    assert result["Flexure_Check"] == "NOT_EVALUATED"
    assert result["Overall_OK"] is None
    assert result["Overall_Check"] == "NOT_EVALUATED"
    assert result["Shear_OK"] is True
    assert result["Axial_OK"] is True
    # Baseline snapshots show this safety patch did not change the retained
    # legacy As_required calculations. They do not verify those calculations.
    assert result["As_required"] == LEGACY_CODES[code][1]


def public_structure(code):
    return {
        "code_id": code,
        "materials": [{"id": "M1", "name": "Concrete", "fc_mpa": 25,
                       "fy_mpa": 420, "elastic_modulus_mpa": 25000}],
        "sections": [{"id": "S1", "name": "Rect", "shape": "rectRC",
                      "width_m": 0.3, "depth_m": 0.6, "cover_m": 0.04}],
        "nodes": [{"id": "N1", "x_m": 0, "y_m": 0, "support_id": "fixed"},
                  {"id": "N2", "x_m": 5, "y_m": 0, "support_id": "free"}],
        "members": [{"id": "B1", "n1": "N1", "n2": "N2", "member_type": "beam",
                     "section_id": "S1", "material_id": "M1",
                     "loads": [{"case_id": "dead", "line_load_kn_per_m": 5}]}],
        "slabs": [],
    }


@pytest.mark.parametrize("code", LEGACY_CODES)
def test_v1_keeps_legacy_design_under_unverified_output(code):
    response = CLIENT.post("/api/v1/analysis/structure", json=public_structure(code))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["verification_status"] == "UNVERIFIED"
    assert all("design" not in result for result in body["combinations"].values())
    for result in body["legacy_unverified"]["results"].values():
        design = result["design"]["B1"]
        assert design["As_provided"] is None
        assert design["Flexure_Check"] == "NOT_EVALUATED"
        assert design["Overall_OK"] is None
        assert design["Overall_Check"] == "NOT_EVALUATED"


def test_legacy_element_beam_remains_unverified():
    response = CLIENT.post("/api/v1/analysis/element", json={
        "code_id": "aci",
        "input": {
            "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
            "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
            "bar_count": 4, "bar_diameter_mm": 16,
            "line_loads_kn_per_m": {"dead": 5, "live": 3},
        },
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["verification_status"] == "UNVERIFIED"
    assert "legacy_unverified" in body


def test_pdf_never_turns_legacy_overall_flag_into_safe_label(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = generate_pdf(
        {"code": "ACI"},
        {"LC1": {"design": {"B1": {"Overall_OK": True}}}},
        "legacy-status.pdf",
    )
    raw = Path(filename).read_bytes()
    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.DOTALL)
    text = b"".join(zlib.decompress(stream) for stream in streams)
    assert b"Overall: NOT EVALUATED" in text
    assert b"legacy, unverified" in text
    assert b"SAFE" not in text


def test_legacy_source_has_no_numeric_as_provided_assignment():
    source_dir = Path(__file__).resolve().parents[1] / "api" / "codes"
    checked = 0
    for filename, _ in LEGACY_CODES.values():
        tree = ast.parse((source_dir / filename).read_text(encoding="utf-8"))
        assignments = [
            value
            for node in ast.walk(tree) if isinstance(node, ast.Dict)
            for key, value in zip(node.keys, node.values)
            if isinstance(key, ast.Constant) and key.value == "As_provided"
        ]
        assert len(assignments) == 1, filename
        assert isinstance(assignments[0], ast.Constant) and assignments[0].value is None
        checked += 1
    assert checked == 11
