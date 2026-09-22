"""Focused PostgreSQL release gate for P12.

The suite is intentionally opt-in. CI sets STRUCTICODE_POSTGRES_TEST and runs it
against a clean PostgreSQL 16 service after Alembic has created the schema.
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api.data.database import configure_database
from backend.api.main import app


DATABASE_URL = os.getenv("STRUCTICODE_DATABASE_URL", "")
pytestmark = pytest.mark.skipif(
    os.getenv("STRUCTICODE_POSTGRES_TEST") != "1" or not DATABASE_URL.startswith("postgresql"),
    reason="PostgreSQL compatibility gate is enabled only in the PostgreSQL CI job",
)


ELEMENT = {
    "kind": "beam", "width_cm": 30, "depth_cm": 60, "span_m": 5,
    "cover_cm": 3, "fc_mpa": 25, "fy_mpa": 420,
    "bar_count": 4, "bar_diameter_mm": 16,
}


def _headers(account: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {account['access_token']}"}


@pytest.fixture(scope="module", autouse=True)
def configured_postgres():
    previous_url = os.environ.get("STRUCTICODE_DATABASE_URL")
    previous_secret = os.environ.get("STRUCTICODE_AUTH_SECRET")
    os.environ["STRUCTICODE_DATABASE_URL"] = DATABASE_URL
    os.environ["STRUCTICODE_AUTH_SECRET"] = "p12-postgres-test-secret-with-32-bytes"
    configure_database(DATABASE_URL)
    yield
    if previous_url is None:
        os.environ.pop("STRUCTICODE_DATABASE_URL", None)
    else:
        os.environ["STRUCTICODE_DATABASE_URL"] = previous_url
    if previous_secret is None:
        os.environ.pop("STRUCTICODE_AUTH_SECRET", None)
    else:
        os.environ["STRUCTICODE_AUTH_SECRET"] = previous_secret
    configure_database()


def test_postgres_auth_project_persistence_report_tenant_isolation_and_versioning():
    client = TestClient(app)
    suffix = uuid4().hex[:10]
    alpha = client.post("/api/v1/auth/register", json={
        "email": f"alpha-{suffix}@example.com", "password": "P12-postgres-password!",
        "display_name": "Alpha",
    })
    beta = client.post("/api/v1/auth/register", json={
        "email": f"beta-{suffix}@example.com", "password": "P12-postgres-password!",
        "display_name": "Beta",
    })
    assert alpha.status_code == 201 and beta.status_code == 201
    alpha_body, beta_body = alpha.json(), beta.json()
    alpha_headers, beta_headers = _headers(alpha_body), _headers(beta_body)

    organizations = client.get("/api/v1/organizations", headers=alpha_headers)
    assert organizations.status_code == 200
    project = client.post("/api/v1/projects", headers=alpha_headers, json={
        "organization_id": organizations.json()[0]["id"],
        "name": "PostgreSQL release gate",
    })
    assert project.status_code == 201
    project_id = project.json()["id"]

    updated = client.patch(
        f"/api/v1/projects/{project_id}", headers=alpha_headers,
        json={"name": "PostgreSQL release gate v2", "expected_version": 1},
    )
    assert updated.status_code == 200 and updated.json()["version"] == 2
    conflict = client.patch(
        f"/api/v1/projects/{project_id}", headers=alpha_headers,
        json={"name": "stale", "expected_version": 1},
    )
    assert conflict.status_code == 409

    run = client.post(
        "/api/v1/analysis/element", headers=alpha_headers,
        json={"code_id": "aci", "project_id": project_id, "input": ELEMENT},
    )
    assert run.status_code == 200 and run.json()["persistence_state"] == "PROJECT_PERSISTED"
    run_id = run.json()["analysis_run_id"]
    assert client.get(f"/api/v1/analysis-runs/{run_id}", headers=alpha_headers).status_code == 200
    report = client.get(f"/api/v1/reports/{run_id}.pdf", headers=alpha_headers)
    assert report.status_code == 200 and report.content.startswith(b"%PDF")

    assert client.get(f"/api/v1/analysis-runs/{run_id}").status_code == 401
    assert client.get(f"/api/v1/analysis-runs/{run_id}", headers=beta_headers).status_code == 404
    assert client.get(f"/api/v1/reports/{run_id}.pdf", headers=beta_headers).status_code == 404
