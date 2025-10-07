"""
Recommendation orchestration service that routes requests to appropriate providers.
Coordinates between different LLM services and validates responses.
"""

from typing import Dict, Any
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider
from src.services.simple_recommendation_service import SimpleRecommendationService
from src.services.ollama_service import OllamaService
from src.services.openai_service import OpenAIService
from src.services.response_validator import ResponseValidatorService
from src.services.llm_provider_factory import get_provider_factory
from src.models import session_manager


class RecommendationService:
    """Main orchestration service for LLM recommendations."""

    def __init__(self):
        """Initialize the recommendation service with all providers."""
        self.simple_service = SimpleRecommendationService()
        self.ollama_service = OllamaService()
        self.openai_service = OpenAIService()
        self.validator = ResponseValidatorService()
        self.provider_factory = get_provider_factory()

    def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Generate recommendation using the specified provider.

        Args:
            request: RecommendationRequest with provider and context.

        Returns:
            RecommendationResponse from the specified provider.
        """
        try:
            # If no session exists, return a generic static recommendation
            if session_manager.get_session_count() == 0:
                raise ValueError("No active session available")

            # Use last-created session
            session = list(session_manager._sessions.values())[-1]

            # Validate provider availability
            if not self._validate_provider_availability(request.llm_provider):
                # Fall back to simple provider if requested provider unavailable
                fallback_request = self._create_fallback_request(request)
                return self._generate_with_fallback(fallback_request, request)

            # Route to appropriate service
            response = self._route_request(request)

            # Validate response
            validation_result = self.validator.validate_response(response, request.previous_guesses)

            # If validation fails, try to fix or fallback
            if not validation_result["valid"]:
                response = self._handle_invalid_response(request, response, validation_result)

            session.last_recommendation = response.recommended_words

            return response

        except Exception as e:
            # Last resort fallback
            return self._create_error_response(request, str(e))

    def _validate_provider_availability(self, provider: LLMProvider) -> bool:
        """Check if the requested provider is available.

        Args:
            provider: LLMProvider to validate.

        Returns:
            True if provider is available and configured.
        """
        try:
            available_providers = self.provider_factory.get_available_providers()
            return available_providers.get(provider.provider_type, False)
        except Exception:
            return False

    def _route_request(self, request: RecommendationRequest) -> RecommendationResponse:
        """Route request to the appropriate service based on provider type.

        Args:
            request: RecommendationRequest to route.

        Returns:
            RecommendationResponse from the appropriate service.
        """
        provider_type = request.llm_provider.provider_type

        if provider_type == "simple":
            return self.simple_service.generate_recommendation(request)
        elif provider_type == "ollama":
            return self.ollama_service.generate_recommendation(request)
        elif provider_type == "openai":
            return self.openai_service.generate_recommendation(request)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    def _create_fallback_request(self, original_request: RecommendationRequest) -> RecommendationRequest:
        """Create a fallback request using simple provider.

        Args:
            original_request: Original request that failed.

        Returns:
            New request with simple provider.
        """
        fallback_provider = LLMProvider(provider_type="simple", model_name=None)

        return RecommendationRequest(
            llm_provider=fallback_provider,
            remaining_words=original_request.remaining_words,
            previous_guesses=original_request.previous_guesses,
            puzzle_context=original_request.puzzle_context,
        )

    def _generate_with_fallback(
        self, fallback_request: RecommendationRequest, original_request: RecommendationRequest
    ) -> RecommendationResponse:
        """Generate response with fallback and add fallback notice.

        Args:
            fallback_request: Request with fallback provider.
            original_request: Original request that failed.

        Returns:
            Response with fallback indication.
        """
        response = self.simple_service.generate_recommendation(fallback_request)

        # Update explanation to indicate fallback was used
        original_provider = original_request.llm_provider.provider_type
        fallback_explanation = (
            f"Fallback to simple provider (original {original_provider} "
            f"unavailable). {response.connection_explanation}"
        )

        return RecommendationResponse(
            recommended_words=response.recommended_words,
            connection_explanation=fallback_explanation,
            confidence_score=max(0.1, response.confidence_score - 0.2),  # Lower confidence
            provider_used=response.provider_used,
            generation_time_ms=response.generation_time_ms,
        )

    def _handle_invalid_response(
        self, request: RecommendationRequest, response: RecommendationResponse, validation_result: Dict[str, Any]
    ) -> RecommendationResponse:
        """Handle invalid response by attempting fixes or fallback.

        Args:
            request: Original request.
            response: Invalid response.
            validation_result: Validation failure details.

        Returns:
            Fixed or fallback response.
        """
        critical_failures = validation_result.get("critical_failures", [])

        # If only minor issues, try to fix the response
        if not critical_failures:
            return self._attempt_response_fix(response, validation_result)

        # For critical failures, fallback to simple provider
        fallback_request = self._create_fallback_request(request)
        fallback_response = self.simple_service.generate_recommendation(fallback_request)

        # Add error notice to explanation
        error_explanation = (
            f"Validation failed, using fallback. Issues: "
            f"{', '.join(critical_failures)}. {fallback_response.connection_explanation}"
        )

        return RecommendationResponse(
            recommended_words=fallback_response.recommended_words,
            connection_explanation=error_explanation,
            confidence_score=0.3,  # Low confidence due to validation failure
            provider_used=fallback_response.provider_used,
            generation_time_ms=fallback_response.generation_time_ms,
        )

    def _attempt_response_fix(
        self, response: RecommendationResponse, validation_result: Dict[str, Any]
    ) -> RecommendationResponse:
        """Attempt to fix minor response issues.

        Args:
            response: Response to fix.
            validation_result: Validation details.

        Returns:
            Fixed response or original if cannot fix.
        """
        fixed_words = response.recommended_words.copy()

        # Fix word count if needed
        if len(fixed_words) > 4:
            fixed_words = fixed_words[:4]
        elif len(fixed_words) < 4:
            # Pad with fallback words
            fallback_words = ["BASS", "FLOUNDER", "SALMON", "TROUT"]
            while len(fixed_words) < 4:
                for word in fallback_words:
                    if word not in fixed_words:
                        fixed_words.append(word)
                        break

        # Fix duplicates
        seen = set()
        unique_words = []
        for word in fixed_words:
            word_upper = word.upper()
            if word_upper not in seen:
                seen.add(word_upper)
                unique_words.append(word)

        # If we lost words due to deduplication, add fallbacks
        fallback_words = ["WORD1", "WORD2", "WORD3", "WORD4"]
        while len(unique_words) < 4:
            for word in fallback_words:
                if word not in seen:
                    unique_words.append(word)
                    seen.add(word)
                    break

        return RecommendationResponse(
            recommended_words=unique_words[:4],
            connection_explanation=response.connection_explanation + " (auto-corrected)",
            confidence_score=max(0.1, response.confidence_score - 0.3),
            provider_used=response.provider_used,
            generation_time_ms=response.generation_time_ms,
        )

    def _create_error_response(self, request: RecommendationRequest, error_message: str) -> RecommendationResponse:
        """Create an error response as last resort.

        Args:
            request: Original request.
            error_message: Error description.

        Returns:
            Error response with fallback recommendations.
        """
        return RecommendationResponse(
            recommended_words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
            connection_explanation=f"Error occurred: {error_message}. Using fallback recommendation.",
            confidence_score=0.1,
            provider_used=LLMProvider(provider_type="simple", model_name=None),
            generation_time_ms=10,
        )

    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available providers.

        Returns:
            Dictionary with provider availability and capabilities.
        """
        try:
            availability = self.provider_factory.get_available_providers()

            provider_info = {}

            # Simple provider info
            provider_info["simple"] = {
                "available": availability.get("simple", True),
                "info": self.simple_service.get_service_info(),
                "requires_config": False,
            }

            # Ollama provider info
            provider_info["ollama"] = {
                "available": availability.get("ollama", False),
                "info": self.ollama_service.get_service_info(),
                "requires_config": True,
            }

            # OpenAI provider info
            provider_info["openai"] = {
                "available": availability.get("openai", False),
                "info": self.openai_service.get_service_info(),
                "requires_config": True,
            }

            return provider_info

        except Exception as e:
            return {
                "error": f"Failed to get provider information: {str(e)}",
                "simple": {"available": True, "info": {}, "requires_config": False},
            }

    def validate_request(self, request: RecommendationRequest) -> Dict[str, Any]:
        """Validate a recommendation request before processing.

        Args:
            request: Request to validate.

        Returns:
            Validation result.
        """
        try:
            # Check basic request validity
            if len(request.remaining_words) < 4:
                return {
                    "valid": False,
                    "error": "Must have at least 4 remaining words",
                    "details": {"word_count": len(request.remaining_words)},
                }

            # Check provider availability
            if not self._validate_provider_availability(request.llm_provider):
                return {
                    "valid": False,
                    "error": f"Provider {request.llm_provider.provider_type} is not available",
                    "details": {"requested_provider": request.llm_provider.provider_type},
                }

            return {"valid": True, "message": "Request is valid"}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}", "details": {}}

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics and health information.

        Returns:
            Service statistics and status.
        """
        return {
            "service_name": "recommendation_orchestration",
            "version": "1.0",
            "available_providers": list(self.provider_factory.get_available_providers().keys()),
            "capabilities": ["provider_routing", "response_validation", "automatic_fallback", "error_handling"],
            "validator_rules": len(self.validator.validation_rules),
        }
