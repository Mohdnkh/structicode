"""Versioned API with typed inputs and explicitly unverified legacy output."""

import logging
from typing import Any

from fastapi import APIRouter

from .domain.identifiers import DesignCode, ElementId, LEGACY_CODE_NAMES
from .legacy_capabilities import supports_element, supports_structure
from .domain.legacy_adapters import (
    element_to_legacy, normalize_element, normalize_structure, structure_to_legacy,
)
from .domain.schemas import (
    CanonicalCombinationResult, CanonicalDisplacement, CanonicalMemberEndForce,
    CanonicalMemberForces, CanonicalReaction,
    ColumnInput, ElementRequest, ElementResponse, FootingInput,
    LegacyElementOutput, LegacyStructureOutput, SlabInput, StaircaseInput,
    StructureRequest, StructureResponse, VerificationStatus,
)
from .domain.units import Dimension as D, to_canonical
from .engine.code_router import get_code_handler
from .engine.concrete.beam import analyze_concrete_beam
from .engine.concrete.column import analyze_concrete_column
from .engine.concrete.footing import analyze_concrete_footing
from .engine.concrete.slab_hollow import analyze_hollow_slab
from .engine.concrete.slab_solid import analyze_solid_slab
from .engine.concrete.slab_waffle import analyze_waffle_slab
from .engine.concrete.staircase import analyze_concrete_staircase
from .engine.load_combination import generate_combinations
from .engine.structure_analyzer import (
    SolverInputError, SolverNumericalError, StructureAnalyzer,
    StructureUnstableError, UnsupportedSlabError,
)


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analysis", tags=["v1 analysis"])


class ContractError(Exception):
    def __init__(
        self, code: str, message: str, status_code: int = 400,
        verification_status: VerificationStatus = VerificationStatus.NOT_EVALUATED,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.verification_status = verification_status


def _unsupported(message: str) -> ContractError:
    return ContractError("NOT_IMPLEMENTED", message, 400, VerificationStatus.NOT_IMPLEMENTED)


def _legacy_unsupported_element(result: dict) -> bool:
    """Recognize only explicit legacy dispatch refusals, not calculation errors."""
    if result.get("status") == "not_implemented":
        return True
    if result.get("status") != "error" or not isinstance(result.get("message"), str):
        return False
    message = result["message"]
    return message.startswith("Unsupported element type: ") or (
        message.startswith("Unsupported element type '") and message.endswith(" for IS code.")
    ) or (
        message.startswith("Element '") and message.endswith("not supported in steel analysis")
    )


def _plain(value: Any) -> Any:
    """Convert NumPy scalar outputs without interpreting legacy check values."""
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "item") and callable(value.item):
        return _plain(value.item())
    return value


def _legacy_element_result(request: ElementRequest, data: dict) -> dict:
    code_name = LEGACY_CODE_NAMES[request.code_id]
    kind = request.input.kind
    if kind == "beam":
        return analyze_concrete_beam(data, code_name)
    if kind == "column":
        return analyze_concrete_column(data, code_name)
    if kind == "slab":
        return {
            "solid": analyze_solid_slab,
            "hollow": analyze_hollow_slab,
            "waffle": analyze_waffle_slab,
        }[request.input.slab_type](data)
    if kind == "footing":
        return analyze_concrete_footing(data, code_name)
    if kind == "staircase":
        return analyze_concrete_staircase(data, code_name)
    handler = get_code_handler(request.code_id.value)
    if handler is None:
        raise _unsupported("No legacy handler exists for this design-code family")
    return handler.analyze(kind, data)


