# LLM Integration Domain — Deep Dive

## Overview

LLM integration is a first-class architectural concern. The codebase centralizes provider creation and interaction in `backend/src/services/llm_provider_factory.py` and organizes provider-specific logic in provider classes (Simple, Ollama, OpenAI). Prompt construction, invocation, and response normalization live in services like `prompt_service.py` and `response_validator.py`.

## Key files & exact excerpts

- `backend/src/services/llm_provider_factory.py` contains provider classes and factory logic; e.g. the factory exposes:

```python
class LLMProviderFactory:
    def create_provider(self, llm_provider: LLMProvider) -> BaseLLMProvider:
        ...

# Global factory instance
def get_provider_factory() -> LLMProviderFactory:
    ...
```

- Providers implement `BaseLLMProvider` and the `generate_recommendation` method which normalizes many possible LLM return shapes.

## Required patterns

- Always use the provider factory to create providers; do not instantiate provider classes directly across the codebase.
- Prompt logic and validation are encapsulated in `prompt_service` and `response_validator` rather than scattered.
- Providers should attempt `with_structured_output` when available and fall back to safe normalization code paths (see `_normalize_generate_result`).

## Integration constraints

- Provider-agnostic design: code must support `simple`, `ollama`, and `openai` providers.
- All LLM calls should be routed through service abstractions so they can be mocked in tests (the codebase uses `FakeListLLM` for simple testing).

## Example flow

1. The API endpoint constructs a `RecommendationRequest` pydantic model.
2. The `RecommendationService` uses the provider factory to create an LLM provider instance.
3. The provider's `generate_recommendation` is called and its result normalized.
4. `response_validator` parses/validates structured fields before returning to the API layer.

---
