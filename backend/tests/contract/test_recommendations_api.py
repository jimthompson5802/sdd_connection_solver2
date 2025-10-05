"""
Contract tests for POST /api/v2/recommendations endpoint.
These tests validate API contract compliance and will initially FAIL until implementation is complete.
"""

import pytest
from fastapi.testclient import TestClient


class TestRecommendationsContract:
    """Contract tests for /api/v2/recommendations endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture - will fail until FastAPI app exists"""
        # This will need to import the actual FastAPI app when implemented
        from src.main import app

        return TestClient(app)

    @pytest.mark.contract
    def test_simple_provider_request_contract(self, client):
        """Test that simple provider requests follow expected contract"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR", "VIOLIN", "DRUMS"],
            "previous_guesses": [],
        }

        # This should fail until implementation exists
        response = client.post("/api/v2/recommendations", json=request_data)

        # Expected contract behavior (will fail initially)
        assert response.status_code == 200
        data = response.json()

        # Validate response schema
        assert "recommended_words" in data
        assert len(data["recommended_words"]) == 4
        assert data["connection_explanation"] is None
        assert data["confidence_score"] is None
        assert data["provider_used"]["provider_type"] == "simple"
        assert data["generation_time_ms"] is None

        # Validate all recommended words are from remaining words
        for word in data["recommended_words"]:
            assert word in request_data["remaining_words"]

    @pytest.mark.contract
    def test_ollama_provider_request_contract(self, client):
        """Test that ollama provider requests follow expected contract"""
        request_data = {
            "llm_provider": {"provider_type": "ollama", "model_name": "llama2"},
            "remaining_words": ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR"],
            "previous_guesses": [
                {
                    "words": ["RED", "BLUE", "GREEN", "YELLOW"],
                    "outcome": "incorrect",
                    "actual_connection": None,
                    "timestamp": "2025-10-05T10:30:00Z",
                }
            ],
        }

        # This should fail until implementation exists
        response = client.post("/api/v2/recommendations", json=request_data)

        # Expected contract behavior (will fail initially)
        assert response.status_code == 200
        data = response.json()

        # Validate response schema
        assert "recommended_words" in data
        assert len(data["recommended_words"]) == 4
        assert data["connection_explanation"] is not None
        assert isinstance(data["confidence_score"], (float, type(None)))
        assert data["provider_used"]["provider_type"] == "ollama"
        assert data["provider_used"]["model_name"] == "llama2"
        assert isinstance(data["generation_time_ms"], int)

        # Validate no previous guesses included
        previous_words = [word for guess in request_data["previous_guesses"] for word in guess["words"]]
        for word in data["recommended_words"]:
            assert word not in previous_words

    @pytest.mark.contract
    def test_openai_provider_request_contract(self, client):
        """Test that openai provider requests follow expected contract"""
        request_data = {
            "llm_provider": {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
            "remaining_words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
            "previous_guesses": [],
        }

        # This should fail until implementation exists
        response = client.post("/api/v2/recommendations", json=request_data)

        # Expected contract behavior (will fail initially)
        assert response.status_code == 200
        data = response.json()

        # Validate response schema matches OpenAI provider expectations
        assert len(data["recommended_words"]) == 4
        assert data["connection_explanation"] is not None
        assert data["provider_used"]["provider_type"] == "openai"

    @pytest.mark.contract
    def test_invalid_provider_format_error_contract(self, client):
        """Test error response contract for invalid provider format"""
        request_data = {
            "llm_provider": {"provider_type": "invalid_provider", "model_name": "some_model"},
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            "previous_guesses": [],
        }

        # This should fail until implementation exists
        response = client.post("/api/v2/recommendations", json=request_data)

        # Expected contract behavior (will fail initially)
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "INVALID_PROVIDER_FORMAT"
        assert "error" in data
        assert "detail" in data

    @pytest.mark.contract
    def test_insufficient_words_error_contract(self, client):
        """Test error response contract when fewer than 4 words remain"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": ["WORD1", "WORD2"],  # Only 2 words
            "previous_guesses": [],
        }

        # This should fail until implementation exists
        response = client.post("/api/v2/recommendations", json=request_data)

        # Expected contract behavior (will fail initially)
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "INSUFFICIENT_WORDS"

    @pytest.mark.contract
    def test_request_validation_contract(self, client):
        """Test that request validation follows Pydantic schema"""
        # Missing required field
        invalid_request = {
            "llm_provider": {
                "provider_type": "simple"
                # missing model_name
            },
            "remaining_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            # missing previous_guesses
        }

        response = client.post("/api/v2/recommendations", json=invalid_request)

        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.contract
    def test_response_format_consistency(self, client):
        """Test that all responses follow consistent format"""
        request_data = {
            "llm_provider": {"provider_type": "simple", "model_name": None},
            "remaining_words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
            "previous_guesses": [],
        }

        response = client.post("/api/v2/recommendations", json=request_data)

        if response.status_code == 200:
            data = response.json()
            required_fields = [
                "recommended_words",
                "connection_explanation",
                "confidence_score",
                "provider_used",
                "generation_time_ms",
            ]
            for field in required_fields:
                assert field in data, f"Response missing required field: {field}"
        else:
            # Error responses should have consistent format
            data = response.json()
            error_fields = ["error", "detail", "error_code"]
            for field in error_fields:
                assert field in data, f"Error response missing required field: {field}"
