"""
GuessAttempt model for LLM Provider Integration.
Represents a previous guess attempt with its outcome.
"""

from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List, Optional
from enum import Enum


class GuessOutcome(str, Enum):
    """Possible outcomes for a guess attempt."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    ONE_AWAY = "one_away"


class GuessAttempt(BaseModel):
    """A previous guess attempt in the puzzle."""

    words: List[str]
    outcome: GuessOutcome
    actual_connection: Optional[str] = None
    timestamp: datetime

    @field_validator("words")
    @classmethod
    def validate_words(cls, v: List[str]) -> List[str]:
        """Validate words in guess attempt."""
        if len(v) != 4:
            raise ValueError("words must contain exactly 4 items")

        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("words must not contain duplicates")

        # Check for empty or whitespace-only words
        cleaned_words = []
        for word in v:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("all words must be non-empty strings")
            cleaned_words.append(word.strip().lower())

        return cleaned_words

    @field_validator("actual_connection")
    @classmethod
    def validate_actual_connection(cls, v: Optional[str], info) -> Optional[str]:
        """Validate actual_connection based on outcome."""
        outcome = info.data.get("outcome")

        if outcome == GuessOutcome.CORRECT:
            if v is None or v.strip() == "":
                raise ValueError("actual_connection is required when outcome is correct")
            return v.strip()

        # For incorrect or one_away, actual_connection can be None or provided
        if v is not None:
            return v.strip() if v.strip() else None

        return v

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Validate timestamp is not in the future."""
        if v > datetime.now():
            raise ValueError("timestamp cannot be in the future")
        return v

    def was_successful(self) -> bool:
        """Check if this guess was successful."""
        return self.outcome == GuessOutcome.CORRECT

    def get_attempted_words(self) -> List[str]:
        """Get the list of words that were attempted."""
        return self.words.copy()

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                    "outcome": "correct",
                    "actual_connection": "Fish",
                    "timestamp": "2025-10-05T10:30:00Z",
                },
                {
                    "words": ["RED", "BLUE", "GREEN", "PURPLE"],
                    "outcome": "one_away",
                    "actual_connection": None,
                    "timestamp": "2025-10-05T10:25:00Z",
                },
                {
                    "words": ["PIANO", "GUITAR", "VIOLIN", "DRUMS"],
                    "outcome": "incorrect",
                    "actual_connection": None,
                    "timestamp": "2025-10-05T10:20:00Z",
                },
            ]
        }
