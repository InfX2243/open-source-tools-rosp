# Contributing to DataDiff

Thank you for your interest in contributing to DataDiff!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/InfX2243/open-source-tools-rosp.git
   cd open-source-tools-rosp/datadiff
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in editable mode with development dependencies:**
   ```bash
   pip install -e .[dev]
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## Pull Request Guidelines
- Add unit tests for any new comparators, adapters, or policies.
- Ensure all tests pass.
- Write clear commit messages and documentation.
