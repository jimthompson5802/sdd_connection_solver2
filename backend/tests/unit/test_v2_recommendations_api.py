"""
Simplified unit tests for v2 recommendations API endpoints.
Focus on critical API behavior and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime

from src.api.v2_recommendations import router, get_recommendation_service
from src.models import RecommendationResponse, LLMProvider
from src.llm_models.guess_attempt import GuessAttempt, GuessOutcome
from src.services.recommendation_service import RecommendationService
from src.exceptions import (
    LLMProviderError,
    ValidationError as AppValidationError,
    InsufficientWordsError,
)


@pytest.fixture
def test_client():
    """Create FastAPI test client with the router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_request_data():
    """Sample recommendation request data."""
    return {
        "llm_provider": {"provider_type": "simple", "model_name": None},
        "remaining_words": ["BASS", "PIKE", "SOLE", "CARP", "APPLE", "BANANA", "CHERRY", "GRAPE"],
        "previous_guesses": [],
        "puzzle_context": None,
    }


class TestGetRecommendationService:
    """Tests for the get_recommendation_service dependency."""

    def test_successful_service_creation(self):
        """Test successful creation of RecommendationService."""
        with patch('src.api.v2_recommendations.RecommendationService') as mock_service_class:
            mock_service_instance = Mock()
            mock_service_class.return_value = mock_service_instance
            
            result = get_recommendation_service()
            
            assert result == mock_service_instance
            mock_service_class.assert_called_once()

    def test_service_creation_failure(self):
        """Test HTTPException when service creation fails."""
        with patch('src.api.v2_recommendations.RecommendationService') as mock_service_class:
            mock_service_class.side_effect = Exception("Service initialization failed")
            
            with pytest.raises(HTTPException) as exc_info:
                get_recommendation_service()
            
            assert exc_info.value.status_code == 500
            assert "Failed to initialize recommendation service" in exc_info.value.detail


