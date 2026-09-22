"""Persistent P9 ownership, project, and trace metadata models."""
from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utc_now() -> datetime: return datetime.now(timezone.utc)
def uuid_id() -> str: return str(uuid4())

class MembershipRole(StrEnum): OWNER="OWNER"; MEMBER="MEMBER"
class ProjectState(StrEnum): ACTIVE="ACTIVE"; ARCHIVED="ARCHIVED"

class User(Base):
    __tablename__="users"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    email: Mapped[str]=mapped_column(String(320),unique=True,index=True,nullable=False)
    password_hash: Mapped[str]=mapped_column(String(255),nullable=False)
    display_name: Mapped[str]=mapped_column(String(120),nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now,onupdate=utc_now)

class Organization(Base):
    __tablename__="organizations"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    name: Mapped[str]=mapped_column(String(160),nullable=False)
    created_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False,index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now,onupdate=utc_now)

class OrganizationMembership(Base):
    __tablename__="organization_memberships"
    __table_args__=(UniqueConstraint("organization_id","user_id",name="uq_membership_organization_user"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    organization_id: Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="CASCADE"),nullable=False,index=True)
    user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    role: Mapped[str]=mapped_column(String(16),nullable=False,default=MembershipRole.MEMBER.value)
    created_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)

class Project(Base):
    __tablename__="projects"
    __table_args__=(Index("ix_projects_organization_created", "organization_id", "created_at"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    organization_id: Mapped[str]=mapped_column(ForeignKey("organizations.id",ondelete="RESTRICT"),nullable=False,index=True)
    name: Mapped[str]=mapped_column(String(160),nullable=False)
    description: Mapped[str|None]=mapped_column(Text,nullable=True)
    state: Mapped[str]=mapped_column(String(16),nullable=False,default=ProjectState.ACTIVE.value)
    version: Mapped[int]=mapped_column(Integer,nullable=False,default=1)
    created_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False)
    updated_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now,onupdate=utc_now)

class EngineVersion(Base):
    __tablename__="engine_versions"
    __table_args__=(UniqueConstraint("engine_id","engine_version","repository_commit_sha","analysis_run_schema_version","report_schema_version",name="uq_engine_version_identity"),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    engine_id: Mapped[str]=mapped_column(String(120),nullable=False)
    engine_version: Mapped[str]=mapped_column(String(80),nullable=False)
    repository_commit_sha: Mapped[str]=mapped_column(String(80),nullable=False,default="unknown")
    analysis_run_schema_version: Mapped[str]=mapped_column(String(80),nullable=False)
    report_schema_version: Mapped[str]=mapped_column(String(80),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)

class PersistentAnalysisRun(Base):
    __tablename__="persistent_analysis_runs"
    __table_args__=(Index("ix_runs_project_created", "project_id", "created_at"),)
    run_id: Mapped[str]=mapped_column(String(36),primary_key=True)
    project_id: Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="RESTRICT"),nullable=False,index=True)
    created_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False,index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    analysis_kind: Mapped[str]=mapped_column(String(20),nullable=False)
    code_family_id: Mapped[str]=mapped_column(String(40),nullable=False)
    verification_status: Mapped[str]=mapped_column(String(48),nullable=False)
    analysis_run_schema_version: Mapped[str]=mapped_column(String(80),nullable=False)
    engine_version_id: Mapped[str]=mapped_column(ForeignKey("engine_versions.id",ondelete="RESTRICT"),nullable=False)
    record_json: Mapped[str]=mapped_column(Text,nullable=False)
    input_sha256: Mapped[str]=mapped_column(String(64),nullable=False)
    result_sha256: Mapped[str]=mapped_column(String(64),nullable=False)
    record_sha256: Mapped[str]=mapped_column(String(64),nullable=False)

class ReportRecord(Base):
    __tablename__="report_records"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uuid_id)
    run_id: Mapped[str]=mapped_column(ForeignKey("persistent_analysis_runs.run_id",ondelete="RESTRICT"),nullable=False,index=True)
    project_id: Mapped[str]=mapped_column(ForeignKey("projects.id",ondelete="RESTRICT"),nullable=False,index=True)
    generated_by_user_id: Mapped[str]=mapped_column(ForeignKey("users.id",ondelete="RESTRICT"),nullable=False)
    report_schema_version: Mapped[str]=mapped_column(String(80),nullable=False)
    content_sha256: Mapped[str|None]=mapped_column(String(64),nullable=True)
    generated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,default=utc_now)
