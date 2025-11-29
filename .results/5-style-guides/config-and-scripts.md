# Style Guide — config-and-scripts

Unique conventions:

- Backend config and tooling are centralized in `pyproject.toml` (dependencies, mypy/black, pytest options).
- Frontend scripts follow CRA conventions in `package.json` with `lint`, `format`, and `type-check` scripts.
- Use the `get_config_service` abstraction for runtime configuration and provider settings.

File examples: `backend/pyproject.toml`, `frontend/package.json`.
