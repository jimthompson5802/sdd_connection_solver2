# Style Guide — llm-adapters

Unique conventions:

- All LLM providers inherit from `BaseLLMProvider` and implement `_create_llm`, `get_provider_info`, and use `generate_recommendation` for normalization.
- Provider types supported: `simple`, `ollama`, `openai`. Keep provider registration in `LLMProviderFactory` mapping.
- Attempt `with_structured_output` wrappers when available and fall back to normalization that handles multiple LangChain return shapes.
- Tests may use `FakeListLLM` or patch provider classes directly.

File examples: `backend/src/services/llm_provider_factory.py`, `backend/src/langchain_community/llms/ollama.py`.
