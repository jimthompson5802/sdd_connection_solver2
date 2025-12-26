"""Unit tests for LLM Provider Factory."""

import pytest
from unittest.mock import Mock, patch
from src.services.llm_provider_factory import (
    LLMProviderFactory,
    SimpleLLMProvider,
    OllamaLLMProvider,
    OpenAILLMProvider,
    BaseLLMProvider,
    get_provider_factory,
)
from src.llm_models.llm_provider import LLMProvider, LLMRecommendationResponse


class TestBaseLLMProvider:
    """Test cases for BaseLLMProvider base class."""

    def test_base_provider_initialization(self):
        """Test base provider initialization."""
        config = {"test_key": "test_value"}

        # Create a concrete implementation for testing
        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return Mock()

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider(config)
        assert provider.config == config
        assert provider._llm is None

    def test_llm_property_lazy_initialization(self):
        """Test that LLM is created lazily."""
        mock_llm = Mock()

        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return mock_llm

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider({})

        # LLM should not be created yet
        assert provider._llm is None

        # First access should create LLM
        llm = provider.llm
        assert llm is mock_llm
        assert provider._llm is mock_llm

        # Second access should return same instance
        llm2 = provider.llm
        assert llm2 is mock_llm

    @patch("src.services.llm_provider_factory.BaseLLMProvider._create_llm")
    def test_generate_recommendation_with_structured_output(self, mock_create_llm):
        """Test generate_recommendation with structured output support."""
        mock_llm = Mock()
        mock_wrapper = Mock()
        mock_result = LLMRecommendationResponse(
            recommendations=["test", "result", "words", "here"],
            connection="test connection",
            explanation="test explanation for the connection",
        )

        mock_llm.with_structured_output.return_value = mock_wrapper
        mock_wrapper.invoke.return_value = mock_result
        mock_create_llm.return_value = mock_llm

        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return mock_create_llm()

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider({})
        result = provider.generate_recommendation("test prompt")

        assert result == mock_result
        mock_llm.with_structured_output.assert_called_once_with(LLMRecommendationResponse)
        mock_wrapper.invoke.assert_called_once_with("test prompt")

    @patch("src.services.llm_provider_factory.BaseLLMProvider._create_llm")
    def test_generate_recommendation_fallback_to_generate(self, mock_create_llm):
        """Test generate_recommendation fallback when structured output fails."""
        mock_llm = Mock()
        mock_llm.with_structured_output.side_effect = Exception("Structured output not supported")

        # Mock the llm to return a string directly (since __call__ is called first)
        mock_llm.return_value = "test,result,words,here"
        mock_create_llm.return_value = mock_llm

        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return mock_create_llm()

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider({})
        result = provider.generate_recommendation("test prompt")

        assert result == "test,result,words,here"
        mock_llm.assert_called_once_with("test prompt")

    @patch("src.services.llm_provider_factory.BaseLLMProvider._create_llm")
    def test_generate_recommendation_handles_llm_result_object(self, mock_create_llm):
        """Test generate_recommendation handles LLMResult-like objects."""
        mock_llm = Mock()
        mock_llm.with_structured_output.side_effect = Exception("Not supported")

        # Create a mock LLMResult-like object
        mock_generation = Mock()
        mock_generation.text = "test,result,words,here"
        mock_result = Mock()
        mock_result.generations = [[mock_generation]]

        # Mock __call__ to fail, and remove invoke so it goes to generate path
        mock_llm.side_effect = Exception("Call failed")
        # Delete the invoke attribute so hasattr(llm, "invoke") returns False
        if hasattr(mock_llm, "invoke"):
            delattr(mock_llm, "invoke")
        mock_llm.generate.return_value = mock_result
        mock_create_llm.return_value = mock_llm

        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return mock_create_llm()

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider({})
        result = provider.generate_recommendation("test prompt")
        assert result == "test,result,words,here"

    @patch("src.services.llm_provider_factory.BaseLLMProvider._create_llm")
    def test_generate_recommendation_error_handling(self, mock_create_llm):
        """Test generate_recommendation error handling."""
        mock_llm = Mock()
        mock_llm.with_structured_output.side_effect = Exception("LLM error")
        mock_llm.generate.side_effect = Exception("Generate error")
        mock_create_llm.return_value = mock_llm

        class TestProvider(BaseLLMProvider):
            def _create_llm(self):
                return mock_create_llm()

            def get_provider_info(self):
                return {"provider_type": "test"}

        provider = TestProvider({})

        with pytest.raises(RuntimeError, match="LLM generation failed"):
            provider.generate_recommendation("test prompt")


