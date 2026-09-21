"""Legacy combination definitions and deterministic load-factor mechanics."""

import math
import re


LOAD_CASES = frozenset({"D", "L", "W", "S", "E"})
_TERM = re.compile(r"(?P<factor>(?:\d+(?:\.\d*)?|\.\d+))\s*(?P<case>[A-Za-z])")


def parse_combination(expr: str) -> dict[str, float]:
    """Parse signed, additive load terms; an absent case has factor zero."""
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("Load combination expression must be a nonempty string")
    factors: dict[str, float] = {}
    position = 0
    first = True
    while position < len(expr):
        while position < len(expr) and expr[position].isspace():
            position += 1
        if position == len(expr):
            break
        sign = 1.0
        if expr[position] in "+-":
            sign = -1.0 if expr[position] == "-" else 1.0
            position += 1
        elif not first:
            raise ValueError("Load combination terms must be separated by + or -")
        while position < len(expr) and expr[position].isspace():
            position += 1
        term = _TERM.match(expr, position)
        if term is None:
            raise ValueError("Malformed load combination term")
        case_id = term.group("case").upper()
        if case_id not in LOAD_CASES:
            raise ValueError(f"Unsupported load case: {case_id}")
        factor = sign * float(term.group("factor"))
        if not math.isfinite(factor):
            raise ValueError("Load factor must be finite")
        factors[case_id] = factors.get(case_id, 0.0) + factor
        if not math.isfinite(factors[case_id]):
            raise ValueError("Combined load factor must be finite")
        position = term.end()
        if position < len(expr) and not (expr[position].isspace() or expr[position] in "+-"):
            raise ValueError("Malformed load combination expression")
        first = False
    if first or expr.rstrip()[-1] in "+-":
        raise ValueError("Malformed load combination expression")
    return factors

def combine_loads(loads: dict, factors: dict) -> float:
    """Sum named loads; cases omitted from a combination contribute zero."""
    return sum(
        float(loads.get(case, 0.0)) * factors.get(case, 0.0)
        for case in ("dead", "live", "wind", "snow", "earthquake")
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
