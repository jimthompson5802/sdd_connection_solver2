"""
Contract tests for /api/v2/game_results endpoints.

These tests validate the API contract compliance for recording and retrieving
game results. Tests should fail until implementation is complete (TDD approach).
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient


class TestRecordGameContract:
    """Contract tests for POST /api/v2/game_results endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def session_manager(self):
        """Get session manager from app"""
        from src.main import session_manager
        return session_manager

    @pytest.fixture
    def completed_session(self, session_manager):
        """Create a completed puzzle session for testing"""
        # Create session with test words
        words = [
            "apple", "banana", "cherry", "date",
            "egg", "flour", "garlic", "honey",
            "ice", "jam", "kale", "lemon",
            "milk", "nut", "olive", "pepper"
        ]
        session = session_manager.create_session(words)

        # Mark 4 groups as found to complete the game
        from src.models import ResponseResult
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT, color="yellow")
        session.record_attempt(["egg", "flour", "garlic", "honey"], ResponseResult.CORRECT, color="green")
        session.record_attempt(["ice", "jam", "kale", "lemon"], ResponseResult.CORRECT, color="blue")
        session.record_attempt(["milk", "nut", "olive", "pepper"], ResponseResult.CORRECT, color="purple")

        # Set LLM info
        session.set_llm_info("openai", "gpt-4")

        return session

    @pytest.fixture
    def incomplete_session(self, session_manager):
        """Create an incomplete puzzle session for testing"""
        words = [
            "red", "blue", "green", "yellow",
            "cat", "dog", "bird", "fish",
            "car", "bus", "train", "plane",
            "sun", "moon", "star", "cloud"
        ]
        session = session_manager.create_session(words)

        # Only mark 2 groups as found (incomplete)
        from src.models import ResponseResult
        session.record_attempt(["red", "blue", "green", "yellow"], ResponseResult.CORRECT, color="yellow")
        session.record_attempt(["cat", "dog", "bird", "fish"], ResponseResult.CORRECT, color="green")

        return session

    @pytest.mark.contract
    def test_record_game_success_contract(self, client, completed_session):
        """
        T011: Test successful game recording (201 Created)

        Validates:
        - Request accepts session_id and game_date
        - Returns 201 Created on success
        - Response includes status="created" and complete result object
        - Result includes all required fields with correct types
        """
        request_data = {
            "session_id": completed_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 201 Created
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate response structure
        assert "status" in data
        assert data["status"] == "created"
        assert "result" in data

        result = data["result"]

        # Validate all required fields exist
        required_fields = [
            "result_id", "puzzle_id", "game_date", "puzzle_solved",
            "count_groups_found", "count_mistakes", "total_guesses",
            "llm_provider_name", "llm_model_name"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Validate field types and values
        assert isinstance(result["result_id"], int)
        assert result["result_id"] > 0

        assert isinstance(result["puzzle_id"], str)
        assert len(result["puzzle_id"]) == 36  # UUID format

        assert isinstance(result["game_date"], str)
        # Should be UTC ISO 8601 format
        assert result["game_date"].endswith("+00:00") or result["game_date"].endswith("Z")

        assert isinstance(result["puzzle_solved"], bool)
        assert result["puzzle_solved"] is True  # Completed session should be solved

        assert isinstance(result["count_groups_found"], int)
        assert result["count_groups_found"] == 4  # All groups found

        assert isinstance(result["count_mistakes"], int)
        assert 0 <= result["count_mistakes"] <= 4

        assert isinstance(result["total_guesses"], int)
        assert result["total_guesses"] >= 4  # At least 4 guesses to find 4 groups

        assert isinstance(result["llm_provider_name"], str)
        assert result["llm_provider_name"] == "openai"

        assert isinstance(result["llm_model_name"], str)
        assert result["llm_model_name"] == "gpt-4"

    @pytest.mark.contract
    def test_record_game_duplicate_detection_contract(self, client, completed_session):
        """
        T012: Test duplicate record detection (409 Conflict)

        Validates:
        - Recording the same puzzle_id and game_date twice returns 409 Conflict
        - Response includes appropriate error message
        - First record succeeds, second record is rejected
        """
        request_data = {
            "session_id": completed_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        # First request should succeed
        response1 = client.post("/api/v2/game_results", json=request_data)
        assert response1.status_code == 201, f"First request should succeed: {response1.text}"

        # Second request with same puzzle_id and game_date should fail with 409
        response2 = client.post("/api/v2/game_results", json=request_data)
        assert response2.status_code == 409, f"Expected 409 Conflict, got {response2.status_code}: {response2.text}"

        data = response2.json()

        # Validate error response structure
        assert "status" in data
        assert data["status"] == "conflict"

        assert "code" in data
        assert data["code"] == "duplicate_record"

        assert "message" in data
        assert "already exists" in data["message"].lower()

    @pytest.mark.contract
    def test_record_game_incomplete_session_contract(self, client, incomplete_session):
        """
        T013: Test incomplete session validation (400 Bad Request)

        Validates:
        - Attempting to record an incomplete session returns 400 Bad Request
        - Response includes appropriate error message
        - Only completed sessions (is_finished=True) can be recorded
        """
        request_data = {
            "session_id": incomplete_session.session_id,
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 400 Bad Request
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate error message
        assert "detail" in data
        assert "completed" in data["detail"].lower() or "finished" in data["detail"].lower()

    @pytest.mark.contract
    def test_record_game_session_not_found_contract(self, client):
        """
        Test session not found validation (404 Not Found)

        Validates:
        - Attempting to record with non-existent session_id returns 404
        - Response includes appropriate error message
        """
        request_data = {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "game_date": "2025-12-24T15:30:00-08:00"
        }

        response = client.post("/api/v2/game_results", json=request_data)

        # Should return 404 Not Found
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

        data = response.json()

        # Validate error message
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    @pytest.mark.contract
    def test_record_game_invalid_request_format_contract(self, client):
        """
        Test invalid request format validation (422 Unprocessable Entity)

        Validates:
        - Missing required fields returns 422
        - Invalid date format returns 422
        - Response includes validation error details
        """
        # Test missing session_id
        response = client.post("/api/v2/game_results", json={"game_date": "2025-12-24T15:30:00-08:00"})
        assert response.status_code == 422, f"Expected 422 for missing session_id, got {response.status_code}"

        # Test missing game_date
        response = client.post("/api/v2/game_results", json={"session_id": "123e4567-e89b-12d3-a456-426614174000"})
        assert response.status_code == 422, f"Expected 422 for missing game_date, got {response.status_code}"

        # Test invalid date format
        response = client.post("/api/v2/game_results", json={
            "session_id": "123e4567-e89b-12d3-a456-426614174000",
            "game_date": "not-a-date"
        })
        assert response.status_code == 422, f"Expected 422 for invalid date, got {response.status_code}"
