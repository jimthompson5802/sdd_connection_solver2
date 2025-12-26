"""
Database connection and initialization module.

This module provides SQLite database connection management,
initialization, and migration support for game history storage.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .schema import get_schema_ddl


def get_database_path() -> Path:
    """
    Get the database file path from environment or use default.

    Returns:
        Path object pointing to the SQLite database file
    """
    # Check environment variable first
    db_path_str = os.environ.get("DATABASE_PATH")

    if db_path_str:
        return Path(db_path_str)

    # Default to backend/data/connect_puzzle_game.db
    backend_dir = Path(__file__).parent.parent.parent
    return backend_dir / "data" / "connect_puzzle_game.db"


def initialize_database(db_path: Path | None = None) -> None:
    """
    Initialize the database by creating tables and indexes if they don't exist.

    Args:
        db_path: Optional path to database file. If None, uses get_database_path()

    Raises:
        sqlite3.Error: If database initialization fails
    """
    if db_path is None:
        db_path = get_database_path()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create connection and execute schema DDL
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()

        # Execute all schema DDL statements
        for ddl_statement in get_schema_ddl():
            cursor.execute(ddl_statement)

        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_database_connection(db_path: Path | None = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.

    Provides a database connection that automatically commits on success
    and rolls back on error, then closes the connection.

    Args:
        db_path: Optional path to database file. If None, uses get_database_path()

    Yields:
        sqlite3.Connection: Database connection

    Example:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM game_results")
            results = cursor.fetchall()
    """
    if db_path is None:
        db_path = get_database_path()

    # Initialize database if it doesn't exist
    if not db_path.exists():
        initialize_database(db_path)

    conn = sqlite3.connect(str(db_path))
    # Enable row factory for dict-like access
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
