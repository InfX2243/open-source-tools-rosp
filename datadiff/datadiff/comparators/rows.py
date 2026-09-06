"""High-performance vectorized row-level comparator using Polars."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import polars as pl

from datadiff.core.models import (
    FieldChange,
    NormalizationRules,
    RowChange,
    RowDiffSummary,
)
from datadiff.core.normalizer import ValueNormalizer


class RowComparator:
    """Compares row records between datasets using primary key indexing."""

    @classmethod
    def compare(
        cls,
        df_a: pl.DataFrame,
        df_b: pl.DataFrame,
        keys: List[str],
        ignore_columns: Optional[List[str]] = None,
        rules: Optional[NormalizationRules] = None,
        max_samples: int = 50,
    ) -> RowDiffSummary:
        ignore_set = set(ignore_columns or [])
        norm = ValueNormalizer(rules or NormalizationRules())

        # Validate that keys exist in both dataframes
        for k in keys:
            if k not in df_a.columns:
                raise ValueError(f"Key column '{k}' not found in source dataset.")
            if k not in df_b.columns:
                raise ValueError(f"Key column '{k}' not found in target dataset.")

        # Check duplicate keys
        dup_a = df_a.select(keys).is_duplicated().sum()
        dup_b = df_b.select(keys).is_duplicated().sum()
        dup_count = int(dup_a + dup_b)

        # 1. Added records: In target df_b but not in source df_a
        added_df = df_b.join(df_a.select(keys), on=keys, how="anti")
        added_count = len(added_df)
        sample_added: List[RowChange] = []
        for row in added_df.head(max_samples).iter_rows(named=True):
            key_vals = {k: row[k] for k in keys}
            sample_added.append(
                RowChange(change_type="added", key_values=key_vals, row_data=row)
            )

        # 2. Removed records: In source df_a but not in target df_b
        removed_df = df_a.join(df_b.select(keys), on=keys, how="anti")
        removed_count = len(removed_df)
        sample_removed: List[RowChange] = []
        for row in removed_df.head(max_samples).iter_rows(named=True):
            key_vals = {k: row[k] for k in keys}
            sample_removed.append(
                RowChange(change_type="removed", key_values=key_vals, row_data=row)
            )

        # 3. Common records: Inner join
        # Find columns to compare (common to both and not in keys or ignore_columns)
        common_cols = [
            c for c in df_a.columns
            if c in df_b.columns and c not in keys and c not in ignore_set
        ]

        sample_modified: List[RowChange] = []
        modified_count = 0
        unchanged_count = 0

        if common_cols:
            joined_df = df_a.join(df_b, on=keys, how="inner", suffix="_tgt")
            for row in joined_df.iter_rows(named=True):
                key_vals = {k: row[k] for k in keys}
                field_diffs: List[FieldChange] = []

                for col in common_cols:
                    val_a = row[col]
                    val_b = row.get(f"{col}_tgt")
                    if not norm.are_equal(val_a, val_b):
                        field_diffs.append(
                            FieldChange(
                                column=col,
                                source_value=val_a,
                                target_value=val_b,
                            )
                        )

                if field_diffs:
                    modified_count += 1
                    if len(sample_modified) < max_samples:
                        sample_modified.append(
                            RowChange(
                                change_type="modified",
                                key_values=key_vals,
                                field_changes=field_diffs,
                            )
                        )
                else:
                    unchanged_count += 1
        else:
            # No common non-key columns to compare
            common_rows = len(df_a.join(df_b.select(keys), on=keys, how="inner"))
            unchanged_count = common_rows

        return RowDiffSummary(
            keys=keys,
            source_row_count=len(df_a),
            target_row_count=len(df_b),
            added_count=added_count,
            removed_count=removed_count,
            modified_count=modified_count,
            unchanged_count=unchanged_count,
            duplicate_keys_count=dup_count,
            sample_added=sample_added,
            sample_removed=sample_removed,
            sample_modified=sample_modified,
        )
