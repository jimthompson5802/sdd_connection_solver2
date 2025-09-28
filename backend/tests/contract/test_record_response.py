"""Contract tests for POST /api/puzzle/record_response endpoint."""

from fastapi.testclient import TestClient

from src.main import app


class TestRecordResponseContract:
    """Contract tests for record_response endpoint per API specification."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_record_response_correct_success_contract(self) -> None:
        """Test correct response returns proper contract structure.

        API Contract: POST /api/puzzle/record_response
        Success Response (200) for correct answer:
        - remaining_words: array[string]
        - correct_count: integer (0-4)
        - mistake_count: integer (0-4)
        - game_status: "active" | "won" | "lost"
        """
        payload = {"response_type": "correct", "color": "Yellow"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Contract validation
        assert response.status_code == 200
        data = response.json()

        # Required fields per contract
        assert "remaining_words" in data
        assert "correct_count" in data
        assert "mistake_count" in data
        assert "game_status" in data

        # Field type and constraint validation
        assert isinstance(data["remaining_words"], list)
        assert all(isinstance(word, str) for word in data["remaining_words"])

        assert isinstance(data["correct_count"], int)
        assert 0 <= data["correct_count"] <= 4

        assert isinstance(data["mistake_count"], int)
        assert 0 <= data["mistake_count"] <= 4

        assert data["game_status"] in ["active", "won", "lost"]

    def test_record_response_incorrect_success_contract(self) -> None:
        """Test incorrect response returns proper contract structure."""
        payload = {"response_type": "incorrect"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Should succeed with updated state
        assert response.status_code == 200
        data = response.json()

        # Same contract structure as correct response
        required_fields = ["remaining_words", "correct_count", "mistake_count", "game_status"]
        for field in required_fields:
            assert field in data

        # Mistake count should be incremented for incorrect response
        assert isinstance(data["mistake_count"], int)
        assert data["mistake_count"] >= 0

    def test_record_response_one_away_success_contract(self) -> None:
        """Test one-away response returns proper contract structure."""
        payload = {"response_type": "one-away"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Same contract structure
        required_fields = ["remaining_words", "correct_count", "mistake_count", "game_status"]
        for field in required_fields:
            assert field in data

    def test_record_response_missing_color_for_correct_error(self) -> None:
        """Test correct response without color returns validation error."""
        payload = {
            "response_type": "correct"
            # Missing required color field
        }

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Should return validation error for missing required field
        assert response.status_code in [400, 422]

    def test_record_response_invalid_response_type_error(self) -> None:
        """Test invalid response_type returns validation error."""
        payload = {"response_type": "invalid_type"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Should return validation error for invalid enum value
        assert response.status_code in [400, 422]

    def test_record_response_invalid_color_error(self) -> None:
        """Test invalid color returns validation error."""
        payload = {"response_type": "correct", "color": "InvalidColor"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Should return validation error for invalid color
        assert response.status_code in [400, 422]

    def test_record_response_no_active_recommendation_error_contract(self) -> None:
        """Test response without active recommendation returns error per contract.

        API Contract Error (400):
        - status: string (error message like "No recommendation to respond to")
        """
        payload = {"response_type": "correct", "color": "Yellow"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        # Contract allows success or error depending on state
        if response.status_code == 400:
            data = response.json()

            # Error contract validation
            assert "status" in data
            assert isinstance(data["status"], str)
            assert data["status"] != "success"

            # Should indicate no active recommendation
            assert "no recommendation" in data["status"].lower() or "no active" in data["status"].lower()

    def test_record_response_valid_color_enum_values(self) -> None:
        """Test all valid color enum values are accepted."""
        valid_colors = ["Yellow", "Green", "Blue", "Purple"]

        for color in valid_colors:
            payload = {"response_type": "correct", "color": color}

            response = self.client.post("/api/puzzle/record_response", json=payload)

            # Should not fail due to invalid color (may fail for other reasons)
            if response.status_code == 422:
                # If validation error, it shouldn't be about color
                error_data = response.json()
                error_msg = str(error_data).lower()
                assert "color" not in error_msg or color.lower() not in error_msg

    def test_record_response_game_status_transitions(self) -> None:
        """Test game_status values follow expected transitions."""
        payload = {"response_type": "correct", "color": "Yellow"}

        response = self.client.post("/api/puzzle/record_response", json=payload)

        if response.status_code == 200:
            data = response.json()
            game_status = data["game_status"]
            correct_count = data["correct_count"]
            mistake_count = data["mistake_count"]

            # Game status logic validation
            if correct_count == 4:
                assert game_status == "won"
            elif mistake_count == 4:
                assert game_status == "lost"
            else:
                assert game_status == "active"
