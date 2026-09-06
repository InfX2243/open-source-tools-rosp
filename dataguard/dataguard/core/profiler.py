"""Statistical dataset profiling engine."""

from typing import Any, Dict, List
import math
from dataguard.core.models import ColumnProfile, DatasetProfile

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False


class DataProfiler:
    """Computes comprehensive statistical profiles for tabular datasets."""

    @classmethod
    def profile_dataframe(cls, df: Any, source_name: str = "dataset") -> DatasetProfile:
        """Profile a Polars DataFrame (or fallback)."""
        if POLARS_AVAILABLE and isinstance(df, pl.DataFrame):
            return cls._profile_polars(df, source_name)
        return cls._profile_generic(df, source_name)

    @classmethod
    def _profile_polars(cls, df: "pl.DataFrame", source_name: str) -> DatasetProfile:
        row_count = df.height
        col_count = df.width
        est_bytes = df.estimated_size()
        col_profiles: Dict[str, ColumnProfile] = {}

        for col_name in df.columns:
            series = df[col_name]
            dtype_str = str(series.dtype).lower()

            null_count = series.null_count()
            null_pct = round((null_count / row_count * 100.0) if row_count > 0 else 0.0, 2)

            # Unique values count
            try:
                distinct_count = series.n_unique()
            except Exception:
                distinct_count = 0
            unique_pct = round((distinct_count / row_count * 100.0) if row_count > 0 else 0.0, 2)

            min_val = None
            max_val = None
            mean_val = None
            median_val = None
            std_val = None

            # Numeric metrics
            if series.dtype.is_numeric():
                try:
                    raw_min = series.min()
                    min_val = float(raw_min) if raw_min is not None else None
                except Exception:
                    pass
                try:
                    raw_max = series.max()
                    max_val = float(raw_max) if raw_max is not None else None
                except Exception:
                    pass
                try:
                    raw_mean = series.mean()
                    mean_val = round(float(raw_mean), 3) if raw_mean is not None else None
                except Exception:
                    pass
                try:
                    raw_median = series.median()
                    median_val = round(float(raw_median), 3) if raw_median is not None else None
                except Exception:
                    pass
                try:
                    raw_std = series.std()
                    std_val = round(float(raw_std), 3) if raw_std is not None else None
                except Exception:
                    pass
            elif series.dtype in (pl.Date, pl.Datetime, pl.Time):
                try:
                    min_val = str(series.min())
                    max_val = str(series.max())
                except Exception:
                    pass

            # Top frequent values
            top_vals: List[Dict[str, Any]] = []
            try:
                vc = series.value_counts(sort=True).head(5)
                for row in vc.iter_rows(named=True):
                    val = row[col_name]
                    cnt = row["count"]
                    pct = round((cnt / row_count * 100.0) if row_count > 0 else 0.0, 2)
                    top_vals.append({
                        "value": str(val) if val is not None else "<NULL>",
                        "count": cnt,
                        "percentage": pct,
                    })
            except Exception:
                pass

            col_profiles[col_name] = ColumnProfile(
                column_name=col_name,
                detected_type=dtype_str,
                total_count=row_count,
                null_count=null_count,
                null_percentage=null_pct,
                distinct_count=distinct_count,
                unique_percentage=unique_pct,
                min_value=min_val,
                max_value=max_val,
                mean_value=mean_val,
                median_value=median_val,
                std_value=std_val,
                top_values=top_vals,
            )

        return DatasetProfile(
            source_name=source_name,
            row_count=row_count,
            column_count=col_count,
            estimated_memory_kb=round(est_bytes / 1024.0, 2),
            columns=col_profiles,
        )

    @classmethod
    def _profile_generic(cls, data: Any, source_name: str) -> DatasetProfile:
        """Generic fallback profiler for list of dicts or pandas."""
        rows = list(data) if not isinstance(data, list) else data
        row_count = len(rows)
        columns = list(rows[0].keys()) if row_count > 0 else []
        col_profiles: Dict[str, ColumnProfile] = {}

        for col in columns:
            vals = [r.get(col) for r in rows]
            non_nulls = [v for v in vals if v is not None and str(v).strip() != ""]
            null_count = row_count - len(non_nulls)
            null_pct = round((null_count / row_count * 100.0) if row_count > 0 else 0.0, 2)
            distinct_set = set(str(v) for v in non_nulls)
            distinct_count = len(distinct_set)
            unique_pct = round((distinct_count / row_count * 100.0) if row_count > 0 else 0.0, 2)

            # Detect type
            is_numeric = all(isinstance(v, (int, float)) for v in non_nulls) if non_nulls else False
            min_val, max_val, mean_val, median_val, std_val = None, None, None, None, None
            if is_numeric and non_nulls:
                num_vals = [float(v) for v in non_nulls]
                min_val = min(num_vals)
                max_val = max(num_vals)
                mean_val = round(sum(num_vals) / len(num_vals), 3)
                sorted_vals = sorted(num_vals)
                mid = len(sorted_vals) // 2
                median_val = round(sorted_vals[mid], 3)
                variance = sum((x - mean_val) ** 2 for x in num_vals) / len(num_vals)
                std_val = round(math.sqrt(variance), 3)

            col_profiles[col] = ColumnProfile(
                column_name=col,
                detected_type="numeric" if is_numeric else "string",
                total_count=row_count,
                null_count=null_count,
                null_percentage=null_pct,
                distinct_count=distinct_count,
                unique_percentage=unique_pct,
                min_value=min_val,
                max_value=max_val,
                mean_value=mean_val,
                median_value=median_val,
                std_value=std_val,
                top_values=[],
            )

        return DatasetProfile(
            source_name=source_name,
            row_count=row_count,
            column_count=len(columns),
            estimated_memory_kb=round((row_count * len(columns) * 16) / 1024.0, 2),
            columns=col_profiles,
        )
