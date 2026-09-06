"""Unit tests for Dockerfile parser."""

from containersec.core.parser import DockerfileParser


def test_parse_simple_dockerfile():
    content = """FROM python:3.11\nWORKDIR /app\nCMD ["python", "app.py"]"""
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    assert len(instructions) == 3
    assert instructions[0].instruction == "FROM"
    assert instructions[0].arguments == "python:3.11"
    assert instructions[1].instruction == "WORKDIR"
    assert instructions[2].instruction == "CMD"


def test_parse_multiline_continuation():
    content = """RUN apt-get update \\\n    && apt-get install -y curl \\\n    && rm -rf /var/lib/apt/lists/*"""
    parser = DockerfileParser()
    instructions = parser.parse_content(content)

    assert len(instructions) == 1
    assert instructions[0].instruction == "RUN"
    assert "curl" in instructions[0].arguments
    assert "rm -rf" in instructions[0].arguments
