"""Temporary conversions between canonical models and unverified legacy engines.

The conversions here are compatibility boundaries. No structural formula belongs here.
"""

from .design_code_registry import legacy_name
from .identifiers import DesignCode, LEGACY_LOAD_IDS, SupportId
from .schemas import (
    AreaLoads, BeamInput, CanonicalBeam, CanonicalColumn, CanonicalElement,
    CanonicalFooting, CanonicalMaterial, CanonicalMember, CanonicalMemberLoad,
    CanonicalNode, CanonicalSection, CanonicalSlab, CanonicalSlabGeometry,
    CanonicalStaircase, CanonicalSteelBeam, CanonicalSteelColumn,
    CanonicalStructure, ColumnInput, ElementInput, FootingInput, LineLoads,
    SlabInput, StaircaseInput, SteelBeamInput, SteelColumnInput, StructureRequest,
)
from .units import Dimension as D, from_canonical, to_canonical


def _loads_to_canonical(loads: LineLoads | AreaLoads, dimension: D, source: str):
    cls = AreaLoads if dimension == D.AREA_LOAD else LineLoads
    return cls(**{
        key: to_canonical(value, dimension, source)
        for key, value in loads.model_dump().items()
    })


def _loads_from_canonical(loads: LineLoads | AreaLoads, dimension: D, target: str) -> dict:
    return {
        key: from_canonical(value, dimension, target)
        for key, value in loads.model_dump().items()
    }


def normalize_element(value: ElementInput) -> CanonicalElement:
    if isinstance(value, BeamInput):
        return CanonicalBeam(
            beam_type=value.beam_type, width_mm=to_canonical(value.width_cm, D.LENGTH, "cm"),
            depth_mm=to_canonical(value.depth_cm, D.LENGTH, "cm"),
            span_mm=to_canonical(value.span_m, D.LENGTH, "m"),
            cover_mm=to_canonical(value.cover_cm, D.LENGTH, "cm"),
            fc_mpa=value.fc_mpa, fy_mpa=value.fy_mpa,
            bar_count=value.bar_count, bar_diameter_mm=value.bar_diameter_mm,
            line_loads_n_per_mm=_loads_to_canonical(value.line_loads_kn_per_m, D.LINE_LOAD, "kN/m"),
        )
    if isinstance(value, ColumnInput):
        return CanonicalColumn(
            column_type=value.column_type,
            width_mm=to_canonical(value.width_cm, D.LENGTH, "cm"),
            depth_mm=to_canonical(value.depth_cm, D.LENGTH, "cm"),
            height_mm=to_canonical(value.height_m, D.LENGTH, "m"),
            bar_diameter_mm=value.bar_diameter_mm, bar_count=value.bar_count,
            tie_spacing_mm=to_canonical(value.tie_spacing_cm, D.LENGTH, "cm"),
            fc_mpa=value.fc_mpa, fy_mpa=value.fy_mpa,
            axial_force_n=to_canonical(value.axial_force_kn, D.FORCE, "kN"),
            moment_n_mm=to_canonical(value.moment_kn_m, D.MOMENT, "kN*m"),
        )
    if isinstance(value, SlabInput):
        return CanonicalSlab(
            slab_type=value.slab_type,
            thickness_mm=to_canonical(value.thickness_cm, D.LENGTH, "cm"),
            length_mm=to_canonical(value.length_m, D.LENGTH, "m"),
            width_mm=to_canonical(value.width_m, D.LENGTH, "m"),
            fc_mpa=value.fc_mpa, fy_mpa=value.fy_mpa,
            bar_diameter_mm=value.bar_diameter_mm,
            top_bar_count=value.top_bar_count, bottom_bar_count=value.bottom_bar_count,
            block_height_mm=(to_canonical(value.block_height_cm, D.LENGTH, "cm")
                             if value.block_height_cm is not None else None),
            rib_width_mm=(to_canonical(value.rib_width_cm, D.LENGTH, "cm")
                          if value.rib_width_cm is not None else None),
            rib_spacing_mm=(to_canonical(value.rib_spacing_cm, D.LENGTH, "cm")
                            if value.rib_spacing_cm is not None else None),
            area_loads_n_per_mm2=_loads_to_canonical(value.area_loads_kn_per_m2, D.AREA_LOAD, "kN/m2"),
        )
    if isinstance(value, FootingInput):
        return CanonicalFooting(
            footing_type=value.footing_type,
            length_mm=to_canonical(value.length_m, D.LENGTH, "m"),
            width_mm=to_canonical(value.width_m, D.LENGTH, "m"),
            thickness_mm=to_canonical(value.thickness_cm, D.LENGTH, "cm"),
            axial_force_n=to_canonical(value.axial_force_kn, D.FORCE, "kN"),
            bar_diameter_mm=value.bar_diameter_mm,
            bar_spacing_mm=to_canonical(value.bar_spacing_cm, D.LENGTH, "cm"),
            fc_mpa=value.fc_mpa, fy_mpa=value.fy_mpa, soil_type=value.soil_type,
        )
    if isinstance(value, StaircaseInput):
        return CanonicalStaircase(
            stair_type=value.stair_type,
            width_mm=to_canonical(value.width_cm, D.LENGTH, "cm"),
            riser_mm=to_canonical(value.riser_cm, D.LENGTH, "cm"),
            tread_mm=to_canonical(value.tread_cm, D.LENGTH, "cm"),
            steps=value.steps,
            thickness_mm=to_canonical(value.thickness_cm, D.LENGTH, "cm"),
            bar_diameter_mm=value.bar_diameter_mm,
            fc_mpa=value.fc_mpa, fy_mpa=value.fy_mpa,
            area_loads_n_per_mm2=_loads_to_canonical(value.area_loads_kn_per_m2, D.AREA_LOAD, "kN/m2"),
        )
    if isinstance(value, SteelBeamInput):
        return CanonicalSteelBeam(
            section_type=value.section_type, section_size=value.section_size,
            dimensions=value.dimensions, fy_mpa=value.fy_mpa, span_mm=value.span_mm,
            uniform_load_n_per_mm=to_canonical(value.uniform_load_kn_per_m, D.LINE_LOAD, "kN/m"),
            support_type=value.support_type,
        )
    if isinstance(value, SteelColumnInput):
        return CanonicalSteelColumn(
            section_type=value.section_type, section_size=value.section_size,
            dimensions=value.dimensions, fy_mpa=value.fy_mpa,
            axial_force_n=to_canonical(value.axial_force_kn, D.FORCE, "kN"),
            length_mm=value.length_mm, k_factor=value.k_factor,
            boundary_condition=value.boundary_condition,
        )
    raise TypeError("Unknown element input")


