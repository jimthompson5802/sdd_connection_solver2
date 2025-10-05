"""
CompletedGroup model for LLM Provider Integration.
Represents a successfully solved group in the connection puzzle.
"""

from pydantic import BaseModel, field_validator
from typing import List
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels for connection groups."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    TRICKY = "tricky"


class CompletedGroup(BaseModel):
    """A successfully solved group of 4 connected words."""
    
    words: List[str]
    connection: str
    difficulty: DifficultyLevel
    
    @field_validator('words')
    @classmethod
    def validate_words(cls, v: List[str]) -> List[str]:
        """Validate words in completed group."""
        if len(v) != 4:
            raise ValueError("words must contain exactly 4 items")
        
        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("words must not contain duplicates")
        
        # Clean and validate words
        cleaned_words = []
        for word in v:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("all words must be non-empty strings")
            cleaned_word = word.strip().upper()
            cleaned_words.append(cleaned_word)
        
        return cleaned_words
    
    @field_validator('connection')
    @classmethod
    def validate_connection(cls, v: str) -> str:
        """Validate connection description."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("connection must be a non-empty string")
        
        connection = v.strip()
        if len(connection) > 100:
            raise ValueError("connection description cannot exceed 100 characters")
        
        return connection
    
    def get_difficulty_score(self) -> int:
        """Get numeric difficulty score (1-4, higher is harder)."""
        difficulty_scores = {
            DifficultyLevel.EASY: 1,
            DifficultyLevel.MEDIUM: 2,
            DifficultyLevel.HARD: 3,
            DifficultyLevel.TRICKY: 4
        }
        return difficulty_scores[self.difficulty]
    
    def contains_word(self, word: str) -> bool:
        """Check if this group contains a specific word."""
        return word.upper() in [w.upper() for w in self.words]
    
    def get_word_list(self) -> List[str]:
        """Get a copy of the words in this group."""
        return self.words.copy()
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "examples": [
                {
                    "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                    "connection": "Fish",
                    "difficulty": "easy"
                },
                {
                    "words": ["PIANO", "GUITAR", "VIOLIN", "DRUMS"],
                    "connection": "Musical instruments",
                    "difficulty": "medium"
                },
                {
                    "words": ["RED", "BLUE", "GREEN", "YELLOW"],
                    "connection": "Colors",
                    "difficulty": "easy"
                },
                {
                    "words": ["BANK", "YARD", "INTEREST", "COMPOUND"],
                    "connection": "Can precede 'STATEMENT'",
                    "difficulty": "tricky"
                }
            ]
        }