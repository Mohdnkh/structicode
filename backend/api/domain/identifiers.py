"""Stable family, element, support, and load identifiers; no code editions implied."""

from enum import StrEnum


class DesignCode(StrEnum):
    ACI = "aci"
    BS = "bs"
    EUROCODE = "eurocode"
    AS = "as"
    CSA = "csa"
    IS = "is"
    JORDAN = "jordan"
    EGYPT = "egypt"
    SAUDI = "saudi"
    UAE = "uae"
    TURKEY = "turkey"
    STEEL = "steel"


def normalize_code_id(value: str | DesignCode) -> DesignCode:
    if isinstance(value, DesignCode):
        return value
    if not isinstance(value, str):
        raise ValueError("Design code must be a string")
    try:
        return DesignCode(value.strip().casefold())
    except ValueError as exc:
        raise ValueError("Unsupported design-code family") from exc


class ElementId(StrEnum):
    BEAM = "beam"
    COLUMN = "column"
    SLAB = "slab"
    FOOTING = "footing"
    STAIRCASE = "staircase"
    STEEL_BEAM = "steel_beam"
    STEEL_COLUMN = "steel_column"


class LoadCase(StrEnum):
    DEAD = "dead"
    LIVE = "live"
    WIND = "wind"
    SNOW = "snow"
    EARTHQUAKE = "earthquake"


LEGACY_LOAD_IDS = {
    LoadCase.DEAD: "D", LoadCase.LIVE: "L", LoadCase.WIND: "W",
    LoadCase.SNOW: "S", LoadCase.EARTHQUAKE: "E",
}


class SupportId(StrEnum):
    FREE = "free"
    PIN = "pin"
    ROLLER = "roller"
    FIXED = "fixed"


def normalize_support_id(value: str | SupportId) -> SupportId:
    if isinstance(value, SupportId):
        return value
    if not isinstance(value, str):
        raise ValueError("Support must be a string")
    value = value.strip().casefold()
    return SupportId.FIXED if value == "fix" else SupportId(value)
