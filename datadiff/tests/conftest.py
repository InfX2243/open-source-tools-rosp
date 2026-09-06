"""Pytest fixtures for DataDiff test suite."""

import pytest
import polars as pl


@pytest.fixture
def sample_df_a():
    """Baseline dataset fixture."""
    return pl.DataFrame({
        "id": [101, 102, 103, 104],
        "name": ["Rahul", "Aisha", "John", "Elena"],
        "age": [22, 24, 21, 29],
        "score": [95.5, 88.0, 72.3, 91.0],
        "email": ["rahul@example.com", "aisha@example.com", "john@example.com", None],
    })


@pytest.fixture
def sample_df_b():
    """Target dataset fixture with modifications, addition, removal."""
    return pl.DataFrame({
        "id": [101, 102, 104, 105],
        "name": ["Rahul", "Aisha", "Elena", "Sara"],
        "age": [23, 24, 29, 25],
        "score": [95.505, 88.0, 91.0, 84.0],
        "email": ["rahul.sharma@new.com", "aisha@example.com", "elena@new.com", "sara@new.com"],
        "tier": ["gold", "silver", "platinum", "bronze"],
    })
