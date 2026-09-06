"""Core DataDiff Engine that orchestrates semantic dataset comparison."""

from __future__ import annotations

import time
from typing import List, Optional, Union
from pathlib import Path
import polars as pl

from datadiff.comparators.rows import RowComparator
from datadiff.comparators.schema import SchemaComparator
from datadiff.comparators.statistics import StatsComparator
from datadiff.core.models import (
    ComparisonPolicy,
    DiffConfig,
    DiffSummary,
    NormalizationRules,
    PolicyReport,
    RowDiffSummary,
    SchemaDiff,
    StatsDiff,
)
from datadiff.core.normalizer import ValueNormalizer
from datadiff.core.policies import PolicyEvaluator
from datadiff.sources.base import BaseSourceAdapter
from datadiff.sources.csv import CSVSourceAdapter
from datadiff.sources.json import JSONSourceAdapter
from datadiff.sources.parquet import ParquetSourceAdapter


class DataDiffEngine:
    """Core semantic comparison engine for datasets."""

    @classmethod
    def load_adapter(cls, path_or_adapter: Union[str, Path, BaseSourceAdapter], format_hint: Optional[str] = None) -> BaseSourceAdapter:
        """Resolve file path or adapter into a BaseSourceAdapter instance."""
        if isinstance(path_or_adapter, BaseSourceAdapter):
            return path_or_adapter

        path = Path(path_or_adapter)
        ext = (format_hint or path.suffix).lower().lstrip(".")

        if ext in ("csv", "tsv", "txt"):
            return CSVSourceAdapter(path)
        elif ext in ("parquet", "pq"):
            return ParquetSourceAdapter(path)
        elif ext in ("json", "ndjson", "jsonl"):
            return JSONSourceAdapter(path)
        else:
            # Default to CSV if unknown
            return CSVSourceAdapter(path)

    @classmethod
    def compare_sources(
        cls,
        source: Union[str, Path, BaseSourceAdapter, pl.DataFrame],
        target: Union[str, Path, BaseSourceAdapter, pl.DataFrame],
        key: Optional[Union[str, List[str]]] = None,
        ignore_columns: Optional[List[str]] = None,
        rules: Optional[NormalizationRules] = None,
        policies: Optional[ComparisonPolicy] = None,
        config: Optional[DiffConfig] = None,
        source_name: str = "source",
        target_name: str = "target",
    ) -> DiffSummary:
        """Execute comprehensive dataset comparison across schema, rows, statistics, and policies."""
        start_time = time.perf_counter()

        # Merge or build config
        cfg = config or DiffConfig()
        if key:
            cfg.key = [key] if isinstance(key, str) else list(key)
        if ignore_columns:
            cfg.ignore_columns = list(ignore_columns)
        if rules:
            cfg.rules = rules
        if policies:
            cfg.policies = policies

        # Load dataframes
        df_a: pl.DataFrame
        df_b: pl.DataFrame
        name_a: str = source_name
        name_b: str = target_name

        if isinstance(source, pl.DataFrame):
            df_a = source
        else:
            adapter_a = cls.load_adapter(source, cfg.source.format if cfg.source else None)
            df_a = adapter_a.load()
            if isinstance(source, (str, Path)):
                name_a = Path(source).name

        if isinstance(target, pl.DataFrame):
            df_b = target
        else:
            adapter_b = cls.load_adapter(target, cfg.target.format if cfg.target else None)
            df_b = adapter_b.load()
            if isinstance(target, (str, Path)):
                name_b = Path(target).name

        # 1. Schema Comparison
        schema_diff: SchemaDiff = SchemaComparator.compare(df_a, df_b)

        # 2. Row Comparison
        row_diff: RowDiffSummary
        if cfg.key:
            row_diff = RowComparator.compare(
                df_a=df_a,
                df_b=df_b,
                keys=cfg.key,
                ignore_columns=cfg.ignore_columns,
                rules=cfg.rules,
            )
        else:
            # No keys provided: Row count comparison only or fallback
            row_diff = RowDiffSummary(
                keys=[],
                source_row_count=len(df_a),
                target_row_count=len(df_b),
                added_count=max(0, len(df_b) - len(df_a)),
                removed_count=max(0, len(df_a) - len(df_b)),
                modified_count=0,
                unchanged_count=min(len(df_a), len(df_b)),
            )

        # 3. Statistical Profiling & Diff
        stats_diff: StatsDiff = StatsComparator.compare(
            df_a=df_a,
            df_b=df_b,
            stats_config=cfg.stats_config,
        )

        # 4. CI/CD Policy Quality Gate Evaluation
        policy_report: PolicyReport = PolicyEvaluator.evaluate(
            schema_diff=schema_diff,
            row_diff=row_diff,
            stats_diff=stats_diff,
            policy=cfg.policies,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return DiffSummary(
            source_name=name_a,
            target_name=name_b,
            schema_diff=schema_diff,
            row_diff=row_diff,
            stats_diff=stats_diff,
            policy_report=policy_report,
            execution_time_ms=elapsed_ms,
        )
