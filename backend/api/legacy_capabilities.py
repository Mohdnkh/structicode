"""Temporary v1 routing availability for existing legacy software paths.

This map does not describe design-code editions or engineering verification.
"""

from .domain.identifiers import DesignCode, ElementId


CONCRETE_ELEMENTS = frozenset({
    ElementId.BEAM, ElementId.COLUMN, ElementId.SLAB,
    ElementId.FOOTING, ElementId.STAIRCASE,
})
STEEL_ELEMENTS = frozenset({ElementId.STEEL_BEAM, ElementId.STEEL_COLUMN})
MIXED_FAMILIES = frozenset({
    DesignCode.ACI, DesignCode.BS, DesignCode.EUROCODE, DesignCode.AS,
    DesignCode.CSA, DesignCode.JORDAN, DesignCode.EGYPT,
    DesignCode.SAUDI, DesignCode.UAE, DesignCode.TURKEY,
})

LEGACY_ELEMENT_PATHS: dict[DesignCode, frozenset[ElementId]] = {
    **{family: CONCRETE_ELEMENTS | STEEL_ELEMENTS for family in MIXED_FAMILIES},
    DesignCode.IS: CONCRETE_ELEMENTS,
    DesignCode.STEEL: STEEL_ELEMENTS,
}
LEGACY_STRUCTURE_PATHS = MIXED_FAMILIES | {DesignCode.IS}


def supports_element(family: DesignCode, element: ElementId) -> bool:
    return element in LEGACY_ELEMENT_PATHS[family]


def supports_structure(family: DesignCode) -> bool:
    return family in LEGACY_STRUCTURE_PATHS
