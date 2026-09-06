"""SARIF v2.1.0 reporter for GitHub Code Scanning integration."""

from __future__ import annotations

import json
from typing import Any, Dict
from containersec.core.models import ScanResult, Severity


def to_sarif_report(result: ScanResult) -> str:
    """Generate SARIF JSON output for GitHub Security tab integration."""
    rules_dict: Dict[str, Any] = {}
    sarif_results = []

    level_map = {
        Severity.CRITICAL: "error",
        Severity.HIGH: "error",
        Severity.MEDIUM: "warning",
        Severity.LOW: "note",
        Severity.INFO: "note",
    }

    for f in result.findings:
        if f.rule_id not in rules_dict:
            rules_dict[f.rule_id] = {
                "id": f.rule_id,
                "name": f.title,
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.description},
                "defaultConfiguration": {
                    "level": level_map.get(f.severity, "warning")
                },
                "properties": {
                    "category": f.category,
                    "tags": ["security", "docker", "cis"],
                },
            }

        line_num = f.line_number if f.line_number and f.line_number > 0 else 1
        sarif_results.append({
            "ruleId": f.rule_id,
            "level": level_map.get(f.severity, "warning"),
            "message": {"text": f"{f.title}: {f.description}"},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": result.file_path.replace("\\", "/"),
                        },
                        "region": {
                            "startLine": line_num,
                            "startColumn": 1,
                        },
                    }
                }
            ],
        })

    sarif_log = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ContainerSec",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/open-source-tools/containersec",
                        "rules": list(rules_dict.values()),
                    }
                },
                "results": sarif_results,
            }
        ],
    }

    return json.dumps(sarif_log, indent=2)
