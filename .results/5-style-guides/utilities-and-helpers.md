# Style Guide — utilities-and-helpers

Unique conventions:

- Shared utilities and lightweight tooling live under `src/` (top-level) and `backend/src/*` for backend helpers.
- Keep helpers small, explicitly typed, and add docstrings. Prefer dataclasses for structured data shapes.
- Avoid cross-cutting imports that create circular dependencies; keep shared utilities dependency-free where possible.

File examples: `src/__init__.py`, `backend/src/recommendation_engine.py`.
