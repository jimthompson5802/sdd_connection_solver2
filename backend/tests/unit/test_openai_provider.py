import pytest
from src.services.llm_providers.openai_provider import OpenAIProvider
from src.exceptions import ConfigurationError


class TestOpenAIProvider:
    """Test cases for OpenAIProvider."""

    def test_constructor_with_valid_api_key(self):
        """Test constructor with valid API key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider._api_key == "test-key"

    def test_constructor_with_empty_api_key(self):
        """Test constructor with empty API key raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="API key is required"):
            OpenAIProvider(api_key="")

    def test_constructor_with_whitespace_api_key(self):
        """Test constructor with whitespace API key raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="API key is required"):
            OpenAIProvider(api_key="   ")

    def test_constructor_with_model_name(self):
        """Test constructor with custom model name."""
        provider = OpenAIProvider(api_key="test-key", model_name="gpt-3.5-turbo")
        assert provider._model_name == "gpt-3.5-turbo"

    def test_constructor_with_empty_model_name(self):
        """Test constructor with empty model name raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="model_name is required"):
            OpenAIProvider(api_key="test-key", model_name="")

    def test_has_required_methods(self):
        """Test that provider has required public methods."""
        provider = OpenAIProvider(api_key="test-key")

        # Check methods exist
        assert hasattr(provider, "generate_recommendations")
        assert hasattr(provider, "generate_recommendation")

        # Check methods are callable
        assert callable(provider.generate_recommendations)
        assert callable(provider.generate_recommendation)

    def test_default_model_name(self):
        """Test that default model name is set correctly."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider._model_name == "gpt-4o-mini"
