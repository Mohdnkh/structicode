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
from ..codes.steel import SteelCode  # ✅ الكود الجديد اللي أضفناه

def get_code_handler(code_name: str):
    mapping = {
        "ACI": ACI(),
        "BS": BS(),
        "Eurocode": Eurocode(),
        "AS": ASCode(),
        "CSA": CSA(),
        "IS": ISCode(),
        "Jordan": JordanCode(),
        "Egypt": EgyptianCode(),
        "Saudi": SaudiCode(),
        "UAE": UAECode(),
        "Turkey": TurkishCode(),
        "Steel": SteelCode()  # ✅ الدعم الجديد لعناصر الفولاذ
    }
    return mapping.get(code_name)
