"""
Recommendation engine for suggesting word groups in NYT Connections puzzles.
Uses basic heuristics and pattern matching to suggest likely word groupings.
"""

from typing import List, Tuple, Optional
import random
from itertools import combinations
from collections import defaultdict, Counter

from .models import PuzzleSession, ResponseResult


class RecommendationEngine:
    """
    Engine for generating word group recommendations based on various heuristics.

    This is a simplified implementation that uses pattern matching, word similarity,
    and attempt history to suggest likely groupings. In a production system, this
    would use more sophisticated NLP and ML techniques.
    """

    def __init__(self):
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

    def get_recommendation(self, session: PuzzleSession) -> Tuple[List[str], float]:
        """
        Get the next best recommendation for the given session.

        Returns:
            Tuple of (recommended_words, confidence_score)
        """
        remaining_words = session.get_remaining_words()

        if len(remaining_words) < 4:
            return [], 0.0

        # Get all possible 4-word combinations
        all_combinations = list(combinations(remaining_words, 4))

        if not all_combinations:
            return [], 0.0

        # Score each combination based on various heuristics
        scored_combinations = []
        for combo in all_combinations:
            score = self._score_combination(list(combo), session)
            if score > 0:  # Only consider combinations with some potential
                scored_combinations.append((list(combo), score))

        if not scored_combinations:
            # Fallback to random selection if no good matches found
            random_combo = random.choice(all_combinations)
            return list(random_combo), 0.1

        # Sort by score and return the best one
        scored_combinations.sort(key=lambda x: x[1], reverse=True)
        best_combo, best_score = scored_combinations[0]

        # Normalize confidence to 0-1 range
        confidence = min(best_score / 10.0, 1.0)

        return best_combo, confidence

    def _score_combination(self, words: List[str], session: PuzzleSession) -> float:
        """
        Score a combination of 4 words based on how likely they are to form a group.

        Higher scores indicate more likely groupings.
        """
        score = 0.0

        # Check for exact matches with known categories
        score += self._score_category_match(words) * 5.0

        # Check for pattern-based similarities
        score += self._score_pattern_similarity(words) * 3.0

        # Check for length similarities
        score += self._score_length_similarity(words) * 1.0

        # Check for alphabetical clustering
        score += self._score_alphabetical_clustering(words) * 0.5

        # Penalize combinations that were already tried incorrectly
        score -= self._score_previous_attempts(words, session) * 2.0

        # Bonus for combinations that avoid previously incorrect patterns
        score += self._score_avoidance_patterns(words, session) * 1.0

        return max(score, 0.0)

    def _score_category_match(self, words: List[str]) -> float:
        """Score based on matching known categories."""
        for category, category_words in self.category_patterns.items():
            matches = sum(1 for word in words if word.lower() in category_words)
            if matches >= 3:  # At least 3 words match a category
                return matches / 4.0
        return 0.0

    def _score_pattern_similarity(self, words: List[str]) -> float:
        """Score based on similar patterns (prefixes, suffixes, etc.)."""
        score = 0.0

        # Check suffix patterns
        for suffix, examples in self.suffix_patterns.items():
            suffix_matches = sum(1 for word in words if word.lower().endswith(suffix))
            if suffix_matches >= 3:
                score += suffix_matches / 4.0

        # Check prefix patterns (first 2-3 characters)
        for prefix_len in [2, 3]:
            if all(len(word) >= prefix_len for word in words):
                prefixes = [word[:prefix_len].lower() for word in words]
                if len(set(prefixes)) == 1:  # All same prefix
                    score += 1.0

        # Check for rhyming patterns (same ending sounds)
        endings = defaultdict(list)
        for word in words:
            if len(word) >= 3:
                ending = word[-2:].lower()
                endings[ending].append(word)

        for ending, ending_words in endings.items():
            if len(ending_words) >= 3:
                score += len(ending_words) / 4.0

        return score

    def _score_length_similarity(self, words: List[str]) -> float:
        """Score based on similar word lengths."""
        lengths = [len(word) for word in words]
        length_counter = Counter(lengths)

        # Bonus if most words have same length
        most_common_count = length_counter.most_common(1)[0][1]
        return most_common_count / 4.0

    def _score_alphabetical_clustering(self, words: List[str]) -> float:
        """Score based on alphabetical proximity."""
        first_letters = [word[0].lower() for word in words]
        first_letters.sort()

        # Check if letters are consecutive or close together
        ascii_values = [ord(letter) for letter in first_letters]
        max_gap = max(ascii_values) - min(ascii_values)

        if max_gap <= 3:  # Letters are close together
            return 1.0 if max_gap <= 1 else 0.5

        return 0.0

    def _score_previous_attempts(self, words: List[str], session: PuzzleSession) -> float:
        """Penalize combinations similar to previous incorrect attempts."""
        penalty = 0.0
        word_set = set(word.lower() for word in words)

        for attempt in session.attempts:
            if attempt.result == ResponseResult.INCORRECT:
                attempt_set = set(attempt.words)
                overlap = len(word_set.intersection(attempt_set))

                if overlap == 4:  # Exact same combination
                    penalty += 10.0
                elif overlap == 3:  # 3 out of 4 words same
                    penalty += 3.0
                elif overlap >= 2:  # 2 out of 4 words same
                    penalty += 1.0

        return penalty

    def _score_avoidance_patterns(self, words: List[str], session: PuzzleSession) -> float:
        """Bonus for avoiding patterns that led to mistakes."""
        if not session.attempts:
            return 0.0

        # Look for patterns in incorrect attempts
        incorrect_attempts = [attempt for attempt in session.attempts if attempt.result == ResponseResult.INCORRECT]

        if not incorrect_attempts:
            return 0.0

        # Simple heuristic: avoid word combinations that share characteristics
        # with many incorrect attempts
        word_set = set(word.lower() for word in words)

        # Count how often each word appeared in incorrect attempts
        incorrect_word_frequency = Counter()
        for attempt in incorrect_attempts:
            for word in attempt.words:
                incorrect_word_frequency[word] += 1

        # Bonus if this combination uses words that weren't often incorrect
        total_incorrect_frequency = sum(incorrect_word_frequency.get(word, 0) for word in word_set)

        # Lower frequency in incorrect attempts = higher bonus
        if total_incorrect_frequency == 0:
            return 1.0
        elif total_incorrect_frequency <= 2:
            return 0.5
        else:
            return 0.0

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
