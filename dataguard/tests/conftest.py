"""Pytest fixtures and test configurations for DataGuard test suite."""

import pytest
import polars as pl
import os
import tempfile


@pytest.fixture
def sample_valid_df():
    """Polars DataFrame with valid, clean customer records."""
    return pl.DataFrame({
        "customer_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Evan", "Fiona", "George", "Hannah", "Ian", "Julia"],
        "email": [
            "alice@test.com", "bob@test.com", "charlie@test.org", "diana@test.net", "evan@test.co",
            "fiona@test.com", "george@test.org", "hannah@test.edu", "ian@test.com", "julia@test.fr"
        ],
        "age": [25, 30, 45, 29, 52, 24, 61, 19, 41, 37],
        "status": ["active", "inactive", "active", "pending", "active", "active", "suspended", "active", "active", "inactive"],
        "score": [95.5, 88.0, 72.3, 91.0, 84.6, 99.0, 68.4, 94.2, 85.0, 90.1],
    })


@pytest.fixture
def sample_dirty_df():
    """Polars DataFrame with intentional rule violations."""
    return pl.DataFrame({
        "customer_id": [1, 2, 1, 4, 5],  # Duplicate ID (1)
        "name": ["Alice", "Bob", None, "Diana", "Evan"],  # Null name
        "email": ["alice@test.com", "not-an-email", "charlie@test.org", "", "evan@test.co"],  # Invalid & empty emails
        "age": [25, -5, 150, 29, 52],  # Out of bounds [-5, 150]
        "status": ["active", "unknown_val", "active", "pending", "invalid"],  # Disallowed values
        "score": [95.5, 88.0, None, 91.0, 84.6],
    })


@pytest.fixture
def temp_csv_file(sample_valid_df):
    """Temporary CSV file on disk."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        path = f.name
    sample_valid_df.write_csv(path)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def temp_json_file():
    """Temporary JSON file on disk."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('[{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]')
        path = f.name
    yield path
    if os.path.exists(path):
        os.remove(path)
