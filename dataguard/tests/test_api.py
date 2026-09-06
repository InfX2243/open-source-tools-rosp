"""Tests for FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "DataGuard"


def test_rule_templates():
    res = client.get("/api/v1/rules/templates")
    assert res.status_code == 200
    templates = res.json()
    assert "customer" in templates
    assert "ecommerce" in templates


def test_upload_and_validate(temp_csv_file):
    with open(temp_csv_file, "rb") as f:
        res = client.post(
            "/api/v1/validations/upload",
            files={"file": ("test.csv", f, "text/csv")},
            data={"project_name": "API Test Project"},
        )
    assert res.status_code == 200
    summary = res.json()
    assert summary["quality_score"] == 100.0
    assert summary["passed_gate"] is True


def test_validation_history():
    res = client.get("/api/v1/validations/history")
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    assert len(history) > 0


def test_projects_crud():
    import uuid
    # List projects
    res = client.get("/api/v1/projects")
    assert res.status_code == 200

    proj_name = f"Pipeline_{uuid.uuid4().hex[:8]}"
    # Create new project
    res_post = client.post(
        "/api/v1/projects",
        json={"name": proj_name, "description": "ETL warehouse checks"},
    )
    assert res_post.status_code == 200
    data = res_post.json()
    assert data["name"] == proj_name
