def analyze_steel_beam(data, code='AISC'):
    """
    Analyzes steel I-beam under uniform load.
    Calculates max moment and compares with plastic moment capacity.

    Parameters:
    - data: {
        sectionType, sectionSize,
        dimensions: { depth (mm), width (mm), flangeThickness, webThickness },
        steelGrade (fy),
        span (m), uniformLoad (kN/m), supportType
    }

    Returns:
    - dict with status and results
    """
    fy = data.get('steelGrade')  # MPa
    span = data.get('span')      # m
    w = data.get('uniformLoad')  # kN/m
    support = data.get('supportType', 'Simply Supported')

    dims = data.get('dimensions', {})
    h = dims.get('depth')        # mm
    b = dims.get('width')        # mm
    tf = dims.get('flangeThickness')  # mm
    tw = dims.get('webThickness')     # mm

    phi = 0.9 if code in ['AISC', 'Eurocode', 'Jordan', 'Egypt'] else 1.0

    if not all([fy, span, w, h, b, tf, tw]):
        return {"status": "error", "message": "Missing required beam parameters."}

    # Approximate plastic section modulus Zx (simplified for I-section)
    Zx = (b * tf * (h - tf)) / 10  # cm³

    # Plastic moment capacity Mp
    Mp = fy * Zx / 100  # kN·m

    # Maximum moment based on support type
    if support == "Simply Supported":
        Mu = w * (span ** 2) / 8
    elif support == "Fixed":
        Mu = w * (span ** 2) / 12
    elif support == "Cantilever":
        Mu = w * (span ** 2) / 2
    elif support == "Continuous":
        Mu = w * (span ** 2) / 10
    else:
        Mu = w * (span ** 2) / 8  # default

    status = "safe" if Mu <= phi * Mp else "unsafe"

    # Recommendations if unsafe
    recommendations = []
    if status == "unsafe":
        ratio = round(Mu / (phi * Mp), 2)
        recommendations.append(f"🔸 Moment demand exceeds capacity by {ratio}x.")
        recommendations.append("🔸 Choose a larger steel section with higher Zx.")
        recommendations.append("🔸 Consider increasing steel grade fy.")
        recommendations.append("🔸 Reduce beam span or apply intermediate supports.")
        recommendations.append("🔸 Check if uniform load can be reduced.")

    return {
        "element": "steel_beam",
        "section": data.get('sectionSize'),
        "fy (MPa)": fy,
        "Zx (cm³)": round(Zx, 2),
        "Mp (kN·m)": round(Mp, 2),
        "Mu (kN·m)": round(Mu, 2),
        "phi": phi,
        "status": "unverified",
        "verification_status": "UNVERIFIED",
        "check_state": "NOT_EVALUATED",
        "legacy_status": status,
        "warning": "Legacy steel comparison only; engineering adequacy has not been evaluated.",
        "details": {
            "support_type": support,
            "usage (%)": round(Mu / (phi * Mp) * 100, 1),
            "note": f"Legacy unverified flexural comparison labeled {code}",
            "span (m)": span,
            "uniform_load (kN/m)": w
        },
        "recommendations": recommendations
    }
