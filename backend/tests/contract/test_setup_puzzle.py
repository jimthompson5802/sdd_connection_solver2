"""Contract tests for POST /api/puzzle/setup_puzzle endpoint."""

from fastapi.testclient import TestClient

from src.main import app


class TestSetupPuzzleContract:
    """Contract tests for setup_puzzle endpoint per API specification."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_setup_puzzle_success_response_contract(self) -> None:
        """Test successful puzzle setup returns correct contract structure.

        API Contract: POST /api/puzzle/setup_puzzle
        Success Response (200):
        - remaining_words: array[string] (16 items)
        - status: "success"
        """
        # Valid CSV with exactly 16 words
        payload = {
            "file_content": (
                "apple,banana,cherry,date,elderberry,fig,grape,honeydew,"
                "kiwi,lemon,mango,orange,papaya,quince,raspberry,strawberry"
            )
        }

        response = self.client.post("/api/puzzle/setup_puzzle", json=payload)

        # Contract validation
        assert response.status_code == 200
        data = response.json()

        # Required fields per contract
        assert "remaining_words" in data
        assert "status" in data

        # Field type and constraint validation
        assert isinstance(data["remaining_words"], list)
        assert len(data["remaining_words"]) == 16
        assert all(isinstance(word, str) for word in data["remaining_words"])
        assert data["status"] == "success"

        # Verify words are from the input CSV
        expected_words = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elderberry",
            "fig",
            "grape",
            "honeydew",
            "kiwi",
            "lemon",
            "mango",
            "orange",
            "papaya",
            "quince",
            "raspberry",
            "strawberry",
        ]
        assert set(data["remaining_words"]) == set(expected_words)

    def test_setup_puzzle_invalid_csv_error_contract(self) -> None:
        """Test invalid CSV returns correct error contract structure.

        API Contract: POST /api/puzzle/setup_puzzle
        Error Response (400):
        - status: string (error message)
        """
        # Invalid CSV with wrong number of words
        payload = {"file_content": "word1,word2,word3"}

        response = self.client.post("/api/puzzle/setup_puzzle", json=payload)

        # Contract validation
        assert response.status_code == 400
        data = response.json()

        # Required fields per contract
        assert "status" in data
        assert isinstance(data["status"], str)
        assert "error" in data["status"].lower() or data["status"] != "success"

    def test_setup_puzzle_empty_csv_error_contract(self) -> None:
        """Test empty CSV returns error per contract."""
        payload = {"file_content": ""}

        response = self.client.post("/api/puzzle/setup_puzzle", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "status" in data
        assert data["status"] != "success"

    def test_setup_puzzle_missing_file_content_error_contract(self) -> None:
        """Test missing file_content field returns validation error."""
        payload = {}

        response = self.client.post("/api/puzzle/setup_puzzle", json=payload)

        # Should return 422 for missing required field
        assert response.status_code == 422

    def test_setup_puzzle_duplicate_words_handling(self) -> None:
        """Test CSV with duplicate words handling per contract."""
        # CSV with duplicate words (should have 16 unique)
        payload = {
            "file_content": (
                "apple,banana,apple,date,elderberry,fig,grape,honeydew,"
                "kiwi,lemon,mango,orange,papaya,quince,raspberry,strawberry,extra"
            )
        }

        response = self.client.post("/api/puzzle/setup_puzzle", json=payload)

        # This should either succeed with deduplication or fail - depends on business logic
        # Contract allows both behaviors as long as response structure is correct
        if response.status_code == 200:
            data = response.json()
            assert len(data["remaining_words"]) == 16
            assert len(set(data["remaining_words"])) == 16  # All unique
        else:
            assert response.status_code == 400
            data = response.json()
            assert "status" in data
