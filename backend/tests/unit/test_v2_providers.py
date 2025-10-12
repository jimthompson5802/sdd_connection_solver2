"""
Unit tests for the v2 providers API endpoints.
Tests provider validation and status functionality.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.v2_providers import (
    router,
    validate_provider,
    get_providers_status,
    _validate_openai_provider,
    _validate_ollama_provider,
    ProviderValidationRequest,
    ProviderValidationResponse,
)
from src.exceptions import InvalidProviderError, ConfigurationError, LLMProviderError


@pytest.fixture
def app():
    """Create FastAPI app with router for testing."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_request():
    """Create mock FastAPI request object."""
    request = Mock()
    request.client = Mock()
    request.client.host = "127.0.0.1"
    request.url = Mock()
    request.url.path = "/api/v2/providers/validate"
    return request


@pytest.fixture
def mock_config_service():
    """Create mock configuration service."""
    with patch('src.api.v2_providers.ConfigurationService') as mock_service:
        yield mock_service


@pytest.fixture
def mock_llm_provider_factory():
    """Create mock LLM provider factory."""
    with patch('src.api.v2_providers.LLMProviderFactory') as mock_factory:
        yield mock_factory


@pytest.fixture
def mock_log_request_info():
    """Mock the log_request_info function."""
    with patch('src.api.v2_providers.log_request_info') as mock_log:
        yield mock_log


class TestValidateProvider:
    """Test cases for the validate_provider endpoint."""

    @pytest.mark.asyncio
    async def test_validate_simple_provider_success(self, mock_request, mock_log_request_info):
        """Test validation of simple provider (always valid)."""
        request_data = ProviderValidationRequest(provider_type="simple")
        
        result = await validate_provider(request_data, mock_request)
        
        assert result.provider_type == "simple"
        assert result.is_valid is True
        assert result.status == "available"
        assert "always available" in result.message
        mock_log_request_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_invalid_provider_type(self, mock_request):
        """Test validation with invalid provider type."""
        request_data = ProviderValidationRequest(provider_type="invalid_provider")
        
        result = await validate_provider(request_data, mock_request)
        
        assert result.provider_type == "invalid_provider"
        assert result.is_valid is False
        assert result.status == "invalid"
        assert "Unknown provider type" in result.message
        assert "valid_providers" in result.details

    @pytest.mark.asyncio
    @patch('src.api.v2_providers._validate_openai_provider')
    async def test_validate_openai_provider_called(self, mock_validate_openai, mock_request, mock_config_service):
        """Test that OpenAI validation function is called for openai provider."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key="sk-test123")
        expected_response = ProviderValidationResponse(
            provider_type="openai",
            is_valid=True,
            status="available",
            message="OpenAI provider configuration is valid"
        )
        mock_validate_openai.return_value = expected_response
        
        result = await validate_provider(request_data, mock_request)
        
        mock_validate_openai.assert_called_once()
        assert result == expected_response

    @pytest.mark.asyncio
    @patch('src.api.v2_providers._validate_ollama_provider')
    async def test_validate_ollama_provider_called(self, mock_validate_ollama, mock_request, mock_config_service):
        """Test that Ollama validation function is called for ollama provider."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url="http://localhost:11434")
        expected_response = ProviderValidationResponse(
            provider_type="ollama",
            is_valid=True,
            status="available",
            message="Ollama provider configuration is valid"
        )
        mock_validate_ollama.return_value = expected_response
        
        result = await validate_provider(request_data, mock_request)
        
        mock_validate_ollama.assert_called_once()
        assert result == expected_response

    @pytest.mark.asyncio
    async def test_validate_provider_invalid_provider_error(self, mock_request, mock_config_service):
        """Test handling of InvalidProviderError."""
        request_data = ProviderValidationRequest(provider_type="openai")
        
        with patch('src.api.v2_providers._validate_openai_provider') as mock_validate:
            mock_validate.side_effect = InvalidProviderError("Invalid provider", "INVALID_PROVIDER")
            
            with pytest.raises(HTTPException) as exc_info:
                await validate_provider(request_data, mock_request)
            
            assert exc_info.value.status_code == 400
            assert "Invalid Provider" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_provider_configuration_error(self, mock_request, mock_config_service):
        """Test handling of ConfigurationError."""
        request_data = ProviderValidationRequest(provider_type="openai")
        
        with patch('src.api.v2_providers._validate_openai_provider') as mock_validate:
            mock_validate.side_effect = ConfigurationError("Config error", "CONFIG_ERROR")
            
            with pytest.raises(HTTPException) as exc_info:
                await validate_provider(request_data, mock_request)
            
            assert exc_info.value.status_code == 500
            assert "Configuration Error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_validate_provider_unexpected_error(self, mock_request, mock_config_service):
        """Test handling of unexpected errors."""
        request_data = ProviderValidationRequest(provider_type="openai")
        
        with patch('src.api.v2_providers._validate_openai_provider') as mock_validate:
            mock_validate.side_effect = Exception("Unexpected error")
            
            with pytest.raises(HTTPException) as exc_info:
                await validate_provider(request_data, mock_request)
            
            assert exc_info.value.status_code == 500
            assert "Internal Server Error" in str(exc_info.value.detail)


