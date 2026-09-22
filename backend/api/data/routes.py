"""Minimal authenticated organization and project APIs."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.api.auth.security import EnterpriseError, current_user
from backend.api.data.database import get_db
from backend.api.data.models import Organization, OrganizationMembership, PersistentAnalysisRun, Project, User
from backend.api.data.services import LOCAL_ENTITLEMENTS, membership_for_project
router=APIRouter(prefix="/api/v1",tags=["v1 projects"])
class Model(BaseModel): model_config=ConfigDict(extra="forbid")
class OrganizationResponse(Model): id:str; name:str; role:str; created_at:datetime
class ProjectCreate(Model): organization_id:str; name:str=Field(min_length=1,max_length=160); description:str|None=Field(default=None,max_length=4000)
class ProjectUpdate(Model): name:str|None=Field(default=None,min_length=1,max_length=160); description:str|None=Field(default=None,max_length=4000); expected_version:int|None=Field(default=None,ge=1)
class ProjectResponse(Model): id:str; organization_id:str; name:str; description:str|None; state:str; version:int; created_by_user_id:str; updated_by_user_id:str; created_at:datetime; updated_at:datetime
class RunSummary(Model): run_id:str; analysis_kind:str; code_family_id:str; verification_status:str; created_at:datetime; input_sha256:str; result_sha256:str; record_sha256:str

def project_response(item:Project)->ProjectResponse:return ProjectResponse.model_validate(item,from_attributes=True)
@router.get("/organizations",response_model=list[OrganizationResponse])
def organizations(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(select(Organization,OrganizationMembership).join(OrganizationMembership,Organization.id==OrganizationMembership.organization_id).where(OrganizationMembership.user_id==user.id).order_by(Organization.created_at)).all()
    return [OrganizationResponse(id=org.id,name=org.name,role=membership.role,created_at=org.created_at) for org,membership in rows]
@router.get("/projects",response_model=list[ProjectResponse])
def projects(limit:int=Query(default=50,ge=1,le=100),user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Project).join(OrganizationMembership,Project.organization_id==OrganizationMembership.organization_id).where(OrganizationMembership.user_id==user.id).order_by(Project.updated_at.desc()).limit(limit)).all(); return [project_response(row) for row in rows]
@router.post("/projects",response_model=ProjectResponse,status_code=201)
def create_project(body:ProjectCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    if not LOCAL_ENTITLEMENTS.can_create_project(user.id):raise EnterpriseError("ENTITLEMENT_DENIED","Project creation is not available",403)
    member=db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==body.organization_id,OrganizationMembership.user_id==user.id))
    if member is None: raise EnterpriseError("PROJECT_NOT_FOUND","Organization was not found",404)
    item=Project(organization_id=body.organization_id,name=body.name.strip(),description=body.description.strip() if body.description else None,created_by_user_id=user.id,updated_by_user_id=user.id);db.add(item);db.flush();return project_response(item)
@router.get("/projects/{project_id}",response_model=ProjectResponse)
def project(project_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):return project_response(membership_for_project(db,user.id,project_id))
@router.patch("/projects/{project_id}",response_model=ProjectResponse)
def update_project(project_id:str,body:ProjectUpdate,user:User=Depends(current_user),db:Session=Depends(get_db)):
    item=membership_for_project(db,user.id,project_id)
    if body.expected_version is not None and body.expected_version!=item.version:raise EnterpriseError("PROJECT_VERSION_CONFLICT","Project was changed by another request",409)
    if body.name is not None:item.name=body.name.strip()
    if body.description is not None:item.description=body.description.strip() or None
    item.version+=1;item.updated_by_user_id=user.id;db.flush();return project_response(item)
@router.get("/projects/{project_id}/analysis-runs",response_model=list[RunSummary])
def project_runs(project_id:str,limit:int=Query(default=25,ge=1,le=100),user:User=Depends(current_user),db:Session=Depends(get_db)):
    membership_for_project(db,user.id,project_id);rows=db.scalars(select(PersistentAnalysisRun).where(PersistentAnalysisRun.project_id==project_id).order_by(PersistentAnalysisRun.created_at.desc()).limit(limit)).all();return [RunSummary(run_id=x.run_id,analysis_kind=x.analysis_kind,code_family_id=x.code_family_id,verification_status=x.verification_status,created_at=x.created_at,input_sha256=x.input_sha256,result_sha256=x.result_sha256,record_sha256=x.record_sha256) for x in rows]
