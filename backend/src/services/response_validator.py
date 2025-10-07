"""
Response validation service for LLM output validation.
Ensures recommendations meet puzzle requirements and quality standards.
"""

from typing import List, Dict, Any, Set, Optional
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.guess_attempt import GuessAttempt


class ResponseValidatorService:
    """Service for validating LLM recommendation responses."""

    def __init__(self):
        """Initialize the response validator."""
        self.common_words = self._load_common_words()
        self.validation_rules = self._load_validation_rules()

    def _load_common_words(self) -> Set[str]:
        """Load common English words for validation."""
        # Basic word list - in a real implementation, this might come from a file
        return {
            "apple",
            "banana",
            "orange",
            "grape",
            "bass",
            "trout",
            "salmon",
            "flounder",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "dog",
            "cat",
            "bird",
            "fish",
            "car",
            "truck",
            "bike",
            "plane",
            "book",
            "pen",
            "paper",
            "desk",
            "chair",
            "table",
            "door",
            "window",
        }

    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules with weights and descriptions."""
        return {
            "word_count": {"weight": 1.0, "description": "Must have exactly 4 words", "critical": True},
            "word_uniqueness": {"weight": 1.0, "description": "All words must be unique", "critical": True},
            "word_format": {"weight": 0.8, "description": "Words should be valid English words", "critical": False},
            "explanation_quality": {
                "weight": 0.6,
                "description": "Should have meaningful explanation",
                "critical": False,
            },
            "confidence_range": {
                "weight": 0.4,
                "description": "Confidence score should be reasonable",
                "critical": False,
            },
            "no_repetition": {"weight": 0.7, "description": "Should not repeat previous guesses", "critical": False},
        }

    def validate_response(
        self, response: RecommendationResponse, previous_guesses: Optional[List[GuessAttempt]] = None
    ) -> Dict[str, Any]:
        """Validate a recommendation response comprehensively.

        Args:
            response: RecommendationResponse to validate.
            previous_guesses: List of previous guess attempts.

        Returns:
            Validation result with detailed feedback.
        """
        previous_guesses = previous_guesses or []

        validation_results = {}
        overall_score = 0.0
        total_weight = 0.0
        critical_failures = []

        # Run all validation checks
        for rule_name, rule_config in self.validation_rules.items():
            result = self._run_validation_rule(rule_name, response, previous_guesses)
            validation_results[rule_name] = result

            # Calculate weighted score
            rule_score = result["score"] * rule_config["weight"]
            overall_score += rule_score
            total_weight += rule_config["weight"]

            # Track critical failures
            if rule_config["critical"] and result["score"] < 0.5:
                critical_failures.append(rule_name)

        # Calculate final score
        final_score = overall_score / total_weight if total_weight > 0 else 0.0

        # Determine if response is valid
        is_valid = len(critical_failures) == 0 and final_score >= 0.6

        return {
            "valid": is_valid,
            "overall_score": final_score,
            "rule_results": validation_results,
            "critical_failures": critical_failures,
            "recommendations": self._generate_recommendations(validation_results),
            "summary": self._generate_summary(is_valid, final_score, critical_failures),
        }

    def _run_validation_rule(
        self, rule_name: str, response: RecommendationResponse, previous_guesses: List[GuessAttempt]
    ) -> Dict[str, Any]:
        """Run a specific validation rule.

        Args:
            rule_name: Name of the validation rule.
            response: Response to validate.
            previous_guesses: Previous guess attempts.

        Returns:
            Rule validation result.
        """
        if rule_name == "word_count":
            return self._validate_word_count(response.recommended_words)
        elif rule_name == "word_uniqueness":
            return self._validate_word_uniqueness(response.recommended_words)
        elif rule_name == "word_format":
            return self._validate_word_format(response.recommended_words)
        elif rule_name == "explanation_quality":
            return self._validate_explanation_quality(response.connection_explanation)
        elif rule_name == "confidence_range":
            return self._validate_confidence_range(response.confidence_score)
        elif rule_name == "no_repetition":
            return self._validate_no_repetition(response.recommended_words, previous_guesses)
        else:
            return {"score": 1.0, "feedback": "Unknown rule", "details": {}}

    def _validate_word_count(self, words: List[str]) -> Dict[str, Any]:
        """Validate that exactly 4 words are provided."""
        score = 1.0 if len(words) == 4 else 0.0
        return {
            "score": score,
            "feedback": f"Expected 4 words, got {len(words)}",
            "details": {"word_count": len(words), "expected": 4},
        }

    def _validate_word_uniqueness(self, words: List[str]) -> Dict[str, Any]:
        """Validate that all words are unique."""
        unique_words = set(word.lower() for word in words)
        score = 1.0 if len(unique_words) == len(words) else 0.0
        return {
            "score": score,
            "feedback": f"Found {len(words) - len(unique_words)} duplicate words",
            "details": {"unique_count": len(unique_words), "total_count": len(words)},
        }

    def _validate_word_format(self, words: List[str]) -> Dict[str, Any]:
        """Validate word format and check if they're real words."""
        valid_count = 0
        issues = []

        for word in words:
            word_lower = word.lower()

            # Check if word contains only letters
            if not word_lower.isalpha():
                issues.append(f"'{word}' contains non-letter characters")
                continue

            # Check minimum length
            if len(word_lower) < 2:
                issues.append(f"'{word}' is too short")
                continue

            # Check if it's a common word (basic check)
            if word_lower in self.common_words or len(word_lower) >= 3:
                valid_count += 1
            else:
                issues.append(f"'{word}' may not be a valid word")

        score = valid_count / len(words) if words else 0.0

        return {
            "score": score,
            "feedback": f"{valid_count}/{len(words)} words passed format validation",
            "details": {"valid_words": valid_count, "issues": issues},
        }

    def _validate_explanation_quality(self, explanation: Optional[str]) -> Dict[str, Any]:
        """Validate the quality of the connection explanation."""
        if not explanation:
            return {
                "score": 0.0,
                "feedback": "No explanation provided",
                "details": {"length": 0, "quality_indicators": []},
            }

        quality_score = 0.5  # Base score for having an explanation
        quality_indicators = []

        # Check length
        if len(explanation) > 10:
            quality_score += 0.2
            quality_indicators.append("adequate_length")

        # Check for connection words
        connection_keywords = ["all", "each", "type", "kind", "category", "group", "share", "common"]
        if any(keyword in explanation.lower() for keyword in connection_keywords):
            quality_score += 0.2
            quality_indicators.append("uses_connection_language")

        # Check for specificity
        if len(explanation.split()) > 5:
            quality_score += 0.1
            quality_indicators.append("detailed")

        return {
            "score": min(quality_score, 1.0),
            "feedback": f"Explanation quality: {len(quality_indicators)} quality indicators found",
            "details": {"length": len(explanation), "quality_indicators": quality_indicators},
        }

    def _validate_confidence_range(self, confidence: Optional[float]) -> Dict[str, Any]:
        """Validate that confidence score is in reasonable range."""
        if confidence is None:
            return {
                "score": 0.5,
                "feedback": "No confidence score provided",
                "details": {"confidence": None, "in_range": False},
            }

        in_range = 0.0 <= confidence <= 1.0
        reasonable = 0.1 <= confidence <= 0.9  # Not too extreme

        score = 1.0 if in_range else 0.0
        if in_range and reasonable:
            score = 1.0
        elif in_range:
            score = 0.7  # In range but extreme

        return {
            "score": score,
            "feedback": f"Confidence {confidence:.2f} is {'reasonable' if reasonable else 'extreme'}",
            "details": {"confidence": confidence, "in_range": in_range, "reasonable": reasonable},
        }

    def _validate_no_repetition(self, words: List[str], previous_guesses: List[GuessAttempt]) -> Dict[str, Any]:
        """Validate that words don't repeat previous unsuccessful guesses."""
        if not previous_guesses:
            return {
                "score": 1.0,
                "feedback": "No previous guesses to check against",
                "details": {"repeated_guesses": 0},
            }

        current_set = set(word.lower() for word in words)
        repeated_guesses = 0

        for guess in previous_guesses:
            guess_set = set(word.lower() for word in guess.words)
            if current_set == guess_set:
                repeated_guesses += 1

        score = 1.0 if repeated_guesses == 0 else max(0.0, 1.0 - (repeated_guesses * 0.5))

        return {
            "score": score,
            "feedback": f"Found {repeated_guesses} exact repetitions of previous guesses",
            "details": {"repeated_guesses": repeated_guesses},
        }

    def _generate_recommendations(self, validation_results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations based on validation results."""
        recommendations = []

        for rule_name, result in validation_results.items():
            if result["score"] < 0.8:
                rule_config = self.validation_rules[rule_name]
                recommendations.append(f"Improve {rule_name}: {rule_config['description']}")

        return recommendations

    def _generate_summary(self, is_valid: bool, score: float, critical_failures: List[str]) -> str:
        """Generate a summary of the validation results."""
        if is_valid:
            return f"Response is valid with score {score:.2f}"

        if critical_failures:
            return f"Response failed critical validations: {', '.join(critical_failures)}"

        return f"Response is below quality threshold (score: {score:.2f})"

    def quick_validate(self, words: List[str]) -> bool:
        """Quick validation for basic requirements.

        Args:
            words: List of words to validate.

        Returns:
            True if passes basic validation.
        """
        return (
            len(words) == 4
            and len(set(word.upper() for word in words)) == 4
            and all(word.isalpha() and len(word) > 1 for word in words)
        )

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation capabilities.

        Returns:
            Summary of validation rules and capabilities.
        """
        return {
            "total_rules": len(self.validation_rules),
            "critical_rules": [name for name, config in self.validation_rules.items() if config["critical"]],
            "validation_categories": ["format", "content", "quality", "uniqueness"],
            "common_words_count": len(self.common_words),
        }
