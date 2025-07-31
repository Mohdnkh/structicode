from backend.api.engine.concrete.beam import analyze_concrete_beam
from backend.api.engine.concrete.column import analyze_concrete_column
from api.engine.concrete.slab_solid import analyze_solid_slab
from api.engine.concrete.slab_hollow import analyze_hollow_slab
from api.engine.concrete.slab_waffle import analyze_waffle_slab
from backend.api.engine.concrete.footing import analyze_concrete_footing
from backend.api.engine.concrete.staircase import analyze_concrete_staircase
from backend.api.engine.steel.steel_beam import analyze_steel_beam
from backend.api.engine.steel.steel_column import analyze_steel_column

class Eurocode:
    """
    Eurocode (EN 1992 for Concrete, EN 1993 for Steel)
    European structural design standards.
    """

    def __init__(self):
        self.name = "Eurocode"
        self.country = "European Union"
        self.version = "EN 1992 (Concrete), EN 1993 (Steel)"
        self.code_type = "Concrete and Steel Design"

        self.load_factors = {
            "dead": 1.35,
            "live": 1.5,
            "wind": 1.5,
            "snow": 1.5,
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
        elif element_type == "steel_beam":
            return self.analyze_steel_beam(data)
        elif element_type == "steel_column":
            return self.analyze_steel_column(data)
        else:
            return {"status": "error", "message": f"Unsupported element type: {element_type}"}

    def analyze_concrete_beam(self, data):
        return analyze_concrete_beam(data, code="Eurocode")

    def analyze_concrete_column(self, data):
        return analyze_concrete_column(data, code="Eurocode")

    def analyze_solid_slab(self, data):
        return analyze_solid_slab(data | {"code": "Eurocode"})

    def analyze_hollow_slab(self, data):
        return analyze_hollow_slab(data | {"code": "Eurocode"})

    def analyze_waffle_slab(self, data):
        return analyze_waffle_slab(data | {"code": "Eurocode"})

    def analyze_concrete_footing(self, data):
        return analyze_concrete_footing(data, code="Eurocode")

    def analyze_concrete_staircase(self, data):
        return analyze_concrete_staircase(data, code="Eurocode")

    def analyze_steel_beam(self, data):
        return analyze_steel_beam(data, code="EN1993")

    def analyze_steel_column(self, data):
        return analyze_steel_column(data, code="EN1993")

    def analyze_seismic(self, data):
        return {
            "seismic_demand": 0,
            "resistance": 0,
            "status": "safe",
            "recommendations": []
        }

    def get_code_info(self):
        return {
            "name": self.name,
            "country": self.country,
            "version": self.version,
            "type": self.code_type
        }
