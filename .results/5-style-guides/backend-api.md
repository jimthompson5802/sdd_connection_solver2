# Style Guide — backend-api

What makes this project’s API code unique:

- All endpoints are typed with Pydantic request/response models (use `src.models` or `backend/src/pydantic.py`).
- Use FastAPI dependency injection (`Depends(...)`) to obtain service instances instead of creating them inline.
- Follow the `/api/v2` router pattern for stable, versioned endpoints (`backend/src/api/v2_*`).
- Error handling: catch domain exceptions and return structured `HTTPException` payloads with `error`, `message`, `error_code`, and `details` keys (see `v2_recommendations.py`).
- Logging: use module-level logger and call `log_request_info` middleware helper for diagnostic metadata.

File examples: `backend/src/api/v2_recommendations.py`, `backend/src/api/v2_providers.py`.
