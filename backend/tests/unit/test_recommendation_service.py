"""Unit tests for recommendation engine logic.

Tests cover:
- RecommendationEngine initialization and configuration
- Word grouping logic and similarity analysis
- Edge cases and error handling
- Performance and reliability characteristics
"""

import pytest
from unittest.mock import Mock, patch
from src.recommendation_engine import RecommendationEngine
from src.models import PuzzleSession
from src.services.recommendation_service import RecommendationService
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider
from src.exceptions import (
    LLMProviderError,
    InsufficientWordsError,
    InvalidInputError,
)


class TestRecommendationEngine:
    """Test suite for RecommendationEngine functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = RecommendationEngine()
        self.sample_session = PuzzleSession(
            [
                "BASS",
                "FLOUNDER",
                "SALMON",
                "TROUT",
                "GUITAR",
                "PIANO",
                "VIOLIN",
                "DRUMS",
                "RED",
                "BLUE",
                "GREEN",
                "YELLOW",
                "CAR",
                "BUS",
                "TRAIN",
                "PLANE",
            ]
        )

    def test_initialization(self):
        """Test that RecommendationEngine initializes with proper defaults."""
        engine = RecommendationEngine()
        assert engine is not None

    def test_get_recommendation_returns_tuple(self):
        """Test that get_recommendation returns a tuple of (words, connection)."""
        recommendation = self.engine.get_recommendation(self.sample_session)

        assert isinstance(recommendation, tuple)
        assert len(recommendation) == 2

        words, connection = recommendation
        assert isinstance(words, list)
        assert isinstance(connection, str)

    def test_get_recommendation_returns_four_words(self):
        """Test that recommendations always return exactly 4 words."""
        recommendation = self.engine.get_recommendation(self.sample_session)
        words, _ = recommendation

        assert len(words) == 4
        for word in words:
            assert isinstance(word, str)
            assert len(word.strip()) > 0

    def test_get_recommendation_words_are_from_session(self):
        """Test that recommended words come from the session's remaining words."""
        recommendation = self.engine.get_recommendation(self.sample_session)
        words, _ = recommendation

        session_words = [w.lower() for w in self.sample_session.get_remaining_words()]
        for word in words:
            assert word.lower() in session_words

    def test_get_recommendation_with_minimal_words(self):
        """Test recommendation with exactly 4 words remaining."""
        # Start with 16 words (required by PuzzleSession)
        all_words = [
            "APPLE", "BANANA", "CHERRY", "DATE",
            "RED", "BLUE", "GREEN", "YELLOW",
            "DOG", "CAT", "BIRD", "FISH",
            "SUN", "MOON", "STAR", "CLOUD"
        ]
        minimal_session = PuzzleSession(all_words)

        # Mark 12 words as found (3 groups), leaving 4 words remaining
        from src.models import ResponseResult
        minimal_session.record_attempt(["RED", "BLUE", "GREEN", "YELLOW"], ResponseResult.CORRECT, color="yellow")
        minimal_session.record_attempt(["DOG", "CAT", "BIRD", "FISH"], ResponseResult.CORRECT, color="green")
        minimal_session.record_attempt(["SUN", "MOON", "STAR", "CLOUD"], ResponseResult.CORRECT, color="blue")

        recommendation = self.engine.get_recommendation(minimal_session)

        words, connection = recommendation
        assert len(words) == 4
        assert connection == "this is the connection reason"

    def test_get_recommendation_consistency_with_same_session(self):
        """Test that the same session produces the same recommendation."""
        rec1 = self.engine.get_recommendation(self.sample_session)
        rec2 = self.engine.get_recommendation(self.sample_session)

        # Should be deterministic for the same session
        assert rec1 == rec2

    def test_get_recommendation_different_with_different_sessions(self):
        """Test that different sessions can produce different recommendations."""
        words1 = [
            "one",
            "two",
            "three",
            "four",
            "cat",
            "dog",
            "bird",
            "fish",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "banana",
            "cherry",
            "grape",
        ]
        words2 = [
            "car",
            "bus",
            "train",
            "plane",
            "happy",
            "sad",
            "angry",
            "excited",
            "north",
            "south",
            "east",
            "west",
            "hot",
            "cold",
            "warm",
            "cool",
        ]

        session1 = PuzzleSession(words1)
        session2 = PuzzleSession(words2)
        rec1 = self.engine.get_recommendation(session1)
        rec2 = self.engine.get_recommendation(session2)

        # Different sessions should potentially produce different recommendations
        # (may be the same if algorithm finds similar patterns, but at least one should differ)
        assert rec1 != rec2 or rec1[0] != rec2[0]

    def test_performance_with_reasonable_input_size(self):
        """Test that recommendation generation completes in reasonable time."""
        import time

        start_time = time.time()
        recommendation = self.engine.get_recommendation(self.sample_session)
        end_time = time.time()

        # Should complete within 5 seconds for reasonable input
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Recommendation took {execution_time:.2f} seconds"

        # Verify result is still valid
        words, connection = recommendation
        assert len(words) == 4
        assert connection == "this is the connection reason"


