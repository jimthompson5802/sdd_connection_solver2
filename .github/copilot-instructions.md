# Copilot Project Instructions (Generated)

This file summarizes the project's tech stack, architecture, file categorization, domain deep dives, style guides, and build instructions to help AI assistants (e.g., Copilot) generate consistent, convention-following code for this repository.

## Project Overview
This repository contains the codebase for the Connection Solver application, which provides puzzle-solving recommendations using large language models (LLMs). The project is structured into a Python backend and a React frontend, with comprehensive testing and documentation.

**Generated artifacts** (detailed files in `.results/`):
- `.results/1-determine-techstack.md` — Tech stack summary
- `.results/2-file-categorization.json` — File categories and representative files
- `.results/3-architectural-domains.json` — Architectural domains, required patterns, constraints
- `.results/4-domains/` — Domain deep dives (per-domain `.md` files)
- `.results/5-style-guides/` — Style guides per file category
- `.results/6-build-instructions.md` — How to build, test, and run the app

---

## Quick Overview

- Backend: Python 3.11+ with FastAPI, Pydantic, Uvicorn. LLM orchestration via LangChain and provider adapters (OpenAI, Ollama, Simple provider).
- Frontend: React + TypeScript (Create React App). Tests with React Testing Library. Styling via component-scoped `.css`.
- Data: CSV-based puzzle/word lists under `/data`.
- Testing & quality: `pytest`, `mypy`, `black`, `prettier`, `eslint` configured.

Refer to `.results/1-determine-techstack.md` for the full tech stack analysis.

## File Categories (high level)

- backend-api: `backend/src/api/*` (v2 endpoints) — use Pydantic models and DI
- backend-services: `backend/src/services/*` — business logic and LLM orchestration
- llm-adapters: provider classes in `backend/src/services/llm_provider_factory.py` and `backend/src/langchain_community/llms/`
- frontend-components: `frontend/src/components/*.tsx` — typed React functional components
- frontend-services: `frontend/src/services/*` — API wrappers
- data-files: `data/*.csv` — canonical input data
- docs, tests, utilities: `docs/`, `backend/tests/`, `src/`

See `.results/2-file-categorization.json` for a JSON mapping of categories to representative files.

## Architectural Domains & Rules (Key points)

- LLM Integration: All LLM usage must go through the provider factory and service abstractions. Prefer provider-agnostic code paths and validate/normalize outputs via the shared response validator.
- API: Versioned endpoints under `/api/v2` follow a pattern of using Pydantic models, dependency injection (`Depends`), and structured HTTP error responses.
- Data: The codebase treats CSVs in `/data` as the primary data source — avoid introducing direct DB access without centralizing data-layer abstractions.
- Config & Ops: Use `get_config_service` for provider configuration and follow `pyproject.toml` quality rules.

Full domain definitions and constraints are in `.results/3-architectural-domains.json` and `.results/4-domains/`.

## Coding conventions
- Class names use PascalCase (e.g., MyClass).
- variables and function names use snake_case (e.g., this_variable, compute_something).
- Follow PEP 8 with the exception:
  - allow line lengths up to 120 characters
- Use type annotations for public functions and methods.
- Keep functions single-responsibility.
- Prefer explicit is better than implicit; avoid clever one-liners that reduce readability.
- Use `dataclass` / NamedTuple for simple structured data.
- Use f-strings for formatting.

## Style & Contribution Rules (Essentials for Copilot)

- Do not invent new architectural patterns; follow existing ones in `.results/5-style-guides/` (one file per category).
- For new backend endpoints: create Pydantic request/response models, place route under `backend/src/api/v2_*`, and implement business logic in a service class under `backend/src/services/`.
- For new LLM providers: implement `BaseLLMProvider` subclass and register it in `LLMProviderFactory`.
- For frontend components: add `.tsx` under `frontend/src/components/`, include an adjacent `.css` and `*.test.tsx` when applicable, and call backend APIs only via `frontend/src/services/*`.
- Tests: follow existing pytest markers and structure; include mocks for LLM calls when appropriate.

See the per-category style guides under `.results/5-style-guides/` for detailed, project-specific conventions.

## Build & Run (short)

Backend (bash):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
export PYTHONPATH=src
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (bash):

```bash
cd frontend
npm install
npm start
```

Full build and test instructions are in `.results/6-build-instructions.md`.

---

## How to use these instructions with Copilot or an AI agent

- Provide this file's path as the context for Copilot or your LLM agent before asking to scaffold changes.
- When requesting feature scaffolds, include the target category (e.g., `backend-services`, `frontend-components`) so the agent picks the right style guide from `.results/5-style-guides/`.
- For any change touching LLM integration, require the agent to show how provider creation goes through `LLMProviderFactory` and how output validation uses `response_validator`.

---

## Where to find the generated analysis files

- `.results/1-determine-techstack.md`
- `.results/2-file-categorization.json`
- `.results/3-architectural-domains.json`
- `.results/4-domains/*` (per-domain deep dives)
- `.results/5-style-guides/*` (per-category style guides)
- `.results/6-build-instructions.md`

---

If you want, I can now:
- Run a more comprehensive scan and insert code snippets into the domain files where useful,
- Open a PR with these files committed, or
- Run the test suite to validate nothing regressed.

Which would you like next?