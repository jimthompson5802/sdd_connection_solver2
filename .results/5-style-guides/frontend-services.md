# Style Guide — frontend-services

Unique conventions:

- Encapsulate network requests and LLM API interactions in `frontend/src/services/llm-api.ts`.
- Services should return typed payloads (TypeScript interfaces) and not directly render UI.
- Keep testable logic in services so it can be unit-tested independently of components.

File examples: `frontend/src/services/llm-api.ts`.
