"""Capture v1 responses into server-owned P7 trace records."""

from __future__ import annotations

from pathlib import Path
import subprocess

from ..domain.design_code_registry import get_element_capability, get_family
from ..domain.schemas import ElementResponse, StructureResponse
from .models import EngineMetadata, build_analysis_run
from .run_store import AnalysisRunStore, RUN_STORE


def _repository_commit_sha() -> str:
    """Resolve once at import; Git metadata is optional at runtime."""
    try:
        root = Path(__file__).resolve().parents[3]
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True, timeout=1,
        )
        return completed.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


REPOSITORY_COMMIT_SHA = _repository_commit_sha()


def _capability_snapshot(code_id, element_id: str | None) -> dict:
    family = get_family(code_id)
    if family is None:
        raise ValueError("Analysis response references an unknown design-code family")
    snapshot = family.model_dump(mode="json")
    if element_id is not None:
        capability = get_element_capability(code_id, element_id)
        snapshot["relevant_element_capability"] = capability.model_dump(mode="json")
    return snapshot


def create_element_run(response: ElementResponse, store: AnalysisRunStore = RUN_STORE) -> str:
    run = build_analysis_run(
        analysis_kind="element", code_family_id=response.code_id.value,
        element_id=response.element_id, request_status=response.request_status,
        verification_status=response.verification_status,
        canonical_input_snapshot=response.canonical_input.model_dump(mode="json"),
        canonical_result_snapshot={
            "element_id": response.element_id,
            "request_status": response.request_status,
            "verification_status": response.verification_status,
        },
        legacy_unverified_snapshot=response.legacy_unverified.model_dump(mode="json"),
        warnings=tuple(dict.fromkeys(response.warnings)),
        capability_snapshot=_capability_snapshot(response.code_id, response.element_id),
        engine_metadata=EngineMetadata(
            engine_id="legacy_element_compatibility", engine_version="p7",
            engineering_status="LEGACY_UNVERIFIED",
            repository_commit_sha=REPOSITORY_COMMIT_SHA,
            notes=("Stored after validated v1 analysis; not re-run for reporting.",),
        ),
    )
    store.put(run)
    return run.run_id


def create_structure_run(response: StructureResponse, store: AnalysisRunStore = RUN_STORE) -> str:
    run = build_analysis_run(
        analysis_kind="structure", code_family_id=response.code_id.value,
        element_id=None, request_status=response.request_status,
        verification_status=response.verification_status,
        canonical_input_snapshot=response.canonical_input.model_dump(mode="json"),
        canonical_result_snapshot={
            "combinations": {key: value.model_dump(mode="json")
                             for key, value in response.combinations.items()},
            "request_status": response.request_status,
            "verification_status": response.verification_status,
        },
        legacy_unverified_snapshot=response.legacy_unverified.model_dump(mode="json"),
        warnings=tuple(dict.fromkeys(response.warnings)),
        capability_snapshot=_capability_snapshot(response.code_id, None),
        engine_metadata=EngineMetadata(
            engine_id="p3_linear_elastic_frame_with_legacy_design", engine_version="p3",
            engineering_status="ENGINEERING_REVIEW_REQUIRED",
            repository_commit_sha=REPOSITORY_COMMIT_SHA,
            notes=(
                "2D linear-elastic mechanics have bounded P3 analytical benchmarks.",
                "Complete code-specific structure design remains LEGACY_UNVERIFIED.",
            ),
        ),
    )
    store.put(run)
    return run.run_id
