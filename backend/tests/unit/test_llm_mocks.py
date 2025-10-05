"""
Unit tests for LLM provider mocks

Tests that verify the mock LLM providers work correctly and provide
consistent responses for testing scenarios.
"""

import pytest
from tests.mocks.llm_mocks import (
    MockLLMProvider,
    MockSimpleProvider,
    MockOllamaProvider,
    MockOpenAIProvider,
    MockProviderFactory,
    MOCK_RECOMMENDATION_RESPONSES,
    MOCK_ERROR_RESPONSES,
    MOCK_PROVIDER_VALIDATION,
    mock_factory,
    mock_all_providers_working,
    mock_ollama_down,
    mock_openai_invalid_key,
    mock_network_issues,
    mock_rate_limits,
    mock_timeouts,
    create_mock_langchain_response,
    create_mock_environment_config,
)


class TestMockLLMProvider:
    """Test base mock LLM provider functionality"""

    def test_mock_provider_initialization(self):
        """Test basic provider initialization"""
        provider = MockLLMProvider("simple")

        assert provider.provider_type == "simple"
        assert provider.should_fail is False
        assert provider.fail_reason == "network_error"
        assert provider.call_count == 0

    def test_mock_provider_failure_configuration(self):
        """Test configuring provider to fail"""
        provider = MockLLMProvider("ollama", should_fail=True, fail_reason="timeout_error")

        assert provider.should_fail is True
        assert provider.fail_reason == "timeout_error"

    @pytest.mark.asyncio
    async def test_mock_provider_validation_success(self):
        """Test provider validation when working"""
        provider = MockLLMProvider("simple")
        validation = await provider.validate()

        assert validation["is_valid"] is True
        assert validation["provider_type"] == "simple"

    @pytest.mark.asyncio
    async def test_mock_provider_validation_failure(self):
        """Test provider validation when failing"""
        provider = MockLLMProvider("ollama", should_fail=True)
        validation = await provider.validate()

        assert validation["is_valid"] is False
        assert validation["provider_type"] == "ollama"


class TestMockSimpleProvider:
    """Test simple provider mock"""

    @pytest.mark.asyncio
    async def test_simple_provider_recommendation(self):
        """Test simple provider generates recommendations"""
        provider = MockSimpleProvider()
        request = {
            "remaining_words": ["BASS", "PIKE", "SOLE", "CARP", "APPLE", "BANANA", "CHERRY", "GRAPE"],
            "previous_guesses": [],
        }

        response = await provider.generate_recommendation(request)

        assert response["recommended_words"] == ["BASS", "PIKE", "SOLE", "CARP"]
        assert response["provider_used"] == "simple"
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_simple_provider_failure(self):
        """Test simple provider configured to fail"""
        provider = MockSimpleProvider(should_fail=True)
        request = {"remaining_words": ["TEST"]}

        with pytest.raises(Exception) as exc_info:
            await provider.generate_recommendation(request)

        assert "Simple provider internal error" in str(exc_info.value)


class TestMockOllamaProvider:
    """Test Ollama provider mock"""

    @pytest.mark.asyncio
    async def test_ollama_provider_recommendation(self):
        """Test Ollama provider generates recommendations"""
        provider = MockOllamaProvider()
        request = {"words": ["BASS", "PIKE", "SOLE", "CARP"], "previous_guesses": []}

        response = await provider.generate_recommendation(request)

        assert response["recommended_words"] == ["BASS", "PIKE", "SOLE", "CARP"]
        assert response["provider_used"] == "ollama"
        assert response["generation_time_ms"] == 2340
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_ollama_provider_contextual_response(self):
        """Test Ollama provider gives different response with previous guesses"""
        provider = MockOllamaProvider()
        request = {"words": ["BASS", "PIKE", "SOLE", "CARP"], "previous_guesses": [["WRONG", "GUESS", "HERE", "TOO"]]}

        response = await provider.generate_recommendation(request)

        assert response["recommended_words"] == ["RED", "BLUE", "GREEN", "YELLOW"]
        assert "colors" in response["connection_explanation"]

    @pytest.mark.asyncio
    async def test_ollama_provider_timeout(self):
        """Test Ollama provider timeout scenario"""
        provider = MockOllamaProvider(should_fail=True, fail_reason="timeout_error")
        request = {"words": ["TEST"]}

        with pytest.raises(Exception) as exc_info:
            await provider.generate_recommendation(request)

        assert "took too long to respond" in str(exc_info.value)


