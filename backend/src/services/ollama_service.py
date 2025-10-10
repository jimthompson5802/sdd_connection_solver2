"""
Ollama integration service using langchain for local LLM integration.
Provides intelligent word recommendations through Ollama models.
"""

import time
from typing import Dict, Any, List
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider
from src.services.llm_provider_factory import get_provider_factory
from src.services.prompt_service import PromptTemplateService


class OllamaService:
    """Service for interacting with Ollama LLM models."""

    def __init__(self):
        """Initialize the Ollama service."""
        self.provider_factory = get_provider_factory()
        self.prompt_service = PromptTemplateService()

    def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Generate recommendation using Ollama LLM.

        Args:
            request: RecommendationRequest with puzzle context.

        Returns:
            RecommendationResponse with LLM-generated recommendations.
        """
        start_time = time.time()

        # Create Ollama provider
        ollama_provider = self.provider_factory.create_provider(request.llm_provider)

        # Generate prompt
        base_prompt = self.prompt_service.generate_recommendation_prompt(request)
        enhanced_prompt = self.prompt_service.add_provider_specific_instructions(base_prompt, "ollama")

        # Generate response from LLM
        try:
            llm_response = ollama_provider.generate_recommendation(enhanced_prompt)
        except ValueError as e:
            # Provider returned a non-JSON/faulty response; translate to application error
            from src.exceptions import LLMProviderError

            raise LLMProviderError(
                f"Ollama provider returned malformed response: {str(e)}",
                provider_type="ollama",
                error_code="MALFORMED_PROVIDER_RESPONSE",
            )

        # If provider returned a structured dict (new format), prefer it
        if isinstance(llm_response, dict):
            words = llm_response.get("recommended_words") or llm_response.get("words") or []
            explanation = (
                llm_response.get("explanation")
                or llm_response.get("connection")
                or llm_response.get("connection_explanation")
                or ""
            )
            confidence = llm_response.get("confidence") or llm_response.get("confidence_score")
            generation_time = llm_response.get("generation_time_ms")

            # If generation_time missing, compute elapsed time
            if generation_time is None:
                generation_time = int((time.time() - start_time) * 1000)

            # If confidence missing, compute using available textual data
            if confidence is None:
                try:
                    import json

                    confidence = self._calculate_confidence(json.dumps(llm_response), words or [], explanation or "")
                except Exception:
                    confidence = None

            return RecommendationResponse(
                recommended_words=words,
                connection_explanation=explanation or None,
                confidence_score=confidence,
                provider_used=request.llm_provider,
                generation_time_ms=generation_time,
            )

        # Legacy/string response path -- freeform parsing removed
        raise ValueError("not json object")

    # _parse_llm_response removed: freeform text parsing is no longer supported here.

    def _calculate_confidence(self, response: str, words: List[str], explanation: str) -> float:
        """Calculate confidence score based on response quality.

        Args:
            response: Raw LLM response.
            words: Extracted words.
            explanation: Extracted explanation.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        confidence = 0.5  # Base confidence

        # Increase confidence if explanation is provided
        if explanation and len(explanation) > 10:
            confidence += 0.2

        # Increase confidence if response is well-structured
        if len(response.split("\n")) > 2:
            confidence += 0.1

        # Increase confidence if words are actual words (not random strings)
        if all(len(word) > 2 and word.isalpha() for word in words):
            confidence += 0.1

        # Decrease confidence if fallback was used
        if words == ["BASS", "FLOUNDER", "SALMON", "TROUT"]:
            confidence = min(confidence, 0.3)

        return min(confidence, 1.0)

    def validate_connection(self, words: List[str]) -> Dict[str, Any]:
        """Validate a potential connection using Ollama.

        Args:
            words: List of 4 words to validate.

        Returns:
            Validation result with score and explanation.
        """
        try:
            # Create a basic LLM provider for validation
            llm_provider = LLMProvider(provider_type="ollama", model_name="llama2")
            ollama_provider = self.provider_factory.create_provider(llm_provider)

            # Generate validation prompt
            validation_prompt = self.prompt_service.generate_validation_prompt(words)

            # Get validation response
            response = ollama_provider.generate_recommendation(validation_prompt)

            # Parse validation response
            return self._parse_validation_response(response)

        except Exception as e:
            return {"valid": False, "score": 0.0, "explanation": f"Validation failed: {str(e)}"}

    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse validation response from LLM.

        Args:
            response: Raw validation response.

        Returns:
            Parsed validation result.
        """
        try:
            # Look for rating in the response
            score = 0.5  # Default score

            # Simple parsing for rating (look for numbers 1-10)
            import re

            rating_match = re.search(r"(\d+)/10|(\d+)\s*out\s*of\s*10|rating[:\s]*(\d+)", response.lower())
            if rating_match:
                rating = int(rating_match.group(1) or rating_match.group(2) or rating_match.group(3))
                score = rating / 10.0

            return {"valid": score >= 0.6, "score": score, "explanation": response.strip()}

        except Exception:
            return {"valid": False, "score": 0.0, "explanation": "Unable to parse validation response"}

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the Ollama service.

        Returns:
            Service metadata and capabilities.
        """
        return {
            "service_type": "ollama_llm",
            "version": "1.0",
            "capabilities": [
                "context_aware_recommendations",
                "explanation_generation",
                "connection_validation",
                "local_processing",
            ],
            "requires_api_key": False,
            "supports_offline": True,
            "expected_response_time": "medium",
        }
