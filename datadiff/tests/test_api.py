"""Tests for FastAPI backend."""

from fastapi.testclient import TestClient
from datadiff.api.app import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "datadiff"


def test_api_sample_compare():
    res = client.get("/api/v1/compare/sample/customers")
    assert res.status_code == 200
    data = res.json()
    assert data["source_name"] == "customers_v1.csv"
    assert data["row_diff"]["added_count"] == 1
    assert data["row_diff"]["removed_count"] == 1


def test_api_history():
    res = client.get("/api/v1/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
