"""
Unit tests for GameResultsRepository.

Tests cover database operations:
- insert method (successful inserts, duplicate detection)
- check_duplicate method
- get_all method (ordering, empty state)
- get_by_id method
- _row_to_model conversion

Uses in-memory SQLite database for testing to avoid file system dependencies.
"""

import sqlite3
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

import pytest

from src.database.game_results_repository import GameResultsRepository
from src.game_result import GameResult


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test_game_results.db"

    # Create the database schema
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            puzzle_id TEXT NOT NULL,
            game_date TEXT NOT NULL,
            puzzle_solved TEXT NOT NULL,
            count_groups_found INTEGER NOT NULL CHECK(count_groups_found >= 0 AND count_groups_found <= 4),
            count_mistakes INTEGER NOT NULL CHECK(count_mistakes >= 0 AND count_mistakes <= 4),
            total_guesses INTEGER NOT NULL CHECK(total_guesses > 0),
            llm_provider_name TEXT,
            llm_model_name TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(puzzle_id, game_date)
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_puzzle_date
        ON game_results(puzzle_id, game_date)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_game_date_desc
        ON game_results(game_date DESC)
    """)

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_db_connection(test_db):
    """Mock get_database_connection to use test database."""
    def get_connection():
        conn = sqlite3.connect(str(test_db))
        conn.row_factory = sqlite3.Row
        return conn

    # Context manager wrapper
    class ConnectionContextManager:
        def __init__(self, db_path):
            self.db_path = db_path
            self.conn = None

        def __enter__(self):
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            return self.conn

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
                self.conn.close()

    return lambda: ConnectionContextManager(test_db)


class TestGameResultsRepository:
    """Test GameResultsRepository database operations."""

    def test_insert_creates_new_record(self, mock_db_connection):
        """Test that insert creates a new record and returns result_id."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4"
            }

            result_id = GameResultsRepository.insert(game_data)

            assert result_id is not None
            assert result_id > 0

    def test_insert_without_optional_fields(self, mock_db_connection):
        """Test that insert works without optional LLM fields."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "false",
                "count_groups_found": 2,
                "count_mistakes": 4,
                "total_guesses": 6
            }

            result_id = GameResultsRepository.insert(game_data)

            assert result_id is not None
            assert result_id > 0

    def test_insert_duplicate_raises_integrity_error(self, mock_db_connection):
        """Test that inserting duplicate (puzzle_id, game_date) raises IntegrityError."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4"
            }

            # First insert should succeed
            GameResultsRepository.insert(game_data)

            # Second insert with same puzzle_id and game_date should fail
            with pytest.raises(sqlite3.IntegrityError):
                GameResultsRepository.insert(game_data)

    def test_check_duplicate_returns_true_for_existing_record(self, mock_db_connection):
        """Test that check_duplicate returns True for existing record."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8
            }

            GameResultsRepository.insert(game_data)

            # Check for duplicate
            is_duplicate = GameResultsRepository.check_duplicate(
                "550e8400-e29b-41d4-a716-446655440000",
                "2025-12-24T15:30:00+00:00"
            )

            assert is_duplicate is True

    def test_check_duplicate_returns_false_for_nonexistent_record(self, mock_db_connection):
        """Test that check_duplicate returns False for non-existent record."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            is_duplicate = GameResultsRepository.check_duplicate(
                "550e8400-e29b-41d4-a716-446655440000",
                "2025-12-24T15:30:00+00:00"
            )

            assert is_duplicate is False

    def test_check_duplicate_different_date_same_puzzle(self, mock_db_connection):
        """Test that same puzzle_id with different date is not a duplicate."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8
            }

            GameResultsRepository.insert(game_data)

            # Different date, same puzzle_id - should not be duplicate
            is_duplicate = GameResultsRepository.check_duplicate(
                "550e8400-e29b-41d4-a716-446655440000",
                "2025-12-25T15:30:00+00:00"  # Different date
            )

            assert is_duplicate is False

    def test_get_all_returns_empty_list_when_no_records(self, mock_db_connection):
        """Test that get_all returns empty list when no records exist."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            results = GameResultsRepository.get_all()

            assert results == []

    def test_get_all_returns_all_records_ordered_by_date_desc(self, mock_db_connection):
        """Test that get_all returns records ordered by game_date DESC."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            # Insert multiple records with different dates
            game1 = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
                "game_date": "2025-12-24T10:00:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 1,
                "total_guesses": 5
            }

            game2 = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440002",
                "game_date": "2025-12-25T10:00:00+00:00",
                "puzzle_solved": "false",
                "count_groups_found": 2,
                "count_mistakes": 4,
                "total_guesses": 6
            }

            game3 = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440003",
                "game_date": "2025-12-23T10:00:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 0,
                "total_guesses": 4
            }

            GameResultsRepository.insert(game1)
            GameResultsRepository.insert(game2)
            GameResultsRepository.insert(game3)

            results = GameResultsRepository.get_all()

            assert len(results) == 3
            # Should be ordered by date DESC (most recent first)
            assert results[0].game_date == "2025-12-25T10:00:00+00:00"
            assert results[1].game_date == "2025-12-24T10:00:00+00:00"
            assert results[2].game_date == "2025-12-23T10:00:00+00:00"

    def test_get_all_returns_game_result_objects(self, mock_db_connection):
        """Test that get_all returns GameResult Pydantic models."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4"
            }

            GameResultsRepository.insert(game_data)

            results = GameResultsRepository.get_all()

            assert len(results) == 1
            assert isinstance(results[0], GameResult)
            assert results[0].puzzle_id == "550e8400-e29b-41d4-a716-446655440000"
            assert results[0].puzzle_solved == "true"
            assert results[0].count_groups_found == 4

    def test_get_by_id_returns_record(self, mock_db_connection):
        """Test that get_by_id returns the correct record."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4"
            }

            result_id = GameResultsRepository.insert(game_data)

            result = GameResultsRepository.get_by_id(result_id)

            assert result is not None
            assert isinstance(result, GameResult)
            assert result.result_id == result_id
            assert result.puzzle_id == "550e8400-e29b-41d4-a716-446655440000"
            assert result.puzzle_solved == "true"

    def test_get_by_id_returns_none_for_nonexistent_id(self, mock_db_connection):
        """Test that get_by_id returns None for non-existent ID."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            result = GameResultsRepository.get_by_id(99999)

            assert result is None

    def test_row_to_model_conversion(self, mock_db_connection):
        """Test that _row_to_model correctly converts database row to GameResult."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4"
            }

            result_id = GameResultsRepository.insert(game_data)
            result = GameResultsRepository.get_by_id(result_id)

            # Verify all fields are correctly mapped
            assert result.result_id == result_id
            assert result.puzzle_id == game_data["puzzle_id"]
            assert result.game_date == game_data["game_date"]
            assert result.puzzle_solved == game_data["puzzle_solved"]
            assert result.count_groups_found == game_data["count_groups_found"]
            assert result.count_mistakes == game_data["count_mistakes"]
            assert result.total_guesses == game_data["total_guesses"]
            assert result.llm_provider_name == game_data["llm_provider_name"]
            assert result.llm_model_name == game_data["llm_model_name"]
            assert result.created_at is not None  # Auto-generated

    def test_get_all_custom_ordering(self, mock_db_connection):
        """Test that get_all respects custom order_by parameter."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game1 = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440001",
                "game_date": "2025-12-24T10:00:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 1,
                "total_guesses": 5
            }

            game2 = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440002",
                "game_date": "2025-12-25T10:00:00+00:00",
                "puzzle_solved": "false",
                "count_groups_found": 2,
                "count_mistakes": 4,
                "total_guesses": 6
            }

            id1 = GameResultsRepository.insert(game1)
            id2 = GameResultsRepository.insert(game2)

            # Order by result_id ASC
            results = GameResultsRepository.get_all(order_by="result_id ASC")

            assert len(results) == 2
            assert results[0].result_id == id1
            assert results[1].result_id == id2

    def test_get_all_invalid_ordering_uses_default(self, mock_db_connection):
        """Test that get_all uses default ordering for invalid order_by value."""
        with patch('src.database.game_results_repository.get_database_connection', mock_db_connection):
            game_data = {
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8
            }

            GameResultsRepository.insert(game_data)

            # Try invalid order_by - should fall back to default
            results = GameResultsRepository.get_all(order_by="invalid_sql; DROP TABLE game_results;")

            # Should still return results (with default ordering)
            assert len(results) == 1
