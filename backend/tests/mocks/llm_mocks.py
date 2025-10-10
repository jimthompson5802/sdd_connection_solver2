"""
Comprehensive LLM Provider Mocks for Testing

This module provides consistent mock responses for all LLM providers
to ensure reproducible testing across the application.
"""

from unittest.mock import Mock
from typing import Dict, Any, Optional
import json
from datetime import datetime


def create_mock_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a plain dict representing a recommendation response for tests.

    Tests now expect providers to return structured JSON-like objects (dicts).
    """
    # Keep the structure as plain data to mimic a JSON object returned by providers
    # Normalize to the RecommendationResponse schema used by the codebase/tests
    provider = response_data.get("provider_used")
    if isinstance(provider, str):
        provider = {"provider_type": provider, "model_name": response_data.get("provider_model")}

    connection_explanation = (
        response_data.get("connection_explanation")
        or response_data.get("connection")
        or response_data.get("explanation")
    )

    return {
        "recommended_words": response_data["recommended_words"],
        "connection_explanation": connection_explanation,
        "confidence_score": response_data.get("confidence_score") or response_data.get("confidence"),
        "provider_used": provider,
        "generation_time_ms": response_data.get("generation_time_ms"),
        # Include puzzle_state snapshot for tests that validate provider outputs
        "puzzle_state": response_data.get("puzzle_state", {}),
    }


# Create proper plain-dict responses for mocking providers
MOCK_RECOMMENDATION_RESPONSES = {
    "simple": create_mock_response(
        {
            "recommended_words": ["BASS", "PIKE", "SOLE", "CARP"],
            "connection_explanation": None,  # Simple provider has no explanation
            "confidence_score": 0.8,
            "provider_used": {"provider_type": "simple", "model_name": None},
            "generation_time_ms": None,  # Simple provider has no timing
        }
    ),
    "ollama": create_mock_response(
        {
            "recommended_words": ["BASS", "PIKE", "SOLE", "CARP"],
            "connection_explanation": (
                "These words are all types of fish. Bass and pike are freshwater fish "
                "commonly found in lakes and rivers, while sole and carp are also fish species."
            ),
            "confidence_score": 0.92,
            "provider_used": {"provider_type": "ollama", "model_name": "llama2"},
            "generation_time_ms": 2340,
        }
    ),
    "openai": create_mock_response(
        {
            "recommended_words": ["APPLE", "BANANA", "CHERRY", "GRAPE"],
            "connection_explanation": (
                "These are all fruits. They are common fruits that people eat "
                "and are found in grocery stores and orchards."
            ),
            "confidence_score": 0.95,
            "provider_used": {"provider_type": "openai", "model_name": "gpt-3.5-turbo"},
            "generation_time_ms": 1850,
        }
    ),
}

# Mock error responses for testing error scenarios
MOCK_ERROR_RESPONSES = {
    "network_error": {
        "error": "Connection failed",
        "detail": (
            "Failed to connect to LLM provider. Please check your network connection " "and provider configuration."
        ),
        "error_code": "NETWORK_ERROR",
    },
    "api_key_error": {
        "error": "Authentication failed",
        "detail": ("Invalid API key. Please check your OpenAI API key in the environment configuration."),
        "error_code": "AUTH_ERROR",
    },
    "model_not_found": {
        "error": "Model not available",
        "detail": "The specified model is not available. Please check the model name and try again.",
        "error_code": "MODEL_ERROR",
    },
    "timeout_error": {
        "error": "Request timeout",
        "detail": ("The LLM provider took too long to respond. Please try again or switch " "to a different provider."),
        "error_code": "TIMEOUT_ERROR",
    },
    "rate_limit_error": {
        "error": "Rate limit exceeded",
        "detail": ("Too many requests to the LLM provider. Please wait a moment before trying again."),
        "error_code": "RATE_LIMIT_ERROR",
    },
}

# Mock provider validation responses
MOCK_PROVIDER_VALIDATION = {
    "simple": {
        "provider_type": "simple",
        "is_valid": True,
        "status": "available",
        "message": "Simple provider is always available",
    },
    "ollama_valid": {
        "provider_type": "ollama",
        "is_valid": True,
        "status": "available",
        "message": "Ollama is running and model is available",
    },
    "ollama_invalid": {
        "provider_type": "ollama",
        "is_valid": False,
        "status": "not_configured",
        "message": "Ollama service is not running. Please start ollama and ensure the model is available.",
    },
    "openai_valid": {
        "provider_type": "openai",
        "is_valid": True,
        "status": "configured",
        "message": "OpenAI API key is valid and service is available",
    },
    "openai_invalid": {
        "provider_type": "openai",
        "is_valid": False,
        "status": "not_configured",
        "message": "OpenAI API key is missing or invalid. Please check your environment configuration.",
    },
}


class MockLLMProvider:
    """Base mock LLM provider for testing"""

    def __init__(self, provider_type: str, should_fail: bool = False, fail_reason: str = "network_error"):
        self.provider_type = provider_type
        self.should_fail = should_fail
        self.fail_reason = fail_reason
        self.call_count = 0

    def generate_recommendation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock recommendation generation (synchronous for test compatibility)."""
        self.call_count += 1

        if self.should_fail:
            raise Exception(MOCK_ERROR_RESPONSES[self.fail_reason]["detail"])

        return MOCK_RECOMMENDATION_RESPONSES[self.provider_type]

    def validate(self) -> Dict[str, Any]:
        """Mock provider validation (synchronous)."""
        if self.should_fail:
            return MOCK_PROVIDER_VALIDATION[f"{self.provider_type}_invalid"]
        return MOCK_PROVIDER_VALIDATION.get(f"{self.provider_type}_valid", MOCK_PROVIDER_VALIDATION["simple"])


