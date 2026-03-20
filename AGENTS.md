# Agents Guide for VNEDU Data Processing System

This document defines how to operate on the VNEDU data processing project. It is intended for automated agents and engineers who will work inside this repository.

Table of contents
- Build, lint, test commands
- Code style guidelines
- Testing strategy
- Runtime and error handling expectations
- Collaboration and PR hygiene
- Tooling and rules

1. Build, lint, test commands
- Setup
  - Create a virtual environment and install dependencies:
    - python -m venv .venv
    - source .venv/bin/activate  (on Windows: .\\.venv\\Scripts\\activate)
    - if you have a requirements.txt: pip install -r requirements.txt
- Lint
  - Use ruff or flake8 (preferred: ruff) to lint the codebase:
    - ruff check .
  - Optional: pre-commit hooks if configured:
    - pre-commit run --all-files
- Formatting
  - Use Black for code formatting:
    - black .
- Type checking
  - Use mypy if configured:
    - mypy app
- Tests
  - Run all tests:
    - pytest -q
  - Run a single test (example):
    - pytest tests/test_vnedu_parser.py::TestParseVneduFile::test_basic_parse -q
  - Coverage (optional):
    - pytest --cov=app --cov-report=html
- Local server
  - Run Streamlit app (if present):
    - streamlit run app/main.py

2. Code style guidelines
- General
  - Python 3.10+ syntax; type hints everywhere where possible
  - Avoid wildcard imports; prefer explicit imports
- Imports
  - Standard library, blank line, third-party, blank line, local imports
  - Sort imports using isort; enforce stable grouping
- Naming conventions
  - Functions and variables: snake_case
  - Classes: PascalCase
  - Constants: UPPER_SNAKE_CASE
- Formatting
  - Enforce Black 88 line-length convention where possible
  - Add type hints to public functions and methods
- Docstrings
  - All public modules and functions should have docstrings describing purpose, parameters, and return values (Google-style or NumPy-style)
- Error handling
  - Avoid bare exceptions; catch specific exceptions
  - Log errors with context rather than printing stack traces to stdout
- Logging
  - Use Python logging module for runtime messages; avoid print statements in library code
- Validation
  - Validate inputs/outputs at boundaries; raise meaningful exceptions or return validation results

3. Testing strategy
- Unit tests for core utilities (parsers, validators, transformers)
- Integration tests for end-to-end flows (parse → transform → store)
- Property-based tests where feasible for normalization rules
- Mock I/O for Excel parsing to avoid dependency on real files in unit tests
- Use fixtures for common dataset samples

4. Runtime expectations
- Idempotency: upserts should be safe to retry without duplicate side effects
- Deterministic behavior: parse results should be stable given the same input
- Performance: consider streaming large Excel files; optimize hot paths in parsing if needed

5. Cursor and Copilot rules
- If .cursor/rules/ exists, respect cursor constraints (ordering, limits, safety)
- If .github/copilot-instructions.md exists, follow the given coding standards and safety guidelines

6. Security and secrets
- Do not commit credentials or secrets; use environment variables or config files excluded from VCS
- Avoid printing sensitive data to logs

7. PR hygiene
- Small, focused PRs with one logical change per PR
- Include a short rationale for the change and test results
- Update documentation when user-facing changes occur

8. Quick reference commands (recap)
- Unit tests: pytest -q
- Single test: pytest path/to/test.py::Class::method -q
- Lint: ruff check .
- Format: black .
- Type-check: mypy app
- Docs: update MD files in docs/ as needed

End of guidelines.
