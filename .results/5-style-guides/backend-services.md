# Style Guide — backend-services

Unique conventions:

- Services are classes (e.g., `RecommendationService`) that encapsulate business logic and are created via DI in API routes.
- Service methods return typed pydantic-like objects or primitives; side-effects (I/O) should be localized and well-abstracted.
- LLM calls must be made through provider instances created by `LLMProviderFactory` rather than direct LLM instantiation.
- Keep prompt construction and response parsing in dedicated modules: `prompt_service.py` and `response_validator.py`.
- Avoid raw `print` logging in services; use `logging.getLogger(__name__)` and structured logging.

File examples: `backend/src/services/recommendation_service.py`, `backend/src/services/prompt_service.py`.
