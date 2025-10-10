"""
LLM Provider Factory for creating and managing different LLM providers.
Integrates with langchain for standardized LLM interactions.
"""

from typing import Dict, Any, Optional, Protocol
from abc import ABC, abstractmethod
from langchain.llms.base import LLM
from langchain_community.llms import FakeListLLM
from src.llm_models.llm_provider import LLMProvider
from src.services.config_service import get_config_service


class LLMProviderProtocol(Protocol):
    """Protocol for LLM provider implementations."""

    def generate_recommendation(self, prompt: str) -> str:
        """Generate recommendation based on prompt."""
        ...

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider."""
        ...


class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._llm: Optional[LLM] = None

    @abstractmethod
    def _create_llm(self) -> LLM:
        """Create the underlying langchain LLM instance."""
        pass

    @property
    def llm(self) -> LLM:
        """Get or create the LLM instance."""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm

    def generate_recommendation(self, prompt: str) -> str:
        """Generate recommendation using the LLM."""
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}") from e

    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        pass


class SimpleLLMProvider(BaseLLMProvider):
    """Simple rule-based provider for Phase 1 compatibility."""

    def _create_llm(self) -> LLM:
        """Create a fake LLM that returns predefined responses."""
        responses = [
            "BASS, FLOUNDER, SALMON, TROUT",
            "PIANO, GUITAR, VIOLIN, DRUMS",
            "RED, BLUE, GREEN, YELLOW",
            "APPLE, BANANA, ORANGE, GRAPE",
        ]
        return FakeListLLM(responses=responses)

    def get_provider_info(self) -> Dict[str, Any]:
        """Get simple provider information."""
        return {
            "provider_type": "simple",
            "model_name": None,
            "capabilities": ["basic_recommendations"],
            "requires_api_key": False,
        }


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama provider using langchain integration."""

    def _create_llm(self) -> LLM:
        """Create Ollama LLM instance."""
        try:
            from langchain.llms import Ollama

            base_url = self.config.get("base_url", "http://localhost:11434")
            model_name = self.config.get("model_name", "llama2")
            timeout = self.config.get("timeout", 60)

            return Ollama(base_url=base_url, model=model_name, timeout=timeout)
        except ImportError as e:
            raise RuntimeError("Ollama dependencies not installed") from e
        except Exception as e:
            raise RuntimeError(f"Failed to create Ollama LLM: {str(e)}") from e

    def get_provider_info(self) -> Dict[str, Any]:
        """Get Ollama provider information."""
        return {
            "provider_type": "ollama",
            "model_name": self.config.get("model_name", "llama2"),
            "base_url": self.config.get("base_url", "http://localhost:11434"),
            "capabilities": ["context_aware_recommendations", "explanation_generation"],
            "requires_api_key": False,
        }


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI provider using langchain integration."""

    def _create_llm(self) -> LLM:
        """Create OpenAI LLM instance."""
        try:
            from langchain.llms import OpenAI

            api_key = self.config.get("api_key")
            model_name = self.config.get("model_name", "gpt-3.5-turbo")
            timeout = self.config.get("timeout", 30)

            if not api_key:
                raise ValueError("OpenAI API key is required")

            return OpenAI(openai_api_key=api_key, model_name=model_name, timeout=timeout)
        except ImportError as e:
            raise RuntimeError("OpenAI dependencies not installed") from e
        except Exception as e:
            raise RuntimeError(f"Failed to create OpenAI LLM: {str(e)}") from e

    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information."""
        return {
            "provider_type": "openai",
            "model_name": self.config.get("model_name", "gpt-3.5-turbo"),
            "capabilities": ["context_aware_recommendations", "explanation_generation", "high_quality_reasoning"],
            "requires_api_key": True,
        }


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    def __init__(self):
        self.config_service = get_config_service()
        self._providers: Dict[str, type[BaseLLMProvider]] = {
            "simple": SimpleLLMProvider,
            "ollama": OllamaLLMProvider,
            "openai": OpenAILLMProvider,
        }

    def create_provider(self, llm_provider: LLMProvider) -> BaseLLMProvider:
        """Create a provider instance based on LLMProvider configuration.

        Args:
            llm_provider: LLMProvider model with configuration.

        Returns:
            Configured provider instance.

        Raises:
            ValueError: If provider type is not supported.
            RuntimeError: If provider configuration is invalid.
        """
        provider_type = llm_provider.provider_type

        if provider_type not in self._providers:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        # Get configuration for the provider
        config = self.config_service.get_provider_config(provider_type)
        if config is None and provider_type != "simple":
            raise RuntimeError(f"Provider {provider_type} is not configured")

        # Override model name if specified in LLMProvider
        if llm_provider.model_name is not None:
            if config is None:
                config = {}
            # If config is a pydantic model, call its dict(), otherwise assume it's already a dict-like
            if hasattr(config, "dict"):
                config = dict(config.dict())
            else:
                config = dict(config)
            config["model_name"] = llm_provider.model_name

        # Create provider instance
        provider_class = self._providers[provider_type]
        return provider_class(config or {})

    def get_available_providers(self) -> Dict[str, bool]:
        """Get list of available providers and their status.

        Returns:
            Dictionary mapping provider names to availability.
        """
        return self.config_service.validate_providers()

    def validate_provider(self, llm_provider: LLMProvider) -> bool:
        """Validate that a provider can be created and used.

        Args:
            llm_provider: LLMProvider configuration to validate.

        Returns:
            True if provider is valid and available.
        """
        try:
            provider = self.create_provider(llm_provider)
            # Try to get provider info to ensure it's working
            provider.get_provider_info()
            return True
        except Exception:
            return False


# Global factory instance
_provider_factory: Optional[LLMProviderFactory] = None


def get_provider_factory() -> LLMProviderFactory:
    """Get global provider factory instance."""
    global _provider_factory
    if _provider_factory is None:
        _provider_factory = LLMProviderFactory()
    return _provider_factory
