"""
Database migrations for game history feature.

This module provides database initialization and migration functionality.
"""

from pathlib import Path

from . import get_database_path, initialize_database


def run_migrations() -> None:
    """
    Run all database migrations to ensure schema is up-to-date.

    Currently, this simply initializes the database with the latest schema.
    Future migrations can be added here as needed.
    """
    db_path = get_database_path()

    # Ensure database is initialized with latest schema
    initialize_database(db_path)

    print(f"Database initialized successfully at: {db_path}")


if __name__ == "__main__":
    # Allow running migrations directly via: python -m src.database.migrations
    run_migrations()