class MockSimpleProvider(MockLLMProvider):
    """Mock simple provider (rule-based)"""

    def __init__(self, should_fail: bool = False):
        super().__init__("simple", should_fail)

    def generate_recommendation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Simple provider always returns first 4 words (synchronous)."""
        self.call_count += 1

        if self.should_fail:
            raise Exception("Simple provider internal error")

        words = request.get("remaining_words", [])[:4]
        response = MOCK_RECOMMENDATION_RESPONSES["simple"].copy()
        response["recommended_words"] = words

        return response


class MockOllamaProvider(MockLLMProvider):
    """Mock Ollama provider"""

    def __init__(self, should_fail: bool = False, fail_reason: str = "network_error"):
        super().__init__("ollama", should_fail, fail_reason)

    def generate_recommendation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock Ollama with context-aware responses (synchronous)."""
        self.call_count += 1

        if self.should_fail:
            raise Exception(MOCK_ERROR_RESPONSES[self.fail_reason]["detail"])

        # Return contextual response based on previous guesses
        previous_guesses = request.get("previous_guesses", [])
        if previous_guesses:
            # If there were previous guesses, suggest different words
            response = MOCK_RECOMMENDATION_RESPONSES["ollama"].copy()
            response["recommended_words"] = ["RED", "BLUE", "GREEN", "YELLOW"]
            response["connection_explanation"] = (
                "These are all primary and secondary colors commonly used in art and design."
            )
            response["confidence_score"] = 0.88
        else:
            response = MOCK_RECOMMENDATION_RESPONSES["ollama"].copy()

        return response


class MockOpenAIProvider(MockLLMProvider):
    """Mock OpenAI provider"""

    def __init__(self, should_fail: bool = False, fail_reason: str = "api_key_error"):
        super().__init__("openai", should_fail, fail_reason)

    def generate_recommendation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock OpenAI with high-quality responses (synchronous)."""
        self.call_count += 1

        if self.should_fail:
            raise Exception(MOCK_ERROR_RESPONSES[self.fail_reason]["detail"])

        return MOCK_RECOMMENDATION_RESPONSES["openai"]


class MockProviderFactory:
    """Mock factory for creating LLM providers during testing"""

    def __init__(self):
        self.providers = {}
        self.failure_config = {}

    def set_provider_failure(self, provider_type: str, should_fail: bool, fail_reason: str = "network_error"):
        """Configure a provider to fail for testing error scenarios"""
        self.failure_config[provider_type] = {"should_fail": should_fail, "fail_reason": fail_reason}

    def create_provider(self, provider_type: str, model_name: Optional[str] = None) -> MockLLMProvider:
        """Create a mock provider instance"""
        config = self.failure_config.get(provider_type, {"should_fail": False, "fail_reason": "network_error"})

        if provider_type == "simple":
            return MockSimpleProvider(config["should_fail"])
        elif provider_type == "ollama":
            return MockOllamaProvider(config["should_fail"], config["fail_reason"])
        elif provider_type == "openai":
            return MockOpenAIProvider(config["should_fail"], config["fail_reason"])
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")

    def reset(self):
        """Reset factory state for clean testing"""
        self.providers.clear()
        self.failure_config.clear()


def create_mock_langchain_response(provider_type: str, content: Optional[str] = None) -> Mock:
    """Create a mock langchain response object"""
    mock_response = Mock()

    if content is None:
        content = json.dumps(MOCK_RECOMMENDATION_RESPONSES[provider_type])

    mock_response.content = content
    mock_response.metadata = {"provider": provider_type, "model": "test-model", "timestamp": datetime.now().isoformat()}

    return mock_response


def create_mock_environment_config(
    has_openai_key: bool = True,
    has_ollama_url: bool = True,
    openai_key: str = "test-key-123",
    ollama_url: str = "http://localhost:11434",
) -> Dict[str, str]:
    """Create mock environment configuration for testing"""
    config = {}

    if has_openai_key:
        config["OPENAI_API_KEY"] = openai_key
        config["OPENAI_BASE_URL"] = "https://api.openai.com/v1"

    if has_ollama_url:
        config["OLLAMA_BASE_URL"] = ollama_url
        config["OLLAMA_MODEL"] = "llama2"

    config["DEBUG"] = "true"
    config["LOG_LEVEL"] = "info"

    return config


# Global mock factory instance for convenience
mock_factory = MockProviderFactory()


# Helper functions for common test scenarios
def mock_all_providers_working():
    """Configure all providers to work correctly"""
    mock_factory.reset()


def mock_ollama_down():
    """Configure Ollama to be unavailable"""
    mock_factory.set_provider_failure("ollama", True, "network_error")


def mock_openai_invalid_key():
    """Configure OpenAI with invalid API key"""
    mock_factory.set_provider_failure("openai", True, "api_key_error")


def mock_network_issues():
    """Configure all providers to have network issues"""
    mock_factory.set_provider_failure("ollama", True, "network_error")
    mock_factory.set_provider_failure("openai", True, "network_error")


def mock_rate_limits():
    """Configure providers to hit rate limits"""
    mock_factory.set_provider_failure("openai", True, "rate_limit_error")


def mock_timeouts():
    """Configure providers to timeout"""
    mock_factory.set_provider_failure("ollama", True, "timeout_error")
    mock_factory.set_provider_failure("openai", True, "timeout_error")
