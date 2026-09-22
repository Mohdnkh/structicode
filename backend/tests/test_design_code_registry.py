"""Capability truth, compatibility, and API contract regressions for P6."""

from fastapi.testclient import TestClient
import pytest

from backend.api.domain.design_code_registry import (
    Capability, CapabilityStatus, CombinationProfile, FamilyCapability,
    MetadataConfidence, REGISTRY, StandardMetadata, VerifiedEvidence,
    get_element_capability, get_family, legacy_name, list_families,
    supports_legacy_element, supports_legacy_structure, validate_registry,
)
from backend.api.domain.identifiers import DesignCode, ElementId
from backend.api.engine.code_router import HANDLERS, get_code_handler
from backend.api.engine.load_combination import generate_combinations
from backend.api.engine.seismic_router import get_seismic_handler
from backend.api.main import app
from backend.tests.test_api_contracts import ELEMENT_INPUTS


CLIENT = TestClient(app)
CONCRETE = {ElementId.BEAM, ElementId.COLUMN, ElementId.SLAB,
            ElementId.FOOTING, ElementId.STAIRCASE}
STEEL = {ElementId.STEEL_BEAM, ElementId.STEEL_COLUMN}
MIXED = set(DesignCode) - {DesignCode.IS, DesignCode.STEEL}


def test_registry_has_one_entry_per_stable_family_in_deterministic_order():
    assert [entry.family_id for entry in REGISTRY] == list(DesignCode)
    assert len({entry.family_id for entry in REGISTRY}) == 12
    assert list_families() == REGISTRY
    validate_registry(REGISTRY, HANDLERS)


@pytest.mark.parametrize("family", list(DesignCode))
def test_every_family_has_complete_truthful_element_matrix(family):
    entry = get_family(family)
    assert entry is not None
    assert {item.element_id for item in entry.element_capabilities} == set(ElementId)
    expected = STEEL if family == DesignCode.STEEL else (
        CONCRETE if family == DesignCode.IS else CONCRETE | STEEL
    )
    for element in ElementId:
        capability = get_element_capability(family, element)
        assert supports_legacy_element(family, element) == (element in expected)
        assert capability.status == (
            CapabilityStatus.LEGACY_UNVERIFIED if element in expected
            else CapabilityStatus.NOT_IMPLEMENTED
        )
        assert capability.v1_route == (element in expected)
        assert capability.evidence is None


@pytest.mark.parametrize("family", list(DesignCode))
def test_structure_combination_and_seismic_are_distinct(family):
    entry = get_family(family)
    structure = family != DesignCode.STEEL
    assert supports_legacy_structure(family) == structure
    assert entry.structure_analysis.status == (
        CapabilityStatus.ENGINEERING_REVIEW_REQUIRED if structure
        else CapabilityStatus.NOT_IMPLEMENTED
    )
    assert entry.structure_design.status == (
        CapabilityStatus.LEGACY_UNVERIFIED if structure
        else CapabilityStatus.NOT_IMPLEMENTED
    )
    assert entry.load_combination.status == (
        CapabilityStatus.LEGACY_UNVERIFIED if structure
        else CapabilityStatus.NOT_IMPLEMENTED
    )
    assert entry.seismic.status == (
        CapabilityStatus.LEGACY_UNVERIFIED if structure
        else CapabilityStatus.NOT_IMPLEMENTED
    )
    assert entry.seismic.v1_route is False
    if structure:
        assert entry.load_combination_profile == (
            CombinationProfile.ACI if family == DesignCode.ACI else
            CombinationProfile.BS if family == DesignCode.BS else
            CombinationProfile.EUROCODE if family == DesignCode.EUROCODE else
            CombinationProfile.GENERIC_DEAD_ONLY
        )
    else:
        assert entry.load_combination_profile is None


def test_no_current_design_capability_is_verified_or_has_authoritative_edition():
    for entry in REGISTRY:
        assert entry.standard_metadata.confidence != MetadataConfidence.AUTHORITATIVE
        assert entry.standard_metadata.standard_id is None
        assert entry.standard_metadata.edition is None
        assert all(item.capability.status != CapabilityStatus.VERIFIED
                   for item in entry.element_capabilities)
        assert entry.structure_design.status != CapabilityStatus.VERIFIED
        assert entry.load_combination.status != CapabilityStatus.VERIFIED
        assert entry.seismic.status != CapabilityStatus.VERIFIED
    assert get_family("aci").verification_targets[0].status == CapabilityStatus.SOURCE_BLOCKED
    assert get_family("steel").verification_targets[0].status == CapabilityStatus.SOURCE_BLOCKED


def test_legacy_claim_is_not_authoritative_edition_metadata():
    aci = get_family("aci")
    assert "ACI 318-19" in aci.standard_metadata.legacy_claims
    assert aci.standard_metadata.confidence == MetadataConfidence.LEGACY_CLAIM
    with pytest.raises(ValueError):
        StandardMetadata(confidence=MetadataConfidence.LEGACY_CLAIM,
                         legacy_claims=("legacy label",), standard_id="invented")
    with pytest.raises(ValueError):
        Capability(status=CapabilityStatus.VERIFIED, note="Unproven claim")
    with pytest.raises(ValueError):
        VerifiedEvidence(standard_id="unverified")


@pytest.mark.parametrize("family", list(DesignCode))
def test_registered_legacy_handler_resolves_and_normalizes(family):
    assert type(get_code_handler(family.value.upper())) is HANDLERS[family]
    assert type(get_code_handler(family.value.title())) is HANDLERS[family]
    assert legacy_name(family) == get_family(family).legacy_name
    assert get_family(family).legacy_handler_key == family
    assert get_family(family).legacy_handler_key in HANDLERS


