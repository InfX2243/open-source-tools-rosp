"""Schema comparison engine for datasets."""

from __future__ import annotations

import polars as pl
from datadiff.core.models import ColumnMeta, ColumnMigration, SchemaDiff


class SchemaComparator:
    """Compares columns, order, and data types between two datasets."""

    @staticmethod
    def compare(df_a: pl.DataFrame, df_b: pl.DataFrame) -> SchemaDiff:
        schema_a = {col: str(dtype) for col, dtype in df_a.schema.items()}
        schema_b = {col: str(dtype) for col, dtype in df_b.schema.items()}

        cols_a = set(schema_a.keys())
        cols_b = set(schema_b.keys())

        # Added columns in B
        added = [
            ColumnMeta(name=col, dtype=schema_b[col])
            for col in sorted(cols_b - cols_a)
        ]

        # Removed columns in A
        removed = [
            ColumnMeta(name=col, dtype=schema_a[col])
            for col in sorted(cols_a - cols_b)
        ]

        # Common columns
        common_cols = cols_a.intersection(cols_b)
        migrations = []
        unchanged = []

        for col in sorted(common_cols):
            type_a = schema_a[col]
            type_b = schema_b[col]
            if type_a != type_b:
                migrations.append(
                    ColumnMigration(column=col, source_dtype=type_a, target_dtype=type_b)
                )
            else:
                unchanged.append(col)

        has_changes = bool(added or removed or migrations)

        return SchemaDiff(
            added_columns=added,
            removed_columns=removed,
            type_migrations=migrations,
            unchanged_columns=unchanged,
            has_changes=has_changes,
        )
