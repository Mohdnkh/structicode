"""P9 service boundaries for tenant authorization and immutable P7 persistence."""
from __future__ import annotations
from hashlib import sha256
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.api.auth.security import EnterpriseError
from backend.api.data.models import EngineVersion, OrganizationMembership, PersistentAnalysisRun, Project, ReportRecord
from backend.api.reporting.models import AnalysisRunRecord, hash_canonical

def membership_for_project(session:Session,user_id:str,project_id:str)->Project:
    project=session.get(Project,project_id)
    if project is None: raise EnterpriseError("PROJECT_NOT_FOUND","Project was not found",404)
    member=session.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==project.organization_id,OrganizationMembership.user_id==user_id))
    if member is None: raise EnterpriseError("PROJECT_NOT_FOUND","Project was not found",404)
    return project

def engine_version_for_run(session:Session,record:AnalysisRunRecord)->EngineVersion:
    meta=record.engine_metadata
    item=session.scalar(select(EngineVersion).where(EngineVersion.engine_id==meta.engine_id,EngineVersion.engine_version==meta.engine_version,EngineVersion.repository_commit_sha==meta.repository_commit_sha,EngineVersion.analysis_run_schema_version==record.schema_version,EngineVersion.report_schema_version==meta.report_schema_version))
    if item is None:
        candidate=EngineVersion(engine_id=meta.engine_id,engine_version=meta.engine_version,repository_commit_sha=meta.repository_commit_sha,analysis_run_schema_version=record.schema_version,report_schema_version=meta.report_schema_version)
        try:
            with session.begin_nested():
                session.add(candidate); session.flush()
            item = candidate
        except IntegrityError:
            item = session.scalar(select(EngineVersion).where(EngineVersion.engine_id==meta.engine_id,EngineVersion.engine_version==meta.engine_version,EngineVersion.repository_commit_sha==meta.repository_commit_sha,EngineVersion.analysis_run_schema_version==record.schema_version,EngineVersion.report_schema_version==meta.report_schema_version))
            if item is None: raise
    return item

def assert_integrity(record:AnalysisRunRecord)->None:
    input_hash=hash_canonical(record.canonical_input_snapshot); result_hash=hash_canonical({"canonical_result_snapshot":record.canonical_result_snapshot,"legacy_unverified_snapshot":record.legacy_unverified_snapshot})
    # Rebuild through the P7 deterministic payload path without changing the stored record.
    from backend.api.reporting.models import _record_hash_payload
    payload=_record_hash_payload(analysis_kind=record.analysis_kind,code_family_id=record.code_family_id,element_id=record.element_id,request_status=record.request_status,verification_status=record.verification_status,canonical_input_snapshot=record.canonical_input_snapshot,canonical_result_snapshot=record.canonical_result_snapshot,legacy_unverified_snapshot=record.legacy_unverified_snapshot,warnings=record.warnings,capability_snapshot=record.capability_snapshot,engine_metadata=record.engine_metadata,canonical_units=record.canonical_units,schema_version=record.schema_version)
    if input_hash!=record.input_hash_sha256 or result_hash!=record.result_hash_sha256 or hash_canonical(payload)!=record.record_hash_sha256: raise EnterpriseError("RUN_INTEGRITY_ERROR","Stored analysis integrity validation failed",500)

def persist_run(session:Session,record:AnalysisRunRecord,project:Project,user_id:str)->PersistentAnalysisRun:
    assert_integrity(record); engine=engine_version_for_run(session,record)
    row=PersistentAnalysisRun(run_id=record.run_id,project_id=project.id,created_by_user_id=user_id,created_at=record.created_at,analysis_kind=record.analysis_kind,code_family_id=record.code_family_id,verification_status=record.verification_status.value,analysis_run_schema_version=record.schema_version,engine_version_id=engine.id,record_json=record.model_dump_json(),input_sha256=record.input_hash_sha256,result_sha256=record.result_hash_sha256,record_sha256=record.record_hash_sha256); session.add(row); return row

def load_persistent_run(session:Session,user_id:str,run_id:str)->tuple[PersistentAnalysisRun,AnalysisRunRecord]:
    row=session.get(PersistentAnalysisRun,run_id)
    if row is None: raise EnterpriseError("PROJECT_RUN_NOT_FOUND","Analysis run was not found",404)
    membership_for_project(session,user_id,row.project_id)
    try: record=AnalysisRunRecord.model_validate_json(row.record_json); assert_integrity(record)
    except EnterpriseError: raise
    except Exception as exc: raise EnterpriseError("RUN_INTEGRITY_ERROR","Stored analysis integrity validation failed",500) from exc
    if record.run_id!=row.run_id or record.input_hash_sha256!=row.input_sha256 or record.result_hash_sha256!=row.result_sha256 or record.record_hash_sha256!=row.record_sha256: raise EnterpriseError("RUN_INTEGRITY_ERROR","Stored analysis integrity validation failed",500)
    return row,record

def report_record(session:Session,row:PersistentAnalysisRun,user_id:str,content:bytes,report_schema_version:str)->None:
    session.add(ReportRecord(run_id=row.run_id,project_id=row.project_id,generated_by_user_id=user_id,report_schema_version=report_schema_version,content_sha256=sha256(content).hexdigest()))
class EntitlementProvider:
    def can_create_project(self, _user_id:str)->bool:return True
    def can_persist_analysis_run(self,_user_id:str,_project_id:str)->bool:return True
LOCAL_ENTITLEMENTS=EntitlementProvider()
