"""
Database repository for game results.

This module provides data access methods for game_results table operations
including insert, select, and duplicate checking.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from ..database import get_database_connection
from ..models.game_result import GameResult


class GameResultsRepository:
    """Repository for game_results database operations."""

    @staticmethod
    def insert(game_result_data: Dict[str, Any]) -> int:
        """
        Insert a new game result record.

        Args:
            game_result_data: Dictionary with game result fields

        Returns:
            result_id: The ID of the newly inserted record

        Raises:
            sqlite3.IntegrityError: If duplicate (puzzle_id, game_date) exists
            sqlite3.Error: For other database errors
        """
        with get_database_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO game_results (
                    puzzle_id, game_date, puzzle_solved,
                    count_groups_found, count_mistakes, total_guesses,
                    llm_provider_name, llm_model_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    game_result_data["puzzle_id"],
                    game_result_data["game_date"],
                    game_result_data["puzzle_solved"],
                    game_result_data["count_groups_found"],
                    game_result_data["count_mistakes"],
                    game_result_data["total_guesses"],
                    game_result_data.get("llm_provider_name"),
                    game_result_data.get("llm_model_name"),
                ),
            )

            return cursor.lastrowid

    @staticmethod
    def check_duplicate(puzzle_id: str, game_date: str) -> bool:
        """
        Check if a record with the given puzzle_id and game_date already exists.

        Args:
            puzzle_id: UUID v5 of puzzle words
            game_date: ISO 8601 timestamp

        Returns:
            True if duplicate exists, False otherwise
        """
        with get_database_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*) FROM game_results
                WHERE puzzle_id = ? AND game_date = ?
                """,
                (puzzle_id, game_date),
            )

            count = cursor.fetchone()[0]
            return count > 0

    @staticmethod
    def get_all(order_by: str = "game_date DESC") -> List[GameResult]:
        """
        Retrieve all game results ordered by specified field.

        Args:
            order_by: SQL ORDER BY clause (default: "game_date DESC")

        Returns:
            List of GameResult objects
        """
        with get_database_connection() as conn:
            cursor = conn.cursor()

            # Validate order_by to prevent SQL injection
            allowed_order = ["game_date DESC", "game_date ASC", "result_id DESC", "result_id ASC"]
            if order_by not in allowed_order:
                order_by = "game_date DESC"

            cursor.execute(f"SELECT * FROM game_results ORDER BY {order_by}")

            rows = cursor.fetchall()
            return [GameResultsRepository._row_to_model(row) for row in rows]

    @staticmethod
    def get_by_id(result_id: int) -> Optional[GameResult]:
        """
        Retrieve a single game result by ID.

        Args:
            result_id: Primary key of the game result

        Returns:
            GameResult object or None if not found
        """
        with get_database_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM game_results WHERE result_id = ?", (result_id,))

            row = cursor.fetchone()
            if row:
                return GameResultsRepository._row_to_model(row)
            return None

    @staticmethod
    def _row_to_model(row) -> GameResult:
        """
        Convert a database row to a GameResult model.

        Args:
            row: sqlite3.Row object

        Returns:
            GameResult Pydantic model
        """
        return GameResult(
            result_id=row["result_id"],
            puzzle_id=row["puzzle_id"],
            game_date=row["game_date"],
            puzzle_solved=row["puzzle_solved"],
            count_groups_found=row["count_groups_found"],
            count_mistakes=row["count_mistakes"],
            total_guesses=row["total_guesses"],
            llm_provider_name=row["llm_provider_name"],
            llm_model_name=row["llm_model_name"],
            created_at=row["created_at"],
        )