@router.post("/element", response_model=ElementResponse)
def analyze_element_v1(request: ElementRequest):
    value = request.input
    if request.seismic is not None:
        raise _unsupported("Seismic analysis is not implemented in the v1 contract")
    if not supports_element(request.code_id, ElementId(value.kind)):
        raise _unsupported(f"The {request.code_id.value} family has no legacy {value.kind} analysis path")
    if value.kind == "beam" and value.beam_type == "prestressed":
        raise _unsupported("Prestressed beam analysis is not implemented")
    if isinstance(value, ColumnInput) and value.column_type != "rectangular":
        raise _unsupported("Only the rectangular legacy column path is available")
    if isinstance(value, FootingInput) and value.footing_type != "isolated":
        raise _unsupported("Only the isolated legacy footing path is available")
    if isinstance(value, StaircaseInput) and value.stair_type != "straight":
        raise _unsupported("Only the straight legacy staircase path is available")
    if value.kind == "beam" and value.line_loads_kn_per_m.earthquake:
        raise _unsupported("The legacy beam path does not evaluate earthquake line load")
    if isinstance(value, SlabInput) and value.area_loads_kn_per_m2.earthquake:
        raise _unsupported("The legacy slab path does not evaluate earthquake area load")
    if isinstance(value, StaircaseInput) and (
        value.area_loads_kn_per_m2.snow or value.area_loads_kn_per_m2.earthquake
    ):
        raise _unsupported("The legacy staircase path does not evaluate snow or earthquake area load")

    try:
        canonical = normalize_element(value)
        legacy_data = element_to_legacy(canonical, request.code_id)
    except ValueError as exc:
        raise ContractError("NORMALIZATION_ERROR", "Input cannot be normalized to finite canonical units", 422) from exc
    try:
        legacy_result = _plain(_legacy_element_result(request, legacy_data))
    except ContractError:
        raise
    except Exception as exc:
        logger.exception("Legacy element engine failed")
        raise ContractError("ENGINE_FAILURE", "Analysis could not be completed", 500) from exc

    if isinstance(legacy_result, dict) and _legacy_unsupported_element(legacy_result):
        raise _unsupported("The legacy handler does not implement this element")
    if not isinstance(legacy_result, dict) or "error" in legacy_result or legacy_result.get("status") == "error":
        logger.error("Legacy element engine returned an error: %r", legacy_result)
        raise ContractError("ENGINE_FAILURE", "Analysis could not be completed", 500)

    warnings = ["Legacy calculation output has not been independently verified."]
    if isinstance(value, ColumnInput) and value.moment_kn_m:
        warnings.append("The legacy column calculation does not evaluate the supplied moment.")
    if isinstance(value, FootingInput):
        warnings.append("The legacy footing calculation assumes column geometry and soil bearing values.")
    if isinstance(value, SlabInput):
        warnings.append("Legacy slab load factors and reinforcement mechanics remain unverified.")
    if isinstance(value, StaircaseInput):
        warnings.append("The legacy staircase calculation does not use the entered stair width.")
    if value.kind == "steel_beam":
        warnings.append("The legacy steel beam capacity formula remains unverified; the UI span is interpreted as mm.")
    return ElementResponse(
        code_id=request.code_id, element_id=value.kind, canonical_input=canonical,
        legacy_unverified=LegacyElementOutput(result=legacy_result), warnings=warnings,
    )


