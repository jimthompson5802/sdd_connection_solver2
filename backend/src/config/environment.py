"""
Environment configuration loader for LLM Provider Integration.
Handles loading and validation of environment variables.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class EnvironmentLoader:
    """Loader for environment configuration and variables."""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize environment loader.

        Args:
            env_file: Path to .env file. Defaults to .env in current directory.
        """
        self.env_file = env_file or ".env"
        self._load_env_file()

    def _load_env_file(self) -> None:
        """Load environment variables from .env file if it exists."""
        if os.path.exists(self.env_file):
            load_dotenv(self.env_file)

    def load_openai_config(self) -> Dict[str, Any]:
        """Load OpenAI configuration from environment variables.

        Returns:
            Dictionary with OpenAI configuration.
        """
        config = {}

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            config["api_key"] = api_key
            config["model_name"] = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
            config["timeout"] = int(os.getenv("OPENAI_TIMEOUT", "300"))

        return config

    def load_ollama_config(self) -> Dict[str, Any]:
        """Load Ollama configuration from environment variables.

        Returns:
            Dictionary with Ollama configuration.
        """
        config = {}

        base_url = os.getenv("OLLAMA_BASE_URL")
        if base_url:
            config["base_url"] = base_url
            config["model_name"] = os.getenv("OLLAMA_MODEL_NAME", "qwen2.5:32b")
            config["timeout"] = int(os.getenv("OLLAMA_TIMEOUT", "300"))
        return config

    def load_application_config(self) -> Dict[str, Any]:
        """Load application configuration from environment variables.

        Returns:
            Dictionary with application configuration.
        """
        return {
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "cors_origins": os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        }

    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable value.

        Args:
            key: Environment variable name.
            default: Default value if variable not found.

        Returns:
            Environment variable value or default.
        """
        return os.getenv(key, default)

    def validate_required_vars(self, required_vars: list[str]) -> Dict[str, bool]:
        """Validate that required environment variables are set.

        Args:
            required_vars: List of required variable names.

        Returns:
            Dictionary mapping variable names to whether they're set.
        """
        return {var: os.getenv(var) is not None for var in required_vars}

    def get_all_env_vars(self) -> Dict[str, str]:
        """Get all environment variables (for debugging purposes).

        Returns:
            Dictionary of all environment variables.
        """
        return dict(os.environ)

    def get_safe_env_vars(self) -> Dict[str, str]:
        """Get environment variables excluding sensitive ones for safe logging.

        Returns:
            Dictionary of environment variables with sensitive ones excluded.
        """
        all_vars = dict(os.environ)
        sensitive_keywords = ["key", "secret", "password", "token", "api", "auth", "credential"]

        return {
            k: v for k, v in all_vars.items() if not any(sensitive in k.lower() for sensitive in sensitive_keywords)
        }

    def mask_sensitive_vars(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive environment variables for safe logging.

        Args:
            env_vars: Dictionary of environment variables.

        Returns:
            Dictionary with sensitive values masked.
        """
        sensitive_keywords = ["key", "secret", "password", "token", "api", "auth", "credential"]
        masked_vars = {}

        for key, value in env_vars.items():
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in sensitive_keywords):
                if value:
                    # Show only first 2 chars for values > 8 chars, otherwise mask completely
                    if len(value) > 8:
                        masked_vars[key] = value[:2] + "*" * 6 + "..."
                    else:
                        masked_vars[key] = "****"
                else:
                    masked_vars[key] = "[EMPTY]"
            else:
                masked_vars[key] = value

        return masked_vars
