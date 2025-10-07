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
        llm_response = ollama_provider.generate_recommendation(enhanced_prompt)

        # Parse the response
        parsed_response = self._parse_llm_response(llm_response)

        # Calculate generation time
        generation_time = int((time.time() - start_time) * 1000)

        return RecommendationResponse(
            recommended_words=parsed_response["words"],
            connection_explanation=parsed_response["explanation"],
            confidence_score=parsed_response["confidence"],
            provider_used=request.llm_provider,
            generation_time_ms=generation_time,
        )

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract words and explanation.

        Args:
            response: Raw response from the LLM.

        Returns:
            Dictionary with parsed words, explanation, and confidence.
        """
        try:
            lines = response.strip().split("\n")

            # Look for lines with 4 comma-separated words
            words = []
            explanation = ""

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check if line contains 4 comma-separated words
                if "," in line:
                    potential_words = [word.strip().lower() for word in line.split(",")]
                    if len(potential_words) == 4 and all(word.isalpha() for word in potential_words):
                        words = potential_words
                        break

            # If no words found, try to extract from the last line
            if not words:
                last_line = lines[-1].strip()
                if "," in last_line:
                    words = [word.strip().lower() for word in last_line.split(",")][:4]

            # Extract explanation (everything except the final word line)
            explanation_lines = []
            for line in lines:
                line = line.strip()
                if line and not (len(line.split(",")) == 4 and all(word.strip().isalpha() for word in line.split(","))):
                    explanation_lines.append(line)

            explanation = " ".join(explanation_lines).strip()

            # Fallback if no valid words found
            if not words or len(words) != 4:
                words = ["bass", "flounder", "salmon", "trout"]  # Fallback
                explanation = "Unable to parse LLM response properly (fallback used)"

            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(response, words, explanation)

            return {"words": words, "explanation": explanation or "No explanation provided", "confidence": confidence}

        except Exception as e:
            # Fallback response if parsing fails
            return {
                "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                "explanation": f"Failed to parse LLM response: {str(e)}",
                "confidence": 0.1,
            }

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
