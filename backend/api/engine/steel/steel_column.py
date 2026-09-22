import math
import json
import os

# تحميل بيانات القطاعات إذا لزم
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/steel_sections_data.json')
with open(DATA_PATH, 'r') as f:
    section_db = json.load(f)

def analyze_steel_column(data, code='AISC'):
    """
    Analyze steel column using AISC method.

    Parameters:
    - data: {
        sectionType, sectionSize,
        dimensions: { depth, width, flangeThickness, webThickness },
        steelGrade, axialLoad, length, kFactor
    }

    Returns:
    - Dictionary with capacity, slenderness, and safety status
    """
    section_type = data.get('sectionType')
    section_size = data.get('sectionSize')
    fy = data.get('steelGrade')  # MPa
    Pu = data.get('axialLoad')   # kN
    L = data.get('length') / 10  # mm → cm
    K = data.get('kFactor', 1.0)
    phi = 0.9 if code in ['AISC', 'Eurocode', 'Jordan', 'Egypt'] else 1.0

    # جلب خصائص المقطع
    section = section_db.get(section_type, {}).get(section_size)
    if not section:
        return {"status": "error", "message": "Section data not found."}

    A = section.get('A')   # cm²
    r = section.get('r')   # cm
    if not all([A, r, fy, L]):
        return {"status": "error", "message": "Missing required values (A, r, fy, L)."}

    KL_over_r = K * L / r
    E = 200000  # MPa
    Fe = (math.pi**2 * E) / (KL_over_r ** 2)  # Euler stress
    if fy / Fe <= 2.25:
        Fcr = 0.658 ** (fy / Fe) * fy
    else:
        Fcr = 0.877 * Fe

    Pn = Fcr * A / 10  # → kN
    status = "safe" if Pu <= phi * Pn else "unsafe"

    # Recommendations if unsafe
    recommendations = []
    if status == "unsafe":
        usage_ratio = round(Pu / (phi * Pn), 2)
        recommendations.append(f"🔸 Axial load exceeds capacity by {usage_ratio}x.")
        recommendations.append("🔸 Use a section with higher radius of gyration (r) to reduce slenderness.")
        recommendations.append("🔸 Reduce unbraced length L or use bracing to reduce KL/r.")
        recommendations.append("🔸 Choose a stronger section (higher A or fy).")
        recommendations.append("🔸 Review effective length factor K and support conditions.")

    return {
        "element": "steel_column",
        "section": section_size,
        "fy (MPa)": fy,
        "A (cm²)": A,
        "r (cm)": r,
        "KL/r": round(KL_over_r, 2),
        "Fcr (MPa)": round(Fcr, 2),
        "Pn (kN)": round(Pn, 2),
        "Pu (kN)": Pu,
        "phi": phi,
        "status": "unverified",
        "verification_status": "UNVERIFIED",
        "check_state": "NOT_EVALUATED",
        "legacy_status": status,
        "warning": "Legacy steel comparison only; engineering adequacy has not been evaluated.",
        "details": {
            "boundary_condition": data.get('boundaryCondition'),
            "formula": "Legacy unverified column buckling expression",
            "usage (%)": round(Pu / (phi * Pn) * 100, 1)
        },
        "recommendations": recommendations
    }