def element_to_legacy(value: CanonicalElement, code_id: DesignCode) -> dict:
    if isinstance(value, CanonicalBeam):
        return {
            "type": value.beam_type.title(), "width": from_canonical(value.width_mm, D.LENGTH, "cm"),
            "depth": from_canonical(value.depth_mm, D.LENGTH, "cm"),
            "length": from_canonical(value.span_mm, D.LENGTH, "m"),
            "cover": from_canonical(value.cover_mm, D.LENGTH, "cm"),
            "fc": value.fc_mpa, "fy": value.fy_mpa,
            "rebar": {"count": value.bar_count, "diameter": value.bar_diameter_mm},
            "loads": _loads_from_canonical(value.line_loads_n_per_mm, D.LINE_LOAD, "kN/m"),
        }
    if isinstance(value, CanonicalColumn):
        return {
            "type": value.column_type.title(),
            "geometry": {"b": from_canonical(value.width_mm, D.LENGTH, "cm"),
                         "h": from_canonical(value.depth_mm, D.LENGTH, "cm"),
                         "L": from_canonical(value.height_mm, D.LENGTH, "m")},
            "reinforcement": {"barDiameter": value.bar_diameter_mm, "barCount": value.bar_count,
                              "tieSpacing": from_canonical(value.tie_spacing_mm, D.LENGTH, "cm")},
            "materials": {"fc": value.fc_mpa, "fy": value.fy_mpa},
            "loads": {"axial": from_canonical(value.axial_force_n, D.FORCE, "kN"),
                      "moment": from_canonical(value.moment_n_mm, D.MOMENT, "kN*m")},
        }
    if isinstance(value, CanonicalSlab):
        data = {
            "type": value.slab_type,
            "thickness": from_canonical(value.thickness_mm, D.LENGTH, "cm"),
            "length": from_canonical(value.length_mm, D.LENGTH, "m"),
            "width": from_canonical(value.width_mm, D.LENGTH, "m"),
            "fc": value.fc_mpa, "fy": value.fy_mpa,
            "barDiameter": value.bar_diameter_mm,
            "bottomBarCount": value.bottom_bar_count,
            "loads": _loads_from_canonical(value.area_loads_n_per_mm2, D.AREA_LOAD, "kN/m2"),
            "code": legacy_name(code_id),
        }
        if value.slab_type == "solid":
            data["topBarCount"] = value.top_bar_count
        elif value.slab_type == "hollow":
            data["block"] = {"height": from_canonical(value.block_height_mm, D.LENGTH, "cm")}
        else:
            data["waffle"] = {
                "ribWidth": from_canonical(value.rib_width_mm, D.LENGTH, "cm"),
                "ribSpacing": from_canonical(value.rib_spacing_mm, D.LENGTH, "cm"),
            }
        return data
    if isinstance(value, CanonicalFooting):
        return {
            "type": value.footing_type.title(),
            "length": from_canonical(value.length_mm, D.LENGTH, "m"),
            "width": from_canonical(value.width_mm, D.LENGTH, "m"),
            "thickness": from_canonical(value.thickness_mm, D.LENGTH, "cm"),
            "columnLoad": from_canonical(value.axial_force_n, D.FORCE, "kN"),
            "rebarDiameter": value.bar_diameter_mm,
            "rebarSpacing": from_canonical(value.bar_spacing_mm, D.LENGTH, "cm"),
            "fc": value.fc_mpa, "fy": value.fy_mpa, "soilType": value.soil_type,
        }
    if isinstance(value, CanonicalStaircase):
        return {
            "type": value.stair_type.title(),
            "width": from_canonical(value.width_mm, D.LENGTH, "cm"),
            "riser": from_canonical(value.riser_mm, D.LENGTH, "cm"),
            "tread": from_canonical(value.tread_mm, D.LENGTH, "cm"),
            "steps": value.steps,
            "thickness": from_canonical(value.thickness_mm, D.LENGTH, "cm"),
            "rebar": value.bar_diameter_mm, "fc": value.fc_mpa, "fy": value.fy_mpa,
            "loads": _loads_from_canonical(value.area_loads_n_per_mm2, D.AREA_LOAD, "kN/m2"),
        }
    dimensions = {
        "depth": value.dimensions.depth_mm, "width": value.dimensions.width_mm,
        "flangeThickness": value.dimensions.flange_thickness_mm,
        "webThickness": value.dimensions.web_thickness_mm,
    }
    if isinstance(value, CanonicalSteelBeam):
        # The alternate SteelCode expects mm; the direct legacy beam engine expects m.
        span = value.span_mm if code_id == DesignCode.STEEL else from_canonical(value.span_mm, D.LENGTH, "m")
        support_names = {
            "simply_supported": "Simply Supported", "fixed": "Fixed",
            "cantilever": "Cantilever", "continuous": "Continuous",
        }
        return {
            "sectionType": value.section_type, "sectionSize": value.section_size,
            "dimensions": dimensions, "steelGrade": value.fy_mpa,
            "span": span,
            "uniformLoad": from_canonical(value.uniform_load_n_per_mm, D.LINE_LOAD, "kN/m"),
            "supportType": support_names[value.support_type],
        }
    if isinstance(value, CanonicalSteelColumn):
        return {
            "sectionType": value.section_type, "sectionSize": value.section_size,
            "dimensions": dimensions, "steelGrade": value.fy_mpa,
            "axialLoad": from_canonical(value.axial_force_n, D.FORCE, "kN"),
            "length": value.length_mm, "kFactor": value.k_factor,
            "boundaryCondition": value.boundary_condition,
        }
    raise TypeError("Unknown canonical element")


