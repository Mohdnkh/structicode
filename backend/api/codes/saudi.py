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

class SaudiCode(ACI):
    """
    Saudi Building Code (SBC)
    Based on ACI and IBC with adjustments for local climate and seismic activity.
    """

    def __init__(self):
        super().__init__()
        self.name = "Saudi Building Code (SBC)"
        self.country = "Saudi Arabia"
        self.version = "SBC 304 (Concrete), SBC 301 (Loads), SBC 303 (Steel)"
        self.code_type = "Concrete and Steel Design"

        self.load_factors.update({
            "dead": 1.2,
            "live": 1.6,
            "wind": 1.3,
            "snow": 1.5,
            "earthquake": 1.0
        })

    def apply_local_modifications(self, result):
        result["details"]["note"] = "Checked per Saudi Building Code requirements"
        if "moment_capacity" in result:
            result["moment_capacity"] *= 0.95
        return result

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
            return self.apply_local_modifications(self.analyze_steel_beam(data))
        elif element_type == "steel_column":
            return self.apply_local_modifications(self.analyze_steel_column(data))
        else:
            return {"status": "error", "message": f"Unsupported element type: {element_type}"}

    def analyze_concrete_beam(self, data):
        return analyze_concrete_beam(data, code="Saudi")

    def analyze_concrete_column(self, data):
        return analyze_concrete_column(data, code="Saudi")

    def analyze_solid_slab(self, data):
        return analyze_solid_slab(data | {"code": "Saudi"})

    def analyze_hollow_slab(self, data):
        return analyze_hollow_slab(data | {"code": "Saudi"})

    def analyze_waffle_slab(self, data):
        return analyze_waffle_slab(data | {"code": "Saudi"})

    def analyze_concrete_footing(self, data):
        return analyze_concrete_footing(data, code="Saudi")

    def analyze_concrete_staircase(self, data):
        return analyze_concrete_staircase(data, code="Saudi")

    def analyze_steel_beam(self, data):
        return analyze_steel_beam(data, code="SBC 303")

    def analyze_steel_column(self, data):
        return analyze_steel_column(data, code="SBC 303")

    def analyze_seismic(self, data):
        result = super().analyze_seismic(data)
        result["recommendations"].append("Refer to SBC seismic zone map for appropriate Ss/S1 values")
        return result
