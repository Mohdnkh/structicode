"""Typed software-capability truth for stable design-code family identifiers.

Family names and legacy routes are compatibility metadata, not code compliance.
The registry deliberately contains no verified concrete or steel design module.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Mapping, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .identifiers import DesignCode, ElementId, normalize_code_id


class CapabilityStatus(StrEnum):
    VERIFIED = "VERIFIED"
    ENGINEERING_REVIEW_REQUIRED = "ENGINEERING_REVIEW_REQUIRED"
    LEGACY_UNVERIFIED = "LEGACY_UNVERIFIED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    SOURCE_BLOCKED = "SOURCE_BLOCKED"


class MaterialScope(StrEnum):
    CONCRETE = "CONCRETE"
    STEEL = "STEEL"


class MetadataConfidence(StrEnum):
    AUTHORITATIVE = "AUTHORITATIVE"
    LEGACY_CLAIM = "LEGACY_CLAIM"
    UNKNOWN = "UNKNOWN"


class CombinationProfile(StrEnum):
    ACI = "ACI"
    BS = "BS"
    EUROCODE = "EUROCODE"
    GENERIC_DEAD_ONLY = "GENERIC_DEAD_ONLY"


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class VerifiedEvidence(FrozenModel):
    """Evidence required before a future design capability can be VERIFIED."""

    standard_id: str
    standard_title: str
    edition: str
    jurisdiction: str
    material_scope: MaterialScope
    implemented_scope: tuple[str, ...] = Field(min_length=1)
    canonical_input_contract: str
    canonical_result_contract: str
    engine_id: str
    engine_version: str
    authoritative_references: tuple[str, ...] = Field(min_length=1)
    assumptions: tuple[str, ...]
    applicability_limits: tuple[str, ...]
    benchmark_evidence_ids: tuple[str, ...] = Field(min_length=1)
    unsupported_scope: tuple[str, ...]
    national_annex: str | None = None
    jurisdiction_variant: str | None = None
    local_adoption: str | None = None
    governing_edition: str | None = None

    @model_validator(mode="after")
    def nonblank_evidence(self) -> VerifiedEvidence:
        required = (
            self.standard_id, self.standard_title, self.edition, self.jurisdiction,
            self.canonical_input_contract, self.canonical_result_contract,
            self.engine_id, self.engine_version,
            *self.implemented_scope, *self.authoritative_references,
            *self.benchmark_evidence_ids,
        )
        if any(not value.strip() for value in required):
            raise ValueError("Verified evidence fields cannot be blank")
        return self


class VerifiedDesignModule(Protocol):
    """Future verified modules publish evidence and consume canonical contracts."""

    evidence: VerifiedEvidence

    def evaluate(self, canonical_input: Mapping[str, Any]) -> Mapping[str, Any]: ...


class Capability(FrozenModel):
    status: CapabilityStatus
    v1_route: bool = False
    legacy_route: bool = False
    note: str
    evidence: VerifiedEvidence | None = None

    @model_validator(mode="after")
    def consistent_state(self) -> Capability:
        if not self.note.strip():
            raise ValueError("Capability note cannot be blank")
        if self.status == CapabilityStatus.VERIFIED and self.evidence is None:
            raise ValueError("VERIFIED requires complete authoritative evidence")
        if self.status != CapabilityStatus.VERIFIED and self.evidence is not None:
            raise ValueError("Unverified capability cannot publish verified evidence")
        if self.status in (CapabilityStatus.NOT_IMPLEMENTED, CapabilityStatus.SOURCE_BLOCKED):
            if self.v1_route or self.legacy_route:
                raise ValueError("Unavailable capability cannot claim a runtime route")
        if self.status == CapabilityStatus.LEGACY_UNVERIFIED and not self.legacy_route:
            raise ValueError("Legacy capability requires a legacy runtime route")
        return self


class ElementCapability(FrozenModel):
    element_id: ElementId
    capability: Capability


class StandardMetadata(FrozenModel):
    confidence: MetadataConfidence
    standard_id: str | None = None
    edition: str | None = None
    legacy_claims: tuple[str, ...] = ()
    national_annex: str | None = None
    jurisdiction_variant: str | None = None
    local_adoption: str | None = None
    governing_edition: str | None = None

    @model_validator(mode="after")
    def confidence_boundary(self) -> StandardMetadata:
        if self.confidence == MetadataConfidence.AUTHORITATIVE:
            if not self.standard_id or not self.edition:
                raise ValueError("Authoritative metadata requires exact standard and edition")
        elif self.standard_id is not None or self.edition is not None:
            raise ValueError("Unverified metadata cannot expose an authoritative standard or edition")
        if self.confidence == MetadataConfidence.LEGACY_CLAIM and not self.legacy_claims:
            raise ValueError("Legacy claim confidence requires a recorded claim")
        if self.confidence == MetadataConfidence.UNKNOWN and self.legacy_claims:
            raise ValueError("Unknown metadata cannot contain standard claims")
        return self


class SourceBlockedTarget(FrozenModel):
    target_id: str
    material_scope: MaterialScope
    status: CapabilityStatus = CapabilityStatus.SOURCE_BLOCKED
    source_requirements: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def remains_source_blocked(self) -> SourceBlockedTarget:
        if self.status != CapabilityStatus.SOURCE_BLOCKED:
            raise ValueError("Future target must remain source blocked")
        return self


class FamilyCapability(FrozenModel):
    family_id: DesignCode
    display_name: str
    jurisdiction: str
    legacy_name: str
    legacy_handler_key: DesignCode
    material_scopes: tuple[MaterialScope, ...]
    element_capabilities: tuple[ElementCapability, ...]
    structure_analysis: Capability
    structure_design: Capability
    load_combination: Capability
    load_combination_profile: CombinationProfile | None
    seismic: Capability
    standard_metadata: StandardMetadata
    verification_targets: tuple[SourceBlockedTarget, ...] = ()
    source_requirements: tuple[str, ...] = Field(min_length=1)
    warnings: tuple[str, ...]
    notes: tuple[str, ...]

    @field_validator("display_name", "jurisdiction", "legacy_name")
    @classmethod
    def nonblank_label(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Family labels cannot be blank")
        return value

    @model_validator(mode="after")
    def family_consistency(self) -> FamilyCapability:
        if self.legacy_handler_key != self.family_id:
            raise ValueError("Legacy handler key must match the family identifier")
        element_ids = [item.element_id for item in self.element_capabilities]
        if len(element_ids) != len(set(element_ids)) or set(element_ids) != set(ElementId):
            raise ValueError("Each family must define each element exactly once")
        if not self.material_scopes or len(set(self.material_scopes)) != len(self.material_scopes):
            raise ValueError("Material scopes must be unique and nonempty")
        concrete = {ElementId.BEAM, ElementId.COLUMN, ElementId.SLAB,
                    ElementId.FOOTING, ElementId.STAIRCASE}
        steel = {ElementId.STEEL_BEAM, ElementId.STEEL_COLUMN}
        active = {item.element_id for item in self.element_capabilities if item.capability.legacy_route}
        if (active & concrete) and MaterialScope.CONCRETE not in self.material_scopes:
            raise ValueError("Concrete route requires concrete material scope")
        if (active & steel) and MaterialScope.STEEL not in self.material_scopes:
            raise ValueError("Steel route requires steel material scope")
        if self.structure_analysis.v1_route != self.structure_design.v1_route:
            raise ValueError("Structure analysis and design routes must agree")
        if self.structure_analysis.legacy_route != self.structure_design.legacy_route:
            raise ValueError("Structure analysis and design legacy routes must agree")
        if self.load_combination.v1_route != self.structure_analysis.v1_route:
            raise ValueError("Load combinations must follow structure routing")
        if (self.load_combination_profile is None) == self.load_combination.legacy_route:
            raise ValueError("Combination profile must exist exactly when a legacy route exists")
        if self.standard_metadata.confidence != MetadataConfidence.AUTHORITATIVE:
            capabilities = [*(item.capability for item in self.element_capabilities),
                            self.structure_analysis, self.structure_design,
                            self.load_combination, self.seismic]
            if any(item.status == CapabilityStatus.VERIFIED for item in capabilities):
                raise ValueError("Legacy standard metadata cannot support VERIFIED capability")
        return self


class CapabilityListResponse(FrozenModel):
    families: tuple[FamilyCapability, ...]


CONCRETE_ELEMENTS = frozenset({ElementId.BEAM, ElementId.COLUMN, ElementId.SLAB,
                               ElementId.FOOTING, ElementId.STAIRCASE})
STEEL_ELEMENTS = frozenset({ElementId.STEEL_BEAM, ElementId.STEEL_COLUMN})
ALL_ELEMENTS = CONCRETE_ELEMENTS | STEEL_ELEMENTS

ACI_TARGET = SourceBlockedTarget(
    target_id="aci_318_25", material_scope=MaterialScope.CONCRETE,
    source_requirements=("Authorized ACI CODE-318-25 SI provisions and applicable benchmarks",),
)
AISC_TARGET = SourceBlockedTarget(
    target_id="aisc_360_22", material_scope=MaterialScope.STEEL,
    source_requirements=("ANSI/AISC 360-22 provisions and applicable errata",
                         "Authoritative section properties with definitions and units",
                         "Independent published beam and column benchmark examples"),
)


def _family(
    family_id: DesignCode, display_name: str, jurisdiction: str, legacy_name: str,
    legacy_elements: frozenset[ElementId], structure_route: bool,
    legacy_claims: tuple[str, ...], combination_profile: CombinationProfile | None,
    verification_targets: tuple[SourceBlockedTarget, ...] = (),
) -> FamilyCapability:
    elements = tuple(ElementCapability(
        element_id=element,
        capability=Capability(
            status=(CapabilityStatus.LEGACY_UNVERIFIED if element in legacy_elements
                    else CapabilityStatus.NOT_IMPLEMENTED),
            v1_route=element in legacy_elements,
            legacy_route=element in legacy_elements,
            note=("Existing simplified legacy design path; no edition compliance established."
                  if element in legacy_elements else "No v1 compatibility path."),
        ),
    ) for element in ElementId)
    structure_analysis = Capability(
        status=(CapabilityStatus.ENGINEERING_REVIEW_REQUIRED if structure_route
                else CapabilityStatus.NOT_IMPLEMENTED),
        v1_route=structure_route, legacy_route=structure_route,
        note=("P3 linear-elastic 2D frame mechanics have bounded benchmarks; complete response remains unverified."
              if structure_route else "No structure-level compatibility route."),
    )
    structure_design = Capability(
        status=(CapabilityStatus.LEGACY_UNVERIFIED if structure_route
                else CapabilityStatus.NOT_IMPLEMENTED),
        v1_route=structure_route, legacy_route=structure_route,
        note=("Legacy structure design checks are not engineering-verified."
              if structure_route else "No structure-level design compatibility route."),
    )
    load_combination = Capability(
        status=(CapabilityStatus.LEGACY_UNVERIFIED if structure_route
                else CapabilityStatus.NOT_IMPLEMENTED),
        v1_route=structure_route, legacy_route=structure_route,
        note=("Parser mechanics were stabilized in P3; code-specific factors are not verified."
              if structure_route else "No structure-level combination route."),
    )
    seismic_route = family_id != DesignCode.STEEL
    seismic = Capability(
        status=(CapabilityStatus.LEGACY_UNVERIFIED if seismic_route
                else CapabilityStatus.NOT_IMPLEMENTED),
        v1_route=False, legacy_route=seismic_route,
        note=("Raw legacy seismic handler is a placeholder; v1 seismic is unavailable."
              if seismic_route else "No seismic handler or v1 seismic route."),
    )
    material_scopes = tuple(scope for scope, relevant in (
        (MaterialScope.CONCRETE, CONCRETE_ELEMENTS),
        (MaterialScope.STEEL, STEEL_ELEMENTS),
    ) if legacy_elements & relevant)
    metadata = StandardMetadata(
        confidence=(MetadataConfidence.LEGACY_CLAIM if legacy_claims
                    else MetadataConfidence.UNKNOWN),
        legacy_claims=legacy_claims,
    )
    warnings = ("Family presence does not establish design-code compliance or a verified edition.",
                "Legacy results require independent engineering review.")
    notes = ("Regional wrappers share simplified legacy formulas; labels are not independent validation.",)
    return FamilyCapability(
        family_id=family_id, display_name=display_name, jurisdiction=jurisdiction,
        legacy_name=legacy_name, legacy_handler_key=family_id,
        material_scopes=material_scopes, element_capabilities=elements,
        structure_analysis=structure_analysis, structure_design=structure_design,
        load_combination=load_combination, load_combination_profile=combination_profile,
        seismic=seismic, standard_metadata=metadata,
        verification_targets=verification_targets,
        source_requirements=(
            "Inspect the exact authoritative standard edition, provisions, and applicability limits.",
            "Obtain independently checked benchmarks before any VERIFIED design status.",
        ),
        warnings=warnings, notes=notes,
    )


REGISTRY: tuple[FamilyCapability, ...] = (
    _family(DesignCode.ACI, "ACI family", "United States", "ACI", ALL_ELEMENTS, True,
            ("ACI 318-19",), CombinationProfile.ACI, (ACI_TARGET,)),
    _family(DesignCode.BS, "British Standards family", "United Kingdom", "BS", ALL_ELEMENTS, True,
            ("BS 8110 (Concrete), BS 5950 (Steel)",), CombinationProfile.BS),
    _family(DesignCode.EUROCODE, "Eurocode family", "Europe; national annex unspecified", "Eurocode",
            ALL_ELEMENTS, True, ("EN 1992 (Concrete), EN 1993 (Steel)",), CombinationProfile.EUROCODE),
    _family(DesignCode.AS, "Australian Standards family", "Australia", "AS", ALL_ELEMENTS, True,
            ("AS 3600 (Concrete), AS 4100 (Steel)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.CSA, "Canadian Standards family", "Canada", "CSA", ALL_ELEMENTS, True,
            ("CSA A23.3 (Concrete), CSA S16 (Steel)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.IS, "Indian Standards family", "India", "IS", CONCRETE_ELEMENTS, True,
            ("IS 456",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.JORDAN, "Jordanian Code family", "Jordan", "Jordan", ALL_ELEMENTS, True,
            ("Latest (Based on ACI)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.EGYPT, "Egyptian Code family", "Egypt", "Egypt", ALL_ELEMENTS, True,
            ("ECP 203 (Concrete), ECP 205 (Steel)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.SAUDI, "Saudi Building Code family", "Saudi Arabia", "Saudi", ALL_ELEMENTS, True,
            ("SBC 304 (Concrete), SBC 301 (Loads), SBC 303 (Steel)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.UAE, "UAE Building Code family", "United Arab Emirates", "UAE", ALL_ELEMENTS, True,
            ("Latest UAEBC (Hybrid)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.TURKEY, "Turkish Code family", "Turkey", "Turkey", ALL_ELEMENTS, True,
            ("TS500 (Concrete), TS648 (Steel)",), CombinationProfile.GENERIC_DEAD_ONLY),
    _family(DesignCode.STEEL, "Generic steel legacy family", "Unspecified", "Steel", STEEL_ELEMENTS,
            False, (), None, (AISC_TARGET,)),
)


def validate_registry(
    entries: tuple[FamilyCapability, ...],
    handler_keys: Mapping[DesignCode, object] | None = None,
) -> None:
    ids = [entry.family_id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate design-code family ID")
    if set(ids) != set(DesignCode):
        raise ValueError("Registry must contain exactly the DesignCode families")
    if handler_keys is not None:
        keys = list(handler_keys)
        if len(keys) != len(set(keys)) or set(keys) != set(ids):
            raise ValueError("Legacy handlers and registry families must match exactly")
        for entry in entries:
            if any(item.capability.legacy_route for item in entry.element_capabilities) or (
                entry.structure_analysis.legacy_route
            ):
                if entry.legacy_handler_key not in handler_keys:
                    raise ValueError("Legacy route has no runtime handler")
                handler = handler_keys[entry.legacy_handler_key]
                if not callable(handler) or not callable(getattr(handler, "analyze", None)):
                    raise ValueError("Legacy handler must provide element dispatch")
                if entry.structure_analysis.legacy_route and not callable(
                    getattr(handler, "analyze_structure", None)
                ):
                    raise ValueError("Structure route requires a structure handler")


validate_registry(REGISTRY)
_BY_ID = {entry.family_id: entry for entry in REGISTRY}


def list_families() -> tuple[FamilyCapability, ...]:
    return REGISTRY


def get_family(value: str | DesignCode) -> FamilyCapability | None:
    try:
        return _BY_ID[normalize_code_id(value)]
    except (ValueError, KeyError):
        return None


def get_element_capability(family: str | DesignCode, element: ElementId) -> Capability | None:
    entry = get_family(family)
    if entry is None:
        return None
    return next(item.capability for item in entry.element_capabilities if item.element_id == element)


def supports_legacy_element(family: str | DesignCode, element: ElementId) -> bool:
    capability = get_element_capability(family, element)
    return capability is not None and capability.v1_route and capability.legacy_route


def supports_legacy_structure(family: str | DesignCode) -> bool:
    entry = get_family(family)
    return entry is not None and entry.structure_analysis.v1_route and entry.structure_design.legacy_route


def legacy_name(family: str | DesignCode) -> str:
    entry = get_family(family)
    if entry is None:
        raise ValueError("Unsupported design-code family")
    return entry.legacy_name
