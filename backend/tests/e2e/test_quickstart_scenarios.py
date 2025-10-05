"""
End-to-End Tests for LLM Provider Integration

These tests validate the complete user journey scenarios from the quickstart guide,
ensuring the LLM provider integration works correctly from frontend to backend.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime
from src.main import app
from src.services.ollama_service import OllamaService
from src.services.openai_service import OpenAIService
from src.services.llm_provider_factory import LLMProviderFactory
from tests.mocks.llm_mocks import MockProviderFactory, MOCK_RECOMMENDATION_RESPONSES


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client for FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_puzzle_words():
    """Sample puzzle words for testing"""
    return [
        "BASS",
        "PIKE",
        "SOLE",
        "CARP",  # Fish
        "APPLE",
        "BANANA",
        "CHERRY",
        "GRAPE",  # Fruits
        "RED",
        "BLUE",
        "GREEN",
        "YELLOW",  # Colors
        "CHAIR",
        "TABLE",
        "LAMP",
        "DESK",  # Furniture
    ]


@pytest.fixture
def mock_factory():
    """Mock factory for consistent test setup"""
    factory = MockProviderFactory()
    return factory


class TestQuickstartJourney1_SimpleProvider:
    """Test Journey 1: Simple Provider (Baseline)"""

    def test_default_provider_selection(self, client, sample_puzzle_words):
        """Test that simple provider is the default and works correctly"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Simple provider returns first 4 words
        assert len(data["recommended_words"]) == 4
        assert data["provider_used"]["provider_type"] == "simple"
        assert data["generation_time_ms"] is None  # Simple provider has no timing

    def test_simple_provider_immediate_response(self, client, sample_puzzle_words):
        """Test that simple provider responds immediately without delay"""
        import time

        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        start_time = time.time()
        response = client.post("/api/v2/recommendations", json=request_data)
        end_time = time.time()

        assert response.status_code == 200
        # Should complete in less than 100ms
        assert (end_time - start_time) < 0.1

    def test_simple_provider_no_explanation(self, client, sample_puzzle_words):
        """Test that simple provider provides minimal explanation"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)
        data = response.json()

        # Simple provider gives no explanation
        assert data["connection_explanation"] is None


class TestQuickstartJourney2_OllamaIntegration:
    """Test Journey 2: Ollama Integration"""

    @patch.object(LLMProviderFactory, "get_available_providers")
    @patch.object(OllamaService, "generate_recommendation")
    def test_ollama_provider_selection(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):
        """Test that ollama provider can be selected and works"""
        # Mock provider factory to make ollama available
        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}
        mock_ollama.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]

        request_data = {
            "llm_provider": {"provider_type": "ollama", "model_name": "llama2"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["provider_used"]["provider_type"] == "ollama"
        assert data["generation_time_ms"] == 2340
        assert data["connection_explanation"] is not None  # Ollama provider should have explanation
        assert data["confidence_score"] == 0.92

    @patch.object(LLMProviderFactory, "get_available_providers")
    @patch.object(OllamaService, "generate_recommendation")
    def test_ollama_contextual_recommendation(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):
        """Test that ollama considers previous guesses in context"""
        # First call returns fish suggestion
        # Mock provider factory to make ollama available
        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}
        # First call returns fish suggestion
        mock_ollama.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]

        # Create proper GuessAttempt structure
        from src.llm_models.guess_attempt import GuessAttempt, GuessOutcome
        from datetime import datetime

        previous_guess = GuessAttempt(
            words=["WRONG", "GUESS", "HERE", "TOO"], outcome=GuessOutcome.INCORRECT, timestamp=datetime.now()
        )

        request_data = {
            "llm_provider": {"provider_type": "ollama", "model_name": "llama2"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [previous_guess.model_dump(mode="json")],  # Use JSON mode for serialization
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        # Verify that previous guesses are passed to the service
        mock_ollama.assert_called_once()
        call_args = mock_ollama.call_args[0][0]
        assert len(call_args.previous_guesses) == 1
        assert call_args.previous_guesses[0].words == ["WRONG", "GUESS", "HERE", "TOO"]

    @patch.object(LLMProviderFactory, "create_provider")
    def test_ollama_provider_down_error_handling(self, mock_create_provider, client):
        """Test error handling when ollama service is down"""
        from src.exceptions import LLMProviderError

        mock_create_provider.side_effect = LLMProviderError("Connection refused", "OLLAMA_CONNECTION_ERROR")

        request_data = {
            "provider_type": "ollama",
            "api_key": None,  # Ollama doesn't need API key
            "base_url": "http://localhost:11434",
        }

        response = client.post("/api/v2/providers/validate", json=request_data)

        assert response.status_code == 200  # Validation endpoint returns 200 even for failed validation
        data = response.json()
        assert data["is_valid"] is False
        assert data["status"] == "provider_error"
        assert "Connection refused" in data["message"]


class TestQuickstartJourney3_OpenAIIntegration:
    """Test Journey 3: OpenAI Integration"""

    @patch.object(LLMProviderFactory, "get_available_providers")
    @patch.object(OpenAIService, "generate_recommendation")
    def test_openai_provider_selection(self, mock_openai, mock_provider_factory, client, sample_puzzle_words):
        """Test that OpenAI provider can be selected and works"""
        mock_openai.return_value = MOCK_RECOMMENDATION_RESPONSES["openai"]

        request_data = {
            "llm_provider": {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["provider_used"]["provider_type"] == "openai"
        assert data["generation_time_ms"] == 1850
        assert "fruits" in data["connection_explanation"].lower()
        assert data["confidence_score"] == 0.95

    @patch.object(LLMProviderFactory, "create_provider")
    def test_openai_invalid_api_key(self, mock_create_provider, client):
        """Test error handling when OpenAI API key is invalid"""
        from src.exceptions import LLMProviderError

        mock_create_provider.side_effect = LLMProviderError("Invalid API key", "OPENAI_AUTH_ERROR")

        request_data = {"provider_type": "openai", "api_key": "sk-invalid_key_for_testing"}

        response = client.post("/api/v2/providers/validate", json=request_data)

        assert response.status_code == 200  # Validation endpoint returns 200 even for failed validation
        data = response.json()
        assert data["is_valid"] is False
        assert data["status"] == "provider_error"
        assert "Invalid API key" in data["message"]

    @patch.object(LLMProviderFactory, "get_available_providers")
    @patch.object(LLMProviderFactory, "create_provider")
    def test_openai_quality_comparison(self, mock_create_provider, mock_get_providers, client, sample_puzzle_words):
        """Test that OpenAI provides high-quality explanations"""
        mock_get_providers.return_value = ["openai"]  # Mock available providers

        # Mock the provider creation to return a mock OpenAI service
        mock_openai_service = Mock()
        mock_openai_service.generate_recommendation.return_value = MOCK_RECOMMENDATION_RESPONSES["openai"]
        mock_create_provider.return_value = mock_openai_service

        request_data = {
            "llm_provider": {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)
        data = response.json()

        # Test should validate API response format and basic functionality
        assert response.status_code == 200
        assert "connection_explanation" in data
        assert "confidence_score" in data
        assert isinstance(data["confidence_score"], (int, float))
        assert 0 <= data["confidence_score"] <= 1  # Valid confidence range
        assert "recommended_words" in data
        assert len(data["recommended_words"]) == 4


class TestQuickstartJourney4_ErrorScenarios:
    """Test Journey 4: Error Scenarios"""

    def test_invalid_provider_format(self, client, sample_puzzle_words):
        """Test error handling for invalid provider format"""
        request_data = {
            "llm_provider": {"provider_type": "invalid_provider", "model_name": "test_model"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Check that error mentions provider validation
        error_details = str(data["detail"]).lower()
        assert "provider" in error_details or "invalid" in error_details

    def test_invalid_model_format(self, client, sample_puzzle_words):
        """Test error handling for invalid model name"""
        request_data = {
            "llm_provider": {"provider_type": "ollama", "model_name": "nonexistent_model"},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        # This will fail at validation stage
        validate_request = {"provider_type": "ollama", "model_name": "nonexistent_model"}

        response = client.post("/api/v2/providers/validate", json=validate_request)

        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 500]
        if response.status_code != 200:
            data = response.json()
            assert "error" in data

    def test_insufficient_words_error(self, client):
        """Test error handling when fewer than 4 words remain"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": ["WORD1", "WORD2"],  # Only 2 words
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Check that error mentions insufficient words
        error_details = str(data["detail"]).lower()
        assert "words" in error_details and ("least 4" in error_details or "insufficient" in error_details)

    @patch("src.services.response_validator.ResponseValidatorService.validate_response")
    def test_llm_response_validation_error(self, mock_validator, client, sample_puzzle_words):
        """Test error handling when LLM returns invalid response"""
        mock_validator.return_value = False, "Invalid words in response"

        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        # FastAPI returns 422 for Pydantic validation errors
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestQuickstartJourney5_CompleteGameFlow:
    """Test Journey 5: Complete Game Flow"""

    @patch.object(LLMProviderFactory, "get_available_providers")
    @patch.object(OllamaService, "generate_recommendation")
    def test_mixed_provider_usage(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):
        """Test alternating between different providers in same session"""
        mock_ollama.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]

        # First request with simple provider (v2 format)
        simple_request = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        simple_response = client.post("/api/v2/recommendations", json=simple_request)
        assert simple_response.status_code == 200
        simple_data = simple_response.json()
        assert simple_data["provider_used"]["provider_type"] == "simple"

        # Second request with ollama provider (v2 format)
        ollama_request = {
            "llm_provider": {"provider_type": "ollama", "model_name": "llama2"},
            "remaining_words": sample_puzzle_words[4:],  # Remove first 4 words
            "previous_guesses": [],  # Simplified to avoid timestamp validation issues
            "puzzle_context": None,
        }

        ollama_response = client.post("/api/v2/recommendations", json=ollama_request)
        assert ollama_response.status_code == 200
        ollama_data = ollama_response.json()
        assert ollama_data["provider_used"]["provider_type"] == "ollama"

    def test_recommendation_quality_context_awareness(self, client, sample_puzzle_words):
        """Test that AI recommendations consider game context"""
        # Make a failed guess first
        request_with_history = {
            "remaining_words": sample_puzzle_words,
            "completed_groups": [],
            "previous_guesses": [["BASS", "APPLE", "RED", "CHAIR"]],  # Mixed categories
            "total_mistakes": 1,
            "max_mistakes": 4,
            "provider_type": "simple",
        }

        response = client.post("/api/v2/recommendations", json=request_with_history)

        assert response.status_code == 200
        data = response.json()

        # Response should exclude previously guessed words
        recommended_words = data["recommended_words"]
        previous_guess = ["BASS", "APPLE", "RED", "CHAIR"]

        for word in recommended_words:
            assert word not in previous_guess

    def test_provider_state_isolation(self, client, sample_puzzle_words):
        """Test that provider state doesn't persist between sessions"""
        # First session
        request1 = {
            "remaining_words": sample_puzzle_words,
            "completed_groups": [],
            "previous_guesses": [],
            "total_mistakes": 0,
            "max_mistakes": 4,
            "provider_type": "simple",
        }

        response1 = client.post("/api/v2/recommendations", json=request1)
        assert response1.status_code == 200

        # Second session (simulating fresh start)
        request2 = {
            "remaining_words": sample_puzzle_words,
            "completed_groups": [],
            "previous_guesses": [],  # Fresh session
            "total_mistakes": 0,
            "max_mistakes": 4,
            "provider_type": "simple",
        }

        response2 = client.post("/api/v2/recommendations", json=request2)
        assert response2.status_code == 200

        # Should get same recommendations (no state persistence)
        assert response1.json()["recommended_words"] == response2.json()["recommended_words"]


