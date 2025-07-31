import math

def analyze_solid_slab(data):
    """
    تحليل بلاطة Solid Slab مع حساب تلقائي للتسليح As_required حسب الكود
    """

    try:
        code = data.get("code", "ACI")
        L = data.get("length")
        B = data.get("width", 1)
        h_cm = data.get("thickness")
        loads = data.get("loads", {})

        if None in [L, h_cm]:
            return {"error": "Length and thickness are required."}

        h = h_cm * 10  # mm
        cover = 20     # mm
        d = h - cover  # mm

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
        fc = data.get("fc", 25)

        # الأحمال
        dead = float(loads.get("dead", 0))
        live = float(loads.get("live", 0))
        wind = float(loads.get("wind", 0))
        snow = float(loads.get("snow", 0))

        LF = {"dead": 1.2, "live": 1.6, "wind": 1.0, "snow": 1.0}
        wu = LF["dead"] * dead + LF["live"] * live + LF["wind"] * wind + LF["snow"] * snow
        wu_total = wu * B

        # العزم التصميمي
        Mu = wu_total * (L ** 2) / 8
        Mu_Nmm = Mu * 1e6
        jd = d - (0.4 * d) / 2
        As_required = Mu_Nmm / (phi * fy * jd)

        # التسليح المدخل
        dia = data.get("barDiameter")
        top_n = data.get("topBarCount")
        bot_n = data.get("bottomBarCount")

        if None in [dia, top_n, bot_n]:
            return {"error": "Missing bar diameter or bar counts."}

        As_top = top_n * (math.pi / 4) * dia ** 2
        As_bot = bot_n * (math.pi / 4) * dia ** 2

        status = "safe" if As_bot >= As_required else "unsafe"
        ratio = round(As_required / As_bot, 2)

        recommendations = []
        if status == "unsafe":
            recommendations.append(f"Increase bottom bars or use larger diameter. Current As_bot = {round(As_bot,2)} mm²/m, required = {round(As_required,2)} mm²/m.")
            recommendations.append("Increase thickness or reduce span/load if possible.")

        return {
            "element": "solid_slab",
            "status": status,
            "code": code,
            "geometry": {
                "length (m)": L,
                "width (m)": B,
                "thickness (mm)": h
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
                "As_required (mm²/m)": round(As_required, 2),
                "As_bottom_provided (mm²/m)": round(As_bot, 2),
                "As_top_provided (mm²/m)": round(As_top, 2),
                "phi": phi,
                "fy (MPa)": fy,
                "d (mm)": round(d, 1)
            },
            "recommendations": recommendations,
            "note": "Flexural analysis with user reinforcement"
        }

    except Exception as e:
        return {"error": f"Solid slab analysis failed: {str(e)}"}
