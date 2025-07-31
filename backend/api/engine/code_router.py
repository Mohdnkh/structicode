import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from api.codes.aci import ACI
from api.codes.bs import BS
from api.codes.eurocode import Eurocode
from api.codes.as_code import ASCode
from api.codes.csa import CSA
from api.codes.is_code import ISCode
from api.codes.jordan import JordanCode
from api.codes.egypt import EgyptianCode
from api.codes.saudi import SaudiCode
from api.codes.uae import UAECode
from api.codes.turkey import TurkishCode
from api.codes.steel import SteelCode  # ✅ الكود الجديد اللي أضفناه

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
