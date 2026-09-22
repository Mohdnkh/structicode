"""Computational safety limits, deliberately separate from engineering limits."""
from __future__ import annotations

from typing import Any

from backend.api.auth.security import EnterpriseError

MAX_MATERIALS = 32
MAX_SECTIONS = 64
MAX_NODES = 256
MAX_MEMBERS = 512
MAX_MEMBER_LOADS = 32
MAX_SLABS = 64
MAX_INPUT_MAGNITUDE = 1e12


def _walk(value: Any):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, (int, float)) and abs(value) > MAX_INPUT_MAGNITUDE:
        yield value


def validate_element_input(request: Any) -> None:
    if next(_walk(request.input.model_dump(mode="python")), None) is not None:
        raise EnterpriseError("INPUT_MAGNITUDE_LIMIT", "Input exceeds the computational safety magnitude guard", 422)


def validate_structure_complexity(request: Any) -> None:
    counts = (
        ("materials", len(request.materials), MAX_MATERIALS),
        ("sections", len(request.sections), MAX_SECTIONS),
        ("nodes", len(request.nodes), MAX_NODES),
        ("members", len(request.members), MAX_MEMBERS),
        ("slabs", len(request.slabs), MAX_SLABS),
    )
    for name, count, limit in counts:
        if count > limit:
            raise EnterpriseError("MODEL_COMPLEXITY_LIMIT", f"{name} exceeds the software safety limit of {limit}", 422)
    if any(len(member.loads) > MAX_MEMBER_LOADS for member in request.members):
        raise EnterpriseError("MODEL_COMPLEXITY_LIMIT", f"member loads exceed the software safety limit of {MAX_MEMBER_LOADS}", 422)
    if next(_walk(request.model_dump(mode="python")), None) is not None:
        raise EnterpriseError("INPUT_MAGNITUDE_LIMIT", "Input exceeds the computational safety magnitude guard", 422)
