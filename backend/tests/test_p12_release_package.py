"""P12 deployment-package safety and dependency-boundary regressions."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from backend.api import main as main_module
from backend.api.data.database import configure_database
from backend.api.utils.pdf_generator import generate_pdf
from scripts.production_preflight import validate_environment
import scripts.start_production as start_production


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
    assert any("invalid browser origin" in error for error in errors)


@pytest.mark.parametrize(
    "origin",
    [
        "https://app.example.com",
        "https://app.example.com:8443",
    ],
)
def test_production_preflight_accepts_exact_browser_origins(origin):
    assert validate_environment({**VALID_PRODUCTION, "STRUCTICODE_CORS_ORIGINS": origin}) == []


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "http://app.example.com",
        "https://",
        "https://app.example.com/",
        "https://app.example.com/path",
        "https://app.example.com?x=1",
        "https://app.example.com#fragment",
        "https://user:password@app.example.com",
        "https://app.example.com:bad",
    ],
)
def test_production_preflight_rejects_non_origin_cors_shapes(origin):
    errors = validate_environment({**VALID_PRODUCTION, "STRUCTICODE_CORS_ORIGINS": origin})
    assert any("STRUCTICODE_CORS_ORIGINS contains an invalid browser origin" == error for error in errors)


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql+psycopg2://user:pass@/database",
        "postgresql+psycopg2://user:pass@db.example/",
        "postgresql+psycopg2://user:pass@db.example:bad/database",
    ],
)
def test_production_preflight_rejects_unusable_postgresql_urls(database_url):
    errors = validate_environment({**VALID_PRODUCTION, "STRUCTICODE_DATABASE_URL": database_url})
    assert any(error.startswith("STRUCTICODE_DATABASE_URL") for error in errors)
    assert database_url not in " ".join(errors)


def _set_production_environment(monkeypatch: pytest.MonkeyPatch, **overrides):
    for name, value in {**VALID_PRODUCTION, **overrides}.items():
        monkeypatch.setenv(name, value)


def test_production_launcher_refuses_invalid_configuration(monkeypatch: pytest.MonkeyPatch):
    _set_production_environment(monkeypatch, STRUCTICODE_DATABASE_URL="", STRUCTICODE_AUTH_SECRET="short", STRUCTICODE_CORS_ORIGINS="https://app.example.com/path")
    called = False

    def unexpected_run(**kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(start_production.uvicorn, "run", unexpected_run)
    with pytest.raises(SystemExit) as raised:
        start_production.main()
    assert raised.value.code != 0
    assert called is False


def test_production_launcher_starts_one_valid_worker(monkeypatch: pytest.MonkeyPatch):
    _set_production_environment(monkeypatch, PORT="8123")
    captured = {}

    def stop_after_capture(app, **kwargs):
        captured.update({"app": app, **kwargs})
        raise RuntimeError("test stop")

    monkeypatch.setattr(start_production.uvicorn, "run", stop_after_capture)
    with pytest.raises(RuntimeError, match="test stop"):
        start_production.main()
    assert captured == {
        "app": "backend.api.main:app",
        "host": "0.0.0.0",
        "port": 8123,
        "workers": 1,
        "reload": False,
    }


def test_production_launcher_uses_default_port(monkeypatch: pytest.MonkeyPatch):
    _set_production_environment(monkeypatch)
    monkeypatch.delenv("PORT")
    captured = {}

    def stop_after_capture(app, **kwargs):
        captured.update({"app": app, **kwargs})
        raise RuntimeError("test stop")

    monkeypatch.setattr(start_production.uvicorn, "run", stop_after_capture)
    with pytest.raises(RuntimeError, match="test stop"):
        start_production.main()
    assert captured["port"] == 8000


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
