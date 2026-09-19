"""
Secret detection regex patterns, entropy analysis, and masking utilities.
"""

import math
import re
from typing import List, Optional, Tuple
from envguard.core.models import SecretFinding, Severity


SECRET_RULES = [
    {
        "name": "AWS Access Key ID",
        "pattern": re.compile(r"\b(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b"),
        "severity": Severity.CRITICAL,
        "description": "Exposed AWS Access Key ID detected.",
    },
    {
        "name": "GitHub Personal Access Token",
        "pattern": re.compile(r"\b(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})\b"),
        "severity": Severity.CRITICAL,
        "description": "Exposed GitHub Personal Access Token detected.",
    },
    {
        "name": "OpenAI API Key",
        "pattern": re.compile(r"\b(sk-[a-zA-Z0-9]{32,}|sk-proj-[a-zA-Z0-9_-]{40,})\b"),
        "severity": Severity.CRITICAL,
        "description": "Exposed OpenAI API secret key detected.",
    },
    {
        "name": "Stripe Live Secret Key",
        "pattern": re.compile(r"\b(sk_live_[0-9a-zA-Z]{24,}|rk_live_[0-9a-zA-Z]{24,})\b"),
        "severity": Severity.CRITICAL,
        "description": "Exposed Stripe Live Secret Key detected.",
    },
    {
        "name": "Slack Token",
        "pattern": re.compile(r"\b(xox[baprs]-[0-9a-zA-Z]{10,48})\b"),
        "severity": Severity.HIGH,
        "description": "Exposed Slack Bot/User Token detected.",
    },
    {
        "name": "Slack Webhook URL",
        "pattern": re.compile(r"https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9a-zA-Z]+"),
        "severity": Severity.HIGH,
        "description": "Exposed Slack incoming webhook URL detected.",
    },
    {
        "name": "Private Cryptographic Key",
        "pattern": re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PGP|ENCRYPTED|PRIVATE)? ?KEY-----"),
        "severity": Severity.CRITICAL,
        "description": "Private cryptographic key block detected.",
    },
    {
        "name": "JSON Web Token (JWT)",
        "pattern": re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b"),
        "severity": Severity.HIGH,
        "description": "Raw JSON Web Token (JWT) detected.",
    },
]


def calculate_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not text:
        return 0.0
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    length = len(text)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return round(entropy, 2)


def mask_secret(value: str) -> str:
    """Redact secret string, leaving first 3 and last 2 characters visible."""
    val = value.strip()
    if len(val) <= 6:
        return "*" * len(val)
    return f"{val[:3]}{'*' * (len(val) - 5)}{val[-2:]}"


def scan_text_for_secrets(text: str, file_path: str = "") -> List[SecretFinding]:
    """Scan arbitrary text line-by-line for high-risk secret signatures."""
    findings: List[SecretFinding] = []
    lines = text.splitlines()

    for line_idx, line in enumerate(lines, start=1):
        for rule in SECRET_RULES:
            match = rule["pattern"].search(line)
            if match:
                matched_str = match.group(0)
                findings.append(
                    SecretFinding(
                        file_path=file_path,
                        line_number=line_idx,
                        key_name=rule["name"],
                        secret_type=rule["name"],
                        masked_preview=mask_secret(matched_str),
                        severity=rule["severity"],
                        description=rule["description"],
                    )
                )

    return findings
