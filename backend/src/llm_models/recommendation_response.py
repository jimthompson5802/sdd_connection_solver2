"""
RecommendationResponse model for LLM Provider Integration.
Represents the result from any provider with word recommendations.
"""

from pydantic import BaseModel, field_validator
from typing import List, Optional
from .llm_provider import LLMProvider


class RecommendationResponse(BaseModel):
    """Response containing word recommendations from any provider."""

    recommended_words: List[str]
    connection_explanation: Optional[str] = None
    provider_used: LLMProvider
    generation_time_ms: Optional[int] = None

    @field_validator("recommended_words")
    @classmethod
    def validate_recommended_words(cls, v: List[str]) -> List[str]:
        """Validate recommended words list."""
        if len(v) != 4:
            raise ValueError("recommended_words must contain exactly 4 words")

        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("recommended_words must not contain duplicates")

        # Clean and validate words
        cleaned_words = []
        for word in v:
            if not isinstance(word, str) or not word.strip():
                raise ValueError("all recommended words must be non-empty strings")
            cleaned_word = word.strip().lower()
            cleaned_words.append(cleaned_word)

        return cleaned_words

    @field_validator("connection_explanation")
    @classmethod
    def validate_connection_explanation(cls, v: Optional[str], info) -> Optional[str]:
        """Validate connection explanation based on provider type."""
        provider_used = info.data.get("provider_used")

        if provider_used and provider_used.provider_type == "simple":
            # Simple provider should not provide explanations
            if v is not None:
                raise ValueError("connection_explanation must be null for simple provider")
            return None

        # For LLM providers, explanation can be provided or null
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 1024:
                raise ValueError("connection_explanation cannot exceed 500 characters")

        return v

    @field_validator("generation_time_ms")
    @classmethod
    def validate_generation_time_ms(cls, v: Optional[int], info) -> Optional[int]:
        """Validate generation time."""
        provider_used = info.data.get("provider_used")

        if provider_used and provider_used.provider_type == "simple":
            # Simple provider doesn't track generation time
            if v is not None:
                raise ValueError("generation_time_ms must be null for simple provider")
            return None

        # For LLM providers, generation time can be tracked
        if v is not None:
            if not isinstance(v, int) or v < 0:
                raise ValueError("generation_time_ms must be a non-negative integer")

        return v

    def is_from_llm_provider(self) -> bool:
        """Check if this response came from an LLM provider."""
        return self.provider_used.is_llm_provider()

    def has_explanation(self) -> bool:
        """Check if this response includes a connection explanation."""
        return self.connection_explanation is not None and self.connection_explanation.strip() != ""

    def get_provider_identifier(self) -> str:
        """Get identifier for the provider that generated this response."""
        return self.provider_used.get_provider_identifier()

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "recommended_words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                    "connection_explanation": None,
                    "provider_used": {"provider_type": "simple", "model_name": None},
                    "generation_time_ms": None,
                },
                {
                    "recommended_words": ["PIANO", "GUITAR", "VIOLIN", "DRUMS"],
                    "connection_explanation": "Musical instruments",
                    "provider_used": {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
                    "generation_time_ms": 1250,
                },
                {
                    "recommended_words": ["RED", "BLUE", "GREEN", "YELLOW"],
                    "connection_explanation": "Primary and secondary colors",
                    "provider_used": {"provider_type": "ollama", "model_name": "llama2"},
                    "generation_time_ms": 3200,
                },
            ]
        }
