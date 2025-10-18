"""
Error handling middleware for consistent error responses.
"""

import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.exceptions import BaseApplicationError, LLMProviderError


# Configure logger for error handling
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled exceptions.

    Args:
        request: FastAPI request object.
        exc: Exception that was raised.

    Returns:
        JSONResponse with formatted error information.
    """
    logger.exception(f"Unhandled exception in {request.url.path}: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors.

    Args:
        request: FastAPI request object.
        exc: Pydantic ValidationError.

    Returns:
        JSONResponse with validation error details.
    """
    logger.warning(f"Validation error in {request.url.path}: {str(exc)}")

    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append(
            {"field": ".".join(str(loc) for loc in error["loc"]), "message": error["msg"], "type": error["type"]}
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": "Request validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": errors,
            "path": str(request.url.path),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions.

    Args:
        request: FastAPI request object.
        exc: HTTPException that was raised.

    Returns:
        JSONResponse with HTTP error information.
    """
    logger.info(f"HTTP exception in {request.url.path}: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "path": str(request.url.path),
        },
    )


async def application_exception_handler(request: Request, exc: BaseApplicationError) -> JSONResponse:
    """Handler for custom application exceptions.

    Args:
        request: FastAPI request object.
        exc: BaseApplicationError or subclass.

    Returns:
        JSONResponse with application error information.
    """
    # Determine status code based on exception type
    status_code = 500  # Default
    if isinstance(exc, LLMProviderError):
        status_code = 503  # Service Unavailable
    elif exc.error_code in ["VALIDATION_ERROR", "INSUFFICIENT_WORDS"]:
        status_code = 400  # Bad Request
    elif exc.error_code == "INVALID_PROVIDER":
        status_code = 400  # Bad Request
    elif exc.error_code == "CONFIGURATION_ERROR":
        status_code = 500  # Internal Server Error
    elif exc.error_code == "TIMEOUT_ERROR":
        status_code = 504  # Gateway Timeout

    logger.error(f"Application error in {request.url.path}: {exc.error_code} - {exc.message}")

    response_content = {
        "error": exc.__class__.__name__,
        "detail": exc.message,
        "error_code": exc.error_code,
        "path": str(request.url.path),
    }

    # Add additional details if available
    if exc.details:
        response_content["details"] = exc.details

    # Add provider-specific information for LLM errors
    if isinstance(exc, LLMProviderError) and exc.provider_type:
        response_content["provider_type"] = exc.provider_type

    return JSONResponse(status_code=status_code, content=response_content)


def log_request_info(request: Request, response_data: Dict[str, Any]) -> None:
    """Log request information for monitoring and debugging.

    Args:
        request: FastAPI request object.
        response_data: Response data dictionary.
    """
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response_data.get('status_code', 'unknown')} - "
        f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
    )


def create_error_response(
    error_message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500, details: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Create standardized error response structure.

    Args:
        error_message: Human-readable error message.
        error_code: Machine-readable error code.
        status_code: HTTP status code.
        details: Additional error details.

    Returns:
        Standardized error response dictionary.
    """
    response = {
        "error": "Application Error",
        "detail": error_message,
        "error_code": error_code,
        "status_code": status_code,
    }

    if details:
        response["details"] = details

    return response


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive data in responses for logging.

    Args:
        data: Response data that may contain sensitive information.

    Returns:
        Data with sensitive fields masked.
    """
    sensitive_fields = ["api_key", "password", "secret", "token"]
    masked_data = data.copy()

    for field in sensitive_fields:
        if field in masked_data:
            value = masked_data[field]
            if isinstance(value, str) and len(value) > 4:
                masked_data[field] = value[:4] + "*" * (len(value) - 4)
            else:
                masked_data[field] = "****"

    return masked_data
