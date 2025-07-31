def analyze_concrete_footing(data, code='ACI'):
    """
    Analyze isolated rectangular footing under axial load.
    Checks bearing pressure and punching shear.
    """

    try:
        # Geometry
        L = data.get('length')
        B = data.get('width')
        h_cm = data.get('thickness')
        if any(x is None for x in [L, B, h_cm]):
            return {"error": "Missing geometry input (length, width, or thickness)."}

        h_mm = h_cm * 10

        # Load
        P = data.get('columnLoad')
        if P is None:
            return {"error": "Missing column load (P)."}

        # Reinforcement & Material
        rebar_d = data.get('rebarDiameter')
        rebar_s = data.get('rebarSpacing')
        fc = data.get('fc', 25)
        fy = data.get('fy')  # Optional override
        cover = 75  # mm

        # Get phi and fy from code
        params = get_code_parameters(code)
        phi = params['phi']
        fy = fy or params['fy']

        # Soil type
        soil_type = data.get('soilType', 'sand')
        q_allow = {
            'clay': 150,
            'sand': 250,
            'rock': 500
        }.get(str(soil_type).lower(), 200)

        # Area & pressure
        A = L * B
        if A == 0:
            return {"error": "Footing area cannot be zero."}
        q_actual = P / A

        # Punching shear check (simplified)
        col_size = 0.4  # assume 40x40 cm square column
        bo = 4 * col_size  # perimeter in m
        d = h_mm - cover  # mm
        Vc = 0.17 * (fc ** 0.5) * bo * 1000 * d / 1000  # kN
        punching_safe = P <= phi * Vc

        # Determine status
        if q_actual > q_allow and not punching_safe:
            status = "unsafe (bearing + punching)"
        elif q_actual > q_allow:
            status = "unsafe (bearing)"
        elif not punching_safe:
            status = "unsafe (punching)"
        else:
            status = "safe"

        # Recommendations
        recommendations = []
        if "bearing" in status:
            recommendations.append("🔸 Increase footing area (length × width) to reduce soil pressure.")
            recommendations.append("🔸 Use stronger soil or redistribute loads across more footings.")
        if "punching" in status:
            recommendations.append("🔸 Increase footing thickness to improve punching shear capacity.")
            recommendations.append("🔸 Use higher concrete strength fc.")
            recommendations.append("🔸 Use column heads or shear reinforcement if allowed by code.")

        return {
            "element": "concrete_footing",
            "fc (MPa)": fc,
            "fy (MPa)": fy,
            "area (m²)": round(A, 3),
            "q_actual (kN/m²)": round(q_actual, 2),
            "q_allow (kN/m²)": q_allow,
            "axial_load (kN)": round(P, 2),
            "punching_capacity (kN)": round(phi * Vc, 2),
            "phi": phi,
            "status": status,
            "details": {
                "soil_type": soil_type,
                "rebar_diameter (mm)": rebar_d,
                "rebar_spacing (cm)": rebar_s,
                "effective_depth (mm)": round(d, 1),
                "column_size (m)": col_size,
                "code": code
            },
            "recommendations": recommendations
        }

    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def get_code_parameters(code):
    code = code.upper()

    if code in ['ACI', 'JORDAN', 'SAUDI', 'UAE']:
        return {'phi': 0.75, 'fy': 420}
    elif code == 'EUROCODE':
        return {'phi': 1.0, 'fy': 500}
    elif code == 'BS':
        return {'phi': 1.0, 'fy': 460}
    elif code == 'EGYPT':
        return {'phi': 0.7, 'fy': 360}
    elif code == 'TURKEY':
        return {'phi': 0.75, 'fy': 500}
    elif code == 'CSA':
        return {'phi': 0.7, 'fy': 400}
    elif code == 'IS':
        return {'phi': 0.75, 'fy': 415}
    elif code == 'AS':
        return {'phi': 0.7, 'fy': 500}
    else:
        return {'phi': 0.75, 'fy': 420}
