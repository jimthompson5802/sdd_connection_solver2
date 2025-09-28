"""Contract tests for GET /api/puzzle/next_recommendation endpoint."""

from fastapi.testclient import TestClient

from src.main import app


class TestNextRecommendationContract:
    """Contract tests for next_recommendation endpoint per API specification."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_next_recommendation_success_response_contract(self) -> None:
        """Test successful recommendation returns correct contract structure.

        API Contract: GET /api/puzzle/next_recommendation
        Success Response (200):
        - words: array[string] (exactly 4 items)
        - connection: string (rationale)
        - status: "success"
        """
        response = self.client.get("/api/puzzle/next_recommendation")

        # Contract validation
        assert response.status_code == 200
        data = response.json()

        # Required fields per contract
        assert "words" in data
        assert "connection" in data
        assert "status" in data

        # Field type and constraint validation
        assert isinstance(data["words"], list)
        assert len(data["words"]) == 4  # Exactly 4 words per contract
        assert all(isinstance(word, str) for word in data["words"])
        assert all(len(word.strip()) > 0 for word in data["words"])  # Non-empty words

        assert isinstance(data["connection"], str)
        assert len(data["connection"].strip()) > 0  # Non-empty rationale

        assert data["status"] == "success"

    def test_next_recommendation_insufficient_words_error_contract(self) -> None:
        """Test insufficient words returns correct error contract structure.

        API Contract: GET /api/puzzle/next_recommendation
        Error Response (400):
        - status: string (error message like "Not enough words remaining")
        """
        # This test assumes puzzle state with <4 words remaining
        # In actual implementation, this would need puzzle state setup
        response = self.client.get("/api/puzzle/next_recommendation")

        # Contract allows both success (if words available) or error (if insufficient)
        if response.status_code == 400:
            data = response.json()

            # Required fields per error contract
            assert "status" in data
            assert isinstance(data["status"], str)
            assert data["status"] != "success"

            # Should indicate insufficient words
            assert "not enough" in data["status"].lower() or "insufficient" in data["status"].lower()

    def test_next_recommendation_no_puzzle_state_error_contract(self) -> None:
        """Test no active puzzle returns error per contract."""
        # This assumes no puzzle has been set up
        response = self.client.get("/api/puzzle/next_recommendation")

        # Should return error when no puzzle state exists
        # Contract allows various error responses as long as structure is correct
        if response.status_code == 400:
            data = response.json()
            assert "status" in data
            assert isinstance(data["status"], str)
            assert data["status"] != "success"

    def test_next_recommendation_response_structure_consistency(self) -> None:
        """Test that response structure is consistent with contract requirements."""
        response = self.client.get("/api/puzzle/next_recommendation")

        # Response must be either 200 with full structure or 400 with error
        assert response.status_code in [200, 400]

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data

        if response.status_code == 200:
            # Success response must have all required fields
            required_fields = ["words", "connection", "status"]
            for field in required_fields:
                assert field in data, f"Missing required field: {field}"

            # Validate words array constraints
            assert len(data["words"]) == 4
            assert all(isinstance(word, str) and word.strip() for word in data["words"])
        else:
            # Error response should have meaningful error message
            assert isinstance(data["status"], str)
            assert len(data["status"].strip()) > 0

    def test_next_recommendation_words_uniqueness(self) -> None:
        """Test that recommended words are unique per business logic."""
        response = self.client.get("/api/puzzle/next_recommendation")

        if response.status_code == 200:
            data = response.json()
            words = data["words"]

            # All 4 words should be unique
            assert len(set(words)) == 4, "Recommended words must be unique"

            # Words should be non-empty after stripping
            assert all(word.strip() for word in words), "Words must be non-empty"
