"""P9 identity, tenant isolation, migration, and persistent-run regressions."""
from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import inspect, select

from backend.api.data.database import configure_database, session_scope
from backend.api.data.models import OrganizationMembership, PersistentAnalysisRun, ReportRecord, User
from backend.api.main import app
from backend.api.reporting.run_store import RUN_STORE


ELEMENT = {
    "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
    "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
    "bar_count": 4, "bar_diameter_mm": 16,
}
STRUCTURE = {
    "code_id": "aci",
    "materials": [{"id": "M1", "name": "C25", "fc_mpa": 25, "fy_mpa": 420,
                   "elastic_modulus_mpa": 25000}],
    "sections": [{"id": "S1", "name": "Rect", "shape": "rectRC", "width_m": 0.3,
                  "depth_m": 0.6, "cover_m": 0.04}],
    "nodes": [{"id": "N1", "x_m": 0, "y_m": 0, "support_id": "fixed"},
              {"id": "N2", "x_m": 5, "y_m": 0, "support_id": "free"}],
    "members": [{"id": "B1", "n1": "N1", "n2": "N2", "member_type": "beam",
                 "section_id": "S1", "material_id": "M1",
                 "loads": [{"case_id": "dead", "line_load_kn_per_m": 5}]}],
    "slabs": [],
}


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database = tmp_path / "enterprise.db"
    url = f"sqlite:///{database.as_posix()}"
    monkeypatch.setenv("STRUCTICODE_DATABASE_URL", url)
    monkeypatch.setenv("STRUCTICODE_AUTH_SECRET", "p9-test-secret-not-for-production")
    monkeypatch.setenv("STRUCTICODE_ACCESS_TOKEN_MINUTES", "30")
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    configure_database(url)
    yield TestClient(app)
    configure_database()


def register(client: TestClient, email: str, password: str = "P9-test-password!") -> dict:
    response = client.post("/api/v1/auth/register", json={
        "email": email, "password": password, "display_name": email.split("@")[0],
    })
    assert response.status_code == 201, response.text
    return response.json()


