from ..codes_seismic import (
    JordanSeismic,
    SaudiSeismic,
    EgyptSeismic,
    EurocodeSeismic,
    UAESeismic,
    TurkeySeismic,
    ACISismic,
    BSSeismic,
    ASSeismic,
    CSASeismic,
    ISSeismic
)

def get_seismic_handler(code_name: str):
    mapping = {
        "Jordan": JordanSeismic(),
        "Saudi": SaudiSeismic(),
        "Egypt": EgyptSeismic(),
        "Eurocode": EurocodeSeismic(),
        "UAE": UAESeismic(),
        "Turkey": TurkeySeismic(),
        "ACI": ACISismic(),
        "BS": BSSeismic(),
        "AS": ASSeismic(),
        "CSA": CSASeismic(),
        "IS": ISSeismic()
    }
    return mapping.get(code_name)
