"""FastAPI REST API & static server for ContainerSec Web Dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from containersec import __version__
from containersec.core.engine import SecurityEngine
from containersec.core.fixer import DockerfileFixer
from containersec.rules import ALL_RULES

app = FastAPI(
    title="ContainerSec API",
    description="REST API for Dockerfile security linting, CIS benchmarks, and remediation",
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


class ScanRequest(BaseModel):
    dockerfile: str
    target_name: Optional[str] = "Dockerfile"


class FixRequest(BaseModel):
    dockerfile: str


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the single-page ContainerSec Web Dashboard."""
    index_file = WEB_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ContainerSec Web Dashboard</h1><p>index.html not found.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": __version__}


@app.get("/api/rules")
async def list_rules() -> List[Dict[str, Any]]:
    """Return all available rules definitions."""
    return [rule_cls().definition().model_dump() for rule_cls in ALL_RULES]


@app.post("/api/scan")
async def scan_dockerfile(req: ScanRequest):
    """Scan Dockerfile text directly."""
    if not req.dockerfile.strip():
        raise HTTPException(status_code=400, detail="Dockerfile content cannot be empty")

    engine = SecurityEngine()
    result = engine.scan_content(req.dockerfile, file_path=req.target_name or "Dockerfile")
    policy_report = engine.evaluate_policy(result)

    return {
        "result": result.model_dump(),
        "policy": policy_report.model_dump(),
    }


@app.post("/api/scan/upload")
async def scan_upload(file: UploadFile = File(...)):
    """Upload and scan a Dockerfile."""
    content_bytes = await file.read()
    content = content_bytes.decode("utf-8", errors="replace")

    engine = SecurityEngine()
    result = engine.scan_content(content, file_path=file.filename or "Dockerfile")
    policy_report = engine.evaluate_policy(result)

    return {
        "result": result.model_dump(),
        "policy": policy_report.model_dump(),
        "original_content": content,
    }


@app.post("/api/fix")
async def fix_dockerfile(req: FixRequest):
    """Auto-fix security violations and return remediated Dockerfile."""
    if not req.dockerfile.strip():
        raise HTTPException(status_code=400, detail="Dockerfile content cannot be empty")

    engine = SecurityEngine()
    result = engine.scan_content(req.dockerfile)
    fixer = DockerfileFixer(req.dockerfile, result)
    fixed_content, changes = fixer.fix()

    # Re-scan fixed content to compute new score
    fixed_result = engine.scan_content(fixed_content)

    return {
        "fixed_dockerfile": fixed_content,
        "changes": changes,
        "original_score": result.score.points,
        "new_score": fixed_result.score.points,
        "original_findings_count": len(result.findings),
        "new_findings_count": len(fixed_result.findings),
    }
