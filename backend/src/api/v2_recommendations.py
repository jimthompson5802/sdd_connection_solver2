"""
API endpoints for LLM-powered recommendations (v2).
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import ValidationError
from src.models import RecommendationRequest, RecommendationResponse
from src.services.recommendation_service import RecommendationService
from src.exceptions import (
    BaseApplicationError,
    LLMProviderError,
    ValidationError as AppValidationError,
    InsufficientWordsError,
    InvalidProviderError,
)
from src.middleware.error_handler import log_request_info


# Configure logger
logger = logging.getLogger(__name__)

# Create router for v2 API endpoints
router = APIRouter(prefix="/api/v2", tags=["v2-recommendations"])


def get_recommendation_service() -> RecommendationService:
    """Dependency to get RecommendationService instance.

    Returns:
        RecommendationService instance.
    """
    try:
        return RecommendationService()
    except Exception as e:
        logger.error(f"Failed to create RecommendationService: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize recommendation service")


@router.post("/recommendations", response_model=RecommendationResponse)
async def generate_recommendation(
    request_data: RecommendationRequest,
    request: Request,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    """Generate LLM-powered recommendations for word groupings.

    Args:
        request_data: Request containing words and configuration.
        request: FastAPI request object for logging.
        service: RecommendationService dependency.

    Returns:
        RecommendationResponse with recommendations and metadata.

    Raises:
        HTTPException: For various error conditions.
    """
    try:
        # Log request information
        logger.info(
            f"Generating recommendation for {len(request_data.remaining_words)} words "
            f"using provider: {request_data.llm_provider}"
        )

        # Generate recommendation using service
        response = service.generate_recommendation(request_data)

        # Log successful response
        log_request_info(
            request,
            {
                "status_code": 200,
                "provider_used": response.provider_used,
                "recommendation_count": len(response.recommended_words),
            },
        )

        return response

    except InsufficientWordsError as e:
        logger.warning(f"Insufficient words error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Insufficient Words",
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )

    except InvalidProviderError as e:
        logger.warning(f"Invalid provider error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Provider",
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )

    except LLMProviderError as e:
        logger.error(f"LLM provider error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "LLM Provider Error",
                "message": e.message,
                "error_code": e.error_code,
                "provider_type": e.provider_type,
                "details": e.details,
            },
        )

    except AppValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation Error",
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )

    except BaseApplicationError as e:
        logger.error(f"Application error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Application Error",
                "message": e.message,
                "error_code": e.error_code,
                "details": e.details,
            },
        )

    except ValidationError as e:
        logger.warning(f"Pydantic validation error: {str(e)}")
        # Format validation errors
        errors = []
        for error in e.errors():
            errors.append(
                {"field": ".".join(str(loc) for loc in error["loc"]), "message": error["msg"], "type": error["type"]}
            )

        raise HTTPException(
            status_code=422,
            detail={
                "error": "Request Validation Error",
                "message": "Request validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )

    except Exception as e:
        logger.exception(f"Unexpected error in generate_recommendation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_ERROR",
            },
        )


@router.get("/recommendations/health")
async def health_check(
    request: Request, service: RecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """Health check endpoint for recommendation service.

    Args:
        request: FastAPI request object for logging.
        service: RecommendationService dependency.

    Returns:
        Health status and service information.
    """
    try:
        # Basic service health check
        status = {
            "status": "healthy",
            "service": "recommendation-service",
            "version": "2.0",
            "timestamp": None,  # Will be set by service if available
        }

        # Try to get available providers
        try:
            # This would call a health check method if available
            available_providers = ["simple"]  # Default fallback
            status["available_providers"] = available_providers
        except Exception as e:
            logger.warning(f"Could not check provider availability: {str(e)}")
            status["available_providers"] = ["simple"]  # Fallback

        log_request_info(request, {"status_code": 200, "health": "ok"})
        return status

    except Exception as e:
        logger.exception(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service Unavailable",
                "message": "Health check failed",
                "error_code": "HEALTH_CHECK_FAILED",
            },
        )


@router.get("/recommendations/providers")
async def list_providers(
    request: Request, service: RecommendationService = Depends(get_recommendation_service)
) -> Dict[str, Any]:
    """List available LLM providers and their status.

    Args:
        request: FastAPI request object for logging.
        service: RecommendationService dependency.

    Returns:
        List of available providers with status information.
    """
    try:
        # Get provider information
        providers = {
            "simple": {
                "name": "Simple Rule-Based",
                "type": "simple",
                "status": "available",
                "description": "Rule-based recommendation engine",
                "requires_config": False,
            },
            "ollama": {
                "name": "Ollama Local LLM",
                "type": "ollama",
                "status": "unknown",  # Would check actual availability
                "description": "Local LLM via Ollama",
                "requires_config": True,
            },
            "openai": {
                "name": "OpenAI GPT",
                "type": "openai",
                "status": "unknown",  # Would check actual availability
                "description": "OpenAI GPT models",
                "requires_config": True,
            },
        }

        # Try to validate provider availability
        # This would use the service to check actual provider status

        response = {"providers": providers, "default_provider": "simple", "total_count": len(providers)}

        log_request_info(request, {"status_code": 200, "provider_count": len(providers)})
        return response

    except Exception as e:
        logger.exception(f"Failed to list providers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "Failed to retrieve provider information",
                "error_code": "PROVIDER_LIST_FAILED",
            },
        )
