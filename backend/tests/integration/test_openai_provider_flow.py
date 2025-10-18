"""
Integration tests for OpenAI provider journey flow.
These tests validate the complete OpenAI provider workflow with mocked providers via the factory.
"""

import os
from datetime import datetime
from unittest.mock import patch

import pytest


class TestOpenAIProviderFlow:
    """Integration tests for OpenAI provider workflow"""

    @pytest.mark.integration
    @patch("src.services.llm_provider_factory.LLMProviderFactory.create_provider")
    def test_openai_provider_successful_recommendation_flow(self, mock_create_provider):
        """Test complete successful recommendation flow with OpenAI provider using factory patch."""

        class _FakeProvider:
            def generate_recommendation(self, prompt: str):
                class _Resp:
                    recommendations = ["bass", "flounder", "salmon", "trout"]
                    connection = "Fish"

                return _Resp()

        mock_create_provider.return_value = _FakeProvider()

        from src.services.recommendation_service import RecommendationService
        from src.llm_models.recommendation_request import RecommendationRequest
        from src.llm_models.llm_provider import LLMProvider

        service = RecommendationService()
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=[
                "BASS",
                "FLOUNDER",
                "SALMON",
                "TROUT",
                "PIANO",
                "GUITAR",
                "VIOLIN",
                "DRUMS",
            ],
            previous_guesses=[],
        )

        result = service.get_recommendations(req)

        assert len(result.recommended_words) == 4
        assert set(w.lower() for w in result.recommended_words) == {"bass", "flounder", "salmon", "trout"}
        assert result.connection_explanation == "Fish"
        assert result.provider_used.provider_type == "openai"
        assert isinstance(result.generation_time_ms, int)

    @pytest.mark.integration
    @patch("src.services.llm_provider_factory.LLMProviderFactory.create_provider")
    def test_openai_provider_with_previous_guesses_flow(self, mock_create_provider):
        """Test OpenAI provider respects previous guesses by returning different words."""

        class _FakeProvider:
            def generate_recommendation(self, prompt: str):
                class _Resp:
                    recommendations = ["piano", "guitar", "violin", "drums"]
                    connection = "Instruments"

                return _Resp()

        mock_create_provider.return_value = _FakeProvider()

        from src.services.recommendation_service import RecommendationService
        from src.llm_models.recommendation_request import RecommendationRequest
        from src.llm_models.llm_provider import LLMProvider
        from src.models import PreviousGuess
        from src.llm_models.guess_attempt import GuessOutcome

        service = RecommendationService()
        prev = [
            PreviousGuess(
                words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
                outcome=GuessOutcome.CORRECT,
                actual_connection="Fish",
                timestamp=datetime.now(),
            )
        ]
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=[
                "PIANO",
                "GUITAR",
                "VIOLIN",
                "DRUMS",
                "RED",
                "BLUE",
                "GREEN",
                "YELLOW",
            ],
            previous_guesses=prev,
        )

        result = service.get_recommendations(req)

        prev_words = [w for g in prev for w in g.words]
        for w in result.recommended_words:
            assert w not in prev_words

    @pytest.mark.integration
    @patch("src.services.llm_provider_factory.LLMProviderFactory.create_provider")
    def test_openai_provider_api_error_handling_flow(self, mock_create_provider):
        """Test OpenAI provider handles API errors gracefully via service wrapper."""

        class _FakeProvider:
            def generate_recommendation(self, prompt: str):
                raise Exception("API rate limit exceeded")

        mock_create_provider.return_value = _FakeProvider()

        from src.services.recommendation_service import RecommendationService
        from src.llm_models.recommendation_request import RecommendationRequest
        from src.llm_models.llm_provider import LLMProvider
        from src.exceptions import LLMProviderError

        service = RecommendationService()
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        with pytest.raises(LLMProviderError):
            service.get_recommendations(req)

    @pytest.mark.integration
    @patch("src.services.llm_provider_factory.LLMProviderFactory.create_provider")
    def test_openai_provider_malformed_response_handling(self, mock_create_provider):
        """Test OpenAI provider handles malformed responses by surfacing an app error."""

        class _FakeProvider:
            def generate_recommendation(self, prompt: str):
                return "not-a-structured-object"

        mock_create_provider.return_value = _FakeProvider()

        from src.services.recommendation_service import RecommendationService
        from src.llm_models.recommendation_request import RecommendationRequest
        from src.llm_models.llm_provider import LLMProvider
        from src.exceptions import LLMProviderError

        service = RecommendationService()
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4", "WORD5", "WORD6"],
            previous_guesses=[],
        )

        with pytest.raises(LLMProviderError):
            service.get_recommendations(req)

    @pytest.mark.integration
    @patch("src.services.llm_provider_factory.LLMProviderFactory.create_provider")
    def test_openai_provider_timeout_handling_flow(self, mock_create_provider):
        """Test OpenAI provider handles timeout scenarios and maps to app TimeoutError."""

        class _FakeProvider:
            def generate_recommendation(self, prompt: str):
                raise TimeoutError("Request timed out")

        mock_create_provider.return_value = _FakeProvider()

        from src.services.recommendation_service import RecommendationService
        from src.llm_models.recommendation_request import RecommendationRequest
        from src.llm_models.llm_provider import LLMProvider
        from src.exceptions import LLMProviderError

        service = RecommendationService()
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        with pytest.raises(LLMProviderError):
            service.get_recommendations(req)

    @pytest.mark.integration
    def test_openai_provider_configuration_validation_flow(self):
        """Test OpenAI provider validates configuration before use."""
        from src.services.llm_providers.openai_provider import OpenAIProvider
        from src.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError):
            _ = OpenAIProvider(api_key="", model_name="gpt-3.5-turbo")
        with pytest.raises(ConfigurationError):
            _ = OpenAIProvider(api_key="valid_key", model_name="")

    @pytest.mark.integration
    def test_openai_provider_environment_integration(self):
        """Test OpenAI provider integrates with environment configuration via legacy factory."""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.services.configuration_service import ConfigurationService
        from src.llm_models.llm_provider import LLMProvider

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            _ = ConfigurationService()
            factory = ProviderFactory()
            llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")
            provider = factory.create_provider(llm_provider)
            assert provider is not None
            assert provider.__class__.__name__ == "OpenAIProvider"
