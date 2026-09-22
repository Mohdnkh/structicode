"""SQLAlchemy configuration for the local-first enterprise data foundation."""
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from os import getenv
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DEFAULT_DATABASE_URL = "sqlite:///./.structicode/structicode.db"

class Base(DeclarativeBase):
    pass

def database_url() -> str:
    return getenv("STRUCTICODE_DATABASE_URL", DEFAULT_DATABASE_URL)

def _sqlite_path(url: str) -> None:
    if url.startswith("sqlite:///") and not url.endswith(":memory:"):
        Path(url.removeprefix("sqlite:///")) .parent.mkdir(parents=True, exist_ok=True)

def build_engine(url: str | None = None) -> Engine:
    url = url or database_url()
    _sqlite_path(url)
    options = {"future": True, "pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **options)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor(); cursor.execute("PRAGMA foreign_keys=ON"); cursor.close()
    return engine

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None

def configure_database(url: str | None = None) -> None:
    """Reset process-local engine configuration; primarily used by isolated tests."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = build_engine(url)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False, future=True)

def get_engine() -> Engine:
    global _engine
    if _engine is None:
        configure_database()
    return _engine

def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        configure_database()
    return _session_factory

@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback(); raise
    finally:
        session.close()

def get_db() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session
