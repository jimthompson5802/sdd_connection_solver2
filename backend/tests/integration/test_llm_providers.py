"""
Integration tests for LLM provider functionality.
These tests validate LLM provider services integration.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLLMProviderIntegration:
    """Integration tests for LLM provider services"""

    @pytest.mark.integration
    def test_simple_provider_service_exists(self):
        """Test that simple provider service can be imported and instantiated"""
        # This will fail until implementation exists
        from src.services.llm_providers.simple_provider import SimpleProvider

        provider = SimpleProvider()
        assert provider is not None

    @pytest.mark.integration
    def test_ollama_provider_service_exists(self):
        """Test that ollama provider service can be imported and instantiated"""
        from src.services.llm_providers.ollama_provider import OllamaProvider

        provider = OllamaProvider(base_url="http://localhost:11434", model_name="llama2")
        assert provider is not None

    @pytest.mark.integration
    def test_openai_provider_service_exists(self):
        """Test that openai provider service can be imported and instantiated"""
        from src.services.llm_providers.openai_provider import OpenAIProvider

        provider = OpenAIProvider(api_key="test_key", model_name="gpt-3.5-turbo")
        assert provider is not None

    @pytest.mark.integration
    def test_simple_provider_generate_recommendations(self):
        """Test that simple provider can generate recommendations"""
        from src.services.llm_providers.simple_provider import SimpleProvider

        provider = SimpleProvider()

        # Should have generate_recommendations method
        assert hasattr(provider, "generate_recommendations")
        assert callable(getattr(provider, "generate_recommendations"))

        # Test method call
        remaining_words = ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR", "VIOLIN", "DRUMS"]
        previous_guesses = []

        result = provider.generate_recommendations(remaining_words, previous_guesses)

        # Validate result structure (legacy simple provider shape)
        assert isinstance(result, dict)
        assert "recommended_words" in result
        assert len(result["recommended_words"]) == 4
        assert result.get("connection_explanation") is None
        assert result.get("generation_time_ms") is None

        # All recommended words should be from remaining words
        for word in result["recommended_words"]:
            assert word in remaining_words

    @pytest.mark.integration
    @patch("langchain_community.llms.ollama.Ollama")
    def test_ollama_provider_generate_recommendations(self, mock_ollama):
        """Test that ollama provider can generate recommendations"""
        from src.services.llm_providers.ollama_provider import OllamaProvider

        # Mock ollama response as structured JSON object (dict) per new contract
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = {
            "recommended_words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
            "connection": "These are types of fish",
            "explanation": "Common types of fish found in North America",
        }
        mock_ollama.return_value = mock_llm

        provider = OllamaProvider(base_url="http://localhost:11434", model_name="llama2")

        remaining_words = ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR"]
        previous_guesses = []

        result = provider.generate_recommendations(remaining_words, previous_guesses)

        # Validate result structure for Ollama provider (structured output may include connection/explanation)
        assert isinstance(result, dict)
        assert "recommended_words" in result
        assert len(result["recommended_words"]) == 4
        # Accept either legacy key or new keys depending on provider shim
        assert ("connection_explanation" in result and result["connection_explanation"] is not None) or (
            "connection" in result and "explanation" in result
        )
        assert isinstance(result.get("generation_time_ms", 0), int)

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_generate_recommendations(self, mock_openai):
        """Test that openai provider can generate recommendations"""
        from src.services.llm_providers.openai_provider import OpenAIProvider

        # Mock openai response as structured JSON object (dict) per new contract
        mock_client = MagicMock()
        mock_response = MagicMock()
        # The provider code extracts resp.choices[0].message.content and expects a dict
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = {
            "recommended_words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
            "connection": "These are types of fish",
            "explanation": "Common types of fish found in North America",
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key", model_name="gpt-3.5-turbo")

        remaining_words = ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR"]
        previous_guesses = []

        result = provider.generate_recommendations(remaining_words, previous_guesses)

        # Validate result structure for OpenAI provider (may return structured JSON)
        assert isinstance(result, dict)
        assert "recommended_words" in result
        assert len(result["recommended_words"]) == 4
        assert ("connection_explanation" in result and result["connection_explanation"] is not None) or (
            "connection" in result and "explanation" in result
        )
        assert isinstance(result.get("generation_time_ms", 0), int)

    @pytest.mark.integration
    def test_provider_factory_exists(self):
        """Test that provider factory can be imported and used"""
        from src.services.llm_providers.provider_factory import ProviderFactory

        factory = ProviderFactory()
        assert factory is not None

        # Should have create_provider method
        assert hasattr(factory, "create_provider")
        assert callable(getattr(factory, "create_provider"))

    @pytest.mark.integration
    def test_provider_factory_creates_simple_provider(self):
        """Test that factory can create simple provider"""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.models import LLMProvider

        factory = ProviderFactory()

        llm_provider = LLMProvider(provider_type="simple", model_name=None)
        provider = factory.create_provider(llm_provider)

        assert provider is not None
        assert provider.__class__.__name__ == "SimpleProvider"

    @pytest.mark.integration
    def test_provider_factory_creates_ollama_provider(self):
        """Test that factory can create ollama provider"""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.models import LLMProvider

        factory = ProviderFactory()

        llm_provider = LLMProvider(provider_type="ollama", model_name="llama2")
        provider = factory.create_provider(llm_provider)

        assert provider is not None
        assert provider.__class__.__name__ == "OllamaProvider"

    @pytest.mark.integration
    def test_provider_factory_creates_openai_provider(self):
        """Test that factory can create openai provider"""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.models import LLMProvider

        factory = ProviderFactory()

        llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")
        provider = factory.create_provider(llm_provider)

        assert provider is not None
        assert provider.__class__.__name__ == "OpenAIProvider"
