# Style Guide — tests-backend

Unique conventions:

- Tests use `pytest` with markers configured in `pyproject.toml` (e.g., `llm_mock`, `integration`, `contract`).
- Tests are organized into `backend/tests/unit`, `backend/tests/integration`, `backend/tests/e2e`, and `backend/tests/contract`.
- LLM-related behavior is mocked using provided mocks in `backend/tests/mocks`.
- Maintain coverage thresholds as configured in `pyproject.toml`.

File examples: `backend/tests/unit/test_*.py`, `backend/tests/integration/*`.