@router.post("/structure", response_model=StructureResponse)
def analyze_structure_v1(request: StructureRequest):
    if not supports_structure(request.code_id):
        raise _unsupported(f"The {request.code_id.value} family has no structure-level legacy analysis path")
    if any(section.inertia_mm4 is not None for section in request.sections):
        raise _unsupported("The legacy frame solver does not consume an explicit section inertia")
    if request.slabs:
        raise _unsupported("Slab load transfer to frame members is not implemented")

    try:
        canonical = normalize_structure(request)
        legacy_model = structure_to_legacy(canonical)
    except ValueError as exc:
        raise ContractError("NORMALIZATION_ERROR", "Input cannot be normalized to finite canonical units", 422) from exc
    handler = get_code_handler(request.code_id.value)
    if handler is None or not hasattr(handler, "analyze_structure"):
        raise _unsupported("Structure analysis is unavailable for this code family")
    try:
        legacy_model["loads"]["combinations"] = generate_combinations(LEGACY_CODE_NAMES[request.code_id])
        raw_results = StructureAnalyzer(legacy_model).analyze_combinations()
        # All handlers expect the mapping of every combination, not one result.
        legacy_results = _plain(handler.analyze_structure(legacy_model, raw_results))
        if set(legacy_results) != set(raw_results):
            raise ValueError("Legacy handler returned a mismatched combination mapping")
    except UnsupportedSlabError as exc:
        raise _unsupported(str(exc)) from exc
    except StructureUnstableError as exc:
        raise ContractError(exc.code, str(exc), 422) from exc
    except SolverInputError as exc:
        raise ContractError(exc.code, str(exc), 422) from exc
    except SolverNumericalError as exc:
        logger.exception("Frame solver numerical failure")
        raise ContractError(exc.code, "Frame analysis could not be completed", 500) from exc
    except Exception as exc:
        logger.exception("Legacy structure engine failed")
        raise ContractError("ENGINE_FAILURE", "Structure analysis could not be completed", 500) from exc

    try:
        combinations = _canonical_combinations(raw_results)
    except Exception as exc:
        logger.exception("Legacy structure output could not be normalized")
        raise ContractError("ENGINE_FAILURE", "Structure analysis could not be completed", 500) from exc

    warnings = [
        "Legacy design results and code combinations are not engineering-verified.",
        "The compatibility adapter converts E from MPa to kN/m2 for metre/kN frame geometry.",
        "The 2D linear-elastic frame core is benchmarked only for the documented P3 cases.",
    ]
    warnings.extend(dict.fromkeys(warning for raw in raw_results.values() for warning in raw["warnings"]))
    if request.code_id not in (DesignCode.ACI, DesignCode.BS, DesignCode.EUROCODE):
        warnings.append("The legacy generator uses its generic dead-load combination for this code family.")
    return StructureResponse(
        code_id=request.code_id, canonical_input=canonical, combinations=combinations,
        legacy_unverified=LegacyStructureOutput(results=legacy_results), warnings=warnings,
    )


def _canonical_combinations(raw_results: dict) -> dict[str, CanonicalCombinationResult]:
    combinations = {}
    def canonical_end(end: dict) -> CanonicalMemberEndForce:
        return CanonicalMemberEndForce(
            axial_n=to_canonical(end["axial"], D.FORCE, "kN"),
            shear_n=to_canonical(end["shear"], D.FORCE, "kN"),
            moment_n_mm=to_canonical(end["moment"], D.MOMENT, "kN*m"),
        )
    for combo_id, raw in raw_results.items():
        combinations[combo_id] = CanonicalCombinationResult(
            name=raw["name"], expression=raw["expr"],
            displacements={node_id: CanonicalDisplacement(
                ux_mm=to_canonical(disp["ux"], D.LENGTH, "m"),
                uy_mm=to_canonical(disp["uy"], D.LENGTH, "m"),
                rz_rad=disp["rz"],
            ) for node_id, disp in raw["displacements"].items()},
            reactions={node_id: CanonicalReaction(
                rx_n=to_canonical(reaction["rx"], D.FORCE, "kN"),
                ry_n=to_canonical(reaction["ry"], D.FORCE, "kN"),
                mz_n_mm=to_canonical(reaction["mz"], D.MOMENT, "kN*m"),
            ) for node_id, reaction in raw["reactions"].items()},
            member_forces={member_id: CanonicalMemberForces(
                nmax_n=to_canonical(forces["Nmax"], D.FORCE, "kN"),
                vmax_n=to_canonical(forces["Vmax"], D.FORCE, "kN"),
                mmax_n_mm=to_canonical(forces["Mmax"], D.MOMENT, "kN*m"),
                mmax_x_mm=to_canonical(forces["Mmax_x"], D.LENGTH, "m"),
                midspan_local_y_displacement_mm=to_canonical(
                    forces["midspan_local_y_displacement"], D.LENGTH, "m",
                ),
                applied_uniform_load_n_per_mm=to_canonical(
                    forces["applied_uniform_load"], D.LINE_LOAD, "kN/m",
                ),
                end_1=canonical_end(forces["end_1"]),
                end_2=canonical_end(forces["end_2"]),
            ) for member_id, forces in raw["member_forces"].items()},
            warnings=raw["warnings"],
        )
    return combinations