def normalize_structure(value: StructureRequest) -> CanonicalStructure:
    return CanonicalStructure(
        code_id=value.code_id,
        materials=[CanonicalMaterial(**material.model_dump()) for material in value.materials],
        sections=[CanonicalSection(
            id=section.id, name=section.name, shape=section.shape,
            width_mm=to_canonical(section.width_m, D.LENGTH, "m"),
            depth_mm=to_canonical(section.depth_m, D.LENGTH, "m"),
            cover_mm=to_canonical(section.cover_m, D.LENGTH, "m"),
            area_mm2=(to_canonical(section.area_m2, D.AREA, "m2")
                      if section.area_m2 is not None else None),
            inertia_mm4=section.inertia_mm4,
        ) for section in value.sections],
        nodes=[CanonicalNode(
            id=node.id, x_mm=to_canonical(node.x_m, D.LENGTH, "m"),
            y_mm=to_canonical(node.y_m, D.LENGTH, "m"), support_id=node.support_id,
        ) for node in value.nodes],
        members=[CanonicalMember(
            id=member.id, n1=member.n1, n2=member.n2,
            member_type=member.member_type, section_id=member.section_id,
            material_id=member.material_id,
            loads=[CanonicalMemberLoad(
                case_id=load.case_id,
                line_load_n_per_mm=to_canonical(load.line_load_kn_per_m, D.LINE_LOAD, "kN/m"),
            ) for load in member.loads],
        ) for member in value.members],
        slabs=[CanonicalSlabGeometry(
            id=slab.id, x_mm=to_canonical(slab.x_m, D.LENGTH, "m"),
            y_mm=to_canonical(slab.y_m, D.LENGTH, "m"),
            width_mm=to_canonical(slab.width_m, D.LENGTH, "m"),
            height_mm=to_canonical(slab.height_m, D.LENGTH, "m"),
            thickness_mm=to_canonical(slab.thickness_m, D.LENGTH, "m"),
            material_id=slab.material_id,
        ) for slab in value.slabs],
    )


