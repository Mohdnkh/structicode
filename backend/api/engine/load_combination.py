# load_combination.py – تجميع الأحمال وفقًا لعوامل الكود

def combine_loads(loads: dict, factors: dict) -> float:
    """
    يجمع الأحمال باستخدام معاملات الكود الإنشائي.
    inputs:
      loads: {dead, live, wind, snow, earthquake}
      factors: معامل كل حمل من الكود المختار
    returns:
      القيمة المكافئة للحمل المجمع (kN أو kN/m أو kN/m² حسب العنصر)
    """
    return (
        float(loads.get("dead", 0)) * factors.get("dead", 1.0) +
        float(loads.get("live", 0)) * factors.get("live", 1.0) +
        float(loads.get("wind", 0)) * factors.get("wind", 1.0) +
        float(loads.get("snow", 0)) * factors.get("snow", 1.0) +
        float(loads.get("earthquake", 0)) * factors.get("earthquake", 1.0)
    )
