"""Auth endpoints for the explicitly local P9 identity foundation."""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.api.data.database import session_scope
from backend.api.data.models import MembershipRole, Organization, OrganizationMembership, User
from .security import EnterpriseError, create_access_token, current_user, hash_password, normalize_email, verify_password

router=APIRouter(prefix="/api/v1/auth",tags=["v1 local auth"])
class Model(BaseModel): model_config=ConfigDict(extra="forbid")
class RegisterRequest(Model): email:EmailStr; password:str=Field(min_length=12,max_length=128); display_name:str=Field(min_length=1,max_length=120)
class LoginRequest(Model): email:EmailStr; password:str=Field(min_length=1,max_length=128)
class UserResponse(Model): id:str; email:str; display_name:str; is_active:bool
class AuthResponse(Model): access_token:str; token_type:str="bearer"; user:UserResponse

def user_response(user:User)->UserResponse: return UserResponse(id=user.id,email=user.email,display_name=user.display_name,is_active=user.is_active)
@router.post("/register",response_model=AuthResponse,status_code=201)
def register(body:RegisterRequest):
    email=normalize_email(str(body.email))
    try:
        with session_scope() as session:
            if session.scalar(select(User).where(User.email==email)) is not None: raise EnterpriseError("EMAIL_ALREADY_REGISTERED","Registration could not be completed",409)
            user=User(email=email,password_hash=hash_password(body.password),display_name=body.display_name.strip()); session.add(user); session.flush()
            organization=Organization(name=f"{user.display_name} organization",created_by_user_id=user.id); session.add(organization); session.flush()
            session.add(OrganizationMembership(organization_id=organization.id,user_id=user.id,role=MembershipRole.OWNER.value,created_by_user_id=user.id)); session.flush(); session.expunge(user)
            return AuthResponse(access_token=create_access_token(user.id),user=user_response(user))
    except EnterpriseError: raise
    except IntegrityError as exc: raise EnterpriseError("EMAIL_ALREADY_REGISTERED","Registration could not be completed",409) from exc
    except Exception as exc: raise EnterpriseError("PERSISTENCE_ERROR","Local data storage is unavailable",503) from exc
@router.post("/login",response_model=AuthResponse)
def login(body:LoginRequest):
    email=normalize_email(str(body.email))
    try:
        with session_scope() as session:
            user=session.scalar(select(User).where(User.email==email))
            if user is None or not user.is_active or not verify_password(body.password,user.password_hash): raise EnterpriseError("INVALID_CREDENTIALS","Invalid email or password",401)
            session.expunge(user); return AuthResponse(access_token=create_access_token(user.id),user=user_response(user))
    except EnterpriseError: raise
    except Exception as exc: raise EnterpriseError("PERSISTENCE_ERROR","Local data storage is unavailable",503) from exc
@router.get("/me",response_model=UserResponse)
def me(user:User=Depends(current_user)): return user_response(user)
