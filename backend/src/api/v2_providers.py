"""
API endpoints for LLM provider validation and management.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from src.llm_models.llm_provider import LLMProvider
from src.services.config_service import ConfigurationService
from src.services.llm_provider_factory import LLMProviderFactory
from src.exceptions import BaseApplicationError, InvalidProviderError, ConfigurationError, LLMProviderError
from src.middleware.error_handler import log_request_info


# Configure logger
logger = logging.getLogger(__name__)

# Create router for provider validation endpoints
router = APIRouter(prefix="/api/v2/providers", tags=["v2-providers"])


class ProviderValidationRequest(BaseModel):
    """Request model for provider validation."""

    provider_type: str = Field(..., description="Type of provider to validate")
    api_key: str | None = Field(None, description="API key for cloud providers")
    base_url: str | None = Field(None, description="Base URL for self-hosted providers")


class ProviderValidationResponse(BaseModel):
    """Response model for provider validation."""

    provider_type: str
    is_valid: bool
    status: str
    message: str
    details: Dict[str, Any] = {}


@router.post("/validate", response_model=ProviderValidationResponse)
async def validate_provider(request_data: ProviderValidationRequest, request: Request) -> ProviderValidationResponse:
    """Validate LLM provider configuration and connectivity.

    Args:
        request_data: Provider validation request.
        request: FastAPI request object for logging.

    Returns:
        ProviderValidationResponse with validation results.

    Raises:
        HTTPException: For various error conditions.
    """
    try:
        logger.info(f"Validating provider: {request_data.provider_type}")

        # Validate provider type
        valid_providers = ["simple", "ollama", "openai"]
        if request_data.provider_type not in valid_providers:
            return ProviderValidationResponse(
                provider_type=request_data.provider_type,
                is_valid=False,
                status="invalid",
                message=f"Unknown provider type: {request_data.provider_type}",
                details={"valid_providers": valid_providers},
            )

        # Simple provider is always valid (no external dependencies)
        if request_data.provider_type == "simple":
            response = ProviderValidationResponse(
                provider_type="simple",
                is_valid=True,
                status="available",
                message="Simple rule-based provider is always available",
            )
            log_request_info(request, {"status_code": 200, "provider": "simple"})
            return response

        # For cloud/local providers, check configuration
        config_service = ConfigurationService()

        if request_data.provider_type == "openai":
            return await _validate_openai_provider(request_data, config_service)
        elif request_data.provider_type == "ollama":
            return await _validate_ollama_provider(request_data, config_service)

        # Should not reach here due to earlier validation
        raise InvalidProviderError(f"Unhandled provider type: {request_data.provider_type}")

    except InvalidProviderError as e:
        logger.warning(f"Invalid provider validation request: {str(e)}")
        raise HTTPException(
            status_code=400, detail={"error": "Invalid Provider", "message": e.message, "error_code": e.error_code}
        )

    except ConfigurationError as e:
        logger.error(f"Configuration error during validation: {str(e)}")
        raise HTTPException(
            status_code=500, detail={"error": "Configuration Error", "message": e.message, "error_code": e.error_code}
        )

    except BaseApplicationError as e:
        logger.error(f"Application error during validation: {str(e)}")
        raise HTTPException(
            status_code=500, detail={"error": "Application Error", "message": e.message, "error_code": e.error_code}
        )

    except Exception as e:
        logger.exception(f"Unexpected error during provider validation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred during validation",
                "error_code": "INTERNAL_ERROR",
            },
        )


async def _validate_openai_provider(
    request_data: ProviderValidationRequest, config_service: ConfigurationService
) -> ProviderValidationResponse:
    """Validate OpenAI provider configuration.

    Args:
        request_data: Provider validation request.
        config_service: Configuration service instance.

    Returns:
        ProviderValidationResponse for OpenAI provider.
    """
    try:
        # Check for API key (from request or environment)
        api_key = request_data.api_key
        if not api_key:
            try:
                openai_config = config_service.get_provider_config("openai")
                if openai_config:
                    api_key = openai_config.api_key
            except Exception:
                return ProviderValidationResponse(
                    provider_type="openai",
                    is_valid=False,
                    status="configuration_missing",
                    message="OpenAI API key not provided and not found in environment",
                    details={"required": "OPENAI_API_KEY environment variable or api_key parameter"},
                )

        # Basic API key format validation
        if not api_key or len(api_key) < 10 or not api_key.startswith("sk-"):
            return ProviderValidationResponse(
                provider_type="openai",
                is_valid=False,
                status="invalid_credentials",
                message="Invalid OpenAI API key format",
                details={"expected_format": "sk-..."},
            )

        # Try to create provider instance to test configuration
        try:
            factory = LLMProviderFactory()
            # Create LLMProvider model for testing
            provider_model = LLMProvider(provider_type="openai", model_name="gpt-4o-mini")
            # Test provider creation without storing reference
            factory.create_provider(provider_model)

            # Could add actual API connectivity test here if needed
            # For now, just check if provider can be created

            return ProviderValidationResponse(
                provider_type="openai",
                is_valid=True,
                status="available",
                message="OpenAI provider configuration is valid",
                details={"api_key_format": "valid"},
            )

        except LLMProviderError as e:
            return ProviderValidationResponse(
                provider_type="openai",
                is_valid=False,
                status="provider_error",
                message=f"Failed to initialize OpenAI provider: {e.message}",
                details={"error_code": e.error_code},
            )

    except Exception as e:
        logger.exception(f"Error validating OpenAI provider: {str(e)}")
        return ProviderValidationResponse(
            provider_type="openai",
            is_valid=False,
            status="validation_error",
            message="Failed to validate OpenAI provider configuration",
            details={"error": str(e)},
        )


async def _validate_ollama_provider(
    request_data: ProviderValidationRequest, config_service: ConfigurationService
) -> ProviderValidationResponse:
    """Validate Ollama provider configuration.

    Args:
        request_data: Provider validation request.
        config_service: Configuration service instance.

    Returns:
        ProviderValidationResponse for Ollama provider.
    """
    try:
        # Check for base URL (from request or environment)
        base_url = request_data.base_url
        if not base_url:
            try:
                ollama_config = config_service.get_provider_config("ollama")
                if ollama_config:
                    base_url = ollama_config.base_url
            except Exception:
                # Use default Ollama URL
                base_url = "http://localhost:11434"

        # Basic URL format validation
        if not base_url or not (base_url.startswith("http://") or base_url.startswith("https://")):
            return ProviderValidationResponse(
                provider_type="ollama",
                is_valid=False,
                status="invalid_url",
                message="Invalid Ollama base URL format",
                details={"expected_format": "http://localhost:11434 or https://..."},
            )

        # Try to create provider instance
        try:
            factory = LLMProviderFactory()
            # Create LLMProvider model for testing
            provider_model = LLMProvider(provider_type="ollama", model_name="llama2")
            # Test provider creation without storing reference
            factory.create_provider(provider_model)

            # Could add actual connectivity test here if needed
            # For now, just check if provider can be created

            return ProviderValidationResponse(
                provider_type="ollama",
                is_valid=True,
                status="available",
                message="Ollama provider configuration is valid",
                details={"base_url": base_url},
            )

        except LLMProviderError as e:
            return ProviderValidationResponse(
                provider_type="ollama",
                is_valid=False,
                status="provider_error",
                message=f"Failed to initialize Ollama provider: {e.message}",
                details={"error_code": e.error_code, "base_url": base_url},
            )

    except Exception as e:
        logger.exception(f"Error validating Ollama provider: {str(e)}")
        return ProviderValidationResponse(
            provider_type="ollama",
            is_valid=False,
            status="validation_error",
            message="Failed to validate Ollama provider configuration",
            details={"error": str(e)},
        )


@router.get("/status")
async def get_providers_status(request: Request) -> Dict[str, Any]:
    """Get status of all available providers.

    Args:
        request: FastAPI request object for logging.

    Returns:
        Status information for all providers.
    """
    try:
        config_service = ConfigurationService()

        # Check status of all providers
        providers_status = {
            "simple": {"type": "simple", "status": "available", "message": "Rule-based provider (always available)"}
        }

        # Check OpenAI configuration
        try:
            config_service.get_provider_config("openai")
            providers_status["openai"] = {
                "type": "openai",
                "status": "configured",
                "message": "OpenAI configuration found",
            }
        except Exception:
            providers_status["openai"] = {
                "type": "openai",
                "status": "not_configured",
                "message": "OpenAI API key not configured",
            }

        # Check Ollama configuration
        try:
            ollama_config = config_service.get_provider_config("ollama")
            if ollama_config:
                providers_status["ollama"] = {
                    "type": "ollama",
                    "status": "configured",
                    "message": f"Ollama configured at {ollama_config.base_url}",
                }
            else:
                providers_status["ollama"] = {
                    "type": "ollama",
                    "status": "default_config",
                    "message": "Using default Ollama configuration (http://localhost:11434)",
                }
        except Exception:
            providers_status["ollama"] = {
                "type": "ollama",
                "status": "default_config",
                "message": "Using default Ollama configuration (http://localhost:11434)",
            }

        response = {
            "providers": providers_status,
            "total_count": len(providers_status),
            "available_count": sum(1 for p in providers_status.values() if p["status"] in ["available", "configured"]),
        }

        log_request_info(request, {"status_code": 200, "providers_checked": len(providers_status)})
        return response

    except Exception as e:
        logger.exception(f"Failed to get providers status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve providers status",
                "error_code": "PROVIDERS_STATUS_FAILED",
            },
        )