class TestRecommendationService:
    """Test suite for RecommendationService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = RecommendationService()
        self.sample_request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple"),
            remaining_words=["apple", "banana", "cherry", "date", "elephant", "fox"],
        )

    def test_service_initialization(self):
        """Test that RecommendationService initializes correctly."""
        assert self.service is not None
        assert hasattr(self.service, "provider_factory")
        assert hasattr(self.service, "validator")

    @patch("src.services.recommendation_service.session_manager")
    def test_generate_recommendation_no_session(self, mock_session_manager):
        """Test recommendation generation without active session."""
        mock_session_manager.get_session_count.return_value = 0

        with (
            patch.object(self.service, "_validate_provider_availability", return_value=True),
            patch.object(self.service, "_route_request") as mock_route,
        ):

            mock_response = RecommendationResponse(
                recommended_words=["apple", "banana", "cherry", "date"],
                connection_explanation=None,  # Simple provider doesn't provide explanations
                provider_used=self.sample_request.llm_provider,
                generation_time_ms=None,  # Simple provider doesn't track time
            )
            mock_route.return_value = mock_response

            result = self.service.generate_recommendation(self.sample_request)

            assert result == mock_response
            mock_route.assert_called_once()

    @patch("src.services.recommendation_service.session_manager")
    def test_generate_recommendation_with_session(self, mock_session_manager):
        """Test recommendation generation with active session."""
        mock_session = Mock()
        mock_session.get_remaining_words.return_value = ["WORD1", "WORD2", "WORD3", "WORD4"]
        mock_session_manager.get_session_count.return_value = 1
        mock_session_manager._sessions.values.return_value = [mock_session]

        with (
            patch.object(self.service, "_validate_provider_availability", return_value=True),
            patch.object(self.service, "_route_request") as mock_route,
        ):

            mock_response = RecommendationResponse(
                recommended_words=["word1", "word2", "word3", "word4"],
                connection_explanation=None,
                provider_used=self.sample_request.llm_provider,
                generation_time_ms=None,
            )
            mock_route.return_value = mock_response

            result = self.service.generate_recommendation(self.sample_request)

            assert result == mock_response
            mock_route.assert_called_once()
            # Verify session's last_recommendation was updated
            assert mock_session.last_recommendation == ["word1", "word2", "word3", "word4"]

    def test_generate_recommendation_insufficient_words_error(self):
        """Test recommendation generation raises error for < 4 words."""
        # Test the service-level validation that raises InsufficientWordsError
        # We'll manually create a request with insufficient words at the service level
        insufficient_request = self.sample_request
        insufficient_request.remaining_words = ["apple", "banana", "cherry"]  # Only 3 words

        with pytest.raises(InsufficientWordsError):
            self.service.generate_recommendation(insufficient_request)

    def test_generate_recommendation_duplicate_words_error(self):
        """Test recommendation generation raises error for duplicate words."""
        duplicate_request = self.sample_request
        duplicate_request.remaining_words = ["apple", "banana", "apple", "cherry"]

        with pytest.raises(InvalidInputError):
            self.service.generate_recommendation(duplicate_request)

    def test_generate_recommendation_provider_error_passthrough(self):
        """Test that LLMProviderError is passed through unchanged."""
        provider_error = LLMProviderError("Test error", provider_type="openai")

        with (
            patch.object(self.service, "_validate_provider_availability", return_value=True),
            patch.object(self.service, "_route_request", side_effect=provider_error),
        ):

            with pytest.raises(LLMProviderError) as exc_info:
                self.service.generate_recommendation(self.sample_request)

            assert exc_info.value == provider_error

    def test_generate_recommendation_timeout_error(self):
        """Test recommendation generation with timeout error."""
        with (
            patch.object(self.service, "_validate_provider_availability", return_value=True),
            patch.object(self.service, "_route_request", side_effect=TimeoutError("Request timeout")),
        ):

            with pytest.raises(LLMProviderError) as exc_info:
                self.service.generate_recommendation(self.sample_request)

            # Timeout gets wrapped in LLMProviderError, not AppTimeoutError
            assert "Request timeout" in str(exc_info.value)

    def test_route_request_simple_provider(self):
        """Test request routing to simple provider."""
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple"), remaining_words=["apple", "banana", "cherry", "date"]
        )

        mock_response = RecommendationResponse(
            recommended_words=["apple", "banana", "cherry", "date"],
            connection_explanation=None,  # Simple provider doesn't provide explanations
            provider_used=request.llm_provider,
            generation_time_ms=None,  # Simple provider doesn't track time
        )

        with patch.object(self.service.simple_service, "generate_recommendation", return_value=mock_response):
            result = self.service._route_request(request)
            assert result == mock_response

    def test_route_request_openai_provider(self):
        """Test request routing to OpenAI provider."""
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai"), remaining_words=["apple", "banana", "cherry", "date"]
        )

        mock_response = RecommendationResponse(
            recommended_words=["apple", "banana", "cherry", "date"],
            connection_explanation="These are all fruits",
            provider_used=request.llm_provider,
            generation_time_ms=150,
        )

        with patch.object(self.service.openai_service, "generate_recommendation", return_value=mock_response):
            result = self.service._route_request(request)
            assert result == mock_response

    def test_route_request_ollama_provider(self):
        """Test request routing to Ollama provider."""
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="ollama"), remaining_words=["apple", "banana", "cherry", "date"]
        )

        mock_response = RecommendationResponse(
            recommended_words=["apple", "banana", "cherry", "date"],
            connection_explanation="These are all fruits",
            provider_used=request.llm_provider,
            generation_time_ms=200,
        )

        with patch.object(self.service.ollama_service, "generate_recommendation", return_value=mock_response):
            result = self.service._route_request(request)
            assert result == mock_response

    def test_validate_provider_availability_valid(self):
        """Test provider availability validation for valid provider."""
        provider = LLMProvider(provider_type="simple")

        with patch.object(self.service.provider_factory, "get_available_providers", return_value={"simple": True}):
            result = self.service._validate_provider_availability(provider)
            assert result is True

    def test_validate_provider_availability_invalid(self):
        """Test provider availability validation for invalid provider."""
        provider = LLMProvider(provider_type="openai")  # Use valid type but mock as unavailable

        with (
            patch.object(self.service.provider_factory, "get_available_providers", return_value={"simple": True}),
            patch.object(self.service.provider_factory, "_providers", {}),
        ):  # Empty registry
            result = self.service._validate_provider_availability(provider)
            assert result is False

    def test_get_available_providers(self):
        """Test getting available providers."""
        mock_providers = {"simple": True, "openai": False, "ollama": True}

        with patch.object(self.service.provider_factory, "get_available_providers", return_value=mock_providers):
            result = self.service.get_available_providers()

            # Test that the actual structure is returned (may have more fields than expected)
            assert "simple" in result
            assert "openai" in result
            assert "ollama" in result
            # Check basic structure elements
            assert result["simple"]["available"] is True
            assert result["openai"]["available"] is False
            assert result["ollama"]["available"] is True

    def test_validate_request_valid(self):
        """Test request validation with valid request."""
        result = self.service.validate_request(self.sample_request)

        assert result["valid"] is True
        assert "message" in result

    def test_validate_request_insufficient_words_at_service_level(self):
        """Test request validation with insufficient words using service method."""
        # Create a request with sufficient words for the model but test the service validation
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple"),
            remaining_words=["apple", "banana", "cherry", "date"],  # 4 words
        )

        # Mock the request to have insufficient words for service-level validation
        with patch.object(request, "remaining_words", ["apple", "banana"]):  # Only 2 words
            result = self.service.validate_request(request)

            assert result["valid"] is False
            assert "error" in result
            assert "Must have at least 4" in result["error"]

    def test_validate_request_invalid_provider(self):
        """Test request validation with invalid provider."""
        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai"),  # Use valid type but mock as unavailable
            remaining_words=["apple", "banana", "cherry", "date"],
        )

        with patch.object(self.service, "_validate_provider_availability", return_value=False):
            result = self.service.validate_request(request)

            assert result["valid"] is False
            assert "error" in result
            assert "not available" in result["error"]

    def test_get_service_stats(self):
        """Test getting service statistics."""
        result = self.service.get_service_stats()

        assert "service_name" in result
        assert result["service_name"] == "recommendation_orchestration"
        assert "available_providers" in result
        assert "capabilities" in result
        assert "validator_rules" in result
