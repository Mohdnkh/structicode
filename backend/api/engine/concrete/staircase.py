def analyze_concrete_staircase(data, code='ACI'):
    """
    Analyzes a concrete staircase flight modeled as an inclined slab.
    Supports loads: dead, live, wind.
    """
    try:
        # Geometry inputs
        tread = data.get('tread')              # cm
        riser = data.get('riser')              # cm
        n = data.get('steps')                  # number of steps
        h_cm = data.get('thickness')           # cm
        dia = data.get('rebar')                # mm

        if any(x is None for x in [tread, riser, n, h_cm, dia]):
            return {"error": "Missing geometry or reinforcement inputs (tread, riser, steps, thickness, or rebar)."}

        h = h_cm * 10                           # mm
        b = 1000                                # mm strip width
        cover = 25                              # mm
        d = h - cover                           # effective depth
        n_bars = 4                              # assumed number of bars

        # Material properties
        fc = data.get('fc', 25)                # MPa
        fy = data.get('fy')

        params = get_code_parameters(code)
        phi = params['phi']
        fy = fy or params['fy']

        # Inclined slab length
        tread_m = tread / 100
        riser_m = riser / 100
        L = ((tread_m ** 2 + riser_m ** 2) ** 0.5) * n  # m

        # Steel area
        As = (3.1416 / 4) * (dia ** 2) * n_bars         # mm²

        # Capacity
        a = As * fy / (0.85 * fc * b)
        jd = d - a / 2
        Mn = phi * (As * fy * jd) / 1e6                # kN·m

        # Loads
        loads = data.get('loads', {})
        wu = sum(float(loads.get(k, 0)) for k in ['dead', 'live', 'wind'])  # kN/m²
        Mu = wu * (L ** 2) / 8                         # kN·m (1m wide strip)

        # Result
        status = "safe" if Mu <= Mn else "unsafe"

        # Recommendations
        recommendations = []
        if status == "unsafe":
            ratio = round(Mu / Mn, 2)
            recommendations.append(f"Increase rebar diameter or number of bars. Load exceeds capacity by {ratio}x.")
            recommendations.append("Increase slab thickness to enhance effective depth and moment capacity.")
            recommendations.append("Reduce span by adding intermediate support if applicable.")
            recommendations.append("Use higher strength concrete (fc) or improved reinforcement layout.")

        return {
            "element": "concrete_staircase",
            "fc (MPa)": fc,
            "fy (MPa)": fy,
            "As (mm²)": round(As, 2),
            "Mn (kN·m)": round(Mn, 2),
            "Mu (kN·m)": round(Mu, 2),
            "phi": phi,
            "status": status,
            "details": {
                "note": f"Inclined slab approximation using {code}",
                "effective_depth (mm)": round(d, 1),
                "inclined_length (m)": round(L, 2),
                "strip_width (mm)": b,
                "rebar_diameter (mm)": dia
            },
            "recommendations": recommendations
        }

    except Exception as e:
        return {"error": f"Staircase analysis failed: {str(e)}"}


def get_code_parameters(code):
    code = code.upper()

    if code in ['ACI', 'JORDAN', 'SAUDI', 'UAE']:
        return {'phi': 0.9, 'fy': 420}
    elif code == 'EUROCODE':
        return {'phi': 1.0, 'fy': 500}
    elif code == 'BS':
        return {'phi': 1.0, 'fy': 460}
    elif code == 'EGYPT':
        return {'phi': 0.85, 'fy': 360}
    elif code == 'TURKEY':
        return {'phi': 0.9, 'fy': 500}
    elif code == 'CSA':
        return {'phi': 0.85, 'fy': 400}
    elif code == 'IS':
        return {'phi': 0.87, 'fy': 415}
    elif code == 'AS':
        return {'phi': 0.85, 'fy': 500}
    else:
        return {'phi': 0.9, 'fy': 420}
