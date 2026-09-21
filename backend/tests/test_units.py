import math

import pytest
from pydantic import ValidationError

from backend.api.domain.schemas import BeamInput, SectionInput
from backend.api.domain.units import Dimension as D, convert, from_canonical, to_canonical


@pytest.mark.parametrize("dimension,source,target,expected", [
    (D.LENGTH, "m", "mm", 1000),
    (D.LENGTH, "cm", "mm", 10),
    (D.FORCE, "kN", "N", 1000),
    (D.MOMENT, "kN*m", "N*mm", 1_000_000),
    (D.LINE_LOAD, "kN/m", "N/mm", 1),
    (D.AREA_LOAD, "kN/m2", "N/mm2", 0.001),
    (D.AREA, "cm2", "mm2", 100),
    (D.SECTION_MODULUS, "cm3", "mm3", 1000),
    (D.INERTIA, "cm4", "mm4", 10_000),
    (D.STRESS, "GPa", "MPa", 1000),
])
def test_required_conversion_identity(dimension, source, target, expected):
    assert convert(1, dimension, source, target) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("dimension,source", [
    (D.LENGTH, "m"), (D.FORCE, "kN"), (D.MOMENT, "kN*m"),
    (D.AREA_LOAD, "kN/m2"), (D.STRESS, "GPa"),
])
def test_conversion_round_trip(dimension, source):
    original = 12.3456789
    assert from_canonical(to_canonical(original, dimension, source), dimension, source) == pytest.approx(original, rel=1e-12)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, True])
def test_invalid_number_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        convert(value, D.LENGTH, "m", "mm")


def test_conversion_overflow_rejected():
    with pytest.raises(ValueError, match="Converted quantity must be finite"):
        convert(1e308, D.LENGTH, "m", "mm")


def test_unsupported_or_cross_dimension_conversion_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        convert(1, D.LENGTH, "ft", "mm")
    with pytest.raises(ValueError, match="Unsupported"):
        convert(1, D.FORCE, "m", "N")


def test_negative_geometry_and_inertia_rejected():
    beam = dict(kind="beam", width_cm=-30, depth_cm=60, span_m=5, fc_mpa=25,
                fy_mpa=420, bar_count=4, bar_diameter_mm=16)
    with pytest.raises(ValidationError):
        BeamInput.model_validate(beam)
    section = dict(id="S1", name="rect", width_m=0.3, depth_m=0.6,
                   cover_m=0.04, inertia_mm4=-1)
    with pytest.raises(ValidationError):
        SectionInput.model_validate(section)
