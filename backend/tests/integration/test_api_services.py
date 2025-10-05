"""
Integration tests for API service functionality.
These tests validate the recommendation service integration.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestAPIServiceIntegration:
    """Integration tests for API service functionality"""

    @pytest.mark.integration
    def test_recommendation_service_exists(self):
        """Test that recommendation service can be imported and instantiated"""
        # This will fail until implementation exists
        from src.services.recommendation_service import RecommendationService

        service = RecommendationService()
        assert service is not None

    @pytest.mark.integration
    def test_recommendation_service_methods_exist(self):
        """Test that recommendation service has required methods"""
        from src.services.recommendation_service import RecommendationService

        service = RecommendationService()

        # Should have get_recommendations method
        assert hasattr(service, "get_recommendations")
        assert callable(getattr(service, "get_recommendations"))

    @pytest.mark.integration
    def test_get_recommendations_with_simple_provider(self):
        """Test that service can process simple provider requests"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider

        service = RecommendationService()

        # Create test request
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR", "VIOLIN", "DRUMS"],
            previous_guesses=[],
        )

        # Call service method
        result = service.get_recommendations(request)

        # Validate result structure
        assert hasattr(result, "recommended_words")
        assert hasattr(result, "connection_explanation")
        assert hasattr(result, "confidence_score")
        assert hasattr(result, "provider_used")
        assert hasattr(result, "generation_time_ms")

        # Validate simple provider behavior
        assert len(result.recommended_words) == 4
        assert result.connection_explanation is None
        assert result.confidence_score is None
        assert result.provider_used.provider_type == "simple"
        assert result.generation_time_ms is None

    @pytest.mark.integration
    @patch("src.services.llm_providers.ollama_provider.Ollama")
    def test_get_recommendations_with_ollama_provider(self, mock_ollama):
        """Test that service can process ollama provider requests"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider

        # Mock ollama response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = "BASS, FLOUNDER, SALMON, TROUT"
        mock_ollama.return_value = mock_llm

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="ollama", model_name="llama2"),
            remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR"],
            previous_guesses=[],
        )

        result = service.get_recommendations(request)

        # Validate ollama provider behavior
        assert len(result.recommended_words) == 4
        assert result.connection_explanation is not None
        assert result.provider_used.provider_type == "ollama"
        assert result.provider_used.model_name == "llama2"
        assert isinstance(result.generation_time_ms, int)

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_get_recommendations_with_openai_provider(self, mock_openai):
        """Test that service can process openai provider requests"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider

        # Mock openai response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "BASS, FLOUNDER, SALMON, TROUT"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR"],
            previous_guesses=[],
        )

        result = service.get_recommendations(request)

        # Validate openai provider behavior
        assert len(result.recommended_words) == 4
        assert result.connection_explanation is not None
        assert result.provider_used.provider_type == "openai"
        assert result.provider_used.model_name == "gpt-3.5-turbo"
        assert isinstance(result.generation_time_ms, int)

    @pytest.mark.integration
    def test_service_handles_invalid_provider(self):
        """Test that service properly handles invalid provider types"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InvalidProviderError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="invalid_provider", model_name="some_model"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        # Should raise appropriate exception
        with pytest.raises(InvalidProviderError):
            service.get_recommendations(request)

    @pytest.mark.integration
    def test_service_handles_insufficient_words(self):
        """Test that service properly handles insufficient word count"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InsufficientWordsError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["WORD1", "WORD2"],  # Only 2 words
            previous_guesses=[],
        )

        # Should raise appropriate exception
        with pytest.raises(InsufficientWordsError):
            service.get_recommendations(request)

    @pytest.mark.integration
    def test_service_respects_previous_guesses(self):
        """Test that service excludes words from previous guesses"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider, PreviousGuess
        from datetime import datetime

        service = RecommendationService()

        previous_guesses = [
            PreviousGuess(
                words=["RED", "BLUE", "GREEN", "YELLOW"],
                outcome="incorrect",
                actual_connection=None,
                timestamp=datetime.now(),
            )
        ]

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
            previous_guesses=previous_guesses,
        )

        result = service.get_recommendations(request)

        # Should not include any words from previous guesses
        previous_words = [word for guess in previous_guesses for word in guess.words]
        for word in result.recommended_words:
            assert word not in previous_words

    @pytest.mark.integration
    def test_health_service_exists(self):
        """Test that health service can be imported and instantiated"""
        from src.services.health_service import HealthService

        service = HealthService()
        assert service is not None

    @pytest.mark.integration
    def test_health_service_check_health(self):
        """Test that health service can check system health"""
        from src.services.health_service import HealthService

        service = HealthService()

        # Should have check_health method
        assert hasattr(service, "check_health")
        assert callable(getattr(service, "check_health"))

        # Call health check
        result = service.check_health()

        # Validate health check result structure
        assert hasattr(result, "status")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "version")
        assert hasattr(result, "providers_available")

        # Status should be valid
        assert result.status in ["healthy", "degraded", "unhealthy"]

        # Should have providers information
        assert isinstance(result.providers_available, list)

        # Should at least have simple provider
        provider_types = [p.provider_type for p in result.providers_available]
        assert "simple" in provider_types
