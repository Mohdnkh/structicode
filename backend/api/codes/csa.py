from ..engine.concrete.beam import analyze_concrete_beam
from ..engine.concrete.column import analyze_concrete_column
from ..engine.concrete.slab_solid import analyze_solid_slab
from ..engine.concrete.slab_hollow import analyze_hollow_slab
from ..engine.concrete.slab_waffle import analyze_waffle_slab
from ..engine.concrete.footing import analyze_concrete_footing
from ..engine.concrete.staircase import analyze_concrete_staircase
from ..engine.steel.steel_beam import analyze_steel_beam
from ..engine.steel.steel_column import analyze_steel_column


class CSA:
    """
    Canadian Standards Association (CSA A23.3 for Concrete, S16 for Steel)
    Structural code handler for Canada.
    """

    def __init__(self):
        self.name = "Canadian Standards (CSA)"
        self.country = "Canada"
        self.version = "CSA A23.3 (Concrete), CSA S16 (Steel)"
        self.code_type = "Concrete and Steel Design"

        self.load_factors = {
            "dead": 1.25,
            "live": 1.5,
            "wind": 1.4,
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

    # ================================
    # Concrete elements
    # ================================
    def analyze_concrete_beam(self, data):
        return analyze_concrete_beam(data, code="CSA")

    def analyze_concrete_column(self, data):
        return analyze_concrete_column(data, code="CSA")

    def analyze_solid_slab(self, data):
        return analyze_solid_slab(data | {"code": "CSA"})

    def analyze_hollow_slab(self, data):
        return analyze_hollow_slab(data | {"code": "CSA"})

    def analyze_waffle_slab(self, data):
        return analyze_waffle_slab(data | {"code": "CSA"})

    def analyze_concrete_footing(self, data):
        return analyze_concrete_footing(data, code="CSA")

    def analyze_concrete_staircase(self, data):
        return analyze_concrete_staircase(data, code="CSA")

    # ================================
    # Steel elements
    # ================================
    def analyze_steel_beam(self, data):
        return analyze_steel_beam(data, code="CSA S16")

    def analyze_steel_column(self, data):
        return analyze_steel_column(data, code="CSA S16")

    # ================================
    # Structure-level analysis (with combos)
    # ================================
    def analyze_structure(self, structure_data: dict, raw_results: dict):
        """
        structure_data: JSON كامل للهيكل
        raw_results: نتائج StructureAnalyzer (لكل Combination)
        """
        results = {}
        phi_flexure, phi_shear, phi_axial = 0.9, 0.75, 0.65

        for combo_id, combo_res in raw_results.items():
            design = {}
            for mid, forces in combo_res["member_forces"].items():
                Mu, Vu, Nu = abs(forces["Mmax"]), abs(forces["Vmax"]), abs(forces["Nmax"])
                member = next(m for m in structure_data["members"] if m["id"] == mid)
                sec = next(s for s in structure_data["sections"] if s["id"] == member["sectionId"])
                mat = next(m for m in structure_data["materials"] if m["id"] == member["materialId"])

                bw, h, cover = sec["params"].get("bw", 0.3), sec["params"].get("h", 0.6), sec["params"].get("cover", 0.04)
                d = h - cover
                fc, fy = mat["fc"], mat["fy"]

                # Flexural steel requirement
                As_req = (Mu*1e6) / (phi_flexure * fy * 1e3 * (d - 0.5*cover))

                # Shear capacity
                Vc = 0.17 * (fc**0.5) * bw * d
                shear_ok = Vu <= phi_shear * Vc

                # Axial capacity
                Pn = 0.85 * fc * bw * h * 1e6 / 1000  # kN
                axial_ok = Nu <= phi_axial * Pn

                design[mid] = {
                    "Mu": round(Mu, 2),
                    "Vu": round(Vu, 2),
                    "Nu": round(Nu, 2),
                    "As_required": round(As_req, 2),
                    "As_provided": round(As_req * 1.2, 2),
                    "Shear_OK": shear_ok,
                    "Axial_OK": axial_ok,
                    "Overall_OK": shear_ok and axial_ok
                }

            results[combo_id] = {
                **combo_res,
                "design": design
            }

        return results

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