class TestValidateOpenAIProvider:
    """Test cases for OpenAI provider validation."""

    @pytest.mark.asyncio
    async def test_validate_openai_with_valid_api_key_in_request(self, mock_config_service, mock_llm_provider_factory):
        """Test OpenAI validation with valid API key in request."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key="sk-valid123456789")
        config_service_instance = mock_config_service.return_value
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.provider_type == "openai"
        assert result.is_valid is True
        assert result.status == "available"
        assert "configuration is valid" in result.message
        factory_instance.create_provider.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_openai_with_api_key_from_config(self, mock_config_service, mock_llm_provider_factory):
        """Test OpenAI validation with API key from configuration."""
        request_data = ProviderValidationRequest(provider_type="openai")
        config_service_instance = mock_config_service.return_value
        
        # Mock config with valid API key
        mock_openai_config = Mock()
        mock_openai_config.api_key = "sk-config123456789"
        config_service_instance.get_provider_config.return_value = mock_openai_config
        
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.provider_type == "openai"
        assert result.is_valid is True
        assert result.status == "available"
        config_service_instance.get_provider_config.assert_called_with("openai")

    @pytest.mark.asyncio
    async def test_validate_openai_no_api_key_available(self, mock_config_service):
        """Test OpenAI validation when no API key is available."""
        request_data = ProviderValidationRequest(provider_type="openai")
        config_service_instance = mock_config_service.return_value
        config_service_instance.get_provider_config.side_effect = Exception("No config")
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.provider_type == "openai"
        assert result.is_valid is False
        assert result.status == "configuration_missing"
        assert "API key not provided" in result.message

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_key", [
        "",
        "short",
        "pk-invalid123456789",  # Wrong prefix
        "sk-",  # Too short
        None
    ])
    async def test_validate_openai_invalid_api_key_format(self, invalid_key, mock_config_service):
        """Test OpenAI validation with invalid API key formats."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key=invalid_key)
        config_service_instance = mock_config_service.return_value
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.provider_type == "openai"
        assert result.is_valid is False
        assert result.status == "invalid_credentials"
        assert "Invalid OpenAI API key format" in result.message

    @pytest.mark.asyncio
    async def test_validate_openai_provider_creation_error(self, mock_config_service, mock_llm_provider_factory):
        """Test OpenAI validation when provider creation fails."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key="sk-valid123456789")
        config_service_instance = mock_config_service.return_value
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.side_effect = LLMProviderError("Provider failed", "PROVIDER_ERROR")
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.provider_type == "openai"
        assert result.is_valid is False
        assert result.status == "provider_error"
        assert "Failed to initialize OpenAI provider" in result.message

    @pytest.mark.asyncio
    async def test_validate_openai_unexpected_error(self, mock_config_service):
        """Test OpenAI validation with unexpected error."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key="sk-valid123456789")
        config_service_instance = mock_config_service.return_value
        
        with patch('src.api.v2_providers.LLMProviderFactory') as mock_factory:
            mock_factory.side_effect = Exception("Unexpected error")
            
            result = await _validate_openai_provider(request_data, config_service_instance)
            
            assert result.provider_type == "openai"
            assert result.is_valid is False
            assert result.status == "validation_error"
            assert "Failed to validate OpenAI provider" in result.message


