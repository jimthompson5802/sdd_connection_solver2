# API Domain — Deep Dive

## Overview

The backend API uses FastAPI and organizes endpoints into `backend/src/api/` (v2 endpoints) and top-level route files like `backend/src/api_v1.py` and `backend/src/main.py` for app wiring.

## Key files & examples

- `backend/src/api/v2_recommendations.py` — recommendation endpoints; example function signature:

```python
@router.post("/recommendations", response_model=RecommendationResponse)
async def generate_recommendation(
    request_data: RecommendationRequest,
    request: Request,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    ...
```

- `backend/src/api/v2_providers.py` — provider list/health endpoints.

## Patterns and conventions

- Use Pydantic models for request/response validation (`backend/src/pydantic.py` and `src.models` usage in endpoints).
- Dependency injection via `Depends(...)` to obtain service instances (see `get_recommendation_service`).
- Robust error handling: endpoints raise `HTTPException` with structured details for custom application errors (e.g. `InsufficientWordsError`, `LLMProviderError`).

## Implementation guidance

- New API routes should follow the `api/v2` pattern and use pydantic models.
- Business logic should live in service classes (e.g., `RecommendationService`) and be invoked via DI in endpoints.
- Errors must be translated into structured HTTP responses as in `v2_recommendations.py`.

---
