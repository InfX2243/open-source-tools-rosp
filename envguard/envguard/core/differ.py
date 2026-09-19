"""
Safe, redacted environment comparison engine.
"""

from typing import List
from envguard.core.models import DiffField, DiffResult, DiffType
from envguard.core.parser import parse_env_file
from envguard.core.secrets import calculate_entropy, mask_secret


def diff_environments(file1_path: str, file2_path: str) -> DiffResult:
    """
    Compare two environment files without disclosing sensitive values.
    Returns categorized differences with length, entropy, and masked previews.
    """
    env1 = parse_env_file(file1_path)
    env2 = parse_env_file(file2_path)

    all_keys = sorted(set(env1.variables.keys()) | set(env2.variables.keys()))
    fields: List[DiffField] = []

    matched = 0
    added = 0
    removed = 0
    modified = 0

    for key in all_keys:
        in_1 = key in env1.variables
        in_2 = key in env2.variables

        v1 = env1.variables[key].value if in_1 else None
        v2 = env2.variables[key].value if in_2 else None

        len1 = len(v1) if v1 is not None else None
        len2 = len(v2) if v2 is not None else None

        ent1 = calculate_entropy(v1) if v1 is not None else None
        ent2 = calculate_entropy(v2) if v2 is not None else None

        preview1 = mask_secret(v1) if v1 is not None else None
        preview2 = mask_secret(v2) if v2 is not None else None

        if in_1 and not in_2:
            dtype = DiffType.REMOVED
            removed += 1
        elif not in_1 and in_2:
            dtype = DiffType.ADDED
            added += 1
        elif v1 == v2:
            dtype = DiffType.MATCH
            matched += 1
        else:
            dtype = DiffType.MODIFIED
            modified += 1

        fields.append(
            DiffField(
                key=key,
                diff_type=dtype,
                file1_present=in_1,
                file2_present=in_2,
                file1_len=len1,
                file2_len=len2,
                file1_entropy=ent1,
                file2_entropy=ent2,
                masked_preview1=preview1,
                masked_preview2=preview2,
            )
        )

    return DiffResult(
        file1_path=file1_path,
        file2_path=file2_path,
        fields=fields,
        total_keys=len(all_keys),
        matched=matched,
        added=added,
        removed=removed,
        modified=modified,
    )
