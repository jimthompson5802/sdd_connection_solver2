"""Unit tests for error handler middleware."""

import pytest
from unittest.mock import Mock
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel
from src.middleware.error_handler import (
    global_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    application_exception_handler,
    log_request_info,
    create_error_response,
    mask_sensitive_data,
)
from src.exceptions import BaseApplicationError, LLMProviderError


class ValidationTestModel(BaseModel):
    """Test model for validation errors."""

    name: str
    age: int


class TestErrorHandlers:
    """Test cases for error handler middleware."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_request = Mock(spec=Request)
        self.mock_request.url.path = "/test/path"

    @pytest.mark.asyncio
    async def test_global_exception_handler(self):
        """Test global exception handler."""
        exc = Exception("Test exception")

        response = await global_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500

        content = response.body.decode()
        assert "Internal Server Error" in content
        assert "INTERNAL_ERROR" in content
        assert "/test/path" in content

    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """Test validation exception handler."""
        # Create a validation error
        try:
            ValidationTestModel(name="John", age="invalid")  # age should be int
        except ValidationError as exc:
            response = await validation_exception_handler(self.mock_request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == 422

            content = response.body.decode()
            assert "Validation Error" in content
            assert "VALIDATION_ERROR" in content
            assert "/test/path" in content

    @pytest.mark.asyncio
    async def test_http_exception_handler(self):
        """Test HTTP exception handler."""
        exc = HTTPException(status_code=404, detail="Not found")

        response = await http_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 404

        content = response.body.decode()
        assert "HTTP Error" in content
        assert "Not found" in content
        assert "HTTP_404" in content
        assert "/test/path" in content

    @pytest.mark.asyncio
    async def test_application_exception_handler_base_error(self):
        """Test application exception handler with base error."""
        exc = BaseApplicationError("Test error", "TEST_ERROR")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500  # Default

        content = response.body.decode()
        assert "BaseApplicationError" in content
        assert "Test error" in content
        assert "TEST_ERROR" in content
        assert "/test/path" in content

    @pytest.mark.asyncio
    async def test_application_exception_handler_llm_provider_error(self):
        """Test application exception handler with LLM provider error."""
        exc = LLMProviderError("Provider failed", provider_type="openai")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 503  # Service Unavailable

        content = response.body.decode()
        assert "LLMProviderError" in content
        assert "Provider failed" in content
        assert "openai" in content
        assert "/test/path" in content

    @pytest.mark.asyncio
    async def test_application_exception_handler_validation_error_code(self):
        """Test application exception handler with validation error code."""
        exc = BaseApplicationError("Validation failed", "VALIDATION_ERROR")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400  # Bad Request

    @pytest.mark.asyncio
    async def test_application_exception_handler_insufficient_words(self):
        """Test application exception handler with insufficient words error."""
        exc = BaseApplicationError("Not enough words", "INSUFFICIENT_WORDS")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400  # Bad Request

    @pytest.mark.asyncio
    async def test_application_exception_handler_invalid_provider(self):
        """Test application exception handler with invalid provider error."""
        exc = BaseApplicationError("Invalid provider", "INVALID_PROVIDER")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400  # Bad Request

    @pytest.mark.asyncio
    async def test_application_exception_handler_configuration_error(self):
        """Test application exception handler with configuration error."""
        exc = BaseApplicationError("Config error", "CONFIGURATION_ERROR")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500  # Internal Server Error

    @pytest.mark.asyncio
    async def test_application_exception_handler_timeout_error(self):
        """Test application exception handler with timeout error."""
        exc = BaseApplicationError("Timeout", "TIMEOUT_ERROR")

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 504  # Gateway Timeout

    @pytest.mark.asyncio
    async def test_application_exception_handler_with_details(self):
        """Test application exception handler with additional details."""
        details = {"trace_id": "123", "retry_after": 30}
        exc = BaseApplicationError("Test error", "TEST_ERROR", details=details)

        response = await application_exception_handler(self.mock_request, exc)

        assert isinstance(response, JSONResponse)

        content = response.body.decode()
        assert "trace_id" in content
        assert "retry_after" in content

    def test_log_request_info(self, caplog):
        """Test logging request information."""
        self.mock_request.method = "POST"
        self.mock_request.headers = {"user-agent": "test-agent"}
        response_data = {"status_code": 200}

        # Set the log level to ensure we capture the info logs
        import logging

        caplog.set_level(logging.INFO)

        log_request_info(self.mock_request, response_data)

        assert "POST /test/path" in caplog.text
        assert "Status: 200" in caplog.text
        assert "test-agent" in caplog.text

    def test_log_request_info_missing_user_agent(self, caplog):
        """Test logging request information without user agent."""
        self.mock_request.method = "GET"
        self.mock_request.headers = {}
        response_data = {"status_code": 404}

        # Set the log level to ensure we capture the info logs
        import logging

        caplog.set_level(logging.INFO)

        log_request_info(self.mock_request, response_data)

        assert "GET /test/path" in caplog.text
        assert "Status: 404" in caplog.text
        assert "unknown" in caplog.text

    def test_create_error_response_basic(self):
        """Test creating basic error response."""
        response = create_error_response("Test error", "TEST_CODE", 400)

        assert response["error"] == "Application Error"
        assert response["detail"] == "Test error"
        assert response["error_code"] == "TEST_CODE"
        assert response["status_code"] == 400

    def test_create_error_response_with_details(self):
        """Test creating error response with details."""
        details = {"field": "value", "count": 42}
        response = create_error_response("Test error", "TEST_CODE", 400, details)

        assert response["error"] == "Application Error"
        assert response["detail"] == "Test error"
        assert response["error_code"] == "TEST_CODE"
        assert response["status_code"] == 400
        assert response["details"] == details

    def test_create_error_response_defaults(self):
        """Test creating error response with default values."""
        response = create_error_response("Test error")

        assert response["error"] == "Application Error"
        assert response["detail"] == "Test error"
        assert response["error_code"] == "GENERAL_ERROR"
        assert response["status_code"] == 500
        assert "details" not in response

    def test_mask_sensitive_data_api_key(self):
        """Test masking API key in data."""
        data = {"api_key": "sk-1234567890abcdef", "normal_field": "normal_value"}

        masked = mask_sensitive_data(data)

        assert masked["api_key"] == "sk-1***************"
        assert masked["normal_field"] == "normal_value"

    def test_mask_sensitive_data_password(self):
        """Test masking password in data."""
        data = {"password": "mysecretpassword", "username": "testuser"}

        masked = mask_sensitive_data(data)

        assert masked["password"] == "myse************"
        assert masked["username"] == "testuser"

    def test_mask_sensitive_data_short_value(self):
        """Test masking short sensitive values."""
        data = {"secret": "abc", "token": "abcd"}  # Less than 4 characters  # Exactly 4 characters

        masked = mask_sensitive_data(data)

        assert masked["secret"] == "****"
        assert masked["token"] == "****"

    def test_mask_sensitive_data_multiple_fields(self):
        """Test masking multiple sensitive fields."""
        data = {
            "api_key": "sk-1234567890abcdef",
            "password": "secretpassword",
            "secret": "topsecret",
            "token": "access_token_123",
            "normal_field": "normal_value",
        }

        masked = mask_sensitive_data(data)

        assert masked["api_key"] == "sk-1***************"
        assert masked["password"] == "secr**********"
        assert masked["secret"] == "tops*****"
        assert masked["token"] == "acce************"
        assert masked["normal_field"] == "normal_value"

    def test_mask_sensitive_data_no_sensitive_fields(self):
        """Test masking data with no sensitive fields."""
        data = {"username": "testuser", "email": "test@example.com", "age": 25}

        masked = mask_sensitive_data(data)

        assert masked == data  # Should be unchanged

    def test_mask_sensitive_data_empty_dict(self):
        """Test masking empty dictionary."""
        data = {}

        masked = mask_sensitive_data(data)

        assert masked == {}

    def test_mask_sensitive_data_non_string_values(self):
        """Test masking handles non-string values for sensitive fields."""
        data = {"api_key": 12345, "normal_field": "normal_value"}  # Not a string

        masked = mask_sensitive_data(data)

        assert masked["api_key"] == "****"  # Non-string becomes ****
        assert masked["normal_field"] == "normal_value"
