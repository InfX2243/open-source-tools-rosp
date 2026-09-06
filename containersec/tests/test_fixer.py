"""Unit tests for Dockerfile fixer."""

from containersec.core.engine import SecurityEngine
from containersec.core.fixer import DockerfileFixer


def test_fixer_replaces_add_with_copy():
    content = "FROM python:3.11\nADD main.py /app/main.py\nCMD ['python']"
    engine = SecurityEngine()
    result = engine.scan_content(content)

    fixer = DockerfileFixer(content, result)
    fixed, changes = fixer.fix()

    assert "COPY main.py /app/main.py" in fixed
    assert "USER appuser" in fixed
    assert any("Replaced insecure ADD with COPY" in c for c in changes)
