import math

def analyze_waffle_slab(data):
    """
    تحليل بلاطة Waffle Slab مع حساب تلقائي للتسليح في الأعصاب (ribs)
    """

    try:
        # --- المدخلات الأساسية ---
        code = data.get("code", "ACI")
        L = data.get("length")              # m
        B = data.get("width", 1)            # m
        h_cm = data.get("thickness")        # cm
        waffle = data.get("waffle", {})
        rib_width_cm = waffle.get("ribWidth", 15)      # cm
        rib_spacing_cm = waffle.get("ribSpacing", 60)  # cm

        if None in [L, h_cm]:
            return {"error": "Length and thickness are required."}

        h = h_cm * 10  # mm
        d = h - 20     # mm (cover assumed 20mm)
        rib_spacing = rib_spacing_cm / 100  # m

        fc = data.get("fc", 25)

        phi_values = {
            "ACI": 0.9, "Jordan": 0.9, "Saudi": 0.9, "UAE": 0.9,
            "BS": 1.0, "Eurocode": 1.0, "CSA": 0.9,
            "IS": 0.9, "Egypt": 0.9, "AS": 0.9, "Turkey": 1.0
        }

        fy_defaults = {
            "ACI": 420, "Jordan": 420, "Saudi": 420, "UAE": 420,
            "Egypt": 360, "Eurocode": 500, "BS": 460,
            "CSA": 400, "IS": 415, "AS": 500, "Turkey": 500
        }

        phi = phi_values.get(code, 0.9)
        fy = data.get("fy", fy_defaults.get(code, 420))

        # --- الأحمال ---
        loads = data.get("loads", {})
        dead = float(loads.get("dead", 0))
        live = float(loads.get("live", 0))
        wind = float(loads.get("wind", 0))
        snow = float(loads.get("snow", 0))

        LF = {
            "dead": 1.2,
            "live": 1.6,
            "wind": 1.0,
            "snow": 1.0
        }

        wu = (
            LF["dead"] * dead +
            LF["live"] * live +
            LF["wind"] * wind +
            LF["snow"] * snow
        )  # kN/m²

        wu_total = wu * B  # kN/m on 1m strip

        # --- العزم التصميمي Mu ---
        Mu = wu_total * (L ** 2) / 8  # kN·m
        Mu_Nmm = Mu * 1e6

        jd = d - (0.4 * d) / 2
        As_required = Mu_Nmm / (phi * fy * jd)  # mm² per rib

        # --- المدخلات الخاصة بالتسليح ---
        dia = data.get("barDiameter")
        bot_n = data.get("bottomBarCount")

        if None in [dia, bot_n]:
            return {"error": "Missing bar diameter or bottom bar count."}

        As_bot = bot_n * (math.pi / 4) * dia ** 2
        status = "safe" if As_bot >= As_required else "unsafe"

        recommendations = []
        if status == "unsafe":
            recommendations.append(f"Increase bottom bars or use larger diameter. Current As_bot = {round(As_bot, 2)} mm², required = {round(As_required, 2)} mm².")
            recommendations.append("Increase slab thickness or reduce span/load if possible.")

        return {
            "element": "waffle_slab",
            "status": status,
            "code": code,
            "geometry": {
                "length (m)": L,
                "width (m)": B,
                "thickness (mm)": h,
                "rib_width (cm)": rib_width_cm,
                "rib_spacing (cm)": rib_spacing_cm,
                "effective_depth d (mm)": round(d, 1)
            },
            "loads (kN/m²)": {
                "dead": dead,
                "live": live,
                "wind": wind,
                "snow": snow,
                "wu_total": round(wu_total, 2)
            },
            "design": {
                "Mu (kN·m)": round(Mu, 2),
                "fy (MPa)": fy,
                "phi": phi,
                "As_required_per_rib (mm²)": round(As_required, 2),
                "As_bottom_provided (mm²)": round(As_bot, 2)
            },
            "recommendations": recommendations,
            "note": "Waffle slab rib check using provided reinforcement"
        }

    except Exception as e:
        return {"error": f"Waffle slab analysis failed: {str(e)}"}
