"""
Simple recommendation service for Phase 1 compatibility.
Provides rule-based word recommendations without LLM integration.
"""

from typing import List, Dict, Any
import random
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
            "fish": ["BASS", "FLOUNDER", "SALMON", "TROUT", "COD", "TUNA", "HALIBUT", "MACKEREL"],
            "instruments": ["PIANO", "GUITAR", "VIOLIN", "DRUMS", "FLUTE", "TRUMPET", "CELLO", "HARP"],
            "colors": ["RED", "BLUE", "GREEN", "YELLOW", "ORANGE", "PURPLE", "PINK", "BLACK"],
            "animals": ["DOG", "CAT", "BIRD", "FISH", "HORSE", "COW", "PIG", "SHEEP"],
            "food": ["APPLE", "BANANA", "ORANGE", "GRAPE", "BREAD", "MILK", "CHEESE", "MEAT"],
            "sports": ["FOOTBALL", "BASKETBALL", "BASEBALL", "SOCCER", "TENNIS", "GOLF", "HOCKEY", "VOLLEYBALL"],
            "body_parts": ["HEAD", "ARM", "LEG", "HAND", "FOOT", "EYE", "EAR", "NOSE"],
            "weather": ["SUN", "RAIN", "SNOW", "WIND", "CLOUD", "STORM", "FOG", "HAIL"],
        }

    def _load_fallback_groups(self) -> List[List[str]]:
        """Load fallback word groups when no patterns match."""
        return [
            ["BASS", "FLOUNDER", "SALMON", "TROUT"],
            ["PIANO", "GUITAR", "VIOLIN", "DRUMS"],
            ["RED", "BLUE", "GREEN", "YELLOW"],
            ["APPLE", "BANANA", "ORANGE", "GRAPE"],
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

        # Find available words (not previously guessed)
        available_words = [word for word in request.remaining_words if word not in guessed_words]

        # Try pattern matching first
        recommended_words = self._find_pattern_match(available_words)

        # Fall back to random selection if no pattern found
        if not recommended_words:
            recommended_words = self._select_random_group(available_words)

        # Create provider for response
        provider = LLMProvider(provider_type="simple", model_name=None)

        return RecommendationResponse(
            recommended_words=recommended_words,
            connection_explanation="Simple pattern-based recommendation",
            confidence_score=0.5,  # Always moderate confidence for simple provider
            provider_used=provider,
            generation_time_ms=10,  # Fast generation time
        )

    def _find_pattern_match(self, available_words: List[str]) -> List[str]:
        """Find words that match common patterns.

        Args:
            available_words: Words available for selection.

        Returns:
            List of 4 words that match a pattern, or empty list if none found.
        """
        # Convert to uppercase for matching
        available_upper = [word.upper() for word in available_words]

        # Check each pattern
        for pattern_name, pattern_words in self.common_patterns.items():
            matches = [word for word in available_upper if word in pattern_words]

            # If we have at least 4 matches, return the first 4
            if len(matches) >= 4:
                return matches[:4]

        return []

    def _select_random_group(self, available_words: List[str]) -> List[str]:
        """Select a random group of 4 words.

        Args:
            available_words: Words available for selection.

        Returns:
            List of 4 randomly selected words.
        """
        if len(available_words) < 4:
            # If we don't have enough words, try fallback groups
            for fallback_group in self.fallback_groups:
                if all(word.upper() in [w.upper() for w in available_words] for word in fallback_group):
                    return fallback_group

            # Last resort: return whatever words we have
            return available_words[:4] if available_words else ["WORD1", "WORD2", "WORD3", "WORD4"]

        # Randomly select 4 words
        return random.sample(available_words, 4)

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
