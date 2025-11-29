# 6 — Build & Run Instructions

## Backend (Python / FastAPI)

Prereqs:
- Python 3.11+
- Recommended: create a virtualenv or use a tool like `hatch` / `poetry`.

Install & run (bash):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
# or if you prefer hatch: pip install hatch && hatch run pip install -e .

# Run the API server (development)
export PYTHONPATH=src
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Testing:

```bash
cd backend
source .venv/bin/activate
pytest
# For coverage
pytest --cov=src --cov-report=html:htmlcov
```

Notes:
- Backend depends on optional LLM provider credentials for OpenAI; use environment variables or the config service to provide provider config.
- Provider selection is pluggable: `simple`, `ollama`, `openai`.

## Frontend (React / TypeScript)

Install & run (bash):

```bash
cd frontend
npm install
npm start
# build
npm run build
# test
npm test
```

Linting & formatting:

```bash
cd frontend
npm run lint
npm run format
npm run type-check
```

## End-to-end dev flow

- Start the backend first (port 8000 by default).
- Start the frontend (CRA) and ensure the frontend's `llm-api` service points to the backend API URL.

## Notes for CI

- Backend: `pyproject.toml` contains pytest and quality tool configuration (mypy, black, coverage threshold).
- Frontend: CI should run `npm ci`, `npm run type-check`, `npm test -- --coverage` and `npm run build`.

---
