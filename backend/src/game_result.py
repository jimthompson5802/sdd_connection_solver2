"""
Pydantic models for game result data.

This module defines the data models for game results using Pydantic
for validation and serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class GameResult(BaseModel):
    """
    Represents a single completed and recorded puzzle game.

    This model is used for API responses and data validation.
    """
    result_id: Optional[int] = Field(None, description="Unique identifier (auto-generated)")
    puzzle_id: str = Field(..., min_length=36, max_length=36, description="UUID v5 of sorted puzzle words")
    game_date: str = Field(..., description="ISO 8601 timestamp with timezone (UTC)")
    puzzle_solved: str = Field(..., description="'true' or 'false' string")
    count_groups_found: int = Field(..., ge=0, le=4, description="Number of groups found (0-4)")
    count_mistakes: int = Field(..., ge=0, le=4, description="Number of mistakes made (0-4)")
    total_guesses: int = Field(..., gt=0, description="Total guesses made (minimum 1)")
    llm_provider_name: Optional[str] = Field(None, description="LLM provider name")
    llm_model_name: Optional[str] = Field(None, description="LLM model name")
    created_at: Optional[str] = Field(None, description="Server timestamp when record was created")

    @field_validator("puzzle_solved")
    @classmethod
    def validate_puzzle_solved(cls, v: str) -> str:
        """Validate puzzle_solved is either 'true' or 'false'."""
        if v not in ("true", "false"):
            raise ValueError("puzzle_solved must be 'true' or 'false'")
        return v

    @field_validator("puzzle_id")
    @classmethod
    def validate_puzzle_id(cls, v: str) -> str:
        """Validate puzzle_id is a valid UUID format."""
        import uuid
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("puzzle_id must be a valid UUID string")
        return v

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "result_id": 1,
                "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
                "game_date": "2025-12-24T15:30:00+00:00",
                "puzzle_solved": "true",
                "count_groups_found": 4,
                "count_mistakes": 2,
                "total_guesses": 8,
                "llm_provider_name": "openai",
                "llm_model_name": "gpt-4",
                "created_at": "2025-12-24T15:30:05+00:00"
            }
        }
