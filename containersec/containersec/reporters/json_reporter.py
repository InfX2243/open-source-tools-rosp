"""JSON output formatter for ContainerSec."""

from __future__ import annotations

import json
from containersec.core.models import PolicyReport, ScanResult


def to_json_report(result: ScanResult, policy: PolicyReport | None = None, indent: int = 2) -> str:
    """Serialize scan result and policy output to JSON."""
    data = result.model_dump(mode="json")
    if policy:
        data["policy_evaluation"] = policy.model_dump(mode="json")
    return json.dumps(data, indent=indent)
