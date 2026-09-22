"""Immutable analysis-run record models and deterministic trace hashing."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from ..domain.schemas import RequestStatus, VerificationStatus


ANALYSIS_RUN_SCHEMA_VERSION = "analysis_run_v1"
REPORT_SCHEMA_VERSION = "structicode_report_v1"
CANONICAL_UNITS = {
    "length": "mm", "force": "N", "stress": "MPa", "moment": "N·mm",
    "line_load": "N/mm", "area_load": "N/mm²", "area": "mm²",
    "inertia": "mm⁴", "rotation": "rad",
}


class FrozenRunModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EngineMetadata(FrozenRunModel):
    engine_id: str
    engine_version: str
    engineering_status: str
    application_schema_version: str = ANALYSIS_RUN_SCHEMA_VERSION
    report_schema_version: str = REPORT_SCHEMA_VERSION
    repository_commit_sha: str = "unknown"
    notes: tuple[str, ...] = ()


class AnalysisRunRecord(FrozenRunModel):
    run_id: str
    created_at: datetime
    analysis_kind: Literal["element", "structure"]
    code_family_id: str
    element_id: str | None = None
    request_status: RequestStatus
    verification_status: VerificationStatus
    canonical_input_snapshot: dict[str, Any]
    canonical_result_snapshot: dict[str, Any]
    legacy_unverified_snapshot: dict[str, Any] | None = None
    warnings: tuple[str, ...] = ()
    capability_snapshot: dict[str, Any]
    engine_metadata: EngineMetadata
    canonical_units: dict[str, str] = Field(default_factory=lambda: dict(CANONICAL_UNITS))
    input_hash_sha256: str
    result_hash_sha256: str
    record_hash_sha256: str
    schema_version: str = ANALYSIS_RUN_SCHEMA_VERSION


def canonical_json_bytes(value: Any) -> bytes:
    """Encode JSON deterministically for content hashes, never using repr()."""
    def json_default(item: Any) -> Any:
        if isinstance(item, BaseModel):
            return item.model_dump(mode="json")
        if isinstance(item, Enum):
            return item.value
        if isinstance(item, datetime):
            return item.isoformat()
        raise TypeError(f"Unsupported trace-hash value: {type(item).__name__}")
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False, default=json_default,
    ).encode("utf-8")


def hash_canonical(value: Any) -> str:
    return sha256(canonical_json_bytes(value)).hexdigest()


def _record_hash_payload(
    *, analysis_kind: str, code_family_id: str, element_id: str | None,
    request_status: RequestStatus, verification_status: VerificationStatus,
    canonical_input_snapshot: dict[str, Any], canonical_result_snapshot: dict[str, Any],
    legacy_unverified_snapshot: dict[str, Any] | None, warnings: tuple[str, ...],
    capability_snapshot: dict[str, Any], engine_metadata: EngineMetadata,
    canonical_units: dict[str, str], schema_version: str,
) -> dict[str, Any]:
    # Operational identity/time and derived hash fields are intentionally excluded,
    # so identical engineering content has an identical content hash.
    return {
        "analysis_kind": analysis_kind, "code_family_id": code_family_id,
        "element_id": element_id, "request_status": request_status,
        "verification_status": verification_status,
        "canonical_input_snapshot": canonical_input_snapshot,
        "canonical_result_snapshot": canonical_result_snapshot,
        "legacy_unverified_snapshot": legacy_unverified_snapshot,
        "warnings": warnings, "capability_snapshot": capability_snapshot,
        "engine_metadata": engine_metadata, "canonical_units": canonical_units,
        "schema_version": schema_version,
    }


def build_analysis_run(
    *, analysis_kind: Literal["element", "structure"], code_family_id: str,
    element_id: str | None, request_status: RequestStatus,
    verification_status: VerificationStatus, canonical_input_snapshot: dict[str, Any],
    canonical_result_snapshot: dict[str, Any], legacy_unverified_snapshot: dict[str, Any] | None,
    warnings: tuple[str, ...], capability_snapshot: dict[str, Any],
    engine_metadata: EngineMetadata,
) -> AnalysisRunRecord:
    units = dict(CANONICAL_UNITS)
    # JSON round-trip detaches caller-owned mutable dictionaries before storage.
    input_snapshot = json.loads(canonical_json_bytes(canonical_input_snapshot))
    result_snapshot = json.loads(canonical_json_bytes(canonical_result_snapshot))
    legacy_snapshot = (json.loads(canonical_json_bytes(legacy_unverified_snapshot))
                       if legacy_unverified_snapshot is not None else None)
    capability = json.loads(canonical_json_bytes(capability_snapshot))
    input_hash = hash_canonical(input_snapshot)
    result_hash = hash_canonical({
        "canonical_result_snapshot": result_snapshot,
        "legacy_unverified_snapshot": legacy_snapshot,
    })
    payload = _record_hash_payload(
        analysis_kind=analysis_kind, code_family_id=code_family_id, element_id=element_id,
        request_status=request_status, verification_status=verification_status,
        canonical_input_snapshot=input_snapshot, canonical_result_snapshot=result_snapshot,
        legacy_unverified_snapshot=legacy_snapshot, warnings=warnings,
        capability_snapshot=capability, engine_metadata=engine_metadata,
        canonical_units=units, schema_version=ANALYSIS_RUN_SCHEMA_VERSION,
    )
    return AnalysisRunRecord(
        run_id=str(uuid4()), created_at=datetime.now(timezone.utc), analysis_kind=analysis_kind,
        code_family_id=code_family_id, element_id=element_id,
        request_status=request_status, verification_status=verification_status,
        canonical_input_snapshot=input_snapshot, canonical_result_snapshot=result_snapshot,
        legacy_unverified_snapshot=legacy_snapshot, warnings=warnings,
        capability_snapshot=capability, engine_metadata=engine_metadata,
        canonical_units=units, input_hash_sha256=input_hash,
        result_hash_sha256=result_hash, record_hash_sha256=hash_canonical(payload),
    )
