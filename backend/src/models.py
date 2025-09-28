"""
Data models and types for the NYT Connections puzzle solver.
Defines Pydantic models for request/response validation and internal data structures.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from dataclasses import dataclass
from enum import Enum
import uuid
from datetime import datetime


class ResponseResult(str, Enum):
    """Valid response results from user attempts."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    ONE_AWAY = "one-away"


# Request Models
class SetupPuzzleRequest(BaseModel):
    """Request model for setting up a new puzzle."""

    file_content: str = Field(..., description="Comma-separated list of 16 words")

    @validator("file_content")
    def validate_file_content(cls, v):
        if not v or not v.strip():
            raise ValueError("File content cannot be empty")

        word_list = [word.strip() for word in v.split(",")]

        if len(word_list) != 16:
            raise ValueError("Must provide exactly 16 words")

        if len(set(word_list)) != 16:
            raise ValueError("All words must be unique")

        if any(not word for word in word_list):
            raise ValueError("Words cannot be empty or whitespace")

        return v


class NextRecommendationRequest(BaseModel):
    """Request model for getting next recommendation."""

    session_id: str = Field(..., description="Unique session identifier")

    @validator("session_id")
    def validate_session_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class RecordResponseRequest(BaseModel):
    """Request model for recording a user response."""

    response_type: str = Field(..., description="Type of response: correct, incorrect, one-away")
    color: Optional[str] = Field(None, description="Color for correct responses")

    @validator("response_type")
    def validate_response_type(cls, v):
        valid_types = ["correct", "incorrect", "one-away"]
        if v not in valid_types:
            raise ValueError(f"response_type must be one of {valid_types}")
        return v

    @validator("color")
    def validate_color(cls, v, values):
        if values.get("response_type") == "correct" and not v:
            raise ValueError("color is required for correct responses")
        if v and v not in ["Yellow", "Green", "Blue", "Purple"]:
            raise ValueError("color must be one of: Yellow, Green, Blue, Purple")
        return v


# Response Models
class SetupPuzzleResponse(BaseModel):
    """Response model for puzzle setup."""

    remaining_words: List[str] = Field(..., description="List of words in the puzzle")
    status: str = Field(default="success", description="Status of the operation")


class NextRecommendationResponse(BaseModel):
    """Response model for next recommendation."""

    words: List[str] = Field(..., description="Recommended group of 4 words")
    connection: str = Field(..., description="Rationale for the connection")
    status: str = Field(default="success", description="Status of the operation")


class RecordResponseResponse(BaseModel):
    """Response model for recording response."""

    remaining_words: List[str] = Field(..., description="Words still available to group")
    correct_count: int = Field(..., ge=0, le=4, description="Number of correct groups found")
    mistake_count: int = Field(..., ge=0, le=4, description="Number of mistakes made")
    game_status: str = Field(..., description="Game status: active, won, or lost")


# Internal Data Models
@dataclass
class WordGroup:
    """Represents a group of connected words with their category."""

    category: str
    words: List[str]
    difficulty: int  # 1-4, where 4 is hardest
    found: bool = False

    def __post_init__(self):
        if len(self.words) != 4:
            raise ValueError("Word group must contain exactly 4 words")
        if not 1 <= self.difficulty <= 4:
            raise ValueError("Difficulty must be between 1 and 4")


@dataclass
class UserAttempt:
    """Records a user's attempt at finding a group."""

    words: List[str]
    result: ResponseResult
    timestamp: datetime
    was_recommendation: bool = False

    def __post_init__(self):
        if len(self.words) != 4:
            raise ValueError("Attempt must contain exactly 4 words")


class PuzzleSession:
    """Manages the state of a single puzzle session."""

    def __init__(self, words: List[str]):
        if len(words) != 16:
            raise ValueError("Puzzle must contain exactly 16 words")

        self.session_id = str(uuid.uuid4())
        self.words = [word.strip().lower() for word in words]
        self.groups: List[WordGroup] = []
        self.attempts: List[UserAttempt] = []
        self.created_at = datetime.now()
        self.mistakes_made = 0
        self.max_mistakes = 4
        self.game_complete = False
        self.game_won = False

        # Initialize placeholder groups (will be populated by ML analysis)
        self._initialize_placeholder_groups()

    def _initialize_placeholder_groups(self):
        """Initialize placeholder groups until ML analysis is implemented."""
        # This is a simplified placeholder - in real implementation,
        # this would use ML/NLP to analyze word relationships
        words_copy = self.words.copy()

        for i in range(4):
            group_words = words_copy[i * 4 : (i + 1) * 4]
            self.groups.append(WordGroup(category=f"Category {i+1}", words=group_words, difficulty=i + 1))

    def record_attempt(self, words: List[str], result: ResponseResult, was_recommendation: bool = False):
        """Record a user attempt."""
        attempt = UserAttempt(
            words=[word.strip().lower() for word in words],
            result=result,
            timestamp=datetime.now(),
            was_recommendation=was_recommendation,
        )
        self.attempts.append(attempt)

        if result == ResponseResult.CORRECT:
            self._mark_group_found(words)
        elif result == ResponseResult.INCORRECT:
            self.mistakes_made += 1

        self._check_game_completion()

    def _mark_group_found(self, words: List[str]):
        """Mark a group as found based on the words."""
        normalized_words = [word.strip().lower() for word in words]

        for group in self.groups:
            if set(group.words) == set(normalized_words):
                group.found = True
                break

    def _check_game_completion(self):
        """Check if the game is complete (won or lost)."""
        found_groups = sum(1 for group in self.groups if group.found)

        if found_groups == 4:
            self.game_complete = True
            self.game_won = True
        elif self.mistakes_made >= self.max_mistakes:
            self.game_complete = True
            self.game_won = False

    def get_remaining_words(self) -> List[str]:
        """Get words that haven't been correctly grouped yet."""
        found_words = set()
        for group in self.groups:
            if group.found:
                found_words.update(group.words)

        return [word for word in self.words if word not in found_words]

    def get_remaining_groups_count(self) -> int:
        """Get number of groups remaining to be found."""
        return sum(1 for group in self.groups if not group.found)

    def is_game_over(self) -> bool:
        """Check if the game is over (won or lost)."""
        return self.game_complete

    def get_recommendation_data(self) -> Dict[str, Any]:
        """Get data needed for generating recommendations."""
        return {
            "remaining_words": self.get_remaining_words(),
            "attempts": [
                {"words": attempt.words, "result": attempt.result.value, "timestamp": attempt.timestamp.isoformat()}
                for attempt in self.attempts
            ],
            "mistakes_made": self.mistakes_made,
            "groups_found": sum(1 for group in self.groups if group.found),
        }


# Session storage (in-memory for now)
class SessionManager:
    """Manages puzzle sessions in memory."""

    def __init__(self):
        self._sessions: Dict[str, PuzzleSession] = {}

    def create_session(self, words: List[str]) -> PuzzleSession:
        """Create a new puzzle session."""
        session = PuzzleSession(words)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[PuzzleSession]:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists."""
        return session_id in self._sessions

    def remove_session(self, session_id: str) -> bool:
        """Remove a session from storage."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()