class TestSimpleLLMProvider:
    """Test cases for SimpleLLMProvider."""

    def test_simple_provider_initialization(self):
        """Test SimpleLLMProvider initialization."""
        provider = SimpleLLMProvider({})
        assert provider.config == {}
        assert provider._llm is None

    def test_simple_provider_create_llm(self):
        """Test SimpleLLMProvider LLM creation."""
        provider = SimpleLLMProvider({})
        llm = provider._create_llm()

        # Should return a FakeListLLM
        from langchain_community.llms import FakeListLLM

        assert isinstance(llm, FakeListLLM)

    def test_simple_provider_info(self):
        """Test SimpleLLMProvider info."""
        provider = SimpleLLMProvider({})
        info = provider.get_provider_info()

        expected = {
            "provider_type": "simple",
            "model_name": None,
            "capabilities": ["basic_recommendations"],
            "requires_api_key": False,
        }
        assert info == expected

    def test_simple_provider_generate_recommendation(self):
        """Test SimpleLLMProvider recommendation generation."""
        provider = SimpleLLMProvider({})
        result = provider.generate_recommendation("test prompt")

        # Should return one of the predefined responses
        expected_responses = [
            "BASS, FLOUNDER, SALMON, TROUT",
            "PIANO, GUITAR, VIOLIN, DRUMS",
            "RED, BLUE, GREEN, YELLOW",
            "APPLE, BANANA, ORANGE, GRAPE",
        ]
        assert result in expected_responses


class TestOllamaLLMProvider:
    """Test cases for OllamaLLMProvider."""

    def test_ollama_provider_initialization(self):
        """Test OllamaLLMProvider initialization."""
        config = {"base_url": "http://localhost:11434", "model_name": "llama2"}
        provider = OllamaLLMProvider(config)
        assert provider.config == config

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_provider_create_llm_success(self, mock_chat_ollama):
        """Test successful Ollama LLM creation."""
        config = {"base_url": "http://localhost:11434", "model_name": "llama2", "timeout": 600}
        provider = OllamaLLMProvider(config)

        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance

        llm = provider._create_llm()

        assert llm is mock_instance
        mock_chat_ollama.assert_called_once_with(base_url="http://localhost:11434", model="llama2")

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_provider_create_llm_with_defaults(self, mock_chat_ollama):
        """Test Ollama LLM creation with default values."""
        provider = OllamaLLMProvider({})

        mock_instance = Mock()
        mock_chat_ollama.return_value = mock_instance

        provider._create_llm()

        mock_chat_ollama.assert_called_once_with(base_url="http://localhost:11434", model="qwen2.5:32b")

    def test_ollama_provider_create_llm_import_error(self):
        """Test Ollama LLM creation when dependencies are missing."""
        provider = OllamaLLMProvider({})

        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            with pytest.raises(RuntimeError, match="Ollama dependencies not installed"):
                provider._create_llm()

    @patch("langchain_ollama.ChatOllama")
    def test_ollama_provider_create_llm_general_error(self, mock_chat_ollama):
        """Test Ollama LLM creation with general error."""
        provider = OllamaLLMProvider({})
        mock_chat_ollama.side_effect = Exception("Connection failed")

        with pytest.raises(RuntimeError, match="Failed to create Ollama LLM"):
            provider._create_llm()

    def test_ollama_provider_info(self):
        """Test OllamaLLMProvider info."""
        config = {"base_url": "http://custom:11434", "model_name": "custom_model"}
        provider = OllamaLLMProvider(config)
        info = provider.get_provider_info()

        expected = {
            "provider_type": "ollama",
            "model_name": "custom_model",
            "base_url": "http://custom:11434",
            "capabilities": ["context_aware_recommendations", "explanation_generation"],
            "requires_api_key": False,
        }
        assert info == expected

    def test_ollama_provider_info_defaults(self):
        """Test OllamaLLMProvider info with defaults."""
        provider = OllamaLLMProvider({})
        info = provider.get_provider_info()

        expected = {
            "provider_type": "ollama",
            "model_name": "qwen2.5:32b",
            "base_url": "http://localhost:11434",
            "capabilities": ["context_aware_recommendations", "explanation_generation"],
            "requires_api_key": False,
        }
        assert info == expected


