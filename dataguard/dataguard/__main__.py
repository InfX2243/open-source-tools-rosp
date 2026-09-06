"""Entrypoint for running dataguard as a module: `python -m dataguard`."""
import sys
from dataguard.cli.commands import app

if __name__ == "__main__":
    app()
