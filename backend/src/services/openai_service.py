"""
OpenAI integration service using langchain for cloud LLM integration.
Provides high-quality word recommendations through OpenAI models.
"""

import time
from typing import Dict, Any, List
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider
from src.services.llm_provider_factory import get_provider_factory
from src.services.prompt_service import PromptTemplateService


class OpenAIService:
    """Service for interacting with OpenAI LLM models."""

    def __init__(self):
        """Initialize the OpenAI service."""
        self.provider_factory = get_provider_factory()
        self.prompt_service = PromptTemplateService()

    def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Generate recommendation using OpenAI LLM.

        Args:
            request: RecommendationRequest with puzzle context.

        Returns:
            RecommendationResponse with LLM-generated recommendations.
        """
        start_time = time.time()

        # Create OpenAI provider
        openai_provider = self.provider_factory.create_provider(request.llm_provider)

        # Generate enhanced prompt with OpenAI-specific instructions
        base_prompt = self.prompt_service.generate_recommendation_prompt(request)
        enhanced_prompt = self.prompt_service.add_provider_specific_instructions(base_prompt, "openai")

        # Add structured output request for better parsing
        structured_prompt = self._add_structured_output_request(enhanced_prompt)

        # Generate response from LLM
        llm_response = openai_provider.generate_recommendation(structured_prompt)

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

    def _add_structured_output_request(self, prompt: str) -> str:
        """Add structured output format request to the prompt.

        Args:
            prompt: Base prompt text.

        Returns:
            Enhanced prompt with structured output instructions.
        """
        structured_suffix = """

IMPORTANT: Format your response as follows:
1. First, provide your reasoning and explanation
2. Then, on a new line, provide ONLY the 4 words separated by commas
3. Make sure the words are in UPPERCASE

