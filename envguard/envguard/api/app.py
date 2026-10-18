"""
FastAPI REST API & Static Server for EnvGuard Web Dashboard.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from envguard import __version__
from envguard.core.checker import check_env
from envguard.core.differ import diff_environments
from envguard.core.generator import generate_env_example
from envguard.core.scanner import scan_codebase
from envguard.core.secrets import scan_text_for_secrets

app = FastAPI(
    title="EnvGuard API",
    description="REST API for Environment & Secret Governance, Drift Checking, and Redacted Diffing",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


# Request Models
class CheckApiRequest(BaseModel):
    env_content: str
    example_content: Optional[str] = None
    schema_content: Optional[str] = None
    strict: bool = False


class DiffApiRequest(BaseModel):
    file1_content: str
    file2_content: str
    name1: str = "env_1"
    name2: str = "env_2"


class GenerateApiRequest(BaseModel):
    code_content: Optional[str] = None
    code_language: Optional[str] = "python"
    source_env_content: Optional[str] = None


class SecretsApiRequest(BaseModel):
    text_content: str
    filename: Optional[str] = "input.txt"


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the single-page EnvGuard Web Dashboard."""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>EnvGuard Dashboard</h1><p>index.html not found in web directory.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": __version__, "service": "envguard"}


@app.get("/api/sample-data")
async def get_sample_data():
    """Return pre-configured sample environments and code for one-click testing."""
    sample_env = (
        "ENVIRONMENT=development\n"
        "PORT=8000\n"
        "DEBUG=true\n"
        "DATABASE_URL=postgresql://app:secret123@localhost:5432/myapp_dev\n"
        "REDIS_URL=redis://localhost:6379/0\n"
        "STRIPE_SECRET_KEY=sk_test_51MzFakeKeyForTestingPurposesOnly12345\n"
        "SUPPORT_EMAIL=admin@myproject.org\n"
        "EXTRA_FEATURE_FLAG=enabled\n"
    )
    sample_example = (
        "# Application environment\n"
        "ENVIRONMENT=development\n\n"
        "# Server port\n"
        "PORT=8000\n\n"
        "# Debug mode\n"
        "DEBUG=false\n\n"
        "# Database URL\n"
        "DATABASE_URL=postgresql://user:password@localhost:5432/myapp_dev\n\n"
        "# Redis Cache\n"
        "REDIS_URL=redis://localhost:6379/0\n\n"
        "# Stripe Secret\n"
        "STRIPE_SECRET_KEY=your_stripe_secret_key_here\n\n"
        "# Support contact\n"
        "SUPPORT_EMAIL=support@example.com\n"
    )
    sample_staging = (
        "ENVIRONMENT=staging\n"
        "PORT=8080\n"
        "DEBUG=false\n"
        "DATABASE_URL=postgresql://staging_user:staging_pass@db.staging.internal:5432/staging_db\n"
        "REDIS_URL=redis://redis.staging.internal:6379/0\n"
        "API_KEY=stg_982347a8f723490b8f234908a7092384\n"
        "MAX_WORKERS=4\n"
    )
    sample_prod = (
        "ENVIRONMENT=production\n"
        "PORT=8080\n"
        "DEBUG=false\n"
        "DATABASE_URL=postgresql://prod_admin:pr0d_Str0ng_P@ssw0rd!@db.prod.internal:5432/production_db\n"
        "REDIS_URL=redis://redis.prod.internal:6379/0\n"
        "API_KEY=prd_890a8sdf098a0sdf890asdf890as8d0f\n"
        "MAX_WORKERS=16\n"
        "SENTRY_DSN=https://abc123def456@sentry.io/789\n"
    )
    sample_code = (
        "import os\n\n"
        "port = int(os.getenv('PORT', '8000'))\n"
        "database_url = os.environ['DATABASE_URL']\n"
        "stripe_secret = os.getenv('STRIPE_SECRET_KEY')\n"
        "redis_host = os.environ.get('REDIS_URL', 'redis://localhost:6379')\n"
        "debug_flag = os.getenv('DEBUG', 'false') == 'true'\n"
    )
    sample_secret_text = (
        "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n"
        "OPENAI_KEY=sk-proj-abc1234567890abcdef1234567890abcdef1234\n"
        "GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwxyz12\n"
        "SLACK_WEBHOOK=https://api.example.com/services/T00000000/B00000000/mock-dummy-webhook-token\n"
    )

    return {
        "env": sample_env,
        "example": sample_example,
        "staging": sample_staging,
        "prod": sample_prod,
        "code": sample_code,
        "secrets": sample_secret_text,
    }


@app.post("/api/check")
async def api_check(req: CheckApiRequest):
    """Run drift & schema check against provided .env and .env.example/schema strings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_path = os.path.join(tmpdir, ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(req.env_content)

        example_path = None
        if req.example_content and req.example_content.strip():
            example_path = os.path.join(tmpdir, ".env.example")
            with open(example_path, "w", encoding="utf-8") as f:
                f.write(req.example_content)

        schema_path = None
        if req.schema_content and req.schema_content.strip():
            schema_path = os.path.join(tmpdir, ".env.schema.yaml")
            with open(schema_path, "w", encoding="utf-8") as f:
                f.write(req.schema_content)

        result = check_env(
            env_path=env_path,
            example_path=example_path,
            schema_path=schema_path,
            strict=req.strict,
        )

        return result.model_dump()


@app.post("/api/diff")
async def api_diff(req: DiffApiRequest):
    """Run safe redacted diff between two environment strings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        p1 = os.path.join(tmpdir, f"{req.name1}.env")
        p2 = os.path.join(tmpdir, f"{req.name2}.env")

        with open(p1, "w", encoding="utf-8") as f:
            f.write(req.file1_content)
        with open(p2, "w", encoding="utf-8") as f:
            f.write(req.file2_content)

        diff_res = diff_environments(p1, p2)
        diff_res.file1_path = req.name1
        diff_res.file2_path = req.name2

        return diff_res.model_dump()


@app.post("/api/generate")
async def api_generate(req: GenerateApiRequest):
    """Scan code or source env to generate a sanitized .env.example."""
    with tempfile.TemporaryDirectory() as tmpdir:
        scan_res = None
        if req.code_content and req.code_content.strip():
            ext = ".py" if req.code_language == "python" else ".ts"
            code_file = os.path.join(tmpdir, f"app{ext}")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(req.code_content)
            scan_res = scan_codebase(tmpdir)

        source_env_path = None
        if req.source_env_content and req.source_env_content.strip():
            source_env_path = os.path.join(tmpdir, ".env")
            with open(source_env_path, "w", encoding="utf-8") as f:
                f.write(req.source_env_content)

        generated_text = generate_env_example(
            scan_result=scan_res,
            source_env_path=source_env_path,
        )

        variables_discovered = []
        if scan_res:
            for k, refs in scan_res.variables.items():
                first = refs[0]
                variables_discovered.append(
                    {
                        "key": k,
                        "occurrences": len(refs),
                        "file": first.file_path,
                        "line": first.line_number,
                        "language": first.language,
                    }
                )

        return {
            "generated_example": generated_text,
            "discovered_variables": variables_discovered,
        }


@app.post("/api/scan-secrets")
async def api_scan_secrets(req: SecretsApiRequest):
    """Scan raw text for live credentials and return findings."""
    findings = scan_text_for_secrets(req.text_content, file_path=req.filename or "input.txt")
    return {
        "findings": [f.model_dump() for f in findings],
        "count": len(findings),
    }
