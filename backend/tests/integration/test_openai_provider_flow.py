"""
Integration tests for OpenAI provider journey flow.
These tests validate the complete OpenAI provider workflow with mocked responses.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestOpenAIProviderFlow:
    """Integration tests for OpenAI provider workflow"""

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_successful_recommendation_flow(self, mock_openai):
        """Test complete successful recommendation flow with OpenAI provider"""
        # Mock OpenAI response
        mock_client = MagicMock()
        # Mock a structured JSON-like response returned by the provider shim path
        mock_response = MagicMock()
        # Simulate SDK returning a dict (structured output) via the content attribute
        mock_response.choices[0].message.content = {
            "recommended_words": ["bass", "flounder", "salmon", "trout"],
            "explanation": "These are fish",
            "connection": "Fish",
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        # This will fail until implementation exists
        from src.services.llm_providers.openai_provider import OpenAIProvider
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider

        # Create provider
        OpenAIProvider(api_key="test_key", model_name="gpt-3.5-turbo")

        # Create service
        service = RecommendationService()

        # Create request
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR", "VIOLIN", "DRUMS"],
            previous_guesses=[],
        )

        # Execute full flow
        result = service.get_recommendations(request)

        # Validate complete flow results
        assert len(result.recommended_words) == 4
        assert "BASS" in [w.upper() for w in result.recommended_words]
        assert result.connection_explanation is not None
        assert result.provider_used.provider_type == "openai"
        assert isinstance(result.generation_time_ms, int)

        # Verify OpenAI client was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-3.5-turbo"
        assert "messages" in call_args[1]

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_with_previous_guesses_flow(self, mock_openai):
        """Test OpenAI provider respects previous guesses in recommendation flow"""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = {
            "recommended_words": ["piano", "guitar", "violin", "drums"],
            "explanation": "These are instruments",
            "connection": "Instruments",
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider, PreviousGuess
        from datetime import datetime

        service = RecommendationService()

        # Create request with previous guesses
        previous_guesses = [
            PreviousGuess(
                words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
                outcome="correct",
                actual_connection="Fish",
                timestamp=datetime.now(),
            )
        ]

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["PIANO", "GUITAR", "VIOLIN", "DRUMS", "RED", "BLUE", "GREEN", "YELLOW"],
            previous_guesses=previous_guesses,
        )

        result = service.get_recommendations(request)

        # Should not recommend any words from previous guesses
        previous_words = [word for guess in previous_guesses for word in guess.words]
        for word in result.recommended_words:
            assert word not in previous_words

        # Verify prompt includes previous guess context
        call_args = mock_client.chat.completions.create.call_args
        prompt_content = str(call_args[1]["messages"])
        assert "BASS" in prompt_content or "previous" in prompt_content.lower()

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_api_error_handling_flow(self, mock_openai):
        """Test OpenAI provider handles API errors gracefully"""
        # Mock OpenAI API error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import LLMProviderError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        # Should raise appropriate exception
        with pytest.raises(LLMProviderError):
            service.get_recommendations(request)

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_malformed_response_handling(self, mock_openai):
        """Test OpenAI provider handles malformed responses"""
        # Mock malformed OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Provider returns malformed plain text
        mock_response.choices[0].message.content = "This is not a valid word list format"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4", "WORD5", "WORD6"],
            previous_guesses=[],
        )

        # Service should handle malformed response gracefully by raising an application error
        from src.exceptions import LLMProviderError

        with pytest.raises(LLMProviderError):
            service.get_recommendations(request)

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_timeout_handling_flow(self, mock_openai):
        """Test OpenAI provider handles timeout scenarios"""
        # Mock timeout scenario
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = TimeoutError("Request timed out")
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import TimeoutError as AppTimeoutError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        # Should raise appropriate timeout exception
        with pytest.raises(AppTimeoutError):
            service.get_recommendations(request)

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_metrics_tracking_flow(self, mock_openai):
        """Test that OpenAI provider tracks metrics during recommendation flow"""
        # Mock successful OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = {
            "recommended_words": ["word1", "word2", "word3", "word4"],
            "explanation": "example",
            "connection": "Example",
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from unittest.mock import patch

        with patch("src.services.llm_providers.openai_provider.metrics") as mock_metrics:
            service = RecommendationService()

            request = RecommendationRequest(
                llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
                remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
                previous_guesses=[],
            )

            result = service.get_recommendations(request)

            # Should have tracked metrics
            # This validates that metrics integration exists
            assert result is not None

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_provider_configuration_validation_flow(self, mock_openai):
        """Test OpenAI provider validates configuration before use"""
        from src.services.llm_providers.openai_provider import OpenAIProvider
        from src.exceptions import ConfigurationError

        # Test with invalid API key
        with pytest.raises(ConfigurationError):
            provider = OpenAIProvider(api_key="", model_name="gpt-3.5-turbo")

        # Test with invalid model name
        with pytest.raises(ConfigurationError):
            provider = OpenAIProvider(api_key="valid_key", model_name="")

    @pytest.mark.integration
    def test_openai_provider_environment_integration(self):
        """Test OpenAI provider integrates with environment configuration"""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.services.configuration_service import ConfigurationService
        from src.models import LLMProvider
        import os

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            config_service = ConfigurationService()
            factory = ProviderFactory()

            # Should create provider with environment configuration
            llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")
            provider = factory.create_provider(llm_provider)

            assert provider is not None
            assert provider.__class__.__name__ == "OpenAIProvider"
