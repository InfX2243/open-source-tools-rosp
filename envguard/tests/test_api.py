from fastapi.testclient import TestClient
from envguard.api.app import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "envguard"


def test_api_sample_data():
    res = client.get("/api/sample-data")
    assert res.status_code == 200
    data = res.json()
    assert "env" in data
    assert "example" in data
    assert "staging" in data
    assert "prod" in data


def test_api_dashboard_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "EnvGuard" in res.text
    assert "<!DOCTYPE html>" in res.text


def test_api_check():
    payload = {
        "env_content": "PORT=8000\nDATABASE_URL=https://example.com\n",
        "example_content": "PORT=8000\nDATABASE_URL=https://example.com\n",
        "strict": False,
    }
    res = client.post("/api/check", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["passed"] is True
    assert data["total_checked"] == 2


def test_api_diff():
    payload = {
        "file1_content": "PORT=8000\nAPI_KEY=stg123\n",
        "file2_content": "PORT=8000\nAPI_KEY=prod456\nNEW_KEY=1\n",
        "name1": "staging",
        "name2": "prod",
    }
    res = client.post("/api/diff", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_keys"] == 3
    assert data["matched"] == 1


def test_api_generate():
    payload = {
        "code_content": "import os\nport = os.getenv('APP_PORT', '9000')\n",
        "code_language": "python",
    }
    res = client.post("/api/generate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "APP_PORT" in data["generated_example"]


def test_api_scan_secrets():
    payload = {
        "text_content": "AWS_KEY=AKIAIOSFODNN7EXAMPLE\nSAFE_VAL=hello\n",
        "filename": "test.env",
    }
    res = client.post("/api/scan-secrets", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    assert data["findings"][0]["secret_type"] == "AWS Access Key ID"