class TestValidateOllamaProvider:
    """Test cases for Ollama provider validation."""

    @pytest.mark.asyncio
    async def test_validate_ollama_with_valid_base_url_in_request(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation with valid base URL in request."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url="http://localhost:11434")
        config_service_instance = mock_config_service.return_value
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is True
        assert result.status == "available"
        assert "configuration is valid" in result.message
        assert result.details["base_url"] == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_validate_ollama_with_base_url_from_config(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation with base URL from configuration."""
        request_data = ProviderValidationRequest(provider_type="ollama")
        config_service_instance = mock_config_service.return_value
        
        # Mock config with base URL
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = "https://custom-ollama.example.com"
        config_service_instance.get_provider_config.return_value = mock_ollama_config
        
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is True
        assert result.details["base_url"] == "https://custom-ollama.example.com"

    @pytest.mark.asyncio
    async def test_validate_ollama_default_url_when_no_config(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation falls back to default URL when no config available."""
        request_data = ProviderValidationRequest(provider_type="ollama")
        config_service_instance = mock_config_service.return_value
        config_service_instance.get_provider_config.side_effect = Exception("No config")
        
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is True
        assert result.details["base_url"] == "http://localhost:11434"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_url", [
        "localhost:11434",  # Missing protocol
        "ftp://localhost:11434",  # Wrong protocol
        "invalid-url",
    ])
    async def test_validate_ollama_invalid_base_url_format(self, invalid_url, mock_config_service):
        """Test Ollama validation with invalid base URL formats."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url=invalid_url)
        config_service_instance = mock_config_service.return_value
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is False
        assert result.status == "invalid_url"
        assert "Invalid Ollama base URL format" in result.message

    @pytest.mark.asyncio
    @pytest.mark.parametrize("fallback_url", ["", None])
    async def test_validate_ollama_fallback_to_config_or_default(
        self, fallback_url, mock_config_service, mock_llm_provider_factory
    ):
        """Test Ollama validation falls back to config when request URL is empty/None."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url=fallback_url)
        config_service_instance = mock_config_service.return_value
        
        # Mock config with valid base URL
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = "http://custom:11434"
        config_service_instance.get_provider_config.return_value = mock_ollama_config
        
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is True
        assert result.details["base_url"] == "http://custom:11434"

    @pytest.mark.asyncio
    async def test_validate_ollama_provider_creation_error(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation when provider creation fails."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url="http://localhost:11434")
        config_service_instance = mock_config_service.return_value
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.side_effect = LLMProviderError("Connection failed", "CONNECTION_ERROR")
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        assert result.provider_type == "ollama"
        assert result.is_valid is False
        assert result.status == "provider_error"
        assert "Failed to initialize Ollama provider" in result.message
        assert result.details["error_code"] == "GENERAL_ERROR"

    @pytest.mark.asyncio
    async def test_validate_ollama_unexpected_error(self, mock_config_service):
        """Test Ollama validation with unexpected error."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url="http://localhost:11434")
        config_service_instance = mock_config_service.return_value
        
        with patch('src.api.v2_providers.LLMProviderFactory') as mock_factory:
            mock_factory.side_effect = Exception("Unexpected error")
            
            result = await _validate_ollama_provider(request_data, config_service_instance)
            
            assert result.provider_type == "ollama"
            assert result.is_valid is False
            assert result.status == "validation_error"
            assert "Failed to validate Ollama provider" in result.message


class TestGetProvidersStatus:
    """Test cases for the get_providers_status endpoint."""

    @pytest.mark.asyncio
    async def test_get_providers_status_all_configured(self, mock_request, mock_config_service, mock_log_request_info):
        """Test getting providers status when all are configured."""
        config_service_instance = mock_config_service.return_value
        
        # Mock OpenAI config
        mock_openai_config = Mock()
        mock_openai_config.api_key = "sk-test123"
        
        # Mock Ollama config
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = "http://localhost:11434"
        
        config_service_instance.get_provider_config.side_effect = [
            mock_openai_config,  # First call for OpenAI
            mock_ollama_config   # Second call for Ollama
        ]
        
        result = await get_providers_status(mock_request)
        
        assert "providers" in result
        assert "simple" in result["providers"]
        assert "openai" in result["providers"]
        assert "ollama" in result["providers"]
        
        assert result["providers"]["simple"]["status"] == "available"
        assert result["providers"]["openai"]["status"] == "configured"
        assert result["providers"]["ollama"]["status"] == "configured"
        
        assert result["total_count"] == 3
        assert result["available_count"] == 3
        
        mock_log_request_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_providers_status_openai_not_configured(
        self, mock_request, mock_config_service, mock_log_request_info
    ):
        """Test getting providers status when OpenAI is not configured."""
        config_service_instance = mock_config_service.return_value
        
        # Mock Ollama config
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = "http://localhost:11434"
        
        config_service_instance.get_provider_config.side_effect = [
            Exception("No OpenAI config"),  # First call for OpenAI fails
            mock_ollama_config              # Second call for Ollama succeeds
        ]
        
        result = await get_providers_status(mock_request)
        
        assert result["providers"]["openai"]["status"] == "not_configured"
        assert "API key not configured" in result["providers"]["openai"]["message"]
        assert result["providers"]["ollama"]["status"] == "configured"
        assert result["available_count"] == 2  # simple + ollama

    @pytest.mark.asyncio
    async def test_get_providers_status_ollama_default_config(
        self, mock_request, mock_config_service, mock_log_request_info
    ):
        """Test getting providers status when Ollama uses default config."""
        config_service_instance = mock_config_service.return_value
        
        # Mock OpenAI config
        mock_openai_config = Mock()
        mock_openai_config.api_key = "sk-test123"
        
        config_service_instance.get_provider_config.side_effect = [
            mock_openai_config,             # First call for OpenAI succeeds
            None                            # Second call for Ollama returns None
        ]
        
        result = await get_providers_status(mock_request)
        
        assert result["providers"]["openai"]["status"] == "configured"
        assert result["providers"]["ollama"]["status"] == "default_config"
        assert "default Ollama configuration" in result["providers"]["ollama"]["message"]

    @pytest.mark.asyncio
    async def test_get_providers_status_ollama_exception_fallback(
        self, mock_request, mock_config_service, mock_log_request_info
    ):
        """Test getting providers status when Ollama config check raises exception."""
        config_service_instance = mock_config_service.return_value
        
        config_service_instance.get_provider_config.side_effect = [
            Exception("No OpenAI config"),  # First call for OpenAI fails
            Exception("Ollama config error")  # Second call for Ollama fails
        ]
        
        result = await get_providers_status(mock_request)
        
        assert result["providers"]["ollama"]["status"] == "default_config"
        assert "default Ollama configuration" in result["providers"]["ollama"]["message"]

    @pytest.mark.asyncio
    async def test_get_providers_status_unexpected_error(self, mock_request, mock_config_service):
        """Test get_providers_status with unexpected error."""
        mock_config_service.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_providers_status(mock_request)
        
        assert exc_info.value.status_code == 500
        assert "Failed to retrieve providers status" in str(exc_info.value.detail)


class TestAPIEndpoints:
    """Integration tests for API endpoints."""

    def test_validate_provider_endpoint_simple(self, client):
        """Test the validate endpoint with simple provider via HTTP."""
        with patch('src.api.v2_providers.log_request_info'):
            response = client.post(
                "/api/v2/providers/validate",
                json={"provider_type": "simple"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_type"] == "simple"
        assert data["is_valid"] is True
        assert data["status"] == "available"

    def test_validate_provider_endpoint_invalid_type(self, client):
        """Test the validate endpoint with invalid provider type via HTTP."""
        response = client.post(
            "/api/v2/providers/validate",
            json={"provider_type": "invalid"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_type"] == "invalid"
        assert data["is_valid"] is False
        assert data["status"] == "invalid"

    @patch('src.api.v2_providers.ConfigurationService')
    @patch('src.api.v2_providers.log_request_info')
    def test_status_endpoint(self, mock_log, mock_config_service, client):
        """Test the status endpoint via HTTP."""
        config_service_instance = mock_config_service.return_value
        config_service_instance.get_provider_config.side_effect = [
            Exception("No config"),  # OpenAI
            Exception("No config")   # Ollama
        ]
        
        response = client.get("/api/v2/providers/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "total_count" in data
        assert "available_count" in data
        assert data["total_count"] == 3

    def test_validate_provider_endpoint_missing_provider_type(self, client):
        """Test the validate endpoint with missing provider_type field."""
        response = client.post(
            "/api/v2/providers/validate",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestRequestModels:
    """Test Pydantic request/response models."""

    def test_provider_validation_request_valid(self):
        """Test ProviderValidationRequest with valid data."""
        request = ProviderValidationRequest(
            provider_type="openai",
            api_key="sk-test123",
            base_url="http://localhost:11434"
        )
        
        assert request.provider_type == "openai"
        assert request.api_key == "sk-test123"
        assert request.base_url == "http://localhost:11434"

    def test_provider_validation_request_minimal(self):
        """Test ProviderValidationRequest with minimal data."""
        request = ProviderValidationRequest(provider_type="simple")
        
        assert request.provider_type == "simple"
        assert request.api_key is None
        assert request.base_url is None

    def test_provider_validation_response_creation(self):
        """Test ProviderValidationResponse creation."""
        response = ProviderValidationResponse(
            provider_type="openai",
            is_valid=True,
            status="available",
            message="Test message",
            details={"key": "value"}
        )
        
        assert response.provider_type == "openai"
        assert response.is_valid is True
        assert response.status == "available"
        assert response.message == "Test message"
        assert response.details == {"key": "value"}

    def test_provider_validation_response_default_details(self):
        """Test ProviderValidationResponse with default empty details."""
        response = ProviderValidationResponse(
            provider_type="simple",
            is_valid=True,
            status="available",
            message="Test"
        )
        
        assert response.details == {}


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_openai_config_returns_none_api_key(self, mock_config_service):
        """Test OpenAI validation when config returns object with None api_key."""
        request_data = ProviderValidationRequest(provider_type="openai")
        config_service_instance = mock_config_service.return_value
        
        mock_openai_config = Mock()
        mock_openai_config.api_key = None
        config_service_instance.get_provider_config.return_value = mock_openai_config
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.is_valid is False
        assert result.status == "invalid_credentials"

    @pytest.mark.asyncio
    async def test_ollama_config_returns_none_base_url(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation when config returns object with None base_url."""
        request_data = ProviderValidationRequest(provider_type="ollama")
        config_service_instance = mock_config_service.return_value
        
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = None
        config_service_instance.get_provider_config.return_value = mock_ollama_config
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        # Should fail with invalid URL since None is not a valid HTTP URL
        assert result.is_valid is False
        assert result.status == "invalid_url"

    @pytest.mark.asyncio
    async def test_validate_openai_with_empty_string_api_key(self, mock_config_service):
        """Test OpenAI validation with empty string API key."""
        request_data = ProviderValidationRequest(provider_type="openai", api_key="")
        config_service_instance = mock_config_service.return_value
        
        result = await _validate_openai_provider(request_data, config_service_instance)
        
        assert result.is_valid is False
        assert result.status == "invalid_credentials"

    @pytest.mark.asyncio
    async def test_validate_ollama_with_empty_string_base_url(self, mock_config_service, mock_llm_provider_factory):
        """Test Ollama validation with empty string base URL - should fall back to config."""
        request_data = ProviderValidationRequest(provider_type="ollama", base_url="")
        config_service_instance = mock_config_service.return_value
        
        # Mock config with valid base URL
        mock_ollama_config = Mock()
        mock_ollama_config.base_url = "http://custom:11434"
        config_service_instance.get_provider_config.return_value = mock_ollama_config
        
        factory_instance = mock_llm_provider_factory.return_value
        factory_instance.create_provider.return_value = Mock()
        
        result = await _validate_ollama_provider(request_data, config_service_instance)
        
        # Should use config URL since request URL is empty
        assert result.is_valid is True
        assert result.details["base_url"] == "http://custom:11434"