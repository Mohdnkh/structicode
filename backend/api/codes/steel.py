import math

class SteelCode:
    def analyze(self, element, data):
        if element == "steel_column":
            return self._analyze_column(data)
        elif element == "steel_beam":
            return self._analyze_beam(data)
        else:
            return {
                "status": "error",
                "message": f"Element '{element}' not supported in steel analysis"
            }

    def analyze_steel_column(self, data):
        return self._analyze_column(data)

    def analyze_steel_beam(self, data):
        return self._analyze_beam(data)

    def _analyze_column(self, data):
        fy = data["steelGrade"]  # MPa
        P = data["axialLoad"] * 1000  # kN to N
        length = data["length"] / 1000  # mm to m
        K = data.get("kFactor", 1.0)

        b = data["dimensions"]["width"]
        d = data["dimensions"]["depth"]
        tf = data["dimensions"]["flangeThickness"]
        tw = data["dimensions"]["webThickness"]

        A = 2 * b * tf + (d - 2 * tf) * tw  # mm^2
        A_m2 = A / 1e6  # m^2

        φ = 0.9
        allowable_load = φ * fy * A  # N

        safe = P <= allowable_load
        status = "safe" if safe else "unsafe"
        utilization = round(P / allowable_load * 100, 2)

        return {
            "status": "success",
            "result": {
                "status": status,
                "details": {
                    "note": f"Column utilization: {utilization}%",
                },
                "recommendations": [] if safe else ["Increase section size", "Use higher steel grade"]
            }
        }

    def _analyze_beam(self, data):
        fy = data["steelGrade"]  # MPa
        w = data["uniformLoad"] * 1000  # kN/m to N/m
        L = data["span"] / 1000  # mm to m

        b = data["dimensions"]["width"]
        d = data["dimensions"]["depth"]
        tf = data["dimensions"]["flangeThickness"]
        tw = data["dimensions"]["webThickness"]

        Z = (b * d**2) / 6  # mm^3
        φ = 0.9
        M_allow = φ * fy * Z  # N·mm

        M_max = (w * L**2) / 8  # N·m
        M_max_Nmm = M_max * 1e6  # N·mm

        safe = M_max_Nmm <= M_allow
        status = "safe" if safe else "unsafe"
        utilization = round(M_max_Nmm / M_allow * 100, 2)

        return {
            "status": "success",
            "result": {
                "status": status,
                "details": {
                    "note": f"Beam utilization: {utilization}%",
                },
                "recommendations": [] if safe else ["Increase moment capacity", "Reduce span or load"]
            }
        }
