"""Focused P10 security, abuse-resistance, and failure-boundary regressions."""
from __future__ import annotations

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
import pytest
from sqlalchemy import select

from backend.api.data.database import configure_database, session_scope
from backend.api.data.models import EngineVersion
from backend.api.data.services import engine_version_for_run
from backend.api.main import app
from backend.api.reporting.models import AnalysisRunRecord
from backend.api.reporting.run_store import RUN_STORE
from backend.api.security.config import approved_cors_origins
from backend.api.security.rate_limit import BoundedRateLimiter, RATE_LIMITER


ELEMENT = {
    "code_id": "aci",
    "input": {
        "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
        "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
        "bar_count": 4, "bar_diameter_mm": 16,
        "line_loads_kn_per_m": {"dead": 5, "live": 3},
    },
}


@pytest.fixture()
def enterprise_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database = tmp_path / "p10.db"
    url = f"sqlite:///{database.as_posix()}"
    monkeypatch.setenv("STRUCTICODE_DATABASE_URL", url)
    monkeypatch.setenv("STRUCTICODE_AUTH_SECRET", "p10-local-test-secret-with-at-least-32-bytes")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    configure_database(url)
    RATE_LIMITER.reset()
    RUN_STORE._records.clear()
    yield TestClient(app)
    RATE_LIMITER.reset()
    RUN_STORE._records.clear()
    configure_database()


def structure_payload(*, node_count: int = 2, member_load_count: int = 1) -> dict:
    nodes = [
        {"id": f"N{i}", "x_m": float(i), "y_m": 0, "support_id": "fixed" if i == 0 else "free"}
        for i in range(node_count)
    ]
    loads = [{"case_id": "dead", "line_load_kn_per_m": 5} for _ in range(member_load_count)]
    return {
        "code_id": "aci",
        "materials": [{"id": "M1", "name": "C25", "fc_mpa": 25, "fy_mpa": 420, "elastic_modulus_mpa": 25000}],
        "sections": [{"id": "S1", "name": "Rect", "shape": "rectRC", "width_m": 0.3, "depth_m": 0.6, "cover_m": 0.04}],
        "nodes": nodes,
        "members": [{"id": "B1", "n1": "N0", "n2": f"N{node_count - 1}", "member_type": "beam", "section_id": "S1", "material_id": "M1", "loads": loads}],
        "slabs": [],
    }


def test_cors_defaults_reject_wildcard_and_emit_security_headers(enterprise_client, monkeypatch):
    monkeypatch.setenv("STRUCTICODE_CORS_ORIGINS", "*, https://approved.example")
    assert approved_cors_origins() == ["https://approved.example"]
    allowed = enterprise_client.options("/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    blocked = enterprise_client.options("/health", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"})
    assert blocked.status_code == 400
    assert "access-control-allow-origin" not in blocked.headers
    normal = enterprise_client.get("/health")
    assert normal.headers["x-content-type-options"] == "nosniff"
    assert normal.headers["referrer-policy"] == "no-referrer"
    custom_app = FastAPI()
    custom_app.add_middleware(
        CORSMiddleware,
        allow_origins=approved_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )
    @custom_app.get("/health")
    def custom_health():
        return {"status": "ok"}
    custom = TestClient(custom_app).options(
        "/health",
        headers={"Origin": "https://approved.example", "Access-Control-Request-Method": "GET"},
    )
    assert custom.status_code == 200
    assert custom.headers["access-control-allow-origin"] == "https://approved.example"
    assert "access-control-allow-credentials" not in custom.headers


def test_request_body_limit_uses_accumulated_body(enterprise_client, monkeypatch):
    monkeypatch.setenv("STRUCTICODE_MAX_REQUEST_BYTES", "1024")
    below = enterprise_client.post("/api/v1/analysis/element", content=b"{}")
    assert below.status_code != 413
    above = enterprise_client.post("/api/v1/analysis/element", content=b"{" + (b"a" * 2048) + b"}")
    assert above.status_code == 413
    assert above.json()["error"]["code"] == "REQUEST_TOO_LARGE"
    streamed = enterprise_client.post(
        "/api/v1/analysis/element",
        content=iter((b"{", b"a" * 1500, b"}")),
        headers={"Transfer-Encoding": "chunked"},
    )
    assert streamed.status_code == 413


def test_rate_limiter_is_bounded_and_route_limit_is_deterministic(enterprise_client, monkeypatch):
    limiter = BoundedRateLimiter(max_entries=2)
    assert limiter.allow("a", 1)
    assert not limiter.allow("a", 1)
    assert limiter.allow("b", 1)
    assert limiter.allow("c", 1)
    assert limiter.size() <= 2
    monkeypatch.setenv("STRUCTICODE_RATE_LIMIT_ANALYSIS", "2")
    RATE_LIMITER.reset()
    results = [enterprise_client.post("/api/v1/analysis/element", json={}) for _ in range(3)]
    assert [response.status_code for response in results[:2]] == [422, 422]
    assert results[2].status_code == 429
    assert results[2].json()["error"]["code"] == "RATE_LIMITED"


