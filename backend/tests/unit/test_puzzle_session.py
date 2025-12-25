"""
Unit tests for PuzzleSession model enhancements.

Tests cover the game history feature additions:
- puzzle_id generation (UUID v5)
- set_llm_info method
- to_game_result method
- computed properties (is_finished, groups_found_count, total_guesses_count)
"""

import uuid
from datetime import datetime, timezone

import pytest

from src.models import PuzzleSession, ResponseResult, WordGroup


class TestPuzzleSessionGameHistoryEnhancements:
    """Test game history feature enhancements to PuzzleSession."""

    def test_puzzle_id_generation_is_deterministic(self):
        """Test that puzzle_id is deterministic for the same words."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session1 = PuzzleSession(words)
        session2 = PuzzleSession(words)

        assert session1.puzzle_id == session2.puzzle_id
        assert session1.puzzle_id != session1.session_id  # puzzle_id != session_id

    def test_puzzle_id_is_uuid_v5_format(self):
        """Test that puzzle_id is a valid UUID v5."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Should be parseable as UUID
        parsed_uuid = uuid.UUID(session.puzzle_id)

        # Should be UUID version 5
        assert parsed_uuid.version == 5

    def test_puzzle_id_ignores_word_order(self):
        """Test that puzzle_id is the same regardless of word order."""
        words1 = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                  "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]
        words2 = ["berry", "melon", "lime", "plum", "pear", "peach", "orange", "mango",
                  "lemon", "kiwi", "grape", "fig", "date", "cherry", "banana", "apple"]

        session1 = PuzzleSession(words1)
        session2 = PuzzleSession(words2)

        assert session1.puzzle_id == session2.puzzle_id

    def test_puzzle_id_normalizes_case_and_whitespace(self):
        """Test that puzzle_id normalizes case and whitespace."""
        words1 = ["Apple", "Banana", "Cherry", "Date", "Fig", "Grape", "Kiwi", "Lemon",
                  "Mango", "Orange", "Peach", "Pear", "Plum", "Lime", "Melon", "Berry"]
        words2 = ["apple ", " banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                  "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session1 = PuzzleSession(words1)
        session2 = PuzzleSession(words2)

        assert session1.puzzle_id == session2.puzzle_id

    def test_puzzle_id_differs_for_different_words(self):
        """Test that puzzle_id differs when word set is different."""
        words1 = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                  "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]
        words2 = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                  "mango", "orange", "peach", "pear", "plum", "lime", "melon", "different"]

        session1 = PuzzleSession(words1)
        session2 = PuzzleSession(words2)

        assert session1.puzzle_id != session2.puzzle_id

    def test_set_llm_info_stores_provider_and_model(self):
        """Test that set_llm_info correctly stores LLM information."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Initially None
        assert session.llm_provider_name is None
        assert session.llm_model_name is None

        # Set LLM info
        session.set_llm_info("openai", "gpt-4")

        assert session.llm_provider_name == "openai"
        assert session.llm_model_name == "gpt-4"

    def test_set_llm_info_can_be_updated(self):
        """Test that set_llm_info can be called multiple times."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        session.set_llm_info("openai", "gpt-4")
        assert session.llm_provider_name == "openai"
        assert session.llm_model_name == "gpt-4"

        # Update to different provider
        session.set_llm_info("ollama", "llama2")
        assert session.llm_provider_name == "ollama"
        assert session.llm_model_name == "llama2"

    def test_to_game_result_returns_correct_structure(self):
        """Test that to_game_result returns the expected dictionary structure."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)
        session.set_llm_info("openai", "gpt-4")

        game_date = datetime(2025, 12, 24, 15, 30, 0, tzinfo=timezone.utc)
        result = session.to_game_result(game_date)

        # Check all required fields are present
        assert "puzzle_id" in result
        assert "game_date" in result
        assert "puzzle_solved" in result
        assert "count_groups_found" in result
        assert "count_mistakes" in result
        assert "total_guesses" in result
        assert "llm_provider_name" in result
        assert "llm_model_name" in result

    def test_to_game_result_converts_timestamp_to_utc_iso8601(self):
        """Test that to_game_result converts timestamp to UTC ISO 8601."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        game_date = datetime(2025, 12, 24, 15, 30, 0, tzinfo=timezone.utc)
        result = session.to_game_result(game_date)

        assert result["game_date"] == "2025-12-24T15:30:00+00:00"

    def test_to_game_result_stores_puzzle_solved_as_string(self):
        """Test that to_game_result stores puzzle_solved as 'true' or 'false' string."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)
        game_date = datetime.now(timezone.utc)

        # When not won
        result = session.to_game_result(game_date)
        assert result["puzzle_solved"] == "false"
        assert isinstance(result["puzzle_solved"], str)

        # Simulate winning the game
        session.game_won = True
        result = session.to_game_result(game_date)
        assert result["puzzle_solved"] == "true"
        assert isinstance(result["puzzle_solved"], str)

    def test_to_game_result_includes_llm_info(self):
        """Test that to_game_result includes LLM provider and model information."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)
        session.set_llm_info("openai", "gpt-4")

        game_date = datetime.now(timezone.utc)
        result = session.to_game_result(game_date)

        assert result["llm_provider_name"] == "openai"
        assert result["llm_model_name"] == "gpt-4"

    def test_to_game_result_handles_none_llm_info(self):
        """Test that to_game_result handles None LLM info correctly."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)
        # Don't set LLM info

        game_date = datetime.now(timezone.utc)
        result = session.to_game_result(game_date)

        assert result["llm_provider_name"] is None
        assert result["llm_model_name"] is None

    def test_is_finished_property_when_game_complete(self):
        """Test that is_finished property returns True when game is complete."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Initially not finished
        assert session.is_finished is False

        # Mark game complete
        session.game_complete = True
        assert session.is_finished is True

    def test_groups_found_count_property(self):
        """Test that groups_found_count correctly counts found groups."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Initially 0
        assert session.groups_found_count == 0

        # Add some groups
        session.groups.append(WordGroup(category="Fruits", words=["apple", "banana", "cherry", "date"], difficulty=1, found=True))
        assert session.groups_found_count == 1

        session.groups.append(WordGroup(category="More Fruits", words=["fig", "grape", "kiwi", "lemon"], difficulty=2, found=True))
        assert session.groups_found_count == 2

        # Add unfound group - should not count
        session.groups.append(WordGroup(category="Other", words=["mango", "orange", "peach", "pear"], difficulty=3, found=False))
        assert session.groups_found_count == 2

    def test_total_guesses_count_property(self):
        """Test that total_guesses_count correctly counts attempts."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Initially 0
        assert session.total_guesses_count == 0

        # Record some attempts
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT)
        assert session.total_guesses_count == 1

        session.record_attempt(["fig", "grape", "kiwi", "lemon"], ResponseResult.INCORRECT)
        assert session.total_guesses_count == 2

        session.record_attempt(["mango", "orange", "peach", "pear"], ResponseResult.ONE_AWAY)
        assert session.total_guesses_count == 3

    def test_to_game_result_uses_computed_properties(self):
        """Test that to_game_result uses the computed properties for counts."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Record 2 groups found
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT)
        session.record_attempt(["fig", "grape", "kiwi", "lemon"], ResponseResult.CORRECT)

        # Record 1 mistake
        session.record_attempt(["mango", "orange", "peach", "pear"], ResponseResult.INCORRECT)

        game_date = datetime.now(timezone.utc)
        result = session.to_game_result(game_date)

        assert result["count_groups_found"] == 2
        assert result["count_mistakes"] == 1
        assert result["total_guesses"] == 3

    def test_generate_puzzle_id_method_directly(self):
        """Test the generate_puzzle_id method can be called directly."""
        words = ["apple", "banana", "cherry", "date", "fig", "grape", "kiwi", "lemon",
                 "mango", "orange", "peach", "pear", "plum", "lime", "melon", "berry"]

        session = PuzzleSession(words)

        # Generate new puzzle ID
        new_id = session.generate_puzzle_id()

        # Should be same as the one assigned in __init__
        assert new_id == session.puzzle_id

        # Should be valid UUID
        uuid.UUID(new_id)