def structure_to_legacy(value: CanonicalStructure) -> dict:
    """Give the old frame solver metre/kN geometry and kN/m2 modulus explicitly."""
    return {
        "code": legacy_name(value.code_id),
        "units": {"length": "m", "force": "kN", "modulus": "kN/m2"},
        "materials": [{
            "id": material.id, "name": material.name, "fc": material.fc_mpa,
            "fy": material.fy_mpa,
            "E": from_canonical(material.elastic_modulus_mpa, D.STRESS, "kN/m2"),
        } for material in value.materials],
        "sections": [{
            "id": section.id, "name": section.name, "shape": section.shape,
            "params": {
                "bw": from_canonical(section.width_mm, D.LENGTH, "m"),
                "h": from_canonical(section.depth_mm, D.LENGTH, "m"),
                "cover": from_canonical(section.cover_mm, D.LENGTH, "m"),
                **({"A": from_canonical(section.area_mm2, D.AREA, "m2")}
                   if section.area_mm2 is not None else {}),
            },
        } for section in value.sections],
        "nodes": [{
            "id": node.id, "x": from_canonical(node.x_mm, D.LENGTH, "m"),
            "y": from_canonical(node.y_mm, D.LENGTH, "m"),
            "support": "fix" if node.support_id == SupportId.FIXED else node.support_id.value,
        } for node in value.nodes],
        "members": [{
            "id": member.id, "n1": member.n1, "n2": member.n2,
            "type": member.member_type, "sectionId": member.section_id,
            "materialId": member.material_id,
            "loads": [{
                "type": LEGACY_LOAD_IDS[load.case_id],
                "w": from_canonical(load.line_load_n_per_mm, D.LINE_LOAD, "kN/m"),
            } for load in member.loads],
        } for member in value.members],
        "slabs": [{
            "id": slab.id, "x": from_canonical(slab.x_mm, D.LENGTH, "m"),
            "y": from_canonical(slab.y_mm, D.LENGTH, "m"),
            "w": from_canonical(slab.width_mm, D.LENGTH, "m"),
            "h": from_canonical(slab.height_mm, D.LENGTH, "m"),
            "t": from_canonical(slab.thickness_mm, D.LENGTH, "m"),
            "materialId": slab.material_id,
        } for slab in value.slabs],
        "loads": {"combinations": []},
    }
