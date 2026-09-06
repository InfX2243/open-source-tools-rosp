"""Configuration loader for ContainerSec."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import yaml

from containersec.core.models import ScanConfig, ScanPolicy, Severity


def load_config(config_path: Optional[str | Path] = None) -> ScanConfig:
    """Load configuration from a YAML file or use default settings.

    Looks for:
    1. Specified config_path
    2. .containersec.yaml in current directory
    3. containersec.yaml in current directory
    """
    candidates = []
    if config_path:
        candidates.append(Path(config_path))
    else:
        candidates.extend([
            Path(".containersec.yaml"),
            Path(".containersec.yml"),
            Path("containersec.yaml"),
        ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                policy_data = data.get("policy", {})
                policy = ScanPolicy(
                    max_critical=policy_data.get("max_critical", 0),
                    max_high=policy_data.get("max_high", 0),
                    max_medium=policy_data.get("max_medium", None),
                    min_score=policy_data.get("min_score", 60),
                    fail_on_secrets=policy_data.get("fail_on_secrets", True),
                )

                sev_str = data.get("severity_threshold", "INFO").upper()
                try:
                    sev = Severity(sev_str)
                except ValueError:
                    sev = Severity.INFO

                return ScanConfig(
                    target_path=data.get("target_path"),
                    policy=policy,
                    ignore_rules=data.get("ignore_rules", []),
                    severity_threshold=sev,
                )
            except Exception:
                # Fallback to default on parse errors
                pass

    return ScanConfig()
