"""Integration test to verify LLM 'correct' flow updates remaining words and counters.

This simulates recording a correct response with explicit attempt_words (LLM path)
without requiring a traditional recommendation first. It asserts that the
backend removes those words from remaining_words and increments correct_count.
"""

from fastapi.testclient import TestClient

from src.main import app
from src.models import session_manager


def test_llm_correct_flow_updates_state():
    client = TestClient(app)

    # Setup a puzzle with 16 known words
    words_csv = ",".join(
        [
            "alpha",
            "beta",
            "gamma",
            "delta",
            "eagle",
            "falcon",
            "hawk",
            "owl",
            "red",
            "blue",
            "green",
            "yellow",
            "one",
            "two",
            "three",
            "four",
        ]
    )
    resp = client.post("/api/puzzle/setup_puzzle", json={"file_content": words_csv})
    assert resp.status_code == 200

    # Choose a set of 4 words to mark correct via LLM attempt
    attempt = ["alpha", "beta", "gamma", "delta"]

    # Post record_response as a 'correct' with color and explicit attempt_words
    resp2 = client.post(
        "/api/puzzle/record_response",
        json={
            "response_type": "correct",
            "color": "Yellow",
            "attempt_words": attempt,
        },
    )
    assert resp2.status_code == 200
    data = resp2.json()

    # remaining_words should no longer include the attempt words
    remaining = data["remaining_words"]
    for w in attempt:
        assert w not in remaining

    # correct_count should be at least 1 now
    assert data["correct_count"] >= 1

    # sanity: game should still be active after 1 group
    assert data["game_status"] == "active"

    # Ensure session manager has exactly one session and internal remaining matches API
    # (use last-created session)
    session = list(session_manager._sessions.values())[-1]
    assert set(session.get_remaining_words()) == set(remaining)
