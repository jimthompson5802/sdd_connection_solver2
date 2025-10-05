"""
LLMProvider model for LLM Provider Integration.
Represents configuration for external AI service providers.
"""

from pydantic import BaseModel, field_validator
from typing import Literal, Optional


class LLMProvider(BaseModel):
    """Configuration for LLM service providers."""
    
    provider_type: Literal["simple", "ollama", "openai"]
    model_name: Optional[str] = None
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: Optional[str], info) -> Optional[str]:
        """Validate model_name based on provider_type."""
        provider_type = info.data.get('provider_type')
        
        if provider_type == "simple":
            if v is not None:
                raise ValueError("model_name must be null for simple provider")
            return None
        
        if provider_type in ["ollama", "openai"]:
            if v is None or v.strip() == "":
                raise ValueError(f"model_name is required for {provider_type} provider")
            return v.strip()
        
        return v
    
    @field_validator('provider_type')
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
                {
                    "provider_type": "simple",
                    "model_name": None
                },
                {
                    "provider_type": "ollama",
                    "model_name": "llama2"
                },
                {
                    "provider_type": "openai",
                    "model_name": "gpt-3.5-turbo"
                }
            ]
        }