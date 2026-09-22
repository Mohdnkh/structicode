"""P12 deployment-package safety and dependency-boundary regressions."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from backend.api import main as main_module
from backend.api.data.database import configure_database
from backend.api.utils.pdf_generator import generate_pdf
from scripts.production_preflight import validate_environment


VALID_PRODUCTION = {
    "STRUCTICODE_RUNTIME_MODE": "production",
    "STRUCTICODE_DATABASE_URL": "postgresql+psycopg2://app:password@db.example/app",
    "STRUCTICODE_AUTH_SECRET": "p12-test-secret-with-at-least-32-bytes",
    "STRUCTICODE_CORS_ORIGINS": "https://app.example.com",
    "STRUCTICODE_MAX_REQUEST_BYTES": "1048576",
    "STRUCTICODE_RATE_LIMIT_WINDOW_SECONDS": "60",
    "STRUCTICODE_RATE_LIMIT_AUTH": "60",
    "STRUCTICODE_RATE_LIMIT_ANALYSIS": "1000",
    "PORT": "8000",
}


def test_production_preflight_accepts_valid_postgresql_configuration():
    assert validate_environment(VALID_PRODUCTION) == []


def test_production_preflight_rejects_local_sqlite_and_unsafe_cors():
    values = {**VALID_PRODUCTION, "STRUCTICODE_DATABASE_URL": "sqlite:///./local.db",
              "STRUCTICODE_AUTH_SECRET": "short", "STRUCTICODE_CORS_ORIGINS": "*"}
    errors = validate_environment(values)
    assert any("PostgreSQL" in error for error in errors)
    assert any("32 UTF-8 bytes" in error for error in errors)
    assert any("wildcard" in error for error in errors)


def test_readiness_is_minimal_and_does_not_leak_database_errors(monkeypatch: pytest.MonkeyPatch):
    configure_database("sqlite:///:memory:")
    client = TestClient(main_module.app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}

    class BrokenEngine:
        def connect(self):
            raise RuntimeError("postgres-password-must-not-leak")

    monkeypatch.setattr(main_module, "get_engine", lambda: BrokenEngine())
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "postgres-password" not in response.text
    configure_database()


def test_legacy_pdf_uses_configured_temporary_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("STRUCTICODE_TEMP_DIR", str(tmp_path))
    output = generate_pdf({"code": "ACI", "element": "beam"}, {"result": {"structural": {}}})
    path = Path(output)
    assert path.parent == tmp_path
    assert path.is_file()
    assert not (tmp_path / "reports").exists()
    path.unlink()
