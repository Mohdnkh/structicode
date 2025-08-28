# ================================
# Load Combination Generator
# ================================

def combine_loads(loads: dict, factors: dict) -> float:
    """
    يجمع الأحمال باستخدام معاملات الكود الإنشائي.
    inputs:
      loads: {dead, live, wind, snow, earthquake}
      factors: {dead, live, wind, snow, earthquake}
    returns:
      الحمل المكافئ (kN أو kN/m أو kN/m² حسب العنصر)
    """
    return (
        float(loads.get("dead", 0)) * factors.get("dead", 1.0) +
        float(loads.get("live", 0)) * factors.get("live", 1.0) +
        float(loads.get("wind", 0)) * factors.get("wind", 1.0) +
        float(loads.get("snow", 0)) * factors.get("snow", 1.0) +
        float(loads.get("earthquake", 0)) * factors.get("earthquake", 1.0)
    )


def generate_combinations(code: str):
    """
    بيرجع قائمة بالـ load combinations حسب الكود
    كل combo = {id, name, expr}
    """
    code = code.upper()
    combos = []

    if code == "ACI":
        combos = [
            {"id": "LC1", "name": "1.4D", "expr": "1.4D"},
            {"id": "LC2", "name": "1.2D+1.6L", "expr": "1.2D+1.6L"},
            {"id": "LC3", "name": "1.2D+1.0L+1.0E", "expr": "1.2D+1.0L+1.0E"},
            {"id": "LC4", "name": "0.9D+1.0E", "expr": "0.9D+1.0E"},
        ]
    elif code == "BS":
        combos = [
            {"id": "LC1", "name": "1.4D", "expr": "1.4D"},
            {"id": "LC2", "name": "1.4D+1.6L", "expr": "1.4D+1.6L"},
            {"id": "LC3", "name": "1.0D+1.0L+1.4W", "expr": "1.0D+1.0L+1.4W"},
        ]
    elif code == "EUROCODE":
        combos = [
            {"id": "LC1", "name": "1.35G+1.5Q", "expr": "1.35D+1.5L"},
            {"id": "LC2", "name": "1.35G+1.5Q+1.5W", "expr": "1.35D+1.5L+1.5W"},
            {"id": "LC3", "name": "0.9G+1.5E", "expr": "0.9D+1.5E"},
        ]
    else:
        # Default (لو ما في كود معروف)
        combos = [{"id": "LC1", "name": "1.0D", "expr": "1.0D"}]

    return combos
