"""Bounded local JWT and password helpers; no secret fallback is provided."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from os import getenv
from typing import Annotated
from fastapi import Header, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.api.data.database import session_scope
from backend.api.data.models import User

ALGORITHM="HS256"; ISSUER="structicode-local"; AUDIENCE="structicode-local"; PASSWORDS=CryptContext(schemes=["bcrypt"], deprecated="auto")

class EnterpriseError(Exception):
    def __init__(self, code: str, message: str, status_code: int=400): self.code=code; self.message=message; self.status_code=status_code

def auth_secret() -> str:
    value=getenv("STRUCTICODE_AUTH_SECRET","")
    if not value.strip(): raise EnterpriseError("AUTH_NOT_CONFIGURED","Local authentication is not configured",503)
    return value

def normalize_email(value: str) -> str: return value.strip().casefold()
def validate_password(value: str) -> None:
    if not 12 <= len(value) <= 128: raise EnterpriseError("INVALID_CREDENTIALS","Credentials do not meet the local authentication requirements",422)
def hash_password(value: str) -> str: validate_password(value); return PASSWORDS.hash(value)
def verify_password(value: str, hashed: str) -> bool: return PASSWORDS.verify(value,hashed)
def token_minutes() -> int:
    try: return min(1440,max(1,int(getenv("STRUCTICODE_ACCESS_TOKEN_MINUTES","30"))))
    except ValueError: return 30

def create_access_token(user_id: str) -> str:
    now=datetime.now(timezone.utc); payload={"sub":user_id,"iat":now,"exp":now+timedelta(minutes=token_minutes()),"iss":ISSUER,"aud":AUDIENCE}
    return jwt.encode(payload,auth_secret(),algorithm=ALGORITHM)

def decode_access_token(token: str) -> str:
    try: payload=jwt.decode(token,auth_secret(),algorithms=[ALGORITHM],issuer=ISSUER,audience=AUDIENCE)
    except JWTError as exc: raise EnterpriseError("AUTH_REQUIRED","Authentication is required",401) from exc
    subject=payload.get("sub")
    if not isinstance(subject,str) or not subject: raise EnterpriseError("AUTH_REQUIRED","Authentication is required",401)
    return subject

def user_from_authorization(authorization: str | None) -> User:
    if not authorization or not authorization.startswith("Bearer "): raise EnterpriseError("AUTH_REQUIRED","Authentication is required",401)
    user_id=decode_access_token(authorization.removeprefix("Bearer ").strip())
    try:
        with session_scope() as session:
            user=session.get(User,user_id)
            if user is None or not user.is_active: raise EnterpriseError("AUTH_REQUIRED","Authentication is required",401)
            session.expunge(user); return user
    except EnterpriseError: raise
    except Exception as exc: raise EnterpriseError("PERSISTENCE_ERROR","Local data storage is unavailable",503) from exc

def current_user(authorization: Annotated[str|None,Header()] = None) -> User: return user_from_authorization(authorization)
def current_user_from_request(request: Request) -> User: return user_from_authorization(request.headers.get("Authorization"))