def headers(account: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {account['access_token']}"}


def project(client: TestClient, account: dict, name: str = "Tower") -> dict:
    organizations = client.get("/api/v1/organizations", headers=headers(account))
    assert organizations.status_code == 200, organizations.text
    response = client.post("/api/v1/projects", headers=headers(account), json={
        "organization_id": organizations.json()[0]["id"], "name": name,
        "description": "P9 persistence fixture",
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_empty_database_migration_creates_required_schema(client: TestClient):
    from backend.api.data.database import get_engine
    tables = set(inspect(get_engine()).get_table_names())
    assert {"users", "organizations", "organization_memberships", "projects",
            "persistent_analysis_runs", "report_records", "engine_versions"} <= tables
    constraints = inspect(get_engine()).get_unique_constraints("organization_memberships")
    assert any(set(item["column_names"]) == {"organization_id", "user_id"} for item in constraints)


def test_auth_registration_normalization_login_and_secret_safety(client: TestClient, monkeypatch):
    account = register(client, " Person@Example.com ")
    assert account["user"]["email"] == "person@example.com"
    duplicate = client.post("/api/v1/auth/register", json={"email": "PERSON@example.com", "password": "P9-test-password!", "display_name": "Second"})
    assert duplicate.status_code == 409 and duplicate.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"
    with session_scope() as session:
        stored = session.scalar(select(User).where(User.email == "person@example.com"))
        assert stored and stored.password_hash != "P9-test-password!"
        assert "P9-test-password!" not in stored.password_hash
    login = client.post("/api/v1/auth/login", json={"email": "PERSON@example.com", "password": "P9-test-password!"})
    assert login.status_code == 200
    unknown = client.post("/api/v1/auth/login", json={"email": "missing@example.com", "password": "P9-test-password!"})
    bad_password = client.post("/api/v1/auth/login", json={"email": "person@example.com", "password": "wrong-password!"})
    assert unknown.status_code == bad_password.status_code == 401
    assert unknown.json()["error"] == bad_password.json()["error"]
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/auth/me", headers=headers(account)).status_code == 200
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer broken"}).status_code == 401
    monkeypatch.delenv("STRUCTICODE_AUTH_SECRET")
    unavailable = client.post("/api/v1/auth/login", json={"email": "person@example.com", "password": "P9-test-password!"})
    assert unavailable.status_code == 503 and unavailable.json()["error"]["code"] == "AUTH_NOT_CONFIGURED"


def test_projects_versioning_and_current_membership_authorization(client: TestClient):
    alpha, beta = register(client, "alpha@example.com"), register(client, "beta@example.com")
    owned = project(client, alpha)
    listing = client.get("/api/v1/projects", headers=headers(alpha))
    assert listing.status_code == 200 and listing.json()[0]["id"] == owned["id"]
    update = client.patch(f"/api/v1/projects/{owned['id']}", headers=headers(alpha), json={"name": "Tower revised", "expected_version": 1})
    assert update.status_code == 200 and update.json()["version"] == 2
    stale = client.patch(f"/api/v1/projects/{owned['id']}", headers=headers(alpha), json={"name": "Stale", "expected_version": 1})
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "PROJECT_VERSION_CONFLICT"
    for url, method in ((f"/api/v1/projects/{owned['id']}", "get"),
                        (f"/api/v1/projects/{owned['id']}/analysis-runs", "get")):
        assert getattr(client, method)(url, headers=headers(beta)).status_code == 404
    assert client.patch(f"/api/v1/projects/{owned['id']}", headers=headers(beta), json={"name": "Foreign"}).status_code == 404
    with session_scope() as session:
        membership = session.scalar(select(OrganizationMembership).where(OrganizationMembership.user_id == alpha["user"]["id"]))
        session.delete(membership)
    assert client.get(f"/api/v1/projects/{owned['id']}", headers=headers(alpha)).status_code == 404


def test_anonymous_and_project_runs_have_correct_visibility_integrity_and_restart(client: TestClient):
    alpha, beta = register(client, "owner@example.com"), register(client, "other@example.com")
    owned = project(client, alpha)
    anonymous = client.post("/api/v1/analysis/element", json={"code_id": "aci", "input": ELEMENT})
    assert anonymous.status_code == 200 and anonymous.json()["persistence_state"] == "EPHEMERAL"
    anonymous_id = anonymous.json()["analysis_run_id"]
    assert client.get(f"/api/v1/analysis-runs/{anonymous_id}").status_code == 200
    assert client.get(f"/api/v1/reports/{anonymous_id}.pdf").status_code == 200
    unauthenticated = client.post("/api/v1/analysis/element", json={"code_id": "aci", "project_id": owned["id"], "input": ELEMENT})
    assert unauthenticated.status_code == 401
    foreign = client.post("/api/v1/analysis/element", headers=headers(beta), json={"code_id": "aci", "project_id": owned["id"], "input": ELEMENT})
    assert foreign.status_code == 404
    result = client.post("/api/v1/analysis/element", headers=headers(alpha), json={"code_id": "aci", "project_id": owned["id"], "input": ELEMENT})
    assert result.status_code == 200, result.text
    body, run_id = result.json(), result.json()["analysis_run_id"]
    assert body["persistence_state"] == "PROJECT_PERSISTED" and body["project_id"] == owned["id"]
    saved_record = client.get(f"/api/v1/analysis-runs/{run_id}", headers=headers(alpha))
    assert saved_record.status_code == 200
    hashes = saved_record.json()
    with session_scope() as session:
        row = session.get(PersistentAnalysisRun, run_id)
        assert row and row.project_id == owned["id"] and row.created_by_user_id == alpha["user"]["id"]
        assert row.input_sha256 == hashes["input_hash_sha256"]
        assert row.result_sha256 == hashes["result_hash_sha256"]
        assert row.record_sha256 == hashes["record_hash_sha256"]
    assert client.get(f"/api/v1/analysis-runs/{run_id}").status_code == 401
    assert client.get(f"/api/v1/analysis-runs/{run_id}", headers=headers(beta)).status_code == 404
    assert client.get(f"/api/v1/reports/{run_id}.pdf", headers=headers(beta)).status_code == 404
    RUN_STORE._records.clear()
    retrieved = client.get(f"/api/v1/analysis-runs/{run_id}", headers=headers(alpha))
    assert retrieved.status_code == 200 and retrieved.json()["record_hash_sha256"] == hashes["record_hash_sha256"]
    pdf = client.get(f"/api/v1/reports/{run_id}.pdf", headers=headers(alpha))
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    with session_scope() as session:
        assert session.scalar(select(ReportRecord).where(ReportRecord.run_id == run_id)) is not None
        row = session.get(PersistentAnalysisRun, run_id)
        row.record_json = row.record_json.replace('"analysis_kind":"element"', '"analysis_kind":"structure"', 1)
    tampered = client.get(f"/api/v1/analysis-runs/{run_id}", headers=headers(alpha))
    assert tampered.status_code == 500 and tampered.json()["error"]["code"] == "RUN_INTEGRITY_ERROR"


def test_project_bound_structure_analysis_persists(client: TestClient):
    account = register(client, "structure@example.com")
    owned = project(client, account, "Structure project")
    payload = {**STRUCTURE, "project_id": owned["id"]}
    response = client.post("/api/v1/analysis/structure", headers=headers(account), json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["persistence_state"] == "PROJECT_PERSISTED"
    history = client.get(f"/api/v1/projects/{owned['id']}/analysis-runs", headers=headers(account))
    assert history.status_code == 200 and history.json()[0]["analysis_kind"] == "structure"
