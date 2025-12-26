"""
Database schema definitions for game history storage.

This module defines the SQLite schema for the game_results table
and provides migration/initialization functions.
"""

# SQLite schema for game_results table
GAME_RESULTS_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS game_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    puzzle_id TEXT(36) NOT NULL,
    game_date TEXT NOT NULL,
    puzzle_solved TEXT NOT NULL CHECK(puzzle_solved IN ('true', 'false')),
    count_groups_found INTEGER NOT NULL CHECK(count_groups_found >= 0 AND count_groups_found <= 4),
    count_mistakes INTEGER NOT NULL CHECK(count_mistakes >= 0 AND count_mistakes <= 4),
    total_guesses INTEGER NOT NULL CHECK(total_guesses > 0),
    llm_provider_name TEXT,
    llm_model_name TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
);
"""

# Unique index for preventing duplicate records
UNIQUE_PUZZLE_DATE_INDEX_DDL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_puzzle_date
ON game_results(puzzle_id, game_date);
"""

# Index for efficient retrieval ordering
GAME_DATE_INDEX_DDL = """
CREATE INDEX IF NOT EXISTS idx_game_date_desc
ON game_results(game_date DESC);
"""


def get_schema_ddl() -> list[str]:
    """
    Return list of DDL statements for creating the database schema.

    Returns:
        List of SQL DDL statements to execute in order
    """
    return [
        GAME_RESULTS_TABLE_DDL,
        UNIQUE_PUZZLE_DATE_INDEX_DDL,
        GAME_DATE_INDEX_DDL,
    ]
