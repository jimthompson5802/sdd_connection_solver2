# Style Guide — backend-models

Unique conventions:

- Use Pydantic models for all external-facing DTOs (requests/responses). Keep models in a single place (e.g., `backend/src/pydantic.py` or `src.models`).
- Include metadata fields such as `provider_used`, `recommended_words`, and `explanations` in recommendation response models.
- Prefer strict typing and validation — the repo enforces `mypy` and Pydantic validation in endpoints.

File examples: `backend/src/pydantic.py`, `src/models`.
