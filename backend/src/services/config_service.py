"""
Configuration service for LLM Provider Integration.
Handles loading and validation of environment variables and application settings.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv


class OpenAIConfig(BaseModel):
    """Configuration for OpenAI provider."""

    api_key: str
    model_name: str = "gpt-4o-mini"
    timeout: int = 300


class OllamaConfig(BaseModel):
    """Configuration for Ollama provider."""

    base_url: str = "http://localhost:11434"
    model_name: str = "llama2"
    timeout: int = 300


class ApplicationConfig(BaseModel):
    """Application-wide configuration."""

    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]


class ConfigurationService:
    """Service for loading and managing application configuration."""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration service.

        Args:
            env_file: Path to .env file. If None, uses default .env location.
        """
        self._env_file = env_file or ".env"
        self._config_cache: Dict[str, Any] = {}
        self._load_environment()

    def _load_environment(self) -> None:
        """Load environment variables from .env file."""
        if os.path.exists(self._env_file):
            load_dotenv(self._env_file)

    def load_configuration(self) -> Dict[str, Any]:
        """Load complete application configuration.

        Returns:
            Dictionary containing all configuration sections.
        """
        if "full_config" in self._config_cache:
            return self._config_cache["full_config"]

        config = {
            "openai": self._load_openai_config(),
            "ollama": self._load_ollama_config(),
            "application": self._load_application_config(),
        }

        self._config_cache["full_config"] = config
        return config

    def _load_openai_config(self) -> Optional[OpenAIConfig]:
        """Load OpenAI configuration from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        return OpenAIConfig(
            api_key=api_key,
            model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            timeout=int(os.getenv("OPENAI_TIMEOUT", "300")),
        )

    def _load_ollama_config(self) -> Optional[OllamaConfig]:
        """Load Ollama configuration from environment."""
        base_url = os.getenv("OLLAMA_BASE_URL")
        if not base_url:
            return None

        return OllamaConfig(
            base_url=base_url,
            model_name=os.getenv("OLLAMA_MODEL_NAME", "llama2"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "300")),
        )

    def _load_application_config(self) -> ApplicationConfig:
        """Load application configuration from environment."""
        return ApplicationConfig(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        )

    def validate_providers(self) -> Dict[str, bool]:
        """Validate which providers are properly configured.

        Returns:
            Dictionary mapping provider names to availability status.
        """
        config = self.load_configuration()

        return {
            "simple": True,  # Simple provider always available
            "openai": config["openai"] is not None,
            "ollama": config["ollama"] is not None,
        }

    def get_provider_config(self, provider_type: str) -> Optional[Any]:
        """Get configuration for specific provider.

        Args:
            provider_type: Type of provider (openai, ollama, simple).

        Returns:
            Provider configuration or None if not available.
        """
        if provider_type == "simple":
            return {}  # Simple provider needs no configuration

        config = self.load_configuration()
        return config.get(provider_type)

    def clear_cache(self) -> None:
        """Clear configuration cache to force reload."""
        self._config_cache.clear()


# Global configuration service instance
_config_service: Optional[ConfigurationService] = None


def get_config_service() -> ConfigurationService:
    """Get global configuration service instance."""
    global _config_service
    if _config_service is None:
        _config_service = ConfigurationService()
    return _config_service
