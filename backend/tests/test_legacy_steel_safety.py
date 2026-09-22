"""Trust-boundary regressions for retained, unverified steel calculations."""

import ast
import hashlib
from pathlib import Path
import re
import zlib

from fastapi.testclient import TestClient
import pytest

from backend.api.engine.code_router import get_code_handler
from backend.api.engine.steel.steel_beam import analyze_steel_beam
from backend.api.engine.steel.steel_column import analyze_steel_column
from backend.api.main import app
from backend.api.utils.pdf_generator import generate_pdf


ROOT = Path(__file__).resolve().parents[2]
CLIENT = TestClient(app)
DIRECT_FAMILIES = (
    "aci", "as", "bs", "csa", "egypt", "eurocode", "jordan",
    "saudi", "turkey", "uae",
)
DIMS = {"depth": 300, "width": 150, "flangeThickness": 10, "webThickness": 6}
BEAM = {
    "sectionType": "IPE", "sectionSize": "IPE100", "dimensions": DIMS,
    "steelGrade": 250, "span": 5, "uniformLoad": 10,
    "supportType": "Simply Supported",
}
COLUMN = {
    "sectionType": "IPE", "sectionSize": "IPE100", "dimensions": DIMS,
    "steelGrade": 250, "axialLoad": 1, "length": 3000,
    "kFactor": 1, "boundaryCondition": "Pinned-Pinned",
}
V1_BEAM = {
    "kind": "steel_beam", "section_type": "IPE", "section_size": "IPE100",
    "dimensions": {"depth_mm": 300, "width_mm": 150,
                   "flange_thickness_mm": 10, "web_thickness_mm": 6},
    "fy_mpa": 250, "span_mm": 5000,
    "uniform_load_kn_per_m": 0.01, "support_type": "simply_supported",
}
V1_COLUMN = {
    "kind": "steel_column", "section_type": "IPE", "section_size": "IPE100",
    "dimensions": V1_BEAM["dimensions"], "fy_mpa": 250,
    "axial_force_kn": 1, "length_mm": 3000,
    "k_factor": 1, "boundary_condition": "Pinned-Pinned",
}


def assert_unverified(result):
    assert result["status"] == "unverified"
    assert result["verification_status"] == "UNVERIFIED"
    assert result["check_state"] == "NOT_EVALUATED"
    assert result["legacy_status"] in {"safe", "unsafe"}
    assert "legacy" in result["warning"].lower()


@pytest.mark.parametrize("kind,engine,fixture,load_key", [
    ("steel_beam", analyze_steel_beam, BEAM, "uniformLoad"),
    ("steel_column", analyze_steel_column, COLUMN, "axialLoad"),
])
@pytest.mark.parametrize("load", [1, 10_000_000])
def test_direct_engines_never_report_adequacy(kind, engine, fixture, load_key, load):
    result = engine({**fixture, load_key: load})
    assert result["element"] == kind
    assert_unverified(result)


@pytest.mark.parametrize("family", DIRECT_FAMILIES)
@pytest.mark.parametrize("kind,fixture", [
    ("steel_beam", BEAM), ("steel_column", COLUMN),
])
def test_code_family_wrappers_retain_unverified_boundary(family, kind, fixture):
    result = get_code_handler(family).analyze(kind, fixture)
    assert_unverified(result)


@pytest.mark.parametrize("kind,fixture", [
    ("steel_beam", {**BEAM, "span": 5000}),
    ("steel_column", COLUMN),
])
@pytest.mark.parametrize("load", [1, 10_000_000])
def test_alternate_steel_handler_never_reports_adequacy(kind, fixture, load):
    load_key = "uniformLoad" if kind == "steel_beam" else "axialLoad"
    result = get_code_handler("steel").analyze(kind, {**fixture, load_key: load})
    assert result["status"] == "success"  # Request handling only.
    assert result["verification_status"] == "UNVERIFIED"
    assert result["check_state"] == "NOT_EVALUATED"
    assert_unverified(result["result"])


