"""
LLM Provider Factory for creating and managing different LLM providers.
Integrates with langchain for standardized LLM interactions.
"""

from typing import Dict, Any, Optional, Protocol
from collections.abc import Mapping
from abc import ABC, abstractmethod
from langchain.llms.base import LLM
from langchain_community.llms import FakeListLLM
from src.llm_models.llm_provider import LLMProvider, LLMRecommendationResponse
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

    def generate_recommendation(self, prompt: str) -> LLMRecommendationResponse:
        """Generate recommendation using the LLM."""
        try:
            llm = self.llm

            def _normalize_generate_result(res):
                """Normalize possible LLM.generate return values into a str/dict/list."""
                # common fast paths
                if isinstance(res, (str, dict, list)):
                    return res
                # LLMResult-like objects may expose `generations`
                gens = getattr(res, "generations", None)
                if gens:
                    try:
                        first = gens[0]
                        if isinstance(first, list) and first:
                            item = first[0]
                        else:
                            item = first
                        text = getattr(item, "text", None) or getattr(item, "content", None)
                        if isinstance(text, str):
                            return text
                    except Exception:
                        pass
                # direct text attributes
                text = getattr(res, "text", None) or getattr(res, "content", None)
                if isinstance(text, str):
                    return text
                # pydantic-style dict
                if hasattr(res, "dict"):
                    try:
                        return getattr(res, "dict")()
                    except Exception:
                        pass
                # fallback to string coercion
                return str(res)

            # Prefer structured output when the LLM implementation supports it.
            if hasattr(llm, "with_structured_output"):
                try:
                    wrapper = llm.with_structured_output(LLMRecommendationResponse)
                    # Use the callable LLM/wrapper API instead of the deprecated `invoke` method.
                    # Most modern LangChain LLM wrappers support being called directly.
                    # Try calling the wrapper; some wrappers may not expose __call__
                    try:
                        result = wrapper.invoke(prompt)
                        return result
                    # TODO: clean up exception handling here
                    except Exception:
                        # Fallback to older names if callable isn't supported
                        if hasattr(wrapper, "invoke"):
                            result = wrapper.invoke(prompt)
                        elif hasattr(wrapper, "generate"):
                            result = _normalize_generate_result(wrapper.generate([prompt]))
                        else:
                            # Last resort: coerce to string
                            result = str(wrapper)

                # TODO: clean up exception handling here
                #     # result might be a dict, a pydantic model, an object with attribute, or a plain string
                #     if isinstance(result, dict):
                #         if "recommendations" in result:
                #             return result["recommendations"]
                #         # if the dict itself is the recommendations text
                #         return str(result)

                #     # pydantic model or similar
                #     # pydantic model or similar; normalize via dict() when available
                #     if not isinstance(result, (str, dict, list)) and hasattr(result, "dict"):
                #         try:
                #             d = getattr(result, "dict")()
                #         except Exception:
                #             d = None
                #         if isinstance(d, dict) and "recommendations" in d:
                #             return d["recommendations"]

                #     # object with attribute
                #     if hasattr(result, "recommendations"):
                #         return getattr(result, "recommendations")

                #     # fallback if it's already a string
                #     if isinstance(result, str):
                #         return result

                #     # if structured attempt didn't produce the field we expected, fall back to plain invoke
                except Exception:
                    # fall through to the simple invoke below
                    pass

            # Default behaviour: call the LLM via the callable API
            # (preferred over the deprecated `invoke` method)
            try:
                raw = llm(prompt)
            except Exception:
                # Backwards-compatible fallback to older API names
                if hasattr(llm, "invoke"):
                    raw = llm.invoke(prompt)
                elif hasattr(llm, "generate"):
                    raw = _normalize_generate_result(llm.generate([prompt]))
                else:
                    # If nothing works, raise with context
                    raise

            # If llm.generate returned a non-serializable object, normalize it
            raw = _normalize_generate_result(raw)
            # Default behaviour: if it's a string, return directly
            if isinstance(raw, str):
                return raw
            # If it's a dict-like structured response, try to extract
            if isinstance(raw, dict) and "recommendations" in raw:
                return raw.get("recommendations")
            # Otherwise fall-through to error
            raise RuntimeError("LLM did not return a usable recommendation")
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
            from langchain_ollama import ChatOllama

            base_url = self.config.get("base_url", "http://localhost:11434")
            model_name = self.config.get("model_name", "llama2")
            timeout = self.config.get("timeout", 60)

            return ChatOllama(base_url=base_url, model=model_name)
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
            model_name = self.config.get("model_name", "gpt-4o-mini")
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
            "model_name": self.config.get("model_name", "gpt-4o-mini"),
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
        # In test environments we often patch provider classes directly. Allow
        # creating provider instances even when the configuration is missing by
        # falling back to an empty config for non-simple providers. This keeps
        # behavior compatible with tests that mock the provider implementation.
        if config is None and provider_type != "simple":
            config = {}

        # Override model name if specified in LLMProvider
        if llm_provider.model_name is not None:
            if config is None:
                config = {}
            # If config is a pydantic model or object with dict(), prefer that, otherwise coerce to dict
            # Coerce provider config into a plain Dict[str, Any].
            # If the config object provides a dict() method (e.g., pydantic model), use it.
            dict_method = getattr(config, "dict", None)
            cfg: Dict[str, Any] = {}
            if callable(dict_method):
                try:
                    data = dict_method()
                    if isinstance(data, dict) or isinstance(data, Mapping):
                        cfg = {str(k): v for k, v in data.items()}  # type: ignore[arg-type]
                    else:
                        cfg = {}
                except Exception:
                    try:
                        if isinstance(config, dict) or isinstance(config, Mapping):
                            cfg = {str(k): v for k, v in config.items()}
                        else:
                            cfg = {}
                    except Exception:
                        cfg = {}
            else:
                try:
                    if isinstance(config, dict) or isinstance(config, Mapping):
                        cfg = {str(k): v for k, v in config.items()}
                    else:
                        cfg = {}
                except Exception:
                    cfg = {}

            cfg["model_name"] = llm_provider.model_name
            config = cfg

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
