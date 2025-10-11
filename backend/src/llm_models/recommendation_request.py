"""
RecommendationRequest model for LLM Provider Integration.
Contains all context needed to generate a word recommendation.
"""

from pydantic import BaseModel, field_validator
from typing import List, Optional
from .llm_provider import LLMProvider
from .guess_attempt import GuessAttempt


class RecommendationRequest(BaseModel):
    """Request for word recommendations with full puzzle context."""

    llm_provider: LLMProvider
    remaining_words: List[str]
    previous_guesses: List[GuessAttempt] = []
    puzzle_context: Optional[str] = None

    @field_validator("remaining_words")
    @classmethod
    def validate_remaining_words(cls, v: List[str]) -> List[str]:
        """Validate remaining words list."""
        if len(v) < 4:
            raise ValueError("remaining_words must contain at least 4 words")

        if len(v) > 16:
            raise ValueError("remaining_words cannot contain more than 16 words")

        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("remaining_words must not contain duplicates")

        # Clean and validate words
        cleaned_words = []
        for word in v:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("all words must be non-empty strings")
            cleaned_word = word.strip().lower()
            cleaned_words.append(cleaned_word)

        return cleaned_words

    @field_validator("previous_guesses")
    @classmethod
    def validate_previous_guesses(cls, v: List[GuessAttempt], info) -> List[GuessAttempt]:
        """Validate previous guesses don't conflict with remaining words."""
        remaining_words = info.data.get("remaining_words", [])

        # Extract all words from previous guesses
        guessed_words = set()
        for guess in v:
            for word in guess.words:
                guessed_words.add(word.lower())

        # Check that no previously guessed words appear in remaining words
        remaining_words_set = set(word.lower() for word in remaining_words)
        overlap = guessed_words.intersection(remaining_words_set)

        if overlap:
            raise ValueError(f"words from previous guesses cannot appear in remaining_words: {list(overlap)}")

        return v

    @field_validator("puzzle_context")
    @classmethod
    def validate_puzzle_context(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean puzzle context."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 1000:
                raise ValueError("puzzle_context cannot exceed 1000 characters")
        return v

    def get_total_words_available(self) -> int:
        """Get the total number of words available for recommendation."""
        return len(self.remaining_words)

    def can_make_recommendation(self) -> bool:
        """Check if there are enough words to make a 4-word recommendation."""
        return len(self.remaining_words) >= 4

    def get_previously_attempted_words(self) -> List[str]:
        """Get all words that have been previously attempted."""
        attempted_words = []
        for guess in self.previous_guesses:
            attempted_words.extend(guess.words)
        return attempted_words

    def has_successful_guesses(self) -> bool:
        """Check if there have been any successful guesses."""
        return any(guess.was_successful() for guess in self.previous_guesses)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "llm_provider": {"provider_type": "simple", "model_name": None},
                    "remaining_words": ["BASS", "FLOUNDER", "SALMON", "TROUT", "PIANO", "GUITAR", "VIOLIN", "DRUMS"],
                    "previous_guesses": [],
                    "puzzle_context": None,
                },
                {
                    "llm_provider": {"provider_type": "openai", "model_name": "gpt-4o-mini"},
                    "remaining_words": ["PIANO", "GUITAR", "VIOLIN", "DRUMS"],
                    "previous_guesses": [
                        {
                            "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                            "outcome": "correct",
                            "actual_connection": "Fish",
                            "timestamp": "2025-10-05T10:30:00Z",
                        }
                    ],
                    "puzzle_context": "Music and instruments theme",
                },
            ]
        }
