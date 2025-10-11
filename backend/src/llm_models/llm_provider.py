"""
LLMProvider model for LLM Provider Integration.
Represents configuration for external AI service providers.
"""

from pydantic import BaseModel, conlist, constr, field_validator
from typing import Literal, Optional


class LLMProvider(BaseModel):
    """Configuration for LLM service providers."""

    provider_type: Literal["simple", "ollama", "openai"]
    model_name: Optional[str] = None

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: Optional[str], info) -> Optional[str]:
        """Validate model_name based on provider_type."""
        provider_type = info.data.get("provider_type")

        if provider_type == "simple":
            if v is not None:
                raise ValueError("model_name must be null for simple provider")
            return None

        if provider_type in ["ollama", "openai"]:
            if v is None or v.strip() == "":
                raise ValueError(f"model_name is required for {provider_type} provider")
            return v.strip()

        return v

    @field_validator("provider_type")
    @classmethod
    def validate_provider_type(cls, v: str) -> str:
        """Validate provider_type is supported."""
        valid_types = ["simple", "ollama", "openai"]
        if v not in valid_types:
            raise ValueError(f"provider_type must be one of: {valid_types}")
        return v

    def is_llm_provider(self) -> bool:
        """Check if this is an LLM provider (not simple)."""
        return self.provider_type != "simple"

    def requires_api_key(self) -> bool:
        """Check if this provider requires an API key."""
        return self.provider_type == "openai"

    def get_provider_identifier(self) -> str:
        """Get unique identifier for this provider configuration."""
        if self.provider_type == "simple":
            return "simple"
        return f"{self.provider_type}:{self.model_name}"

    class Config:
        """Pydantic configuration."""

        frozen = True  # Make immutable
        json_schema_extra = {
            "examples": [
                {"provider_type": "simple", "model_name": None},
                {"provider_type": "ollama", "model_name": "llama2"},
                {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
            ]
        }


"""
Pydantic model for LLM recommendation output (the JSON object produced by the prompt).
"""


class LLMRecommendationResponse(BaseModel):
    """Model representing the LLM JSON output for a Connections recommendation.

    Attributes:
        recommended_words: Exactly four words (strings) chosen from the available words.
        connection: Short connection phrase (preferably <= 6 words).
        explanation: Short paragraph explaining why the recommended_words belong together.
    """

    recommendations: conlist(str, min_length=4, max_length=4)
    connection: constr(strip_whitespace=True, min_length=1, max_length=120)
    explanation: constr(strip_whitespace=True, min_length=10, max_length=1000)

    # @field_validator("recommendations")
    # @classmethod
    # def _strip_words(cls, v: str) -> str:
    #     """Ensure words are stripped and non-empty."""
    #     s = v.strip()
    #     if not s:
    #         raise ValueError("recommended_words must contain non-empty strings")
    #     return s

    # @field_validator("connection")
    # def _validate_connection_word_count(cls, v: str) -> str:
    #     """Enforce short connection phrases (<= 6 words) as requested by the prompt."""
    #     word_count = len([w for w in v.split() if w])
    #     if word_count > 6:
    #         raise ValueError("connection should be brief (6 words or fewer)")
    #     return v

    class Config:
        """Pydantic configuration."""

        str_strip_whitespace = True
        str_min_length = 1
