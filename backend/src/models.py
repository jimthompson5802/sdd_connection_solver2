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

# LLM Provider Integration Models (Phase 2)
from .llm_models.llm_provider import LLMProvider
from .llm_models.guess_attempt import GuessAttempt as PreviousGuess, GuessAttempt
from .llm_models.recommendation_request import RecommendationRequest
from .llm_models.recommendation_response import RecommendationResponse
from .llm_models.puzzle_state import PuzzleState
from .llm_models.completed_group import CompletedGroup


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
    def validate_file_content(cls, v: str) -> str:
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


class ExtractedWords(BaseModel):
    """Pydantic model for LLM structured output from image word extraction."""
    
    words: List[str] = Field(
        ..., 
        min_items=16, 
        max_items=16, 
        description="16 words from 4x4 grid in reading order"
    )
    
    @validator('words')
    def validate_word_count(cls, v: List[str]) -> List[str]:
        """Ensure exactly 16 words extracted."""
        if len(v) != 16:
            raise ValueError(f"Expected 16 words, got {len(v)}")
        return v


class ImageSetupRequest(BaseModel):
    """Request model for setting up puzzle from image."""
    
    image_base64: str = Field(
        ..., 
        description="Base64-encoded image content (without data URL prefix)"
    )
    image_mime: str = Field(
        ..., 
        description="Image MIME type (image/png, image/jpeg, image/jpg, image/gif, image/webp)"
    )
    provider_type: str = Field(
        ..., 
        description="LLM provider type for word extraction (openai, ollama, simple)"
    )
    model_name: str = Field(
        ..., 
        description="Specific model name for provider (e.g., gpt-4-vision-preview)"
    )
    
    @validator('image_base64')
    def validate_image_size(cls, v: str) -> str:
        """Validate base64 image doesn't exceed 5MB.
        
        Base64 encoding adds ~33% overhead: 5MB raw = ~6.67MB base64
        """
        max_base64_size = 6_666_666  # bytes (~5MB original)
        if len(v) > max_base64_size:
            raise ValueError("Image size exceeds 5MB limit")
        return v
    
    @validator('image_mime')
    def validate_mime_type(cls, v: str) -> str:
        """Validate image MIME type is supported."""
        supported = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']
        if v not in supported:
            raise ValueError(f"Unsupported MIME type: {v}. Supported types: {supported}")
        return v
    
    @validator('provider_type')
    def validate_provider_type(cls, v: str) -> str:
        """Validate provider type is recognized."""
        supported = ['openai', 'ollama', 'simple']
        if v not in supported:
            raise ValueError(f"Unsupported provider: {v}. Supported providers: {supported}")
        return v


class ImageSetupResponse(BaseModel):
    """Response model for image-based puzzle setup."""
    
    remaining_words: List[str] = Field(
        ..., 
        description="16 words extracted from image (or empty list on error)"
    )
    status: str = Field(
        ..., 
        description="Setup status ('success' or 'error')"
    )
    message: Optional[str] = Field(
        None, 
        description="Error message if status is 'error', None if 'success'"
    )


