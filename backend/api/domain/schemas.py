"""Strict v1 transport and canonical domain schemas."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from .identifiers import DesignCode, LoadCase, SupportId, normalize_code_id, normalize_support_id


Finite = Annotated[float, Field(allow_inf_nan=False)]
Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]
PositiveCount = Annotated[int, Field(gt=0, strict=True)]
Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequestStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    NOT_EVALUATED = "NOT_EVALUATED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class CheckState(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EVALUATED = "NOT_EVALUATED"
    NOT_VERIFIED = "NOT_VERIFIED"


class LineLoads(StrictModel):
    dead: Finite = 0
    live: Finite = 0
    wind: Finite = 0
    snow: Finite = 0
    earthquake: Finite = 0


class AreaLoads(LineLoads):
    pass


class BeamInput(StrictModel):
    kind: Literal["beam"] = "beam"
    beam_type: Literal["normal", "inverted", "tee", "prestressed"] = "normal"
    width_cm: Positive
    depth_cm: Positive
    span_m: Positive
    cover_cm: Nonnegative = 3
    fc_mpa: Positive
    fy_mpa: Positive
    bar_count: PositiveCount
    bar_diameter_mm: Positive
    line_loads_kn_per_m: LineLoads = Field(default_factory=LineLoads)

    @model_validator(mode="after")
    def cover_inside_section(self) -> BeamInput:
        if self.cover_cm >= self.depth_cm:
            raise ValueError("cover_cm must be less than depth_cm")
        return self


class ColumnInput(StrictModel):
    kind: Literal["column"] = "column"
    column_type: Literal["rectangular", "circular", "composite"] = "rectangular"
    width_cm: Positive
    depth_cm: Positive
    height_m: Positive
    bar_diameter_mm: Positive
    bar_count: PositiveCount
    tie_spacing_cm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    axial_force_kn: Nonnegative
    moment_kn_m: Finite = 0


class SlabInput(StrictModel):
    kind: Literal["slab"] = "slab"
    slab_type: Literal["solid", "hollow", "waffle"] = "solid"
    thickness_cm: Positive
    length_m: Positive
    width_m: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    bar_diameter_mm: Positive
    top_bar_count: PositiveCount | None = None
    bottom_bar_count: PositiveCount
    block_height_cm: Positive | None = None
    rib_width_cm: Positive | None = None
    rib_spacing_cm: Positive | None = None
    area_loads_kn_per_m2: AreaLoads = Field(default_factory=AreaLoads)

    @model_validator(mode="after")
    def required_variant_geometry(self) -> SlabInput:
        if self.slab_type == "solid" and self.top_bar_count is None:
            raise ValueError("Solid slab requires top_bar_count")
        if self.slab_type == "hollow" and self.block_height_cm is None:
            raise ValueError("Hollow slab requires block_height_cm")
        if self.slab_type == "waffle" and (self.rib_width_cm is None or self.rib_spacing_cm is None):
            raise ValueError("Waffle slab requires rib_width_cm and rib_spacing_cm")
        return self


class FootingInput(StrictModel):
    kind: Literal["footing"] = "footing"
    footing_type: Literal["isolated", "combined", "strip", "raft"] = "isolated"
    length_m: Positive
    width_m: Positive
    thickness_cm: Positive
    axial_force_kn: Nonnegative
    bar_diameter_mm: Positive
    bar_spacing_cm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    soil_type: Literal["clay", "sand", "rock", "mixed"]


class StaircaseInput(StrictModel):
    kind: Literal["staircase"] = "staircase"
    stair_type: Literal["straight", "l-shaped", "spiral"] = "straight"
    width_cm: Positive
    riser_cm: Positive
    tread_cm: Positive
    steps: PositiveCount
    thickness_cm: Positive
    bar_diameter_mm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    area_loads_kn_per_m2: AreaLoads = Field(default_factory=AreaLoads)


class SteelDimensions(StrictModel):
    depth_mm: Positive
    width_mm: Positive
    flange_thickness_mm: Positive
    web_thickness_mm: Positive


class SteelBeamInput(StrictModel):
    kind: Literal["steel_beam"] = "steel_beam"
    section_type: Identifier
    section_size: Identifier
    dimensions: SteelDimensions
    fy_mpa: Positive
    span_mm: Positive
    uniform_load_kn_per_m: Finite
    support_type: Literal["simply_supported", "fixed", "cantilever", "continuous"] = "simply_supported"


class SteelColumnInput(StrictModel):
    kind: Literal["steel_column"] = "steel_column"
    section_type: Identifier
    section_size: Identifier
    dimensions: SteelDimensions
    fy_mpa: Positive
    axial_force_kn: Nonnegative
    length_mm: Positive
    k_factor: Positive = 1
    boundary_condition: Identifier = "Pinned-Pinned"


ElementInput = Annotated[
    Union[BeamInput, ColumnInput, SlabInput, FootingInput, StaircaseInput, SteelBeamInput, SteelColumnInput],
    Field(discriminator="kind"),
]


class SeismicInput(StrictModel):
    zone: Identifier
    soil: Identifier
    importance: Identifier
    system: Identifier


class ElementRequest(StrictModel):
    code_id: DesignCode
    input: ElementInput
    seismic: SeismicInput | None = None

    @field_validator("code_id", mode="before")
    @classmethod
    def normalize_code(cls, value: str | DesignCode) -> DesignCode:
        return normalize_code_id(value)


class MaterialInput(StrictModel):
    id: Identifier
    name: Identifier
    fc_mpa: Positive
    fy_mpa: Positive
    elastic_modulus_mpa: Positive


class SectionInput(StrictModel):
    id: Identifier
    name: Identifier
    shape: Literal["rectRC"] = "rectRC"
    width_m: Positive
    depth_m: Positive
    cover_m: Nonnegative
    area_m2: Positive | None = None
    inertia_mm4: Positive | None = None

    @model_validator(mode="after")
    def cover_inside_section(self) -> SectionInput:
        if self.cover_m >= self.depth_m:
            raise ValueError("cover_m must be less than depth_m")
        return self


class NodeInput(StrictModel):
    id: Identifier
    x_m: Finite
    y_m: Finite
    support_id: SupportId = SupportId.FREE

    @field_validator("support_id", mode="before")
    @classmethod
    def normalize_support(cls, value: str | SupportId) -> SupportId:
        return normalize_support_id(value)


class MemberLoadInput(StrictModel):
    case_id: LoadCase
    line_load_kn_per_m: Finite


class MemberInput(StrictModel):
    id: Identifier
    n1: Identifier
    n2: Identifier
    member_type: Literal["beam", "column"] = "beam"
    section_id: Identifier
    material_id: Identifier
    loads: list[MemberLoadInput] = Field(default_factory=list)


class SlabGeometryInput(StrictModel):
    id: Identifier
    x_m: Finite
    y_m: Finite
    width_m: Positive
    height_m: Positive
    thickness_m: Positive
    material_id: Identifier


class StructureRequest(StrictModel):
    code_id: DesignCode
    materials: list[MaterialInput] = Field(min_length=1)
    sections: list[SectionInput] = Field(min_length=1)
    nodes: list[NodeInput] = Field(min_length=2)
    members: list[MemberInput] = Field(min_length=1)
    slabs: list[SlabGeometryInput] = Field(default_factory=list)

    @field_validator("code_id", mode="before")
    @classmethod
    def normalize_code(cls, value: str | DesignCode) -> DesignCode:
        return normalize_code_id(value)

    @model_validator(mode="after")
    def validate_graph(self) -> StructureRequest:
        groups = (self.materials, self.sections, self.nodes, self.members, self.slabs)
        for group in groups:
            ids = [item.id for item in group]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate IDs are not allowed within a model collection")
        materials = {item.id for item in self.materials}
        sections = {item.id for item in self.sections}
        nodes = {item.id: item for item in self.nodes}
        if all(node.support_id == SupportId.FREE for node in self.nodes):
            raise ValueError("At least one node must have a support")
        for member in self.members:
            if member.n1 not in nodes or member.n2 not in nodes:
                raise ValueError(f"Member {member.id} references an unknown node")
            if member.section_id not in sections or member.material_id not in materials:
                raise ValueError(f"Member {member.id} references an unknown section or material")
            n1, n2 = nodes[member.n1], nodes[member.n2]
            if n1.x_m == n2.x_m and n1.y_m == n2.y_m:
                raise ValueError(f"Member {member.id} has zero length")
        if any(slab.material_id not in materials for slab in self.slabs):
            raise ValueError("Slab references an unknown material")
        return self


class CanonicalBeam(StrictModel):
    kind: Literal["beam"] = "beam"
    beam_type: str
    width_mm: Positive
    depth_mm: Positive
    span_mm: Positive
    cover_mm: Nonnegative
    fc_mpa: Positive
    fy_mpa: Positive
    bar_count: PositiveCount
    bar_diameter_mm: Positive
    line_loads_n_per_mm: LineLoads


class CanonicalColumn(StrictModel):
    kind: Literal["column"] = "column"
    column_type: str
    width_mm: Positive
    depth_mm: Positive
    height_mm: Positive
    bar_diameter_mm: Positive
    bar_count: PositiveCount
    tie_spacing_mm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    axial_force_n: Nonnegative
    moment_n_mm: Finite


class CanonicalSlab(StrictModel):
    kind: Literal["slab"] = "slab"
    slab_type: str
    thickness_mm: Positive
    length_mm: Positive
    width_mm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    bar_diameter_mm: Positive
    top_bar_count: PositiveCount | None = None
    bottom_bar_count: PositiveCount
    block_height_mm: Positive | None = None
    rib_width_mm: Positive | None = None
    rib_spacing_mm: Positive | None = None
    area_loads_n_per_mm2: AreaLoads


class CanonicalFooting(StrictModel):
    kind: Literal["footing"] = "footing"
    footing_type: str
    length_mm: Positive
    width_mm: Positive
    thickness_mm: Positive
    axial_force_n: Nonnegative
    bar_diameter_mm: Positive
    bar_spacing_mm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    soil_type: str


class CanonicalStaircase(StrictModel):
    kind: Literal["staircase"] = "staircase"
    stair_type: str
    width_mm: Positive
    riser_mm: Positive
    tread_mm: Positive
    steps: PositiveCount
    thickness_mm: Positive
    bar_diameter_mm: Positive
    fc_mpa: Positive
    fy_mpa: Positive
    area_loads_n_per_mm2: AreaLoads


class CanonicalSteelBeam(StrictModel):
    kind: Literal["steel_beam"] = "steel_beam"
    section_type: Identifier
    section_size: Identifier
    dimensions: SteelDimensions
    fy_mpa: Positive
    span_mm: Positive
    uniform_load_n_per_mm: Finite
    support_type: str


class CanonicalSteelColumn(StrictModel):
    kind: Literal["steel_column"] = "steel_column"
    section_type: Identifier
    section_size: Identifier
    dimensions: SteelDimensions
    fy_mpa: Positive
    axial_force_n: Nonnegative
    length_mm: Positive
    k_factor: Positive
    boundary_condition: Identifier


CanonicalElement = Annotated[
    Union[CanonicalBeam, CanonicalColumn, CanonicalSlab, CanonicalFooting,
          CanonicalStaircase, CanonicalSteelBeam, CanonicalSteelColumn],
    Field(discriminator="kind"),
]


class CanonicalMaterial(StrictModel):
    id: Identifier
    name: Identifier
    fc_mpa: Positive
    fy_mpa: Positive
    elastic_modulus_mpa: Positive


class CanonicalSection(StrictModel):
    id: Identifier
    name: Identifier
    shape: str
    width_mm: Positive
    depth_mm: Positive
    cover_mm: Nonnegative
    area_mm2: Positive | None = None
    inertia_mm4: Positive | None = None


class CanonicalNode(StrictModel):
    id: Identifier
    x_mm: Finite
    y_mm: Finite
    support_id: SupportId


class CanonicalMemberLoad(StrictModel):
    case_id: LoadCase
    line_load_n_per_mm: Finite


class CanonicalMember(StrictModel):
    id: Identifier
    n1: Identifier
    n2: Identifier
    member_type: str
    section_id: Identifier
    material_id: Identifier
    loads: list[CanonicalMemberLoad] = Field(default_factory=list)


class CanonicalSlabGeometry(StrictModel):
    id: Identifier
    x_mm: Finite
    y_mm: Finite
    width_mm: Positive
    height_mm: Positive
    thickness_mm: Positive
    material_id: Identifier


class CanonicalStructure(StrictModel):
    code_id: DesignCode
    materials: list[CanonicalMaterial]
    sections: list[CanonicalSection]
    nodes: list[CanonicalNode]
    members: list[CanonicalMember]
    slabs: list[CanonicalSlabGeometry] = Field(default_factory=list)


class LegacyElementOutput(StrictModel):
    result: dict[str, Any]


class ElementResponse(StrictModel):
    request_status: Literal[RequestStatus.SUCCESS] = RequestStatus.SUCCESS
    verification_status: Literal[VerificationStatus.UNVERIFIED] = VerificationStatus.UNVERIFIED
    code_id: DesignCode
    element_id: str
    canonical_input: CanonicalElement
    legacy_unverified: LegacyElementOutput
    warnings: list[str] = Field(default_factory=list)


class CanonicalDisplacement(StrictModel):
    ux_mm: Finite
    uy_mm: Finite
    rz_rad: Finite


class CanonicalMemberForces(StrictModel):
    nmax_n: Finite
    vmax_n: Finite
    mmax_n_mm: Finite


class CanonicalCombinationResult(StrictModel):
    name: str
    expression: str
    displacements: dict[str, CanonicalDisplacement]
    member_forces: dict[str, CanonicalMemberForces]


class LegacyStructureOutput(StrictModel):
    results: dict[str, Any]


class StructureResponse(StrictModel):
    request_status: Literal[RequestStatus.SUCCESS] = RequestStatus.SUCCESS
    verification_status: Literal[VerificationStatus.UNVERIFIED] = VerificationStatus.UNVERIFIED
    code_id: DesignCode
    canonical_input: CanonicalStructure
    combinations: dict[str, CanonicalCombinationResult]
    legacy_unverified: LegacyStructureOutput
    warnings: list[str] = Field(default_factory=list)


class ValidationDetail(StrictModel):
    field: str
    message: str


class ErrorBody(StrictModel):
    code: str
    message: str
    details: list[ValidationDetail] = Field(default_factory=list)


class ErrorEnvelope(StrictModel):
    request_status: Literal[RequestStatus.ERROR] = RequestStatus.ERROR
    verification_status: Literal[VerificationStatus.NOT_EVALUATED, VerificationStatus.NOT_IMPLEMENTED]
    error: ErrorBody