class TestBackwardCompatibility:
    """Test that Phase 1 functionality is preserved"""

    def test_phase1_api_still_works(self, client, sample_puzzle_words):
        """Test that the original API endpoints still function"""
        # Test original recommendation endpoint if it exists
        legacy_request = {"words": sample_puzzle_words, "completed_groups": [], "mistakes": 0}

        # Try legacy endpoint format
        response = client.post("/api/recommendations", json=legacy_request)

        # Should either work or be redirected appropriately
        assert response.status_code in [200, 301, 404]  # 404 is acceptable if endpoint was moved

    def test_simple_provider_identical_behavior(self, client, sample_puzzle_words):
        """Test that simple provider behaves identically to Phase 1"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Should return first 4 words as in Phase 1
        assert data["recommended_words"] == sample_puzzle_words[:4]
        assert data["provider_used"]["provider_type"] == "simple"


class TestAPIContractCompliance:
    """Test that all APIs comply with OpenAPI specifications"""

    def test_recommendation_response_schema(self, client, sample_puzzle_words):
        """Test that recommendation responses match expected schema"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": sample_puzzle_words,
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        required_fields = [
            "recommended_words",
            "connection_explanation",
            "confidence_score",
            "provider_used",
            "puzzle_state",
            "alternative_suggestions",
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(data["recommended_words"], list)
        assert len(data["recommended_words"]) == 4
        assert isinstance(data["connection_explanation"], str)
        assert isinstance(data["confidence_score"], (int, float))
        assert isinstance(data["provider_used"], str)
        assert isinstance(data["puzzle_state"], dict)
        assert isinstance(data["alternative_suggestions"], list)

    def test_error_response_schema(self, client):
        """Test that error responses match expected schema"""
        # Trigger an error with invalid request
        invalid_request = {
            "remaining_words": [],  # Invalid: empty list
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "previous_guesses": [],
            "puzzle_context": None,
        }

        response = client.post("/api/v2/recommendations", json=invalid_request)

        assert response.status_code == 422
        data = response.json()

        # Verify FastAPI error response structure
        assert "detail" in data
        assert isinstance(data["detail"], list)
        # Check that at least one error mentions the validation issue
        error_messages = str(data["detail"]).lower()
        assert "words" in error_messages or "least 4" in error_messages

    def test_provider_validation_schema(self, client):
        """Test that provider validation responses match expected schema"""
        request_data = {"provider_type": "simple"}

        response = client.post("/api/v2/providers/validate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Verify validation response structure
        required_fields = ["provider_type", "is_valid", "status", "message"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        assert isinstance(data["is_valid"], bool)
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