def test_unknown_family_cannot_route():
    assert get_family("unknown") is None
    assert get_code_handler("unknown") is None
    assert supports_legacy_structure("unknown") is False
    assert supports_legacy_element("unknown", ElementId.BEAM) is False
    with pytest.raises(ValueError):
        legacy_name("unknown")


def test_registry_validation_rejects_duplicates_missing_and_handler_drift():
    with pytest.raises(ValueError, match="Duplicate"):
        validate_registry(REGISTRY + (REGISTRY[0],))
    with pytest.raises(ValueError, match="exactly"):
        validate_registry(REGISTRY[:-1])
    with pytest.raises(ValueError, match="handlers"):
        validate_registry(REGISTRY, {key: value for key, value in HANDLERS.items()
                                     if key != DesignCode.STEEL})
    with pytest.raises(ValueError, match="element dispatch"):
        validate_registry(REGISTRY, {**HANDLERS, DesignCode.STEEL: object})


@pytest.mark.parametrize("family", list(DesignCode))
def test_raw_seismic_route_and_combination_profile_match_registry(family):
    entry = get_family(family)
    handler = get_seismic_handler(entry.legacy_name)
    assert (handler is not None) == entry.seismic.legacy_route
    if entry.load_combination_profile is None:
        assert family == DesignCode.STEEL
        return
    combinations = generate_combinations(entry.legacy_name)
    expected_count = {
        CombinationProfile.ACI: 4,
        CombinationProfile.BS: 3,
        CombinationProfile.EUROCODE: 3,
        CombinationProfile.GENERIC_DEAD_ONLY: 1,
    }[entry.load_combination_profile]
    assert len(combinations) == expected_count


def test_typed_validation_rejects_unknown_status_element_and_contradictions():
    entry = REGISTRY[0].model_dump()
    with pytest.raises(ValueError):
        Capability.model_validate({"status": "SAFE", "note": "Invalid"})
    with pytest.raises(ValueError):
        Capability(status=CapabilityStatus.NOT_IMPLEMENTED, legacy_route=True,
                   note="Contradictory")
    with pytest.raises(ValueError):
        FamilyCapability.model_validate({**entry, "display_name": "  "})
    with pytest.raises(ValueError):
        FamilyCapability.model_validate({**entry, "family_id": "unknown"})
    invalid_element = dict(entry)
    invalid_element["element_capabilities"] = [
        {**item, "element_id": "unknown"} if index == 0 else item
        for index, item in enumerate(entry["element_capabilities"])
    ]
    with pytest.raises(ValueError):
        FamilyCapability.model_validate(invalid_element)
    duplicate_element = dict(entry)
    duplicate_element["element_capabilities"] = list(entry["element_capabilities"])
    duplicate_element["element_capabilities"][1] = duplicate_element["element_capabilities"][0]
    with pytest.raises(ValueError):
        FamilyCapability.model_validate(duplicate_element)


def test_list_api_is_typed_complete_stable_and_unverified():
    response = CLIENT.get("/api/v1/capabilities")
    assert response.status_code == 200, response.text
    families = response.json()["families"]
    assert [item["family_id"] for item in families] == [family.value for family in DesignCode]
    assert len({item["family_id"] for item in families}) == 12
    assert CLIENT.get("/api/v1/capabilities").json()["families"] == families
    for family in families:
        assert len(family["element_capabilities"]) == 7
        assert family["standard_metadata"]["standard_id"] is None
        assert family["standard_metadata"]["edition"] is None
        assert all(item["capability"]["status"] != "VERIFIED"
                   for item in family["element_capabilities"])
        assert family["structure_design"]["status"] != "VERIFIED"


@pytest.mark.parametrize("family", ["aci", "steel", "ACI"])
def test_detail_api_returns_typed_family(family):
    response = CLIENT.get(f"/api/v1/capabilities/{family}")
    assert response.status_code == 200, response.text
    assert response.json()["family_id"] == family.lower()


def test_unknown_detail_is_structured_404():
    response = CLIENT.get("/api/v1/capabilities/unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert response.json()["verification_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("family", list(DesignCode))
@pytest.mark.parametrize("element,input_data", ELEMENT_INPUTS)
def test_all_seven_v1_element_routes_match_registry(family, element, input_data):
    availability = supports_legacy_element(family, ElementId(element))
    response = CLIENT.post("/api/v1/analysis/element", json={
        "code_id": family.value, "input": input_data,
    })
    assert response.status_code == (200 if availability else 400), response.text
    assert response.json()["verification_status"] == (
        "UNVERIFIED" if availability else "NOT_IMPLEMENTED"
    )


def test_http_smoke_preserves_health_and_legacy_availability():
    assert CLIENT.get("/health").status_code == 200
    steel_beam = {
        "kind": "steel_beam", "section_type": "IPE", "section_size": "IPE100",
        "dimensions": {"depth_mm": 100, "width_mm": 55,
                       "flange_thickness_mm": 7.1, "web_thickness_mm": 4.1},
        "fy_mpa": 235, "span_mm": 5000,
        "uniform_load_kn_per_m": 5, "support_type": "simply_supported",
    }
    concrete_beam = {
        "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
        "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
        "bar_count": 4, "bar_diameter_mm": 16,
    }
    for code, data, status, verification in (
        ("aci", concrete_beam, 200, "UNVERIFIED"),
        ("aci", steel_beam, 200, "UNVERIFIED"),
        ("is", steel_beam, 400, "NOT_IMPLEMENTED"),
        ("steel", concrete_beam, 400, "NOT_IMPLEMENTED"),
    ):
        response = CLIENT.post("/api/v1/analysis/element", json={"code_id": code, "input": data})
        assert response.status_code == status, response.text
        assert response.json()["verification_status"] == verification
