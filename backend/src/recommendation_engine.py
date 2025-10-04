"""
Recommendation engine for suggesting word groups in NYT Connections puzzles.
Uses basic heuristics and pattern matching to suggest likely word groupings.
"""

from typing import List, Tuple, Optional
from .models import PuzzleSession


class RecommendationEngine:
    """
    Engine for generating word group recommendations based on various heuristics.

    This is a simplified implementation that uses pattern matching, word similarity,
    and attempt history to suggest likely groupings. In a production system, this
    would use more sophisticated NLP and ML techniques.
    """

    def __init__(self) -> None:
        # Common word categories and patterns for basic matching
        self.category_patterns = {
            "colors": ["red", "blue", "green", "yellow", "orange", "purple", "pink", "black", "white", "brown"],
            "animals": ["cat", "dog", "bird", "fish", "lion", "tiger", "bear", "wolf", "fox", "deer"],
            "foods": ["apple", "banana", "orange", "bread", "cheese", "milk", "meat", "rice", "pasta"],
            "sports": ["football", "basketball", "baseball", "tennis", "soccer", "golf", "hockey"],
            "countries": ["usa", "canada", "mexico", "france", "germany", "italy", "spain", "japan"],
            "numbers": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
            "body_parts": ["head", "hand", "foot", "arm", "leg", "eye", "nose", "mouth", "ear"],
        }

        # Word endings that might indicate similar categories
        self.suffix_patterns = {
            "ing": ["running", "walking", "singing", "dancing"],
            "ed": ["walked", "talked", "played", "worked"],
            "ly": ["quickly", "slowly", "carefully", "easily"],
            "tion": ["action", "motion", "emotion", "position"],
            "ness": ["darkness", "sadness", "happiness", "kindness"],
        }

    def get_recommendation(self, session: PuzzleSession) -> Tuple[List[str], str]:
        """
        Get a simple recommendation for the given session.

        This simplified implementation returns the first four remaining words
        as the recommended word group and a fixed explanation string.

        Returns:
            Tuple of (recommended_words, recommended_connection)
        """
        remaining_words = session.get_remaining_words()

        # If there aren't at least 4 remaining words, return empty results
        if len(remaining_words) < 4:
            return [], ""

        # Recommend the first four remaining words (simple deterministic fallback)
        recommended_word_group = list(remaining_words[:4])

        # Fixed human-readable explanation for why these words are grouped
        recommended_connection = "this is the connection reason"

        return recommended_word_group, recommended_connection

    # NOTE: Scoring helper methods were removed — recommendation is a simple
    # deterministic selection of the first four remaining words. If you want
    # to reintroduce scoring later, these helpers can be added back.

    def get_hint(self, session: PuzzleSession, words: List[str]) -> Optional[str]:
        """
        Get a hint about why these words might belong together.

        This is a simple implementation that provides basic hints.
        """
        if len(words) != 4:
            return None

        # Check for obvious category matches
        for category, category_words in self.category_patterns.items():
            matches = sum(1 for word in words if word.lower() in category_words)
            if matches >= 3:
                return f"These might be related to {category.replace('_', ' ')}"

        # Check for pattern matches
        for suffix in self.suffix_patterns:
            suffix_matches = sum(1 for word in words if word.lower().endswith(suffix))
            if suffix_matches >= 3:
                return f"Most of these words end with '{suffix}'"

        # Check for length similarity
        lengths = [len(word) for word in words]
        if len(set(lengths)) == 1:
            return f"All these words have {lengths[0]} letters"

        # Check for alphabetical patterns
        first_letters = sorted([word[0].lower() for word in words])
        if len(set(first_letters)) == len(first_letters):  # All different
            ascii_values = [ord(letter) for letter in first_letters]
            if max(ascii_values) - min(ascii_values) <= 3:
                return "These words start with consecutive letters"

        return "Look for what these words have in common"


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