class TestMockOpenAIProvider:
    """Test OpenAI provider mock"""

    @pytest.mark.asyncio
    async def test_openai_provider_recommendation(self):
        """Test OpenAI provider generates recommendations"""
        provider = MockOpenAIProvider()
        request = {"words": ["APPLE", "BANANA", "CHERRY", "GRAPE"], "previous_guesses": []}

        response = await provider.generate_recommendation(request)

        assert response["recommended_words"] == ["APPLE", "BANANA", "CHERRY", "GRAPE"]
        assert response["provider_used"] == "openai"
        assert response["confidence_score"] == 0.95
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_openai_provider_api_key_error(self):
        """Test OpenAI provider with invalid API key"""
        provider = MockOpenAIProvider(should_fail=True, fail_reason="api_key_error")
        request = {"words": ["TEST"]}

        with pytest.raises(Exception) as exc_info:
            await provider.generate_recommendation(request)

        assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_openai_provider_rate_limit(self):
        """Test OpenAI provider rate limit scenario"""
        provider = MockOpenAIProvider(should_fail=True, fail_reason="rate_limit_error")
        request = {"words": ["TEST"]}

        with pytest.raises(Exception) as exc_info:
            await provider.generate_recommendation(request)

        assert "Too many requests" in str(exc_info.value)


class TestMockProviderFactory:
    """Test mock provider factory"""

    def test_factory_create_provider(self):
        """Test factory creates correct provider types"""
        factory = MockProviderFactory()

        simple_provider = factory.create_provider("simple")
        assert isinstance(simple_provider, MockSimpleProvider)

        ollama_provider = factory.create_provider("ollama")
        assert isinstance(ollama_provider, MockOllamaProvider)

        openai_provider = factory.create_provider("openai")
        assert isinstance(openai_provider, MockOpenAIProvider)

    def test_factory_failure_configuration(self):
        """Test factory configures provider failures"""
        factory = MockProviderFactory()
        factory.set_provider_failure("ollama", True, "timeout_error")

        provider = factory.create_provider("ollama")
        assert provider.should_fail is True
        assert provider.fail_reason == "timeout_error"

    def test_factory_reset(self):
        """Test factory reset functionality"""
        factory = MockProviderFactory()
        factory.set_provider_failure("openai", True, "api_key_error")

        factory.reset()
        provider = factory.create_provider("openai")
        assert provider.should_fail is False


