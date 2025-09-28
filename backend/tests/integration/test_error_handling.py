"""Integration tests for error handling scenarios."""

from fastapi.testclient import TestClient

from src.main import app


class TestErrorHandlingIntegration:
    """Integration tests for error handling scenarios per quickstart.md."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_invalid_file_upload_error_handling(self) -> None:
        """Test invalid file upload error handling per quickstart.md.

        From quickstart: Upload empty file or non-CSV format
        Expected: Error message displayed, setup prevented
        """
        # Test empty file content
        empty_payload = {"file_content": ""}
        empty_response = self.client.post("/api/puzzle/setup_puzzle", json=empty_payload)

        assert empty_response.status_code == 400
        empty_data = empty_response.json()
        assert "status" in empty_data
        assert empty_data["status"] != "success"

        # Test insufficient words (less than 16)
        insufficient_payload = {"file_content": "word1,word2,word3"}
        insufficient_response = self.client.post("/api/puzzle/setup_puzzle", json=insufficient_payload)

        assert insufficient_response.status_code == 400
        insufficient_data = insufficient_response.json()
        assert "status" in insufficient_data
        assert insufficient_data["status"] != "success"

        # Test too many words (more than 16)
        too_many_words = ",".join([f"word{i}" for i in range(1, 25)])  # 24 words
        too_many_payload = {"file_content": too_many_words}
        too_many_response = self.client.post("/api/puzzle/setup_puzzle", json=too_many_payload)

        assert too_many_response.status_code == 400
        too_many_data = too_many_response.json()
        assert "status" in too_many_data
        assert too_many_data["status"] != "success"

    def test_insufficient_words_recommendation_error(self) -> None:
        """Test insufficient words for recommendation error handling.

        From quickstart: Complete puzzle until <4 words remain, click "Next Recommendation"
        Expected: Error message "Not enough words remaining"
        """
        # Setup puzzle with 16 words
        setup_payload = {"file_content": "w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16"}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)
        assert setup_response.status_code == 200

        # Simulate solving most of the puzzle (leaving <4 words)
        # Mark 3 groups correct (12 words removed, 4 remaining)
        for color in ["Yellow", "Green", "Blue"]:
            # Get recommendation
            rec_response = self.client.get("/api/puzzle/next_recommendation")
            assert rec_response.status_code == 200

            # Mark as correct
            resp_response = self.client.post(
                "/api/puzzle/record_response", json={"response_type": "correct", "color": color}
            )
            assert resp_response.status_code == 200

        # Now try to get recommendation when only 4 words remain
        # This should still work since we have exactly 4 words
        rec_response = self.client.get("/api/puzzle/next_recommendation")
        assert rec_response.status_code == 200

        # Mark the last group correct to have 0 words remaining
        resp_response = self.client.post(
            "/api/puzzle/record_response", json={"response_type": "correct", "color": "Purple"}
        )
        assert resp_response.status_code == 200
        resp_data = resp_response.json()
        assert resp_data["game_status"] == "won"

        # Now try to get recommendation when no words remain
        insufficient_response = self.client.get("/api/puzzle/next_recommendation")
        assert insufficient_response.status_code == 400
        insufficient_data = insufficient_response.json()
        assert "status" in insufficient_data
        assert (
            "not enough" in insufficient_data["status"].lower() or "insufficient" in insufficient_data["status"].lower()
        )

    def test_no_active_recommendation_error(self) -> None:
        """Test no active recommendation error handling.

        From quickstart: Before getting any recommendation, click response button
        Expected: Error message "No recommendation to respond to"
        """
        # Setup puzzle first
        setup_payload = {"file_content": "w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16"}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)
        assert setup_response.status_code == 200

        # Try to respond without getting a recommendation first
        no_rec_payload = {"response_type": "correct", "color": "Yellow"}
        no_rec_response = self.client.post("/api/puzzle/record_response", json=no_rec_payload)

        assert no_rec_response.status_code == 400
        no_rec_data = no_rec_response.json()
        assert "status" in no_rec_data
        assert "no recommendation" in no_rec_data["status"].lower() or "no active" in no_rec_data["status"].lower()

    def test_maximum_mistakes_failure_handling(self) -> None:
        """Test maximum mistakes failure handling.

        From quickstart: Make 4 incorrect/one-away responses
        Expected: Failure popup "Unable to Solve puzzle", all buttons disabled except "Setup Puzzle"
        """
        # Setup puzzle
        setup_payload = {"file_content": "w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16"}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)
        assert setup_response.status_code == 200

        # Make 4 mistakes to trigger failure
        for i in range(4):
            # Get recommendation
            rec_response = self.client.get("/api/puzzle/next_recommendation")
            assert rec_response.status_code == 200

            # Make incorrect response
            mistake_payload = {"response_type": "incorrect"}
            mistake_response = self.client.post("/api/puzzle/record_response", json=mistake_payload)
            assert mistake_response.status_code == 200
            mistake_data = mistake_response.json()

            assert mistake_data["mistake_count"] == i + 1

            # Check game status after 4th mistake
            if i == 3:  # 4th mistake (0-indexed)
                assert mistake_data["game_status"] == "lost"
            else:
                assert mistake_data["game_status"] == "active"

        # After game is lost, recommendations should not be available
        lost_rec_response = self.client.get("/api/puzzle/next_recommendation")
        assert lost_rec_response.status_code == 400
        lost_data = lost_rec_response.json()
        assert "status" in lost_data
        assert lost_data["status"] != "success"

    def test_duplicate_words_error_handling(self) -> None:
        """Test handling of CSV files with duplicate words."""
        # CSV with duplicate words
        duplicate_payload = {
            "file_content": "word1,word2,word1,word4,word5,word6,word7,word8,word9,word10,word11,word12,word13,word14,word15,word16"
        }

        duplicate_response = self.client.post("/api/puzzle/setup_puzzle", json=duplicate_payload)

        # Should either handle gracefully or return error
        if duplicate_response.status_code == 200:
            # If successful, should have exactly 16 unique words
            data = duplicate_response.json()
            assert len(data["remaining_words"]) == 16
            assert len(set(data["remaining_words"])) == 16  # All unique
        else:
            # If error, should have proper error structure
            assert duplicate_response.status_code == 400
            data = duplicate_response.json()
            assert "status" in data
            assert data["status"] != "success"

    def test_malformed_csv_error_handling(self) -> None:
        """Test handling of malformed CSV content."""
        malformed_cases = [
            {"file_content": "word1,word2,,word4"},  # Empty field
            {"file_content": "word1,word2,word3,"},  # Trailing comma
            {"file_content": ",word2,word3,word4"},  # Leading comma
            {"file_content": "word1 word2 word3"},  # No commas
        ]

        for case in malformed_cases:
            response = self.client.post("/api/puzzle/setup_puzzle", json=case)

            # Should return error for malformed content
            assert response.status_code == 400
            data = response.json()
            assert "status" in data
            assert data["status"] != "success"

    def test_response_after_game_end_error_handling(self) -> None:
        """Test that responses are rejected after game ends (win/loss)."""
        # Setup and win the game
        setup_payload = {"file_content": "w1,w2,w3,w4,w5,w6,w7,w8,w9,w10,w11,w12,w13,w14,w15,w16"}
        self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)

        # Win the game by getting 4 correct groups
        for color in ["Yellow", "Green", "Blue", "Purple"]:
            self.client.get("/api/puzzle/next_recommendation")
            resp = self.client.post("/api/puzzle/record_response", json={"response_type": "correct", "color": color})
            if color == "Purple":
                assert resp.json()["game_status"] == "won"

        # Try to make another response after winning
        post_win_response = self.client.post(
            "/api/puzzle/record_response", json={"response_type": "correct", "color": "Yellow"}
        )

        assert post_win_response.status_code == 400
        post_win_data = post_win_response.json()
        assert "status" in post_win_data
        assert post_win_data["status"] != "success"