class TestOpenAILLMProvider:
    """Test cases for OpenAILLMProvider."""

    def test_openai_provider_initialization(self):
        """Test OpenAILLMProvider initialization."""
        config = {"api_key": "sk-test123", "model_name": "gpt-4"}
        provider = OpenAILLMProvider(config)
        assert provider.config == config

    @patch("langchain_openai.ChatOpenAI")
    def test_openai_provider_create_llm_success(self, mock_chat_openai):
        """Test successful OpenAI LLM creation."""
        config = {"api_key": "sk-test123", "model_name": "gpt-4", "timeout": 600}
        provider = OpenAILLMProvider(config)

        mock_instance = Mock()
        mock_chat_openai.return_value = mock_instance

        llm = provider._create_llm()

        assert llm is mock_instance
        mock_chat_openai.assert_called_once_with(model_name="gpt-4", openai_api_key="sk-test123")

    def test_openai_provider_create_llm_no_api_key(self):
        """Test OpenAI LLM creation without API key."""
        provider = OpenAILLMProvider({})

        with pytest.raises(RuntimeError, match="Failed to create OpenAI LLM"):
            provider._create_llm()

    def test_openai_provider_create_llm_import_error(self):
        """Test OpenAI LLM creation when dependencies are missing."""
        config = {"api_key": "sk-test123"}
        provider = OpenAILLMProvider(config)

        with patch("builtins.__import__", side_effect=ImportError("Module not found")):
            with pytest.raises(RuntimeError, match="OpenAI dependencies not installed"):
                provider._create_llm()

    @patch("langchain_openai.ChatOpenAI")
    def test_openai_provider_create_llm_general_error(self, mock_chat_openai):
        """Test OpenAI LLM creation with general error."""
        config = {"api_key": "sk-test123"}
        provider = OpenAILLMProvider(config)
        mock_chat_openai.side_effect = Exception("Authentication failed")

        with pytest.raises(RuntimeError, match="Failed to create OpenAI LLM"):
            provider._create_llm()

    def test_openai_provider_info(self):
        """Test OpenAILLMProvider info."""
        config = {"api_key": "sk-test123", "model_name": "gpt-4"}
        provider = OpenAILLMProvider(config)
        info = provider.get_provider_info()

        expected = {
            "provider_type": "openai",
            "model_name": "gpt-4",
            "capabilities": ["context_aware_recommendations", "explanation_generation", "high_quality_reasoning"],
            "requires_api_key": True,
        }
        assert info == expected

    def test_openai_provider_info_defaults(self):
        """Test OpenAILLMProvider info with defaults."""
        provider = OpenAILLMProvider({})
        info = provider.get_provider_info()

        expected = {
            "provider_type": "openai",
            "model_name": "gpt-4o-mini",
            "capabilities": ["context_aware_recommendations", "explanation_generation", "high_quality_reasoning"],
            "requires_api_key": True,
        }
        assert info == expected


