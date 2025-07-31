def analyze_concrete_beam(data, code='ACI'):
    beam_type = data.get('type', 'Normal')

    if beam_type == 'Normal':
        return analyze_normal_beam(data, code)
    elif beam_type == 'Inverted':
        return analyze_inverted_beam(data, code)
    elif beam_type == 'Tee':
        return analyze_tee_beam(data, code)
    elif beam_type == 'Prestressed':
        return analyze_prestressed_beam(data, code)
    else:
        return {"status": "error", "message": f"Unsupported beam type: {beam_type}"}


def get_code_parameters(code):
    code = code.upper()

    if code == 'ACI' or code == 'JORDAN' or code == 'SAUDI' or code == 'UAE':
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
        return {'phi': 0.9, 'fy': 420}  # default fallback


def analyze_normal_beam(data, code='ACI'):
    fc = data.get('fc')
    b = data.get('width')
    h = data.get('depth')
    L = data.get('length')
    cover_cm = data.get('cover', 3)
    rebar = data.get('rebar', {})
    loads = data.get('loads', {})

    if not all([fc, b, h, L, rebar.get('count'), rebar.get('diameter')]):
        return {"status": "error", "message": "Missing required beam input values."}

    b_mm = b * 10
    h_mm = h * 10
    cover_mm = cover_cm * 10
    d = h_mm - cover_mm

    dia = rebar.get('diameter')
    n = rebar.get('count')
    As = (3.1416 / 4) * (dia ** 2) * n

    params = get_code_parameters(code)
    phi = params['phi']
    fy = data.get('fy', params['fy'])

    a = As * fy / (0.85 * fc * b_mm)
    jd = d - a / 2
    Mn = phi * (As * fy * jd) / 1e6

    w_total = sum(float(loads.get(key, 0)) for key in ['dead', 'live', 'wind', 'snow'])
    Mu = w_total * (L ** 2) / 8

    status = "safe" if Mu <= Mn else "unsafe"
    recommendations = []

    if status == "unsafe":
        ratio = round(Mu / Mn, 2)
        if ratio > 1.0:
            recommendations.append(f"Increase steel area As. Current demand exceeds capacity by {ratio}x.")
            recommendations.append("Consider increasing beam depth or width.")
            recommendations.append("Use higher concrete strength fc or reduce applied loads.")
        if d < 400:
            recommendations.append("Effective depth is low. Consider deeper section to improve lever arm.")
        if rebar.get('count') < 3:
            recommendations.append("Add more longitudinal bars to improve moment capacity.")

    return {
        "element": "concrete_beam",
        "type": "Normal",
        "fc (MPa)": fc,
        "As (mm²)": round(As, 2),
        "Mn (kN·m)": round(Mn, 2),
        "Mu (kN·m)": round(Mu, 2),
        "phi": phi,
        "status": status,
        "details": {
            "effective_depth d (mm)": round(d, 1),
            "total_uniform_load w (kN/m)": round(w_total, 2),
            "length (m)": L,
            "code": code,
            "note": f"Analysis performed using {code} design parameters"
        },
        "recommendations": recommendations
    }


def analyze_inverted_beam(data, code='ACI'):
    return analyze_normal_beam(data, code)


def analyze_tee_beam(data, code='ACI'):
    return analyze_normal_beam(data, code)


def analyze_prestressed_beam(data, code='ACI'):
    return {
        "element": "concrete_beam",
        "type": "Prestressed",
        "status": "not_implemented",
        "message": "Prestressed beam analysis is not implemented yet."
    }
