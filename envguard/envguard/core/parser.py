"""
Robust parser for .env files with type inference and quote handling.
"""

import re
import os
from typing import Dict, List, Optional, Tuple
from envguard.core.models import EnvFile, EnvVar


TYPE_INT_REGEX = re.compile(r"^-?\d+$")
TYPE_FLOAT_REGEX = re.compile(r"^-?\d+\.\d+$")
TYPE_BOOL_REGEX = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)
TYPE_URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
TYPE_EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def infer_variable_type(key: str, value: str) -> str:
    """Infer semantic type of an environment variable value."""
    val = value.strip()
    if not val:
        return "empty"

    # Specific key heuristics
    key_upper = key.upper()
    if key_upper.endswith("_PORT") or key_upper == "PORT":
        if TYPE_INT_REGEX.match(val):
            try:
                p = int(val)
                if 1 <= p <= 65535:
                    return "port"
            except ValueError:
                pass

    if TYPE_BOOL_REGEX.match(val):
        return "boolean"

    if TYPE_URL_REGEX.match(val):
        return "url"

    if TYPE_EMAIL_REGEX.match(val):
        return "email"

    if TYPE_INT_REGEX.match(val):
        return "integer"

    if TYPE_FLOAT_REGEX.match(val):
        return "float"

    if (val.startswith("{") and val.endswith("}")) or (val.startswith("[") and val.endswith("]")):
        return "json"

    return "string"


def parse_env_line(line: str) -> Optional[Tuple[str, str, Optional[str], bool]]:
    """
    Parse a single .env line.
    Returns (key, value, comment, is_exported) or None if blank/pure comment.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    is_exported = False
    if stripped.startswith("export "):
        is_exported = True
        stripped = stripped[7:].strip()

    # Look for the first '='
    eq_idx = stripped.find("=")
    if eq_idx == -1:
        # Key without value, e.g. "DEBUG"
        key = stripped.strip()
        return key, "", None, is_exported

    key = stripped[:eq_idx].strip()
    raw_val = stripped[eq_idx + 1:].strip()

    comment = None
    value = ""

    # Check for quotes
    if raw_val.startswith(('"', "'")):
        quote_char = raw_val[0]
        # Find closing quote
        end_quote_idx = -1
        escaped = False
        for i in range(1, len(raw_val)):
            char = raw_val[i]
            if char == "\\" and not escaped:
                escaped = True
                continue
            if char == quote_char and not escaped:
                end_quote_idx = i
                break
            escaped = False

        if end_quote_idx != -1:
            value = raw_val[1:end_quote_idx]
            rest = raw_val[end_quote_idx + 1:].strip()
            if rest.startswith("#"):
                comment = rest[1:].strip()
        else:
            # Unterminated quote, take rest as value
            value = raw_val[1:]
    else:
        # Non-quoted value, check for inline comment
        comment_idx = -1
        in_space = False
        for i, ch in enumerate(raw_val):
            if ch.isspace():
                in_space = True
            elif ch == "#" and (in_space or i == 0):
                comment_idx = i
                break
            else:
                in_space = False

        if comment_idx != -1:
            value = raw_val[:comment_idx].strip()
            comment = raw_val[comment_idx + 1:].strip()
        else:
            value = raw_val

    # Unescape common sequences if double quoted
    if raw_val.startswith('"'):
        value = value.replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\"", '"')

    return key, value, comment, is_exported


def parse_env_file(file_path: str) -> EnvFile:
    """Parse a .env file from disk into an EnvFile model."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Environment file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    variables: Dict[str, EnvVar] = {}
    for idx, line in enumerate(lines, start=1):
        parsed = parse_env_line(line)
        if parsed is None:
            continue

        key, value, comment, is_exported = parsed
        inferred = infer_variable_type(key, value)
        variables[key] = EnvVar(
            key=key,
            value=value,
            line_number=idx,
            comment=comment,
            is_exported=is_exported,
            inferred_type=inferred,
        )

    return EnvFile(
        path=os.path.abspath(file_path),
        variables=variables,
        raw_lines=lines,
    )
