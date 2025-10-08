"""
Custom exceptions for LLM Provider Integration.
"""

from typing import Optional, List, Dict, Any


class BaseApplicationError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GENERAL_ERROR"
        self.details = details or {}


class LLMProviderError(BaseApplicationError):
    """Base exception for LLM provider errors."""

    def __init__(self, message: str, provider_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider_type = provider_type


class InvalidProviderError(LLMProviderError):
    """Exception raised when an invalid or unsupported provider is requested."""

    def __init__(self, provider_type: str, available_providers: Optional[List[str]] = None):
        message = f"Invalid provider: {provider_type}"
        if available_providers:
            message += f". Available providers: {', '.join(available_providers)}"

        super().__init__(message, provider_type=provider_type, error_code="INVALID_PROVIDER")
        self.available_providers = available_providers or []


class InsufficientWordsError(BaseApplicationError):
    """Exception raised when insufficient words are provided for recommendation."""

    def __init__(self, word_count: int, required_count: int = 4):
        message = f"Insufficient words: got {word_count}, need at least {required_count}"
        super().__init__(message, error_code="INSUFFICIENT_WORDS")
        self.word_count = word_count
        self.required_count = required_count


class ConfigurationError(BaseApplicationError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key


class TimeoutError(LLMProviderError):
    """Exception raised when LLM provider operations timeout."""

    def __init__(self, provider_type: str, timeout_seconds: int):
        message = f"Operation timed out after {timeout_seconds} seconds"
        super().__init__(message, provider_type=provider_type, error_code="TIMEOUT_ERROR")
        self.timeout_seconds = timeout_seconds


class OllamaConnectionError(LLMProviderError):
    """Exception raised for Ollama connection issues."""

    def __init__(self, base_url: str, error_details: Optional[str] = None):
        message = f"Failed to connect to Ollama at {base_url}"
        if error_details:
            message += f": {error_details}"

        super().__init__(message, provider_type="ollama", error_code="OLLAMA_CONNECTION_ERROR")
        self.base_url = base_url


class OpenAIAPIError(LLMProviderError):
    """Exception raised for OpenAI API issues."""

    def __init__(self, error_details: str, api_key_valid: Optional[bool] = None):
        message = f"OpenAI API error: {error_details}"
        super().__init__(message, provider_type="openai", error_code="OPENAI_API_ERROR")
        self.api_key_valid = api_key_valid


class SimpleProviderError(LLMProviderError):
    """Exception raised for simple provider issues."""

    def __init__(self, error_details: str):
        message = f"Simple provider error: {error_details}"
        super().__init__(message, provider_type="simple", error_code="SIMPLE_PROVIDER_ERROR")


class ValidationError(BaseApplicationError):
    """Exception raised for response validation errors."""

    def __init__(self, validation_errors: List[str], response_data: Optional[Dict[str, Any]] = None):
        message = f"Validation failed: {'; '.join(validation_errors)}"
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.validation_errors = validation_errors
        self.response_data = response_data or {}


class PromptGenerationError(BaseApplicationError):
    """Exception raised for prompt generation errors."""

    def __init__(self, error_details: str, prompt_type: Optional[str] = None):
        message = f"Prompt generation failed: {error_details}"
        super().__init__(message, error_code="PROMPT_GENERATION_ERROR")
        self.prompt_type = prompt_type


class InvalidInputError(BaseApplicationError):
    """Exception raised for invalid user input scenarios."""

    def __init__(self, message: str, error_code: str = "INVALID_INPUT"):
        super().__init__(message, error_code=error_code)
