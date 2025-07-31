
class JordanSeismic:
    def analyze(self, data):
        zone = data.get("zone", "2A")
        soil = data.get("soil", "medium")
        importance = data.get("importance", "normal")
        system = data.get("system", "moment_frame")

        zone_factor = {
            "1": 0.10,
            "2A": 0.15,
            "2B": 0.20,
            "3": 0.25
        }.get(zone.upper(), 0.15)

        soil_factor = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.2
        }.get(soil.lower(), 1.0)

        importance_factor = {
            "low": 0.8,
            "normal": 1.0,
            "high": 1.2
        }.get(importance.lower(), 1.0)

        base_shear = zone_factor * soil_factor * importance_factor * 1000  # Dummy base shear value

        return {
            "zone": zone,
            "soil": soil,
            "importance": importance,
            "system": system,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Simplified base shear check based on Jordan seismic code"
        }


class SaudiSeismic:
    def analyze(self, data):
        zone = data.get("zone", "D1")
        soil = data.get("soil", "medium")

        Ss = {
            "A": 0.15,
            "B": 0.25,
            "C": 0.35,
            "D1": 0.45,
            "D2": 0.55
        }.get(zone.upper(), 0.25)

        Fa = {
            "rock": 0.8,
            "medium": 1.0,
            "soft": 1.3
        }.get(soil.lower(), 1.0)

        Sds = Ss * Fa
        base_shear = Sds * 1000

        return {
            "zone": zone,
            "soil": soil,
            "Ss": Ss,
            "Fa": Fa,
            "Sds": round(Sds, 2),
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Based on Saudi Building Code seismic provisions"
        }


class EgyptSeismic:
    def analyze(self, data):
        zone = data.get("zone", "2")
        soil = data.get("soil", "medium")
        zone_factor = {
            "1": 0.10,
            "2": 0.20,
            "3": 0.30
        }.get(zone, 0.20)

        soil_modifier = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.2
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_modifier * 1000

        return {
            "zone": zone,
            "soil": soil,
            "zone_factor": zone_factor,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Estimated from Egyptian seismic guidelines"
        }


class EurocodeSeismic:
    def analyze(self, data):
        ag = {
            "low": 0.08,
            "medium": 0.12,
            "high": 0.16
        }.get(data.get("zone", "medium"), 0.12)

        soil = data.get("soil", "medium")
        S = {
            "rock": 1.0,
            "medium": 1.2,
            "soft": 1.4
        }.get(soil, 1.2)

        base_shear = ag * S * 1000

        return {
            "ag": ag,
            "soil": soil,
            "S": S,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Eurocode 8 base shear approximation"
        }


class UAESeismic:
    def analyze(self, data):
        zone = data.get("zone", "Zone 1")
        soil = data.get("soil", "medium")

        zone_factor = {
            "Zone 0": 0.1,
            "Zone 1": 0.15,
            "Zone 2A": 0.2,
            "Zone 2B": 0.3
        }.get(zone, 0.15)

        soil_factor = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.2
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "zone_factor": zone_factor,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Seismic check based on UAE seismic zoning"
        }


class TurkeySeismic:
    def analyze(self, data):
        zone = data.get("zone", "3")
        soil = data.get("soil", "medium")

        zone_factor = {
            "1": 0.4,
            "2": 0.3,
            "3": 0.2,
            "4": 0.1
        }.get(zone, 0.2)

        soil_factor = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.3
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "zone_factor": zone_factor,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "TDY seismic base shear approximation"
        }



class ACISismic:
    def analyze(self, data):
        zone = data.get("zone", "2")
        soil = data.get("soil", "medium")

        zone_factor = {
            "1": 0.10,
            "2": 0.15,
            "3": 0.25,
            "4": 0.35
        }.get(zone, 0.15)

        soil_modifier = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.2
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_modifier * 1000

        return {
            "zone": zone,
            "soil": soil,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Simplified ACI seismic check based on ASCE 7"
        }


class BSSeismic:
    def analyze(self, data):
        zone = data.get("zone", "moderate")
        soil = data.get("soil", "medium")

        zone_factor = {
            "low": 0.08,
            "moderate": 0.12,
            "high": 0.18
        }.get(zone, 0.12)

        soil_factor = {
            "rock": 0.95,
            "medium": 1.0,
            "soft": 1.3
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Approximate seismic check inspired by Eurocode under BS context"
        }


class ASSeismic:
    def analyze(self, data):
        zone = data.get("zone", "A")
        soil = data.get("soil", "medium")

        zone_factor = {
            "A": 0.1,
            "B": 0.15,
            "C": 0.2,
            "D": 0.3
        }.get(zone, 0.15)

        soil_factor = {
            "rock": 0.85,
            "medium": 1.0,
            "soft": 1.25
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Australian seismic approximation (AS1170)"
        }


class CSASeismic:
    def analyze(self, data):
        zone = data.get("zone", "low")
        soil = data.get("soil", "medium")

        zone_factor = {
            "low": 0.08,
            "medium": 0.12,
            "high": 0.18
        }.get(zone, 0.12)

        soil_factor = {
            "rock": 0.9,
            "medium": 1.0,
            "soft": 1.2
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "Simplified Canadian NBCC seismic approximation"
        }


class ISSeismic:
    def analyze(self, data):
        zone = data.get("zone", "III")
        soil = data.get("soil", "medium")

        zone_factor = {
            "II": 0.1,
            "III": 0.16,
            "IV": 0.24,
            "V": 0.36
        }.get(zone.upper(), 0.16)

        soil_factor = {
            "rock": 0.8,
            "medium": 1.0,
            "soft": 1.3
        }.get(soil.lower(), 1.0)

        base_shear = zone_factor * soil_factor * 1000

        return {
            "zone": zone,
            "soil": soil,
            "base_shear (kN)": round(base_shear, 2),
            "status": "safe" if base_shear < 2000 else "review",
            "note": "IS 1893 simplified base shear estimation"
        }