class TestMockHelperFunctions:
    """Test mock helper functions"""

    def test_mock_all_providers_working(self):
        """Test configuring all providers to work"""
        mock_all_providers_working()

        simple_provider = mock_factory.create_provider("simple")
        ollama_provider = mock_factory.create_provider("ollama")
        openai_provider = mock_factory.create_provider("openai")

        assert simple_provider.should_fail is False
        assert ollama_provider.should_fail is False
        assert openai_provider.should_fail is False

    def test_mock_ollama_down(self):
        """Test configuring Ollama as down"""
        mock_ollama_down()

        provider = mock_factory.create_provider("ollama")
        assert provider.should_fail is True
        assert provider.fail_reason == "network_error"

    def test_mock_openai_invalid_key(self):
        """Test configuring OpenAI with invalid key"""
        mock_openai_invalid_key()

        provider = mock_factory.create_provider("openai")
        assert provider.should_fail is True
        assert provider.fail_reason == "api_key_error"

    def test_mock_network_issues(self):
        """Test configuring network issues for all providers"""
        mock_network_issues()

        ollama_provider = mock_factory.create_provider("ollama")
        openai_provider = mock_factory.create_provider("openai")

        assert ollama_provider.should_fail is True
        assert openai_provider.should_fail is True
        assert ollama_provider.fail_reason == "network_error"
        assert openai_provider.fail_reason == "network_error"

    def test_mock_rate_limits(self):
        """Test configuring rate limits"""
        mock_rate_limits()

        provider = mock_factory.create_provider("openai")
        assert provider.should_fail is True
        assert provider.fail_reason == "rate_limit_error"

    def test_mock_timeouts(self):
        """Test configuring timeouts"""
        mock_timeouts()

        ollama_provider = mock_factory.create_provider("ollama")
        openai_provider = mock_factory.create_provider("openai")

        assert ollama_provider.should_fail is True
        assert openai_provider.should_fail is True
        assert ollama_provider.fail_reason == "timeout_error"
        assert openai_provider.fail_reason == "timeout_error"


class TestMockUtilityFunctions:
    """Test mock utility functions"""

    def test_create_mock_langchain_response(self):
        """Test creating mock langchain response"""
        response = create_mock_langchain_response("simple")

        assert hasattr(response, "content")
        assert hasattr(response, "metadata")
        assert response.metadata["provider"] == "simple"

    def test_create_mock_langchain_response_with_content(self):
        """Test creating mock langchain response with custom content"""
        custom_content = '{"test": "data"}'
        response = create_mock_langchain_response("ollama", custom_content)

        assert response.content == custom_content
        assert response.metadata["provider"] == "ollama"

    def test_create_mock_environment_config_full(self):
        """Test creating full mock environment config"""
        config = create_mock_environment_config()

        assert "OPENAI_API_KEY" in config
        assert "OLLAMA_BASE_URL" in config
        assert config["OPENAI_API_KEY"] == "test-key-123"
        assert config["OLLAMA_BASE_URL"] == "http://localhost:11434"

    def test_create_mock_environment_config_partial(self):
        """Test creating partial mock environment config"""
        config = create_mock_environment_config(has_openai_key=False)

        assert "OPENAI_API_KEY" not in config
        assert "OLLAMA_BASE_URL" in config

    def test_create_mock_environment_config_custom_values(self):
        """Test creating mock environment config with custom values"""
        config = create_mock_environment_config(openai_key="custom-key", ollama_url="http://custom:8080")

        assert config["OPENAI_API_KEY"] == "custom-key"
        assert config["OLLAMA_BASE_URL"] == "http://custom:8080"


class TestMockDataConsistency:
    """Test mock data consistency"""

    def test_mock_responses_structure(self):
        """Test that all mock responses have consistent structure"""
        for provider_type, response in MOCK_RECOMMENDATION_RESPONSES.items():
            assert "recommended_words" in response
            assert "connection_explanation" in response
            assert "confidence_score" in response
            assert "provider_used" in response
            assert "puzzle_state" in response
            assert "alternative_suggestions" in response

            # Check puzzle state structure
            puzzle_state = response["puzzle_state"]
            assert "remaining_words" in puzzle_state
            assert "completed_groups" in puzzle_state
            assert "total_mistakes" in puzzle_state
            assert "max_mistakes" in puzzle_state
            assert "game_status" in puzzle_state

    def test_error_responses_structure(self):
        """Test that all error responses have consistent structure"""
        for error_type, error in MOCK_ERROR_RESPONSES.items():
            assert "error" in error
            assert "detail" in error
            assert "error_code" in error

    def test_provider_validation_structure(self):
        """Test that all provider validations have consistent structure"""
        for validation_key, validation in MOCK_PROVIDER_VALIDATION.items():
            assert "provider_type" in validation
            assert "is_valid" in validation
            assert "status" in validation
            assert "message" in validation
