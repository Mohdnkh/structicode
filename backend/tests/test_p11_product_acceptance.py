"""P11 acceptance checks that keep release documentation aligned with P6 truth."""
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.domain.design_code_registry import (
    CapabilityStatus,
    DesignCode,
    ElementId,
    MetadataConfidence,
    get_family,
    list_families,
)
from backend.api.main import app


ROOT = Path(__file__).resolve().parents[2]
MATRIX = (ROOT / "docs" / "PRODUCT_CAPABILITY_MATRIX.md").read_text(encoding="utf-8")


def test_product_matrix_lists_every_registry_family_and_truth_marker():
    for family in list_families():
        assert f"`{family.family_id.value}`" in MATRIX
        assert family.display_name in MATRIX
        assert family.jurisdiction in MATRIX
        assert family.standard_metadata.confidence.value in MATRIX
        assert family.structure_analysis.status.value.split("_")[0] in MATRIX or "REVIEW" in MATRIX
    assert "aci_318_25" in MATRIX
    assert "aisc_360_22" in MATRIX


def test_capability_api_matches_registry_and_release_expectations():
    response = TestClient(app).get("/api/v1/capabilities")
    assert response.status_code == 200
    payload = response.json()
    by_id = {item["family_id"]: item for item in payload["families"]}
    assert set(by_id) == {family.family_id.value for family in list_families()}
    for family in list_families():
        item = by_id[family.family_id.value]
        assert item["standard_metadata"]["confidence"] == family.standard_metadata.confidence.value
        assert item["structure_analysis"]["status"] == family.structure_analysis.status.value
        assert item["structure_design"]["status"] == family.structure_design.status.value
        assert item["load_combination"]["status"] == family.load_combination.status.value
        assert item["seismic"]["status"] == family.seismic.status.value
        assert item["seismic"]["v1_route"] is False


def test_representative_element_and_structure_boundaries_are_explicit():
    aci = get_family(DesignCode.ACI)
    india = get_family(DesignCode.IS)
    steel = get_family(DesignCode.STEEL)
    assert aci and india and steel
    assert aci.element_capabilities[0].capability.status == CapabilityStatus.LEGACY_UNVERIFIED
    assert aci.element_capabilities[-1].capability.status == CapabilityStatus.LEGACY_UNVERIFIED
    assert next(x for x in india.element_capabilities if x.element_id == ElementId.BEAM).capability.legacy_route
    assert next(x for x in india.element_capabilities if x.element_id == ElementId.STEEL_BEAM).capability.status == CapabilityStatus.NOT_IMPLEMENTED
    assert next(x for x in steel.element_capabilities if x.element_id == ElementId.STEEL_BEAM).capability.legacy_route
    assert steel.structure_analysis.status == CapabilityStatus.NOT_IMPLEMENTED
    assert all(not family.seismic.v1_route for family in list_families())


def test_release_scope_names_all_trust_states_without_promoting_legacy():
    scope = (ROOT / "docs" / "RELEASE_SCOPE.md").read_text(encoding="utf-8")
    for label in ("SUPPORTED RELEASE SCOPE", "LIMITED / ENGINEERING REVIEW REQUIRED",
                  "LEGACY / UNVERIFIED", "NOT IMPLEMENTED", "SOURCE BLOCKED"):
        assert label in scope
    assert "P4 and P5 remain `DEFERRED — SOURCE BLOCKED`" in scope
    assert "authoritative SAFE, UNSAFE, PASS, or VERIFIED" in scope
