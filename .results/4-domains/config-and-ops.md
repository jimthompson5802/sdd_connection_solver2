# Config & Ops — Deep Dive

## Overview

Configuration is managed via environment variables (`.env` + `python-dotenv`) and service-level config accessors (`backend/src/config/environment.py`). Build and test tooling is controlled by `pyproject.toml` for the backend and `package.json` for the frontend.

## Key files & patterns

- `backend/pyproject.toml` — defines dependencies, test config (`pytest`), code quality tools (`mypy`, `black`).
- `frontend/package.json` — CRA scripts, linting, TypeScript configuration references.
- Config access functions exist (e.g., `get_config_service`) to centralize provider and app configuration.

## Constraints

- Respect `mypy`/`black` strictness in backend code (see `pyproject.toml`), do not introduce patterns that break type checks without justification.
- Tests are expected to use pytest markers defined in `pyproject.toml` (e.g., `llm_mock`, `integration`, `contract`).

## Implementation guidance

- Use the provided `get_config_service` to fetch provider configs and app settings.
- Add environment-sensitive behavior behind config service abstractions to avoid scattering `os.getenv` calls.

---
