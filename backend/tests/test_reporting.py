"""P7 traceability, ownership, hashing, storage, and report safety regressions."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import re
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from pydantic import ValidationError

from backend.api.main import app
from backend.api.reporting.models import (
    EngineMetadata, RequestStatus, VerificationStatus, build_analysis_run,
    canonical_json_bytes, hash_canonical,
)
from backend.api.reporting.pdf import render_report_bytes
from backend.api.reporting.run_store import InMemoryAnalysisRunStore, RUN_STORE


CLIENT = TestClient(app)
ELEMENT = {
    "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
    "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
    "bar_count": 4, "bar_diameter_mm": 16,
}
STEEL = {
    "kind": "steel_beam", "section_type": "IPE", "section_size": "IPE100",
    "dimensions": {"depth_mm": 100, "width_mm": 55,
                   "flange_thickness_mm": 7.1, "web_thickness_mm": 4.1},
    "fy_mpa": 235, "span_mm": 5000,
    "uniform_load_kn_per_m": 5, "support_type": "simply_supported",
}
STRUCTURE = {
    "code_id": "aci",
    "materials": [{"id": "M1", "name": "C25", "fc_mpa": 25, "fy_mpa": 420,
                   "elastic_modulus_mpa": 25000}],
    "sections": [{"id": "S1", "name": "Rect", "shape": "rectRC", "width_m": 0.3,
                  "depth_m": 0.6, "cover_m": 0.04}],
    "nodes": [{"id": "N1", "x_m": 0, "y_m": 0, "support_id": "fixed"},
              {"id": "N2", "x_m": 5, "y_m": 0, "support_id": "free"}],
    "members": [{"id": "B1", "n1": "N1", "n2": "N2", "member_type": "beam",
                 "section_id": "S1", "material_id": "M1",
                 "loads": [{"case_id": "dead", "line_load_kn_per_m": 5}]}],
    "slabs": [],
}


def synthetic_run(input_value=1, result_value=2):
    return build_analysis_run(
        analysis_kind="element", code_family_id="aci", element_id="beam",
        request_status=RequestStatus.SUCCESS, verification_status=VerificationStatus.UNVERIFIED,
        canonical_input_snapshot={"width_mm": input_value},
        canonical_result_snapshot={"demand_n_mm": result_value},
        legacy_unverified_snapshot={"result": {"legacy_status": "safe"}},
        warnings=("Legacy result requires review.",),
        capability_snapshot={"display_name": "ACI family", "jurisdiction": "United States",
                             "standard_metadata": {"confidence": "LEGACY_CLAIM", "legacy_claims": ["ACI 318-19"]},
                             "structure_analysis": {"status": "ENGINEERING_REVIEW_REQUIRED"},
                             "structure_design": {"status": "LEGACY_UNVERIFIED"},
                             "load_combination": {"status": "LEGACY_UNVERIFIED"},
                             "seismic": {"status": "LEGACY_UNVERIFIED"},
                             "warnings": [], "verification_targets": [],
                             "relevant_element_capability": {"status": "LEGACY_UNVERIFIED"}},
        engine_metadata=EngineMetadata(engine_id="test", engine_version="1",
                                       engineering_status="LEGACY_UNVERIFIED"),
    )


def analyze_element(code="aci", element=ELEMENT):
    response = CLIENT.post("/api/v1/analysis/element", json={"code_id": code, "input": element})
    assert response.status_code == 200, response.text
    return response.json()


def test_hashes_are_deterministic_and_have_documented_boundaries():
    one = synthetic_run()
    two = synthetic_run()
    assert canonical_json_bytes({"b": 2, "a": 1}) == canonical_json_bytes({"a": 1, "b": 2})
    assert hash_canonical({"a": [1, 2]}) == hash_canonical({"a": [1, 2]})
    assert one.input_hash_sha256 == two.input_hash_sha256
    assert one.result_hash_sha256 == two.result_hash_sha256
    assert one.record_hash_sha256 == two.record_hash_sha256
    assert one.run_id != two.run_id
    changed_input = synthetic_run(input_value=3)
    changed_result = synthetic_run(result_value=4)
    assert changed_input.input_hash_sha256 != one.input_hash_sha256
    assert changed_input.record_hash_sha256 != one.record_hash_sha256
    assert changed_result.result_hash_sha256 != one.result_hash_sha256
    assert changed_result.record_hash_sha256 != one.record_hash_sha256


def test_store_is_bounded_fifo_thread_safe_and_defensive():
    store = InMemoryAnalysisRunStore(max_records=2)
    first, second, third = synthetic_run(1), synthetic_run(2), synthetic_run(3)
    store.put(first); store.put(second); store.put(third)
    assert store.get(first.run_id) is None
    assert store.get(second.run_id) is not None and store.get(third.run_id) is not None
    returned = store.get(second.run_id)
    with pytest.raises(ValidationError):
        returned.run_id = "changed"
    returned.canonical_input_snapshot["width_mm"] = 999
    assert store.get(second.run_id).canonical_input_snapshot["width_mm"] == 2


def test_element_response_creates_server_owned_immutable_snapshot_and_report():
    response = analyze_element()
    assert response["verification_status"] == "UNVERIFIED"
    run_id = response["analysis_run_id"]
    assert run_id and run_id != "pending"
    caller_copy = deepcopy(response)
    caller_copy["canonical_input"]["width_mm"] = 999999
    caller_copy["legacy_unverified"]["result"] = {"verification_status": "VERIFIED", "status": "safe"}
    run = CLIENT.get(f"/api/v1/analysis-runs/{run_id}")
    assert run.status_code == 200, run.text
    stored = run.json()
    assert stored["canonical_input_snapshot"]["width_mm"] == 300
    assert stored["verification_status"] == "UNVERIFIED"
    assert stored["capability_snapshot"]["relevant_element_capability"]["status"] == "LEGACY_UNVERIFIED"
    pdf = CLIENT.get(f"/api/v1/reports/{run_id}.pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.headers["x-analysis-run-id"] == run_id
    assert pdf.headers["x-report-schema-version"] == "structicode_report_v1"
    assert pdf.content.startswith(b"%PDF")


def test_trusted_report_has_no_client_result_registration_endpoint():
    assert not any(route.path == "/api/v1/analysis-runs" and "POST" in route.methods
                   for route in app.routes)
    forged = CLIENT.post("/api/v1/analysis-runs", json={
        "verification_status": "VERIFIED", "status": "safe", "result": {"safe": True},
    })
    assert forged.status_code == 405
    assert forged.json()["verification_status"] == "NOT_EVALUATED"


def test_unknown_runs_have_structured_404_for_lookup_and_pdf():
    run_id = str(uuid4())
    for path in (f"/api/v1/analysis-runs/{run_id}", f"/api/v1/reports/{run_id}.pdf"):
        response = CLIENT.get(path)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"
        assert response.json()["verification_status"] == "NOT_EVALUATED"


def test_steel_run_keeps_p5_unverified_and_source_blocked_metadata():
    response = analyze_element("steel", {**STEEL, "uniform_load_kn_per_m": 0.001})
    stored = CLIENT.get(f"/api/v1/analysis-runs/{response['analysis_run_id']}").json()
    assert stored["verification_status"] == "UNVERIFIED"
    assert stored["capability_snapshot"]["relevant_element_capability"]["status"] == "LEGACY_UNVERIFIED"
    assert {item["target_id"] for item in stored["capability_snapshot"]["verification_targets"]} == {"aisc_360_22"}
    legacy = stored["legacy_unverified_snapshot"]["result"]
    assert legacy.get("result", legacy)["legacy_status"] == "safe"
    pdf = CLIENT.get(f"/api/v1/reports/{response['analysis_run_id']}.pdf")
    assert not re.search(rb"(?<![A-Z_])SAFE(?![A-Z_])", pdf.content)
    assert not re.search(rb"(?<![A-Z_])VERIFIED(?![A-Z_])", pdf.content)


def test_structure_run_separates_p3_mechanics_from_legacy_design():
    response = CLIENT.post("/api/v1/analysis/structure", json=STRUCTURE)
    assert response.status_code == 200, response.text
    run = CLIENT.get(f"/api/v1/analysis-runs/{response.json()['analysis_run_id']}")
    assert run.status_code == 200
    capability = run.json()["capability_snapshot"]
    assert capability["structure_analysis"]["status"] == "ENGINEERING_REVIEW_REQUIRED"
    assert capability["structure_design"]["status"] == "LEGACY_UNVERIFIED"
    assert capability["load_combination"]["status"] == "LEGACY_UNVERIFIED"
    assert run.json()["verification_status"] == "UNVERIFIED"
    pdf = CLIENT.get(f"/api/v1/reports/{response.json()['analysis_run_id']}.pdf")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")


def test_structure_snapshot_preserves_p4_not_evaluated_design_boundary():
    response = CLIENT.post("/api/v1/analysis/structure", json=STRUCTURE)
    assert response.status_code == 200, response.text
    run = CLIENT.get(f"/api/v1/analysis-runs/{response.json()['analysis_run_id']}").json()
    design = next(iter(run["legacy_unverified_snapshot"]["results"].values()))["design"]["B1"]
    assert design["As_provided"] is None
    assert design["Flexure_Check"] == "NOT_EVALUATED"
    assert design["Overall_Check"] == "NOT_EVALUATED"
    report = CLIENT.get(f"/api/v1/reports/{response.json()['analysis_run_id']}.pdf")
    assert report.status_code == 200 and b"SAFE" not in report.content


def test_concurrent_reports_are_isolated_by_run_snapshot():
    first = analyze_element("aci", {**ELEMENT, "width_cm": 30})
    second = analyze_element("aci", {**ELEMENT, "width_cm": 40})
    ids = [first["analysis_run_id"], second["analysis_run_id"]]
    with ThreadPoolExecutor(max_workers=2) as executor:
        reports = list(executor.map(lambda run_id: CLIENT.get(f"/api/v1/reports/{run_id}.pdf"), ids))
    assert all(report.status_code == 200 and report.content.startswith(b"%PDF") for report in reports)
    first_record = RUN_STORE.get(ids[0])
    second_record = RUN_STORE.get(ids[1])
    assert first_record.canonical_input_snapshot["width_mm"] == 300
    assert second_record.canonical_input_snapshot["width_mm"] == 400
    assert first_record.record_hash_sha256 != second_record.record_hash_sha256


def test_legacy_pdf_remains_explicitly_client_supplied_unverified(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    response = CLIENT.post("/generate-pdf", json={
        "data": {"code": "ACI", "element": "steel_beam"},
        "result": {"verification_status": "VERIFIED", "status": "safe"},
    })
    assert response.status_code == 200
    assert response.headers["x-structicode-report-status"] == "LEGACY_CLIENT_SUPPLIED_UNVERIFIED"
    assert response.headers["content-type"] == "application/pdf"


def test_renderer_handles_unicode_and_long_untrusted_identifiers():
    run = synthetic_run()
    run = run.model_copy(update={"canonical_input_snapshot": {
        "member_id": "M" * 500 + " Ω", "name": "unsafe <markup> 你好",
    }})
    pdf = render_report_bytes(run)
    assert pdf.startswith(b"%PDF") and len(pdf) > 1000
