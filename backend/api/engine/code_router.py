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
from ..domain.identifiers import DesignCode, normalize_code_id


HANDLERS = {
    DesignCode.ACI: ACI,
    DesignCode.BS: BS,
    DesignCode.EUROCODE: Eurocode,
    DesignCode.AS: ASCode,
    DesignCode.CSA: CSA,
    DesignCode.IS: ISCode,
    DesignCode.JORDAN: JordanCode,
    DesignCode.EGYPT: EgyptianCode,
    DesignCode.SAUDI: SaudiCode,
    DesignCode.UAE: UAECode,
    DesignCode.TURKEY: TurkishCode,
    DesignCode.STEEL: SteelCode,
}


def get_code_handler(code_name: str):
    try:
        handler_type = HANDLERS[normalize_code_id(code_name)]
    except (KeyError, ValueError):
        return None
    return handler_type()
