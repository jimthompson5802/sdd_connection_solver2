"""
PuzzleState model for LLM Provider Integration.
Represents the current state of a connection puzzle.
"""

from pydantic import BaseModel, field_validator
from typing import List
from .completed_group import CompletedGroup
from .guess_attempt import GuessAttempt


class PuzzleState(BaseModel):
    """Current state of a connection puzzle with 16 words and 4 groups."""

    all_words: List[str]
    completed_groups: List[CompletedGroup] = []
    guess_attempts: List[GuessAttempt] = []
    mistakes_remaining: int = 4
    is_completed: bool = False

    @field_validator("all_words")
    @classmethod
    def validate_all_words(cls, v: List[str]) -> List[str]:
        """Validate that we have exactly 16 unique words."""
        if len(v) != 16:
            raise ValueError("all_words must contain exactly 16 words")

        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("all_words must not contain duplicates")

        # Clean and validate words
        cleaned_words = []
        for word in v:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("all words must be non-empty strings")
            cleaned_word = word.strip().lower()
            cleaned_words.append(cleaned_word)

        return cleaned_words

    @field_validator("completed_groups")
    @classmethod
    def validate_completed_groups(cls, v: List[CompletedGroup], info) -> List[CompletedGroup]:
        """Validate completed groups against all words."""
        all_words = info.data.get("all_words", [])
        all_words_set = set(word.lower() for word in all_words)

        # Check that all group words are from the puzzle
        used_words = set()
        for group in v:
            for word in group.words:
                word_lower = word.lower()
                if word_lower not in all_words_set:
                    raise ValueError(f"word '{word}' in completed group not found in puzzle words")
                if word_lower in used_words:
                    raise ValueError(f"word '{word}' appears in multiple completed groups")
                used_words.add(word_lower)

        # Check maximum 4 groups
        if len(v) > 4:
            raise ValueError("cannot have more than 4 completed groups")

        return v

    @field_validator("mistakes_remaining")
    @classmethod
    def validate_mistakes_remaining(cls, v: int) -> int:
        """Validate mistakes remaining is valid."""
        if v < 0 or v > 4:
            raise ValueError("mistakes_remaining must be between 0 and 4")
        return v

    @field_validator("is_completed")
    @classmethod
    def validate_is_completed(cls, v: bool, info) -> bool:
        """Validate completion status against completed groups."""
        completed_groups = info.data.get("completed_groups", [])

        if v and len(completed_groups) != 4:
            raise ValueError("puzzle cannot be completed without 4 completed groups")

        if not v and len(completed_groups) == 4:
            raise ValueError("puzzle must be marked as completed with 4 completed groups")

        return v

    def get_remaining_words(self) -> List[str]:
        """Get list of words not yet in completed groups."""
        completed_words = set()
        for group in self.completed_groups:
            for word in group.words:
                completed_words.add(word.lower())

        remaining = []
        for word in self.all_words:
            if word.lower() not in completed_words:
                remaining.append(word)

        return remaining

    def can_make_guess(self) -> bool:
        """Check if a guess can be made (enough words and mistakes remaining)."""
        remaining_words = self.get_remaining_words()
        return len(remaining_words) >= 4 and self.mistakes_remaining > 0 and not self.is_completed

    def get_completion_percentage(self) -> float:
        """Get completion percentage (0.0 to 1.0)."""
        return len(self.completed_groups) / 4.0

    def is_game_over(self) -> bool:
        """Check if the game is over (completed or no mistakes remaining)."""
        return self.is_completed or self.mistakes_remaining == 0

    def get_incorrect_guess_count(self) -> int:
        """Get number of incorrect guesses made."""
        return 4 - self.mistakes_remaining

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "all_words": [
                        "BASS",
                        "FLOUNDER",
                        "SALMON",
                        "TROUT",
                        "PIANO",
                        "GUITAR",
                        "VIOLIN",
                        "DRUMS",
                        "RED",
                        "BLUE",
                        "GREEN",
                        "YELLOW",
                        "APPLE",
                        "ORANGE",
                        "BANANA",
                        "GRAPE",
                    ],
                    "completed_groups": [
                        {"words": ["BASS", "FLOUNDER", "SALMON", "TROUT"], "connection": "Fish", "difficulty": "easy"}
                    ],
                    "guess_attempts": [
                        {
                            "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                            "outcome": "correct",
                            "actual_connection": "Fish",
                            "timestamp": "2025-10-05T10:30:00Z",
                        }
                    ],
                    "mistakes_remaining": 4,
                    "is_completed": False,
                }
            ]
        }