class NextRecommendationRequest(BaseModel):
    """Request model for getting next recommendation."""

    session_id: str = Field(..., description="Unique session identifier")

    @validator("session_id")
    def validate_session_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class RecordResponseRequest(BaseModel):
    """Request model for recording a user response."""

    response_type: str = Field(..., description="Type of response: correct, incorrect, one-away")
    color: Optional[str] = Field(None, description="Color for correct responses")
    session_id: Optional[str] = Field(None, description="Optional session id to target")
    attempt_words: Optional[List[str]] = Field(
        None, description="Optional explicit list of 4 words for the attempt (overrides last_recommendation)"
    )

    @validator("response_type")
    def validate_response_type(cls, v: str) -> str:
        valid_types = ["correct", "incorrect", "one-away"]
        if v not in valid_types:
            raise ValueError(f"response_type must be one of {valid_types}")
        return v

    @validator("color")
    def validate_color(cls, v: Optional[str], values: dict) -> Optional[str]:
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
    color: Optional[str] = None

    def __post_init__(self) -> None:
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

    def __post_init__(self) -> None:
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
        # Tracks the last recommendation issued to the user (list of 4 words)
        self.last_recommendation: Optional[List[str]] = None

    # TODO: cleanup
    #     # Initialize placeholder groups (will be populated by ML analysis)
    #     self._initialize_placeholder_groups()

    # def _initialize_placeholder_groups(self) -> None:
    #     """Initialize placeholder groups until ML analysis is implemented."""
    #     # This is a simplified placeholder - in real implementation,
    #     # this would use ML/NLP to analyze word relationships
    #     words_copy = self.words.copy()

    #     for i in range(4):
    #         group_words = words_copy[i * 4 : (i + 1) * 4]
    #         self.groups.append(WordGroup(category=f"Category {i+1}", words=group_words, difficulty=i + 1))

    def record_attempt(
        self, words: List[str], result: ResponseResult, was_recommendation: bool = False, color: Optional[str] = None
    ) -> None:
        """Record a user attempt."""
        # Normalize words for comparison
        normalized_words = [word.strip().lower() for word in words]

        # Idempotency: if an identical attempt (same word set and same result) was already recorded, ignore it
        for prev in self.attempts:
            if set(prev.words) == set(normalized_words) and prev.result == result:
                # Do not record duplicate attempts or change game state
                return

        attempt = UserAttempt(
            words=normalized_words,
            result=result,
            timestamp=datetime.now(),
            was_recommendation=was_recommendation,
        )
        self.attempts.append(attempt)

        if result == ResponseResult.CORRECT:
            self._mark_group_found(words, color=color)
        elif result in (ResponseResult.INCORRECT, ResponseResult.ONE_AWAY):
            # Count both incorrect and one-away as mistakes for game progression.
            self.mistakes_made += 1

        self._check_game_completion()

    def _mark_group_found(self, words: List[str], color: Optional[str] = None) -> None:
        """Mark a group as found based on the words and optionally record a color."""
        normalized_words = [word.strip().lower() for word in words]

        # First, try to match an existing group (placeholder or previously created)
        for group in self.groups:
            if set(group.words) == set(normalized_words):
                group.found = True
                # Persist UI color if provided
                if color:
                    group.color = color
                return

        # If we reach here, the attempt doesn't match any existing predefined group.
        # Treat this as a user-confirmed correct group and create it dynamically,
        # as long as none of these words have been found already (validated earlier in API layer).
        user_group_index = sum(1 for g in self.groups if g.category.startswith("User Group")) + 1
        new_group = WordGroup(
            category=f"User Group {user_group_index}",
            words=normalized_words,
            difficulty=1,  # default difficulty for user-confirmed groups
            found=True,
            color=color,
        )
        self.groups.append(new_group)

    def _check_game_completion(self) -> None:
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
            "attempts": self.get_invalid_word_groups(),
            "mistakes_made": self.mistakes_made,
            "groups_found": sum(1 for group in self.groups if group.found),
        }

    def get_invalid_word_groups(self) -> List[List[str]]:
        """Return up to four unique non-correct attempted groups from `self.attempts`.

        Collects attempted groups from newest to oldest whose `result` is not
        `ResponseResult.CORRECT`. Duplicate attempts (same set of words,
        order-insensitive) are collapsed, and the most recent up to four
        unique attempts are returned as lists of words in the normalized form
        stored on the attempts.

        Note: the current implementation does not filter out attempts that
        include words already present in found groups and does not perform any
        fallback chunking of remaining words.
        """
        invalid_groups: List[List[str]] = []
        seen: set = set()

        # Prefer the most recent non-correct attempts first
        for attempt in reversed(self.attempts):
            if attempt.result == ResponseResult.CORRECT:
                continue

            key = tuple(sorted(attempt.words))
            if key in seen:
                continue
            seen.add(key)
            invalid_groups.append(list(attempt.words))

            if len(invalid_groups) >= 4:
                break

        return invalid_groups


# Session storage (in-memory for now)
class SessionManager:
    """Manages puzzle sessions in memory."""

    def __init__(self) -> None:
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

    def get_last_session(self) -> Optional["PuzzleSession"]:
        """Return the most recently created session, or None if no sessions exist.

        Uses dict insertion order to locate the most recently added session.
        """
        if not self._sessions:
            return None
        return list(self._sessions.values())[-1]

    def get_last_session_id(self) -> Optional[str]:
        """Return the session_id for the most recently created session, or None."""
        last = self.get_last_session()
        return last.session_id if last else None


# Global session manager instance
session_manager = SessionManager()


# Export all models for backward compatibility and new functionality
__all__ = [
    # Original Phase 1 models
    "ResponseResult",
    "SetupPuzzleRequest",
    "NextRecommendationRequest",
    "RecordResponseRequest",
    "SetupPuzzleResponse",
    "NextRecommendationResponse",
    "RecordResponseResponse",
    "PuzzleSession",
    "SessionManager",
    "session_manager",
    # Back-compat alias for tests
    "PreviousGuess",
    # New Phase 2 LLM models
    "LLMProvider",
    "GuessAttempt",
    "RecommendationRequest",
    "RecommendationResponse",
    "PuzzleState",
    "CompletedGroup",
    # Phase 4 Image-based puzzle setup models
    "ExtractedWords",
    "ImageSetupRequest", 
    "ImageSetupResponse",
]
