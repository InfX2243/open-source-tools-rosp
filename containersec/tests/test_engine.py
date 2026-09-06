"""Integration tests for SecurityEngine."""

from containersec.core.engine import SecurityEngine
from containersec.core.models import ScanConfig, ScanPolicy, Severity


def test_engine_scans_clean_dockerfile():
    content = """FROM python:3.11-slim
WORKDIR /app
COPY app.py .
USER appuser
HEALTHCHECK CMD curl http://localhost || exit 1
CMD ["python", "app.py"]
"""
    engine = SecurityEngine()
    result = engine.scan_content(content)

    assert result.critical_count == 0
    assert result.score.points >= 90
    assert result.score.grade.value in ["A+", "A"]


def test_engine_policy_enforcement():
    content = """FROM python:latest
ENV AWS_SECRET_ACCESS_KEY="AKIA1234567890EXAMPLE"
"""
    engine = SecurityEngine(config=ScanConfig(policy=ScanPolicy(fail_on_secrets=True)))
    result = engine.scan_content(content)
    policy = engine.evaluate_policy(result)

    assert not policy.passed
    assert len(policy.failures) > 0