def test_complexity_and_magnitude_guards_run_before_engine(enterprise_client, monkeypatch):
    monkeypatch.setattr("backend.api.v1.StructureAnalyzer", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("solver must not run")))
    too_many_nodes = enterprise_client.post("/api/v1/analysis/structure", json=structure_payload(node_count=257))
    assert too_many_nodes.status_code == 422
    assert too_many_nodes.json()["error"]["code"] == "MODEL_COMPLEXITY_LIMIT"
    too_many_loads = enterprise_client.post("/api/v1/analysis/structure", json=structure_payload(member_load_count=33))
    assert too_many_loads.status_code == 422
    assert too_many_loads.json()["error"]["code"] == "MODEL_COMPLEXITY_LIMIT"
    extreme = {**ELEMENT, "input": {**ELEMENT["input"], "span_m": 1e13}}
    response = enterprise_client.post("/api/v1/analysis/element", json=extreme)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "NORMALIZATION_ERROR"


def test_auth_secret_and_cache_policy(enterprise_client, monkeypatch):
    registration = enterprise_client.post("/api/v1/auth/register", json={"email": "p10@example.com", "password": "P10-test-password!", "display_name": "P10"})
    assert registration.status_code == 201
    assert registration.headers["cache-control"] == "no-store"
    monkeypatch.setenv("STRUCTICODE_AUTH_SECRET", "weak")
    blocked = enterprise_client.post("/api/v1/auth/login", json={"email": "p10@example.com", "password": "P10-test-password!"})
    assert blocked.status_code == 503 and blocked.json()["error"]["code"] == "AUTH_NOT_CONFIGURED"


def test_legacy_exception_is_sanitized(enterprise_client, monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("database password should never be returned")

    monkeypatch.setattr("backend.api.main.analyze_concrete_beam", explode)
    response = enterprise_client.post("/analyze", json={"code": "aci", "element": "beam", "data": {}})
    assert response.status_code == 200
    assert "database password" not in response.text
    assert response.json()["message"] == "Legacy analysis could not be completed"


def test_legacy_pdf_uses_isolated_temporary_files(enterprise_client):
    payload = {"data": {"code": "ACI", "element": "beam"}, "result": {"result": {"structural": {}}}}

    def request():
        with TestClient(app) as client:
            return client.post("/generate-pdf", json=payload)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: request(), range(2)))
    assert all(response.status_code == 200 and response.content.startswith(b"%PDF") for response in responses)
    names = [response.headers["content-disposition"] for response in responses]
    assert len(set(names)) == 2


def test_persistent_lookup_database_failure_fails_closed(enterprise_client, monkeypatch):
    from backend.api.reporting import report_api
    from backend.api.auth.security import EnterpriseError

    def fail(_run_id):
        raise EnterpriseError("PERSISTENCE_ERROR", "Local data storage is unavailable", 503)

    monkeypatch.setattr(report_api, "_persistent_row", fail)
    response = enterprise_client.get("/api/v1/analysis-runs/run-that-is-not-known")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PERSISTENCE_ERROR"


def test_persistent_report_database_failure_fails_closed(enterprise_client, monkeypatch):
    from backend.api.reporting import report_api
    from backend.api.auth.security import EnterpriseError

    def fail(_run_id):
        raise EnterpriseError("PERSISTENCE_ERROR", "Local data storage is unavailable", 503)

    monkeypatch.setattr(report_api, "_persistent_row", fail)
    response = enterprise_client.get("/api/v1/reports/run-that-is-not-known.pdf")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PERSISTENCE_ERROR"