class TestAPI:
    """Tests for API endpoint behavior."""

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_successful_recommendation_direct_mock(self, mock_service_class, test_client, sample_request_data):
        """Test successful recommendation with direct service mock."""
        # Setup the mock
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service
        
        # Create a valid response
        expected_response = RecommendationResponse(
            recommended_words=["bass", "pike", "sole", "carp"],
            connection_explanation=None,
            provider_used=LLMProvider(provider_type="simple", model_name=None),
            generation_time_ms=None,
        )
        mock_service.generate_recommendation.return_value = expected_response
        
        # Make the request
        response = test_client.post("/api/v2/recommendations", json=sample_request_data)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["recommended_words"] == ["bass", "pike", "sole", "carp"]
        assert data["connection_explanation"] is None
        assert data["provider_used"]["provider_type"] == "simple"
        assert data["generation_time_ms"] is None
        
        # Verify service was called
        mock_service.generate_recommendation.assert_called_once()

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_insufficient_words_error_handling(self, mock_service_class, test_client, sample_request_data):
        """Test InsufficientWordsError handling."""
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service
        
        # Setup the error
        error = InsufficientWordsError(word_count=2, required_count=4)
        mock_service.generate_recommendation.side_effect = error
        
        response = test_client.post("/api/v2/recommendations", json=sample_request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "Insufficient Words"
        assert data["detail"]["error_code"] == "INSUFFICIENT_WORDS"

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_llm_provider_error_handling(self, mock_service_class, test_client, sample_request_data):
        """Test LLMProviderError handling."""
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service
        
        # Setup the error
        error = LLMProviderError(
            message="Connection failed",
            provider_type="ollama",
            error_code="CONNECTION_ERROR"
        )
        mock_service.generate_recommendation.side_effect = error
        
        response = test_client.post("/api/v2/recommendations", json=sample_request_data)
        
        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error"] == "LLM Provider Error"
        assert data["detail"]["error_code"] == "CONNECTION_ERROR"
        assert data["detail"]["provider_type"] == "ollama"

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_validation_error_handling(self, mock_service_class, test_client, sample_request_data):
        """Test ValidationError handling."""
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service
        
        # Setup the error
        error = AppValidationError(
            validation_errors=["Invalid request format"],
            response_data={"field": "words"}
        )
        mock_service.generate_recommendation.side_effect = error
        
        response = test_client.post("/api/v2/recommendations", json=sample_request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"] == "Validation Error"
        assert data["detail"]["error_code"] == "VALIDATION_ERROR"

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_unexpected_error_handling(self, mock_service_class, test_client, sample_request_data):
        """Test unexpected error handling."""
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service
        
        # Setup the error
        mock_service.generate_recommendation.side_effect = RuntimeError("Unexpected error")
        
        response = test_client.post("/api/v2/recommendations", json=sample_request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert data["detail"]["error"] == "Internal Server Error"
        assert data["detail"]["error_code"] == "INTERNAL_ERROR"

    def test_health_endpoint(self, test_client):
        """Test health check endpoint."""
        with patch('src.api.v2_recommendations.RecommendationService'):
            response = test_client.get("/api/v2/recommendations/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "recommendation-service"
            assert data["version"] == "2.0"
            assert "available_providers" in data

    def test_providers_endpoint(self, test_client):
        """Test providers list endpoint."""
        with patch('src.api.v2_recommendations.RecommendationService'):
            response = test_client.get("/api/v2/recommendations/providers")
            
            assert response.status_code == 200
            data = response.json()
            assert "providers" in data
            assert "default_provider" in data
            assert "total_count" in data
            assert data["default_provider"] == "simple"
            assert data["total_count"] == 3


class TestInputValidation:
    """Tests for input validation."""

    def test_invalid_provider_type(self, test_client):
        """Test invalid provider type validation."""
        invalid_request = {
            "llm_provider": {"provider_type": "invalid", "model_name": None},
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            "previous_guesses": [],
            "puzzle_context": None,
        }
        
        response = test_client.post("/api/v2/recommendations", json=invalid_request)
        assert response.status_code == 422

    def test_missing_required_fields(self, test_client):
        """Test missing required fields validation."""
        incomplete_request = {
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            # Missing llm_provider
        }
        
        response = test_client.post("/api/v2/recommendations", json=incomplete_request)
        assert response.status_code == 422

    def test_empty_words_list_validation(self, test_client):
        """Test empty words list validation."""
        empty_request = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": [],
            "previous_guesses": [],
            "puzzle_context": None,
        }
        
        response = test_client.post("/api/v2/recommendations", json=empty_request)
        assert response.status_code == 422

    def test_malformed_json(self, test_client):
        """Test malformed JSON handling."""
        response = test_client.post(
            "/api/v2/recommendations",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestModelValidation:
    """Tests for model validation rules."""

    def test_simple_provider_response_validation(self):
        """Test that simple provider responses follow validation rules."""
        # Valid simple provider response
        valid_response = RecommendationResponse(
            recommended_words=["word1", "word2", "word3", "word4"],
            connection_explanation=None,  # Must be None for simple
            provider_used=LLMProvider(provider_type="simple", model_name=None),
            generation_time_ms=None,  # Must be None for simple
        )
        assert valid_response.provider_used.provider_type == "simple"
        assert valid_response.connection_explanation is None
        assert valid_response.generation_time_ms is None

    def test_llm_provider_response_validation(self):
        """Test that LLM provider responses allow explanations and timing."""
        # Valid LLM provider response
        valid_response = RecommendationResponse(
            recommended_words=["word1", "word2", "word3", "word4"],
            connection_explanation="These are test words",
            provider_used=LLMProvider(provider_type="openai", model_name="gpt-4"),
            generation_time_ms=1500,
        )
        assert valid_response.provider_used.provider_type == "openai"
        assert valid_response.connection_explanation == "These are test words"
        assert valid_response.generation_time_ms == 1500

    def test_guess_attempt_validation(self):
        """Test GuessAttempt validation."""
        # Valid guess attempt
        guess = GuessAttempt(
            words=["WORD1", "WORD2", "WORD3", "WORD4"],
            outcome=GuessOutcome.INCORRECT,
            timestamp=datetime.now().replace(microsecond=0)
        )
        assert len(guess.words) == 4
        assert guess.outcome == GuessOutcome.INCORRECT

    def test_invalid_guess_attempt_too_few_words(self):
        """Test GuessAttempt validation with too few words."""
        with pytest.raises(ValueError, match="words must contain exactly 4 items"):
            GuessAttempt(
                words=["WORD1", "WORD2"],  # Only 2 words
                outcome=GuessOutcome.INCORRECT,
                timestamp=datetime.now()
            )

    def test_invalid_guess_attempt_duplicate_words(self):
        """Test GuessAttempt validation with duplicate words."""
        with pytest.raises(ValueError, match="words must not contain duplicates"):
            GuessAttempt(
                words=["WORD1", "WORD1", "WORD3", "WORD4"],  # Duplicate
                outcome=GuessOutcome.INCORRECT,
                timestamp=datetime.now()
            )


class TestEndpointIntegration:
    """Integration tests for complete endpoint behavior."""

    def test_all_endpoints_accessible(self, test_client):
        """Test that all expected endpoints are accessible."""
        with patch('src.api.v2_recommendations.RecommendationService'):
            # Test recommendations endpoint
            response = test_client.post("/api/v2/recommendations", json={})
            assert response.status_code != 404  # Should get validation error, not 404

            # Test health endpoint
            response = test_client.get("/api/v2/recommendations/health")
            assert response.status_code == 200

            # Test providers endpoint
            response = test_client.get("/api/v2/recommendations/providers")
            assert response.status_code == 200

    @patch('src.api.v2_recommendations.RecommendationService')
    def test_different_provider_types(self, mock_service_class, test_client):
        """Test different provider types in requests."""
        mock_service = Mock(spec=RecommendationService)
        mock_service_class.return_value = mock_service

        # Test simple provider
        simple_response = RecommendationResponse(
            recommended_words=["word1", "word2", "word3", "word4"],
            connection_explanation=None,
            provider_used=LLMProvider(provider_type="simple", model_name=None),
            generation_time_ms=None,
        )
        mock_service.generate_recommendation.return_value = simple_response

        simple_request = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = test_client.post("/api/v2/recommendations", json=simple_request)
        assert response.status_code == 200
        data = response.json()
        assert data["provider_used"]["provider_type"] == "simple"

        # Test ollama provider  
        ollama_response = RecommendationResponse(
            recommended_words=["word1", "word2", "word3", "word4"],
            connection_explanation="Test explanation",
            provider_used=LLMProvider(provider_type="ollama", model_name="llama2"),
            generation_time_ms=2500,
        )
        mock_service.generate_recommendation.return_value = ollama_response

        ollama_request = {
            "llm_provider": {"provider_type": "ollama", "model_name": "llama2"},
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = test_client.post("/api/v2/recommendations", json=ollama_request)
        assert response.status_code == 200
        data = response.json()
        assert data["provider_used"]["provider_type"] == "ollama"
        assert data["provider_used"]["model_name"] == "llama2"