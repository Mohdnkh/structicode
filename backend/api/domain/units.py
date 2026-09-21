"""Authoritative conversions for the canonical N, mm, MPa unit system."""

from enum import StrEnum
from math import isfinite


class Dimension(StrEnum):
    LENGTH = "length"
    FORCE = "force"
    STRESS = "stress"
    MOMENT = "moment"
    LINE_LOAD = "line_load"
    AREA_LOAD = "area_load"
    AREA = "area"
    SECTION_MODULUS = "section_modulus"
    INERTIA = "inertia"
    ROTATION = "rotation"


# Each factor converts one unit to that dimension's canonical unit.
UNIT_FACTORS: dict[Dimension, dict[str, float]] = {
    Dimension.LENGTH: {"mm": 1, "cm": 10, "m": 1000},
    Dimension.FORCE: {"N": 1, "kN": 1000},
    Dimension.STRESS: {"MPa": 1, "GPa": 1000, "kN/m2": 0.001},
    Dimension.MOMENT: {"N*mm": 1, "kN*m": 1_000_000},
    Dimension.LINE_LOAD: {"N/mm": 1, "kN/m": 1},
    Dimension.AREA_LOAD: {"N/mm2": 1, "kN/m2": 0.001},
    Dimension.AREA: {"mm2": 1, "cm2": 100, "m2": 1_000_000},
    Dimension.SECTION_MODULUS: {"mm3": 1, "cm3": 1000},
    Dimension.INERTIA: {"mm4": 1, "cm4": 10_000, "m4": 1_000_000_000_000},
    Dimension.ROTATION: {"rad": 1},
}

CANONICAL_UNITS: dict[Dimension, str] = {
    dimension: next(iter(factors)) for dimension, factors in UNIT_FACTORS.items()
}


def convert(value: float, dimension: Dimension, source: str, target: str) -> float:
    """Convert a finite number within one dimension; reject unknown units."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError("Quantity must be a finite number")
    try:
        factors = UNIT_FACTORS[Dimension(dimension)]
        converted = float(value) * factors[source] / factors[target]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Unsupported {dimension} conversion: {source} to {target}") from exc
    if not isfinite(converted):
        raise ValueError("Converted quantity must be finite")
    return converted


def to_canonical(value: float, dimension: Dimension, source: str) -> float:
    return convert(value, dimension, source, CANONICAL_UNITS[Dimension(dimension)])


def from_canonical(value: float, dimension: Dimension, target: str) -> float:
    return convert(value, dimension, CANONICAL_UNITS[Dimension(dimension)], target)