def test_persistent_record_precedes_same_id_memory_record(enterprise_client):
    owner = enterprise_client.post("/api/v1/auth/register", json={"email": "owner@example.com", "password": "P10-test-password!", "display_name": "Owner"}).json()
    foreign = enterprise_client.post("/api/v1/auth/register", json={"email": "foreign@example.com", "password": "P10-test-password!", "display_name": "Foreign"}).json()
    owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
    foreign_headers = {"Authorization": f"Bearer {foreign['access_token']}"}
    organizations = enterprise_client.get("/api/v1/organizations", headers=owner_headers).json()
    project = enterprise_client.post("/api/v1/projects", headers=owner_headers, json={"organization_id": organizations[0]["id"], "name": "P10"}).json()
    result = enterprise_client.post("/api/v1/analysis/element", headers=owner_headers, json={**ELEMENT, "project_id": project["id"]})
    assert result.status_code == 200
    run_id = result.json()["analysis_run_id"]
    record = AnalysisRunRecord.model_validate(enterprise_client.get(f"/api/v1/analysis-runs/{run_id}", headers=owner_headers).json())
    RUN_STORE.put(record.model_copy(update={"warnings": (*record.warnings, "MEMORY_CONFLICT_MARKER")}))
    assert enterprise_client.get(f"/api/v1/analysis-runs/{run_id}").status_code == 401
    assert enterprise_client.get(f"/api/v1/analysis-runs/{run_id}", headers=foreign_headers).status_code == 404
    authorized = enterprise_client.get(f"/api/v1/analysis-runs/{run_id}", headers=owner_headers)
    assert authorized.status_code == 200
    assert "MEMORY_CONFLICT_MARKER" not in authorized.json()["warnings"]
    assert authorized.json()["record_hash_sha256"] == record.record_hash_sha256
    assert enterprise_client.get(f"/api/v1/reports/{run_id}.pdf").status_code == 401
    assert enterprise_client.get(f"/api/v1/reports/{run_id}.pdf", headers=foreign_headers).status_code == 404
    from backend.api.reporting import report_api
    captured = {}
    def render(persistent_record):
        captured["record"] = persistent_record
        return b"%PDF-1.4\nP10\n"
    with patch.object(report_api, "render_report_bytes", side_effect=render):
        report = enterprise_client.get(f"/api/v1/reports/{run_id}.pdf", headers=owner_headers)
    assert report.status_code == 200 and report.content.startswith(b"%PDF")
    assert "MEMORY_CONFLICT_MARKER" not in captured["record"].warnings


def test_project_version_compare_and_swap_rejects_stale_update(enterprise_client):
    owner = enterprise_client.post("/api/v1/auth/register", json={"email": "cas@example.com", "password": "P10-test-password!", "display_name": "CAS"}).json()
    headers = {"Authorization": f"Bearer {owner['access_token']}"}
    organization = enterprise_client.get("/api/v1/organizations", headers=headers).json()[0]
    project = enterprise_client.post("/api/v1/projects", headers=headers, json={"organization_id": organization["id"], "name": "Initial"}).json()
    first = enterprise_client.patch(f"/api/v1/projects/{project['id']}", headers=headers, json={"name": "Winner", "expected_version": project["version"]})
    second = enterprise_client.patch(f"/api/v1/projects/{project['id']}", headers=headers, json={"name": "Loser", "expected_version": project["version"]})
    assert first.status_code == 200 and first.json()["version"] == project["version"] + 1
    assert second.status_code == 409 and second.json()["error"]["code"] == "PROJECT_VERSION_CONFLICT"
    final = enterprise_client.get(f"/api/v1/projects/{project['id']}", headers=headers).json()
    assert final["name"] == "Winner" and final["version"] == project["version"] + 1


def test_engine_version_duplicate_recovery_is_deduplicated(enterprise_client):
    owner = enterprise_client.post("/api/v1/auth/register", json={"email": "engine@example.com", "password": "P10-test-password!", "display_name": "Engine"}).json()
    headers = {"Authorization": f"Bearer {owner['access_token']}"}
    organization = enterprise_client.get("/api/v1/organizations", headers=headers).json()[0]
    project = enterprise_client.post("/api/v1/projects", headers=headers, json={"organization_id": organization["id"], "name": "Engine"}).json()
    payload = {**ELEMENT, "project_id": project["id"]}
    first = enterprise_client.post("/api/v1/analysis/element", headers=headers, json=payload)
    second = enterprise_client.post("/api/v1/analysis/element", headers=headers, json=payload)
    assert first.status_code == second.status_code == 200
    first_record = AnalysisRunRecord.model_validate(enterprise_client.get(f"/api/v1/analysis-runs/{first.json()['analysis_run_id']}", headers=headers).json())
    with session_scope() as session:
        existing = session.scalar(select(EngineVersion))
        assert existing is not None
        with patch.object(session, "scalar", side_effect=[None, existing]):
            recovered = engine_version_for_run(session, first_record)
        assert recovered.id == existing.id
        matches = session.query(EngineVersion).filter_by(engine_id=existing.engine_id, engine_version=existing.engine_version, repository_commit_sha=existing.repository_commit_sha, analysis_run_schema_version=existing.analysis_run_schema_version, report_schema_version=existing.report_schema_version).all()
        assert len(matches) == 1


def test_documented_auth_setup_secret_meets_minimum():
    import re
    text = Path("docs/engineering/LOCAL_DATABASE_AND_AUTH.md").read_text(encoding="utf-8")
    value = re.search(r'STRUCTICODE_AUTH_SECRET = "([^"]+)"', text).group(1)
    assert len(value.encode("utf-8")) >= 32


@pytest.mark.parametrize(
    ("path", "allowed"),
    [
        (".env.example", True), (".env", False), (".env.production", False),
        ("frontend/.env.production", False), ("backend/.env.local", False),
        ("local.db", False), ("reports/report.pdf", False),
        ("backend/__pycache__/module.pyc", False),
    ],
)
def test_repository_hygiene_rules_cover_nested_environment_and_generated_files(path, allowed):
    from scripts.check_repository_hygiene import forbidden
    assert forbidden(path) is (not allowed)
