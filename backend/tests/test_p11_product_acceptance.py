"""P11 acceptance checks that keep release documentation aligned with P6 truth."""
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.domain.design_code_registry import (
    CapabilityStatus,
    DesignCode,
    ElementId,
    get_family,
    list_families,
)
from backend.api.main import app


ROOT = Path(__file__).resolve().parents[2]
MATRIX = (ROOT / "docs" / "PRODUCT_CAPABILITY_MATRIX.md").read_text(encoding="utf-8")
STATUS_PRESENTATION = {
    "LEGACY_UNVERIFIED": "LEGACY",
    "ENGINEERING_REVIEW_REQUIRED": "REVIEW",
    "NOT_IMPLEMENTED": "N/I",
    "SOURCE_BLOCKED": "SOURCE BLOCKED",
}


def matrix_rows() -> dict[str, list[str]]:
    rows = {}
    for line in MATRIX.splitlines():
        if not line.startswith("|") or line.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0].startswith("`") and cells[0].endswith("`"):
            rows[cells[0].strip("`")] = cells
    return rows


def aggregate_element_status(family, element_ids: set[ElementId]) -> str:
    statuses = {
        STATUS_PRESENTATION[item.capability.status.value]
        for item in family.element_capabilities
        if item.element_id in element_ids
    }
    return "+".join(sorted(statuses))


def target_cell(family) -> str:
    targets = [target.target_id for target in family.verification_targets]
    return ", ".join(f"`{target}`" for target in targets) if targets else "—"


def test_product_matrix_rows_match_each_registry_family():
    rows = matrix_rows()
    concrete = {ElementId.BEAM, ElementId.COLUMN, ElementId.SLAB, ElementId.FOOTING, ElementId.STAIRCASE}
    steel = {ElementId.STEEL_BEAM, ElementId.STEEL_COLUMN}
    assert set(rows) == {family.family_id.value for family in list_families()}
    for family in list_families():
        row = rows[family.family_id.value]
        assert row[1] == family.display_name
        assert row[2] == family.jurisdiction
        assert row[3] == family.standard_metadata.confidence.value
        assert row[4] == aggregate_element_status(family, concrete)
        assert row[5] == aggregate_element_status(family, steel)
        assert row[6] == STATUS_PRESENTATION[family.structure_analysis.status.value]
        assert row[7] == STATUS_PRESENTATION[family.structure_design.status.value]
        assert row[8] == STATUS_PRESENTATION[family.load_combination.status.value]
        expected_seismic = (
            "N/I" if family.seismic.status == CapabilityStatus.NOT_IMPLEMENTED
            else f"{STATUS_PRESENTATION[family.seismic.status.value]} (v1 false)"
        )
        assert row[9] == expected_seismic
        assert row[10] == target_cell(family)


def test_documentation_regression_has_no_known_stale_release_phrases():
    current_docs = [
        ROOT / "README.md", ROOT / "docs" / "LOCAL_DEVELOPMENT.md",
        ROOT / "docs" / "API_CONTRACTS.md", ROOT / "docs" / "RELEASE_SCOPE.md",
        ROOT / "docs" / "PRODUCT_CAPABILITY_MATRIX.md",
        ROOT / "docs" / "engineering" / "REPORT_TRACEABILITY.md",
        ROOT / "docs" / "engineering" / "ENGINEERING_WORKSPACE_UI.md",
        ROOT / "docs" / "engineering" / "ENTERPRISE_DATA_FOUNDATION.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in current_docs)
    for phrase in (
        "still lacks support and load editing controls",
        "existing report path remains a legacy compatibility route",
        "legacy shared-file implementation",
        "P9 owns those capabilities",
        "P10 must review",
    ):
        assert phrase.casefold() not in text.casefold()
    assert "`.\\.venv\\Scripts\\Activate.ps1`" in (ROOT / "README.md").read_text(encoding="utf-8")


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
