"""Resolve legacy handlers from stable, case-insensitive family identifiers."""

from ..codes.aci import ACI
from ..codes.bs import BS
from ..codes.eurocode import Eurocode
from ..codes.as_code import ASCode
from ..codes.csa import CSA
from ..codes.is_code import ISCode
from ..codes.jordan import JordanCode
from ..codes.egypt import EgyptianCode
from ..codes.saudi import SaudiCode
from ..codes.uae import UAECode
from ..codes.turkey import TurkishCode
from ..codes.steel import SteelCode
from ..domain.design_code_registry import REGISTRY, get_family, validate_registry
from ..domain.identifiers import DesignCode


_HANDLER_ENTRIES = (
    (DesignCode.ACI, ACI),
    (DesignCode.BS, BS),
    (DesignCode.EUROCODE, Eurocode),
    (DesignCode.AS, ASCode),
    (DesignCode.CSA, CSA),
    (DesignCode.IS, ISCode),
    (DesignCode.JORDAN, JordanCode),
    (DesignCode.EGYPT, EgyptianCode),
    (DesignCode.SAUDI, SaudiCode),
    (DesignCode.UAE, UAECode),
    (DesignCode.TURKEY, TurkishCode),
    (DesignCode.STEEL, SteelCode),
)
if len(_HANDLER_ENTRIES) != len({key for key, _ in _HANDLER_ENTRIES}):
    raise ValueError("Duplicate legacy handler key")
HANDLERS = dict(_HANDLER_ENTRIES)
validate_registry(REGISTRY, HANDLERS)


def get_code_handler(code_name: str):
    family = get_family(code_name)
    if family is None:
        return None
    return HANDLERS[family.legacy_handler_key]()