@pytest.mark.parametrize("code,kind,fixture", [
    ("aci", "steel_beam", BEAM), ("aci", "steel_column", COLUMN),
    ("steel", "steel_beam", {**BEAM, "span": 5000}),
    ("steel", "steel_column", COLUMN),
])
def test_raw_api_cannot_promote_legacy_safe(code, kind, fixture):
    response = CLIENT.post("/analyze", json={"code": code, "element": kind, "data": fixture})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"  # Transport status, not adequacy.
    assert body["verification_status"] == "UNVERIFIED"
    assert body["check_state"] == "NOT_EVALUATED"
    structural = body["result"]["structural"]
    assert_unverified(structural.get("result", structural))


@pytest.mark.parametrize("code", ["aci", "steel"])
@pytest.mark.parametrize("fixture", [V1_BEAM, V1_COLUMN])
def test_v1_steel_remains_unverified_even_when_legacy_comparison_is_safe(code, fixture):
    response = CLIENT.post("/api/v1/analysis/element", json={"code_id": code, "input": fixture})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["verification_status"] == "UNVERIFIED"
    assert "legacy_unverified" in body
    result = body["legacy_unverified"]["result"]
    assert_unverified(result.get("result", result))
    assert result.get("result", result)["legacy_status"] == "safe"


def test_no_verified_steel_design_route_exists():
    routes = {(method, route.path) for route in app.routes for method in getattr(route, "methods", ())}
    assert ("POST", "/api/v1/design/steel/beam") not in routes
    assert ("POST", "/api/v1/design/steel/column") not in routes


def test_legacy_beam_unit_discrepancy_is_defect_evidence_only():
    result = analyze_steel_beam(BEAM)
    assert result["Zx (cm³)"] == 43_500
    assert result["Mp (kN·m)"] == 108_750
    assert result["Mu (kN·m)"] == 31.25
    geometric_numerator_mm3 = 150 * 10 * (300 - 10)
    dimensionally_consistent_kn_m = 250 * geometric_numerator_mm3 / 1_000_000
    assert dimensionally_consistent_kn_m == 108.75
    assert result["Mp (kN·m)"] / dimensionally_consistent_kn_m == 1000
    assert result["verification_status"] == "UNVERIFIED"
    # This is a dimensional defect reproduction, never an AISC benchmark.


def test_duplicate_section_data_has_no_verified_provenance():
    paths = [ROOT / "backend/api/engine/data/steel_sections_data.json",
             ROOT / "frontend/src/data/steel_sections_data.json"]
    assert hashlib.sha256(paths[0].read_bytes()).digest() == hashlib.sha256(paths[1].read_bytes()).digest()
    text = paths[0].read_text(encoding="utf-8")
    assert '"source"' not in text and '"units"' not in text and '"version"' not in text
    decision = (ROOT / "docs/audits/P5_BLOCKED_SAFETY_REMEDIATION.md").read_text(encoding="utf-8")
    assert "LEGACY DATASET — PROVENANCE AND UNITS NOT VERIFIED" in decision


def test_pdf_does_not_print_client_supplied_safe_claim(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    filename = generate_pdf(
        {"code": "ACI", "element": "steel_beam"},
        {"status": "safe", "verification_status": "VERIFIED"},
        "steel-legacy.pdf",
    )
    raw = Path(filename).read_bytes()
    streams = re.findall(rb"stream\r?\n(.*?)\r?\nendstream", raw, re.DOTALL)
    content = b"".join(zlib.decompress(stream) for stream in streams)
    assert b"Overall: NOT EVALUATED \\(legacy, unverified\\)" in content
    assert b"LEGACY / UNVERIFIED / CLIENT-SUPPLIED REPORT" in content
    assert not re.search(rb"(?<![A-Z_])SAFE(?![A-Z_])", content)
    assert not re.search(rb"(?<![A-Z_])VERIFIED(?![A-Z_])", content)


@pytest.mark.parametrize("path", [
    "backend/api/engine/steel/steel_beam.py",
    "backend/api/engine/steel/steel_column.py",
    "backend/api/codes/steel.py",
])
def test_active_engine_result_dictionaries_never_expose_raw_status(path):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    status_values = [value for node in ast.walk(tree) if isinstance(node, ast.Dict)
                     for key, value in zip(node.keys, node.values)
                     if isinstance(key, ast.Constant) and key.value == "status"]
    assert status_values
    assert all(not isinstance(value, ast.Name) or value.id != "status" for value in status_values)
