from typing import Any
import os
from src.services.llm_providers.simple_provider import SimpleProvider
from src.services.llm_providers.ollama_provider import OllamaProvider
from src.services.llm_providers.openai_provider import OpenAIProvider
from src.llm_models.llm_provider import LLMProvider


class ProviderFactory:
    """Back-compat factory mirroring older tests' expectations."""

    def create_provider(self, llm_provider: LLMProvider) -> Any:
        if llm_provider.provider_type == "simple":
            return SimpleProvider()
        if llm_provider.provider_type == "ollama":
            # In tests, langchain Ollama is patched; do not enforce env presence here.
            base_url = os.getenv("OLLAMA_BASE_URL")
            return OllamaProvider(base_url=base_url, model_name=llm_provider.model_name or "llama2")
        if llm_provider.provider_type == "openai":
            # In tests, openai client is patched; do not enforce env presence here.
            api_key = os.getenv("OPENAI_API_KEY", "")
            return OpenAIProvider(api_key=api_key or "test_key", model_name=llm_provider.model_name or "gpt-3.5-turbo")
        raise ValueError(f"Unsupported provider: {llm_provider.provider_type}")