class TestLLMProviderFactory:
    """Test cases for LLMProviderFactory."""

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_factory_initialization(self, mock_get_config_service):
        """Test LLMProviderFactory initialization."""
        mock_config_service = Mock()
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()

        assert factory.config_service is mock_config_service
        assert "simple" in factory._providers
        assert "ollama" in factory._providers
        assert "openai" in factory._providers

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_create_simple_provider(self, mock_get_config_service):
        """Test creating simple provider."""
        mock_config_service = Mock()
        mock_config_service.get_provider_config.return_value = {}
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        llm_provider = LLMProvider(provider_type="simple", model_name=None)

        provider = factory.create_provider(llm_provider)

        assert isinstance(provider, SimpleLLMProvider)
        assert provider.config == {}

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_create_openai_provider(self, mock_get_config_service):
        """Test creating OpenAI provider."""
        mock_config_service = Mock()
        mock_config = Mock()
        mock_config.dict.return_value = {"api_key": "sk-test123"}
        mock_config_service.get_provider_config.return_value = mock_config
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        llm_provider = LLMProvider(provider_type="openai", model_name="gpt-4")

        provider = factory.create_provider(llm_provider)

        assert isinstance(provider, OpenAILLMProvider)
        assert provider.config["api_key"] == "sk-test123"
        assert provider.config["model_name"] == "gpt-4"

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_create_provider_with_model_name_override(self, mock_get_config_service):
        """Test creating provider with model name override."""
        mock_config_service = Mock()
        mock_config_service.get_provider_config.return_value = {"base_url": "http://localhost:11434"}
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        llm_provider = LLMProvider(provider_type="ollama", model_name="custom_model")

        provider = factory.create_provider(llm_provider)

        assert isinstance(provider, OllamaLLMProvider)
        assert provider.config["model_name"] == "custom_model"
        assert provider.config["base_url"] == "http://localhost:11434"

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_create_provider_unsupported_type(self, mock_get_config_service):
        """Test creating provider with unsupported type."""
        mock_config_service = Mock()
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()

        # Test by bypassing Pydantic validation and manually setting provider_type
        # Create a Mock LLMProvider instead of real one to test factory logic
        mock_llm_provider = Mock()
        mock_llm_provider.provider_type = "unsupported"
        mock_llm_provider.model_name = None

        with pytest.raises(ValueError, match="Unsupported provider type: unsupported"):
            factory.create_provider(mock_llm_provider)

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_create_provider_no_config(self, mock_get_config_service):
        """Test creating provider when config is None."""
        mock_config_service = Mock()
        mock_config_service.get_provider_config.return_value = None
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        llm_provider = LLMProvider(provider_type="ollama", model_name="test_model")

        provider = factory.create_provider(llm_provider)

        assert isinstance(provider, OllamaLLMProvider)
        assert provider.config["model_name"] == "test_model"

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_get_available_providers(self, mock_get_config_service):
        """Test getting available providers."""
        mock_config_service = Mock()
        mock_config_service.validate_providers.return_value = {"simple": True, "openai": False, "ollama": True}
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        providers = factory.get_available_providers()

        expected = {"simple": True, "openai": False, "ollama": True}
        assert providers == expected

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_validate_provider_success(self, mock_get_config_service):
        """Test successful provider validation."""
        mock_config_service = Mock()
        mock_config_service.get_provider_config.return_value = {}
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()
        llm_provider = LLMProvider(provider_type="simple", model_name=None)

        result = factory.validate_provider(llm_provider)

        assert result is True

    @patch("src.services.llm_provider_factory.get_config_service")
    def test_validate_provider_failure(self, mock_get_config_service):
        """Test provider validation failure."""
        mock_config_service = Mock()
        mock_get_config_service.return_value = mock_config_service

        factory = LLMProviderFactory()

        # Use a mock to bypass Pydantic validation for testing factory logic
        mock_llm_provider = Mock()
        mock_llm_provider.provider_type = "unsupported"
        mock_llm_provider.model_name = None

        result = factory.validate_provider(mock_llm_provider)

        assert result is False


class TestGlobalFactory:
    """Test cases for global factory function."""

    @patch("src.services.llm_provider_factory._provider_factory", None)
    @patch("src.services.llm_provider_factory.LLMProviderFactory")
    def test_get_provider_factory_creates_instance(self, mock_factory_class):
        """Test that get_provider_factory creates new instance."""
        mock_instance = Mock()
        mock_factory_class.return_value = mock_instance

        result = get_provider_factory()

        assert result is mock_instance
        mock_factory_class.assert_called_once()

    def test_get_provider_factory_returns_existing_instance(self):
        """Test that get_provider_factory returns existing instance."""
        # First call should create instance
        factory1 = get_provider_factory()

        # Second call should return same instance
        factory2 = get_provider_factory()

        assert factory1 is factory2