Example format:
These words are all types of fish commonly found in North American waters.
BASS, FLOUNDER, SALMON, TROUT"""

        return prompt + structured_suffix

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse OpenAI response with advanced parsing techniques.

        Args:
            response: Raw response from OpenAI.

        Returns:
            Dictionary with parsed words, explanation, and confidence.
        """
        try:
            lines = [line.strip() for line in response.strip().split("\n") if line.strip()]

            words = []
            explanation_lines = []

            # Look for the line with exactly 4 comma-separated words
            for i, line in enumerate(lines):
                if "," in line:
                    potential_words = [word.strip().upper() for word in line.split(",")]

                    # Check if it's exactly 4 valid words
                    if len(potential_words) == 4 and all(word.isalpha() and len(word) > 1 for word in potential_words):
                        words = potential_words
                        # Everything before this line is explanation
                        explanation_lines = lines[:i]
                        break

            # If no perfect match, try more flexible parsing
            if not words:
                words = self._extract_words_flexible(response)

            # Join explanation lines
            explanation = " ".join(explanation_lines).strip()

            # If no explanation found, extract from response
            if not explanation:
                explanation = self._extract_explanation(response, words)

            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(response, words, explanation)

            return {
                "words": words,
                "explanation": explanation or "High-quality OpenAI recommendation",
                "confidence": confidence,
            }

        except Exception as e:
            # Fallback response
            return {
                "words": ["BASS", "FLOUNDER", "SALMON", "TROUT"],
                "explanation": f"Failed to parse OpenAI response: {str(e)}",
                "confidence": 0.2,
            }

    def _extract_words_flexible(self, response: str) -> List[str]:
        """Extract words using flexible parsing methods.

        Args:
            response: Raw response text.

        Returns:
            List of 4 words or fallback.
        """
        import re

        # Try to find any group of 4 words
        word_pattern = r"\b[A-Z]{2,}\b"
        all_words = re.findall(word_pattern, response)

        if len(all_words) >= 4:
            return all_words[:4]

        # Try comma-separated pattern with any case
        comma_pattern = r"([A-Za-z]+),\s*([A-Za-z]+),\s*([A-Za-z]+),\s*([A-Za-z]+)"
        comma_match = re.search(comma_pattern, response)
        if comma_match:
            return [word.upper() for word in comma_match.groups()]

        # Last resort fallback
        return ["BASS", "FLOUNDER", "SALMON", "TROUT"]

    def _extract_explanation(self, response: str, words: List[str]) -> str:
        """Extract explanation from response.

        Args:
            response: Raw response text.
            words: Extracted words list.

        Returns:
            Explanation text.
        """
        # Remove the words line from explanation
        words_line = ", ".join(words)
        explanation = response.replace(words_line, "").strip()

        # Clean up the explanation
        lines = [line.strip() for line in explanation.split("\n") if line.strip()]

        # Remove common prefixes/suffixes
        cleaned_lines = []
        for line in lines:
            if not any(word.lower() in line.lower() for word in ["format:", "example:", "important:"]):
                cleaned_lines.append(line)

        return " ".join(cleaned_lines[:3])  # Take first 3 meaningful lines

    def _calculate_confidence(self, response: str, words: List[str], explanation: str) -> float:
        """Calculate confidence score for OpenAI response.

        Args:
            response: Raw response text.
            words: Extracted words.
            explanation: Extracted explanation.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        confidence = 0.7  # Higher base confidence for OpenAI

        # Increase confidence for detailed explanation
        if explanation and len(explanation) > 20:
            confidence += 0.15

        # Increase confidence for well-structured response
        if len(response.split("\n")) > 2:
            confidence += 0.1

        # Increase confidence for reasoning keywords
        reasoning_keywords = ["because", "since", "all", "share", "common", "category"]
        if any(keyword in explanation.lower() for keyword in reasoning_keywords):
            confidence += 0.05

        # Decrease confidence for fallback words
        if words == ["BASS", "FLOUNDER", "SALMON", "TROUT"]:
            confidence = min(confidence, 0.4)

        return min(confidence, 1.0)

    def generate_detailed_explanation(self, words: List[str], connection: str) -> str:
        """Generate detailed explanation for a connection using OpenAI.

        Args:
            words: List of 4 connected words.
            connection: Connection description.

        Returns:
            Detailed explanation text.
        """
        try:
            # Create OpenAI provider
            llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")
            openai_provider = self.provider_factory.create_provider(llm_provider)

            # Generate explanation prompt
            explanation_prompt = self.prompt_service.generate_explanation_prompt(words, connection)

            # Get detailed explanation
            explanation = openai_provider.generate_recommendation(explanation_prompt)

            return explanation.strip()

        except Exception as e:
            return f"Unable to generate detailed explanation: {str(e)}"

    def validate_connection(self, words: List[str]) -> Dict[str, Any]:
        """Validate a connection using OpenAI's reasoning capabilities.

        Args:
            words: List of 4 words to validate.

        Returns:
            Validation result with detailed analysis.
        """
        try:
            # Create OpenAI provider
            llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")
            openai_provider = self.provider_factory.create_provider(llm_provider)

            # Generate validation prompt
            validation_prompt = self.prompt_service.generate_validation_prompt(words)

            # Add structured output for validation
            structured_validation = (
                validation_prompt
                + """

Please provide your response in this format:
RATING: X/10
REASONING: [Your detailed reasoning]
VALID: YES/NO"""
            )

            # Get validation response
            response = openai_provider.generate_recommendation(structured_validation)

            return self._parse_validation_response(response)

        except Exception as e:
            return {"valid": False, "score": 0.0, "explanation": f"Validation failed: {str(e)}"}

    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse structured validation response from OpenAI.

        Args:
            response: Raw validation response.

        Returns:
            Parsed validation result.
        """
        import re

        try:
            # Extract rating
            rating_match = re.search(r"RATING:\s*(\d+)/10", response)
            score = 0.5  # Default
            if rating_match:
                score = int(rating_match.group(1)) / 10.0

            # Extract validity
            valid_match = re.search(r"VALID:\s*(YES|NO)", response)
            is_valid = score >= 0.6  # Default based on score
            if valid_match:
                is_valid = valid_match.group(1) == "YES"

            # Extract reasoning
            reasoning_match = re.search(r"REASONING:\s*(.+?)(?=VALID:|$)", response, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else response

            return {"valid": is_valid, "score": score, "explanation": reasoning}

        except Exception:
            return {"valid": False, "score": 0.0, "explanation": "Unable to parse validation response"}

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI service.

        Returns:
            Service metadata and capabilities.
        """
        return {
            "service_type": "openai_llm",
            "version": "1.0",
            "capabilities": [
                "high_quality_recommendations",
                "detailed_explanations",
                "advanced_reasoning",
                "connection_validation",
                "structured_output",
            ],
            "requires_api_key": True,
            "supports_offline": False,
            "expected_response_time": "fast",
        }
