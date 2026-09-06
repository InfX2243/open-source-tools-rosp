# Contributing to DataGuard

Thank you for your interest in contributing to **DataGuard**! As an open-source project, we welcome contributions from the community, ranging from bug fixes and new validators to documentation improvements and database adapters.

---

## 🛠️ Development Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-org/dataguard.git
   cd dataguard
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies in Editable Mode**
   ```bash
   pip install -e ".[all,dev]"
   ```

4. **Verify Installation**
   ```bash
   dataguard --version
   pytest tests/ -v
   ```

---

## 🧩 Adding a New Validator

1. Create a new validator file in `dataguard/validators/<name>.py` extending `Validator`:
   ```python
   from dataguard.validators.base import Validator, ValidatorRegistry
   from dataguard.core.models import ColumnRule, ValidationResult, RuleStatus

   class MyCustomValidator(Validator):
       name = "my_check"

       def validate(self, df, column: str, rule: ColumnRule) -> ValidationResult:
           # Validation logic using Polars DataFrame
           ...

   ValidatorRegistry.register("my_check", MyCustomValidator)
   ```
2. Import the new validator in `dataguard/validators/__init__.py`.
3. Add comprehensive unit tests in `tests/test_validators.py`.

---

## 🧪 Testing Guidelines

- All pull requests must pass the automated pytest test suite:
  ```bash
  pytest tests/ -v
  ```
- Ensure any new feature includes unit tests covering both positive (passing) and negative (violating) cases.

---

## 📜 Pull Request Process

1. Fork the repo and create your feature branch: `git checkout -b feature/my-new-feature`.
2. Commit your changes with clear semantic messages.
3. Ensure linting and tests pass.
4. Push to your branch and open a Pull Request against `main`.
