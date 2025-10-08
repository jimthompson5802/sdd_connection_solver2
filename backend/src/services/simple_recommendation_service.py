"""
Simple recommendation service for Phase 1 compatibility.
Provides rule-based word recommendations without LLM integration.
"""

from typing import List, Dict, Any
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider


class SimpleRecommendationService:
    """Rule-based recommendation service for basic functionality."""

    def __init__(self):
        """Initialize the simple recommendation service."""
        self.common_patterns = self._load_common_patterns()
        self.fallback_groups = self._load_fallback_groups()

    def _load_common_patterns(self) -> Dict[str, List[str]]:
        """Load common word patterns for pattern matching."""
        return {
            "fish": ["bass", "flounder", "salmon", "trout", "cod", "tuna", "halibut", "mackerel"],
            "instruments": ["piano", "guitar", "violin", "drums", "flute", "trumpet", "cello", "harp"],
            "colors": ["red", "blue", "green", "yellow", "orange", "purple", "pink", "black"],
            "animals": ["dog", "cat", "bird", "fish", "horse", "cow", "pig", "sheep"],
            "food": ["apple", "banana", "orange", "grape", "bread", "milk", "cheese", "meat"],
            "sports": ["football", "basketball", "baseball", "soccer", "tennis", "golf", "hockey", "volleyball"],
            "body_parts": ["head", "arm", "leg", "hand", "foot", "eye", "ear", "nose"],
            "weather": ["sun", "rain", "snow", "wind", "cloud", "storm", "fog", "hail"],
        }

    def _load_fallback_groups(self) -> List[List[str]]:
        """Load fallback word groups when no patterns match."""
        return [
            ["bass", "flounder", "salmon", "trout"],
            ["piano", "guitar", "violin", "drums"],
            ["red", "blue", "green", "yellow"],
            ["apple", "banana", "orange", "grape"],
        ]

    def generate_recommendation(self, request: RecommendationRequest) -> RecommendationResponse:
        """Generate a simple rule-based recommendation.

        Args:
            request: RecommendationRequest with puzzle context.

        Returns:
            RecommendationResponse with recommended words.
        """
        # Extract words from previous guesses to avoid repetition
        guessed_words = set()
        for guess in request.previous_guesses:
            guessed_words.update(guess.words)

        # Find available words (not previously guessed). Preserve original casing by referencing the input list.
        available_words = []
        for word in request.remaining_words:
            if word not in guessed_words:
                available_words.append(word)

        # Try pattern matching first
        recommended_words = self._find_pattern_match(available_words)

        # Fall back to deterministic selection if no pattern found
        if not recommended_words:
            recommended_words = self._select_random_group(available_words)

        # Create provider for response
        provider = LLMProvider(provider_type="simple", model_name=None)

        return RecommendationResponse(
            recommended_words=recommended_words,
            connection_explanation=None,  # Simple provider doesn't provide explanations
            confidence_score=None,  # For legacy behavior expectations, omit confidence for simple provider
            provider_used=provider,
            generation_time_ms=None,  # Simple provider doesn't track timing
        )

    def _find_pattern_match(self, available_words: List[str]) -> List[str]:
        """Find words that match common patterns.

        Args:
            available_words: Words available for selection.

        Returns:
            List of 4 words that match a pattern, or empty list if none found.
        """
        # Normalize available words to lowercase for matching
        available_lower = [word.lower() for word in available_words]

        # Check each pattern
        for _, pattern_words in self.common_patterns.items():
            matches = [word for word in available_lower if word in pattern_words]

            # If we have at least 4 matches, return the first 4
            if len(matches) >= 4:
                # Return with original casing from available_words
                picked = matches[:4]
                # map back to original case in available_words
                return [next(w for w in available_words if w.lower() == lw) for lw in picked]

        return []

    def _select_random_group(self, available_words: List[str]) -> List[str]:
        """Select a deterministic group of 4 words.

        Args:
            available_words: Words available for selection.

        Returns:
            List of 4 randomly selected words.
        """
        if len(available_words) < 4:
            # If we don't have enough words, try fallback groups from within available words only
            available_lower = [word.lower() for word in available_words]
            for fallback_group in self.fallback_groups:
                if all(word in available_lower for word in fallback_group):
                    # map back to original case
                    return [next(w for w in available_words if w.lower() == lw) for lw in fallback_group]

            # Otherwise, return whatever valid words we have (no fabricated placeholders)
            return available_words[:4]

        # Deterministic selection for test stability: take first 4 in order
        return available_words[:4]

    def validate_recommendation(self, words: List[str]) -> Dict[str, Any]:
        """Validate a recommendation (basic validation for simple provider).

        Args:
            words: List of words to validate.

        Returns:
            Validation result with score and feedback.
        """
        if len(words) != 4:
            return {"valid": False, "score": 0.0, "feedback": "Must provide exactly 4 words"}

        # Check for duplicates
        if len(set(words)) != 4:
            return {"valid": False, "score": 0.0, "feedback": "Words must be unique"}

        # Basic validation passed
        return {
            "valid": True,
            "score": 0.5,  # Simple provider always gives moderate confidence
            "feedback": "Basic validation passed",
        }

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the simple recommendation service.

        Returns:
            Service metadata and capabilities.
        """
        return {
            "service_type": "simple_recommendation",
            "version": "1.0",
            "capabilities": ["pattern_matching", "random_selection", "fallback_groups"],
            "patterns_count": len(self.common_patterns),
            "fallback_groups_count": len(self.fallback_groups),
            "response_time": "fast",
        }
