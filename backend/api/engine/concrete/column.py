def analyze_concrete_column(data, code='ACI'):
    col_type = data.get('type', 'Rectangular')

    if col_type == 'Rectangular':
        return analyze_rectangular_column(data, code)
    elif col_type == 'Circular':
        return analyze_circular_column(data, code)
    elif col_type == 'Composite':
        return analyze_composite_column(data, code)
    else:
        return {"status": "error", "message": f"Unsupported column type: {col_type}"}


def get_code_parameters(code):
    code = code.upper()

    if code in ['ACI', 'JORDAN', 'SAUDI', 'UAE']:
        return {'phi': 0.65, 'fy': 420}
    elif code == 'EUROCODE':
        return {'phi': 1.0, 'fy': 500}
    elif code == 'BS':
        return {'phi': 1.0, 'fy': 460}
    elif code == 'EGYPT':
        return {'phi': 0.6, 'fy': 360}
    elif code == 'TURKEY':
        return {'phi': 0.65, 'fy': 500}
    elif code == 'CSA':
        return {'phi': 0.6, 'fy': 400}
    elif code == 'IS':
        return {'phi': 0.65, 'fy': 415}
    elif code == 'AS':
        return {'phi': 0.6, 'fy': 500}
    else:
        return {'phi': 0.65, 'fy': 420}


def analyze_rectangular_column(data, code='ACI'):
    b = data['geometry']['b']
    h = data['geometry']['h']
    fc = data['materials']['fc']
    fy = data['materials'].get('fy')
    n_bars = data['reinforcement']['barCount']
    dia = data['reinforcement']['barDiameter']
    Pu = data['loads'].get('axial', 0)

    As = (3.1416 / 4) * (dia ** 2) * n_bars
    As_cm2 = As / 100.0
    Ag_cm2 = b * h

    params = get_code_parameters(code)
    phi = params['phi']
    fy = fy or params['fy']

    Pn = 0.85 * fc * (Ag_cm2 - As_cm2) + fy * As_cm2
    Pn = Pn / 1000

    status = "safe" if Pu <= phi * Pn else "unsafe"
    recommendations = []

    if status == "unsafe":
        ratio = round(Pu / (phi * Pn), 2)
        recommendations.append(f"Increase steel area As or use larger bar diameter. Load exceeds capacity by {ratio}x.")
        recommendations.append("Consider increasing cross-sectional dimensions (b × h).")
        recommendations.append("Use higher concrete strength fc or steel yield strength fy.")
        recommendations.append("Reduce axial load or redistribute load to adjacent columns if possible.")

    return {
        "element": "concrete_column",
        "type": "Rectangular",
        "fc (MPa)": fc,
        "fy (MPa)": fy,
        "As (cm²)": round(As_cm2, 2),
        "Ag (cm²)": round(Ag_cm2, 2),
        "Pn (kN)": round(Pn, 2),
        "Pu (kN)": round(Pu, 2),
        "phi": phi,
        "status": status,
        "details": {
            "note": f"Analysis based on {code} assumptions",
            "bar count": n_bars,
            "bar diameter (mm)": dia
        },
        "recommendations": recommendations
    }


def analyze_circular_column(data, code='ACI'):
    # Placeholder - implement full circular section analysis later
    return {
        "element": "concrete_column",
        "type": "Circular",
        "status": "not_implemented",
        "message": "Circular column analysis is not implemented yet."
    }


def analyze_composite_column(data, code='ACI'):
    # Placeholder - implement composite section logic
    return {
        "element": "concrete_column",
        "type": "Composite",
        "status": "not_implemented",
        "message": "Composite column analysis is not implemented yet."
    }
