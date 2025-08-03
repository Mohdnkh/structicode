from ..engine.concrete.beam import analyze_concrete_beam
from ..engine.concrete.column import analyze_concrete_column
from ..engine.concrete.slab_solid import analyze_solid_slab
from ..engine.concrete.slab_hollow import analyze_hollow_slab
from ..engine.concrete.slab_waffle import analyze_waffle_slab
from ..engine.concrete.footing import analyze_concrete_footing
from ..engine.concrete.staircase import analyze_concrete_staircase
from ..engine.steel.steel_beam import analyze_steel_beam
from ..engine.steel.steel_column import analyze_steel_column
from .aci import ACI

class ISCode:
    """
    Indian Standards (IS 456 for Concrete)
    Structural code handler for India.
    """

    def __init__(self):
        self.name = "Indian Standards (IS)"
        self.country = "India"
        self.version = "IS 456"
        self.code_type = "Concrete Design Only"

        self.load_factors = {
            "dead": 1.5,
            "live": 1.5,
            "wind": 1.2,
            "earthquake": 1.0
        }

    def analyze(self, element_type, data):
        if element_type == "beam":
            return self.analyze_concrete_beam(data)
        elif element_type == "column":
            return self.analyze_concrete_column(data)
        elif element_type == "slab":
            slab_type = data.get("type", "solid")
            if slab_type == "solid":
                return self.analyze_solid_slab(data)
            elif slab_type == "hollow":
                return self.analyze_hollow_slab(data)
            elif slab_type == "waffle":
                return self.analyze_waffle_slab(data)
            else:
                return {"status": "error", "message": f"Unsupported slab type: {slab_type}"}
        elif element_type == "footing":
            return self.analyze_concrete_footing(data)
        elif element_type == "staircase":
            return self.analyze_concrete_staircase(data)
        else:
            return {"status": "error", "message": f"Unsupported element type '{element_type}' for IS code."}

    def analyze_concrete_beam(self, data):
        return analyze_concrete_beam(data, code='IS')

    def analyze_concrete_column(self, data):
        return analyze_concrete_column(data, code='IS')

    def analyze_solid_slab(self, data):
        return analyze_solid_slab(data | {"code": "IS"})

    def analyze_hollow_slab(self, data):
        return analyze_hollow_slab(data | {"code": "IS"})

    def analyze_waffle_slab(self, data):
        return analyze_waffle_slab(data | {"code": "IS"})

    def analyze_concrete_footing(self, data):
        return analyze_concrete_footing(data, code='IS')

    def analyze_concrete_staircase(self, data):
        return analyze_concrete_staircase(data, code='IS')

    def analyze_seismic(self, data):
        return {
            "seismic_demand": 0,
            "resistance": 0,
            "status": "safe",
            "recommendations": ["Follow IS 1893 seismic provisions."]
        }

    def get_code_info(self):
        return {
            "name": self.name,
            "country": self.country,
            "version": self.version,
            "type": self.code_type
        }
