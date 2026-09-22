"""Focused P10 security, abuse-resistance, and failure-boundary regressions."""
from __future__ import annotations

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
import pytest

from backend.api.data.database import configure_database
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


def test_persistent_record_precedes_same_id_memory_record(enterprise_client):
    registration = enterprise_client.post("/api/v1/auth/register", json={"email": "owner@example.com", "password": "P10-test-password!", "display_name": "Owner"}).json()
    organizations = enterprise_client.get("/api/v1/organizations", headers={"Authorization": f"Bearer {registration['access_token']}"}).json()
    project = enterprise_client.post("/api/v1/projects", headers={"Authorization": f"Bearer {registration['access_token']}"}, json={"organization_id": organizations[0]["id"], "name": "P10"}).json()
    result = enterprise_client.post("/api/v1/analysis/element", headers={"Authorization": f"Bearer {registration['access_token']}"}, json={**ELEMENT, "project_id": project["id"]})
    assert result.status_code == 200
    run_id = result.json()["analysis_run_id"]
    record = AnalysisRunRecord.model_validate(enterprise_client.get(f"/api/v1/analysis-runs/{run_id}", headers={"Authorization": f"Bearer {registration['access_token']}"}).json())
    RUN_STORE.put(record)
    anonymous = enterprise_client.get(f"/api/v1/analysis-runs/{run_id}")
    assert anonymous.status_code == 401
