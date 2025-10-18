"""Integration tests for complete puzzle workflow scenarios."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestPuzzleWorkflowIntegration:
    """Integration tests for complete puzzle solving workflows per quickstart.md."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

        # Sample CSV data from quickstart.md
        self.sample_csv = "apple,orange,banana,grape,dog,cat,mouse,bird," "red,blue,green,yellow,chair,table,sofa,desk"

    def test_complete_puzzle_success_workflow(self) -> None:
        """Test complete puzzle solving workflow from setup to success.

        Based on quickstart.md End-to-End Scenario: Complete Puzzle Success
        """
        # Step 1: Setup puzzle with 16 words
        setup_payload = {"file_content": self.sample_csv}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)

        assert setup_response.status_code == 200
        setup_data = setup_response.json()
        assert len(setup_data["remaining_words"]) == 16
        assert setup_data["status"] == "success"

        # Step 2: Get first recommendation
        rec1_response = self.client.get("/api/puzzle/next_recommendation")
        assert rec1_response.status_code == 200
        rec1_data = rec1_response.json()
        assert len(rec1_data["words"]) == 4
        assert rec1_data["status"] == "success"

        # Step 3: Mark first group as correct
        correct_payload = {"response_type": "correct", "color": "Yellow"}
        resp1_response = self.client.post("/api/puzzle/record_response", json=correct_payload)
        assert resp1_response.status_code == 200
        resp1_data = resp1_response.json()
        assert len(resp1_data["remaining_words"]) == 12  # 16 - 4 = 12
        assert resp1_data["correct_count"] == 1
        assert resp1_data["mistake_count"] == 0
        assert resp1_data["game_status"] == "active"

        # Step 4: Get second recommendation and mark incorrect
        rec2_response = self.client.get("/api/puzzle/next_recommendation")
        assert rec2_response.status_code == 200

        incorrect_payload = {"response_type": "incorrect"}
        resp2_response = self.client.post("/api/puzzle/record_response", json=incorrect_payload)
        assert resp2_response.status_code == 200
        resp2_data = resp2_response.json()
        assert len(resp2_data["remaining_words"]) == 12  # Unchanged for incorrect
        assert resp2_data["correct_count"] == 1  # Unchanged
        assert resp2_data["mistake_count"] == 1  # Incremented
        assert resp2_data["game_status"] == "active"

        # Step 5: Get third recommendation and mark one-away
        rec3_response = self.client.get("/api/puzzle/next_recommendation")
        assert rec3_response.status_code == 200

        one_away_payload = {"response_type": "one-away"}
        resp3_response = self.client.post("/api/puzzle/record_response", json=one_away_payload)
        assert resp3_response.status_code == 200
        resp3_data = resp3_response.json()
        assert len(resp3_data["remaining_words"]) == 12  # Unchanged for one-away
        assert resp3_data["correct_count"] == 1  # Unchanged
        assert resp3_data["mistake_count"] == 2  # Incremented
        assert resp3_data["game_status"] == "active"

        # Step 6: Continue with correct responses until win
        for color in ["Green", "Blue", "Purple"]:
            # Get recommendation
            rec_response = self.client.get("/api/puzzle/next_recommendation")
            assert rec_response.status_code == 200

            # Mark as correct
            correct_payload = {"response_type": "correct", "color": color}
            resp_response = self.client.post("/api/puzzle/record_response", json=correct_payload)
            assert resp_response.status_code == 200
            resp_data = resp_response.json()

            # Verify progress
            expected_correct = 2 if color == "Green" else (3 if color == "Blue" else 4)
            expected_remaining = 12 - (expected_correct - 1) * 4

            assert resp_data["correct_count"] == expected_correct
            assert len(resp_data["remaining_words"]) == expected_remaining

            # Check final win condition
            if expected_correct == 4:
                assert resp_data["game_status"] == "won"
            else:
                assert resp_data["game_status"] == "active"

    def test_puzzle_failure_workflow(self) -> None:
        """Test puzzle failure when maximum mistakes reached."""
        # Setup puzzle
        setup_payload = {"file_content": self.sample_csv}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)
        assert setup_response.status_code == 200

        # Parse words from CSV for making different attempts
        words = [word.strip() for word in self.sample_csv.split(",")]

        # Make 4 incorrect responses to trigger failure using different word combinations
        for i in range(4):
            # Use different sets of 4 words for each attempt to avoid idempotency check
            start_idx = i * 4
            attempt_words = words[start_idx : start_idx + 4]

            # Mark as incorrect with explicit attempt words
            incorrect_payload = {"response_type": "incorrect", "attempt_words": attempt_words}
            resp_response = self.client.post("/api/puzzle/record_response", json=incorrect_payload)
            assert resp_response.status_code == 200
            resp_data = resp_response.json()

            assert resp_data["mistake_count"] == i + 1

            # Check game status
            if i == 3:  # 4th mistake
                assert resp_data["game_status"] == "lost"
            else:
                assert resp_data["game_status"] == "active"

    def test_mixed_response_workflow(self) -> None:
        """Test workflow with mixed correct, incorrect, and one-away responses."""
        # Setup puzzle
        setup_payload = {"file_content": self.sample_csv}
        setup_response = self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)
        assert setup_response.status_code == 200

        responses = [
            {"response_type": "correct", "color": "Yellow"},
            {"response_type": "incorrect"},
            {"response_type": "one-away"},
            {"response_type": "correct", "color": "Green"},
        ]

        expected_correct = 0
        expected_mistakes = 0

        for i, response_payload in enumerate(responses):
            # Get recommendation
            rec_response = self.client.get("/api/puzzle/next_recommendation")
            assert rec_response.status_code == 200

            # Send response
            resp_response = self.client.post("/api/puzzle/record_response", json=response_payload)
            assert resp_response.status_code == 200
            resp_data = resp_response.json()

            # Update expected counts
            if response_payload["response_type"] == "correct":
                expected_correct += 1
            elif response_payload["response_type"] in ["incorrect", "one-away"]:
                expected_mistakes += 1

            # Verify state
            assert resp_data["correct_count"] == expected_correct
            assert resp_data["mistake_count"] == expected_mistakes
            assert resp_data["game_status"] == "active"  # No win/loss in this scenario

    def test_state_persistence_across_requests(self) -> None:
        """Test that puzzle state is maintained across multiple API calls."""
        # Setup
        setup_payload = {"file_content": self.sample_csv}
        self.client.post("/api/puzzle/setup_puzzle", json=setup_payload)

        # First interaction
        self.client.get("/api/puzzle/next_recommendation")
        resp1 = self.client.post("/api/puzzle/record_response", json={"response_type": "correct", "color": "Yellow"})
        state1 = resp1.json()

        # Second interaction - state should be preserved
        self.client.get("/api/puzzle/next_recommendation")
        resp2 = self.client.post("/api/puzzle/record_response", json={"response_type": "incorrect"})
        state2 = resp2.json()

        # Verify state progression
        assert state2["correct_count"] == state1["correct_count"]  # Should remain same
        assert state2["mistake_count"] == state1["mistake_count"] + 1  # Should increment
        assert len(state2["remaining_words"]) == len(state1["remaining_words"])  # Same for incorrect
