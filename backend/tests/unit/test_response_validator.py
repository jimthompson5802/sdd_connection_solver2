"""Unit tests for response validator service."""

from datetime import datetime
from src.services.response_validator import ResponseValidatorService
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.guess_attempt import GuessAttempt, GuessOutcome
from src.llm_models.llm_provider import LLMProvider


class TestResponseValidatorService:
    """Test cases for ResponseValidatorService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ResponseValidatorService()
        self.provider = LLMProvider(provider_type="simple")

    def _create_guess_attempt(self, words, outcome="incorrect"):
        """Helper to create GuessAttempt with required fields."""
        return GuessAttempt(
            words=words,
            outcome=GuessOutcome.INCORRECT if outcome == "incorrect" else GuessOutcome.CORRECT,
            timestamp=datetime.now(),
        )

    def _create_recommendation_response(self, words, explanation="test"):
        """Helper to create RecommendationResponse with required fields."""
        return RecommendationResponse(
            recommended_words=words, connection_explanation=explanation, provider_used=self.provider
        )

    def test_init(self):
        """Test service initialization."""
        assert isinstance(self.validator.common_words, set)
        assert len(self.validator.common_words) > 0
        assert isinstance(self.validator.validation_rules, dict)
        assert len(self.validator.validation_rules) > 0

    def test_load_common_words(self):
        """Test common words loading."""
        common_words = self.validator.common_words

        # Check for some expected words
        assert "apple" in common_words
        assert "bass" in common_words
        assert "red" in common_words
        assert "dog" in common_words

    def test_load_validation_rules(self):
        """Test validation rules loading."""
        rules = self.validator.validation_rules

        expected_rules = ["word_count", "word_uniqueness", "word_format", "explanation_quality", "no_repetition"]

        for rule in expected_rules:
            assert rule in rules
            assert "weight" in rules[rule]
            assert "description" in rules[rule]
            assert "critical" in rules[rule]

    def test_validate_word_count_correct(self):
        """Test word count validation with correct count."""
        result = self.validator._validate_word_count(["word1", "word2", "word3", "word4"])

        assert result["score"] == 1.0
        assert result["details"]["word_count"] == 4
        assert result["details"]["expected"] == 4

    def test_validate_word_count_incorrect(self):
        """Test word count validation with incorrect count."""
        result = self.validator._validate_word_count(["word1", "word2", "word3"])

        assert result["score"] == 0.0
        assert result["details"]["word_count"] == 3
        assert result["details"]["expected"] == 4

    def test_validate_word_uniqueness_all_unique(self):
        """Test word uniqueness validation with all unique words."""
        result = self.validator._validate_word_uniqueness(["apple", "banana", "orange", "grape"])

        assert result["score"] == 1.0
        assert result["details"]["unique_count"] == 4
        assert result["details"]["total_count"] == 4

    def test_validate_word_uniqueness_with_duplicates(self):
        """Test word uniqueness validation with duplicate words."""
        result = self.validator._validate_word_uniqueness(["apple", "banana", "apple", "grape"])

        assert result["score"] == 0.0
        assert result["details"]["unique_count"] == 3
        assert result["details"]["total_count"] == 4

    def test_validate_word_uniqueness_case_insensitive(self):
        """Test word uniqueness validation is case insensitive."""
        result = self.validator._validate_word_uniqueness(["Apple", "banana", "APPLE", "grape"])

        assert result["score"] == 0.0
        assert result["details"]["unique_count"] == 3
        assert result["details"]["total_count"] == 4

    def test_validate_word_format_valid_words(self):
        """Test word format validation with valid words."""
        result = self.validator._validate_word_format(["apple", "banana", "orange", "grape"])

        assert result["score"] == 1.0
        assert result["details"]["valid_words"] == 4
        assert len(result["details"]["issues"]) == 0

    def test_validate_word_format_invalid_characters(self):
        """Test word format validation with invalid characters."""
        result = self.validator._validate_word_format(["apple", "ban-ana", "orange123", "grape"])

        assert result["score"] < 1.0
        assert len(result["details"]["issues"]) == 2
        assert any("non-letter characters" in issue for issue in result["details"]["issues"])

    def test_validate_word_format_too_short(self):
        """Test word format validation with too short words."""
        result = self.validator._validate_word_format(["a", "banana", "orange", "grape"])

        assert result["score"] < 1.0
        assert any("too short" in issue for issue in result["details"]["issues"])

    def test_validate_word_format_empty_list(self):
        """Test word format validation with empty word list."""
        result = self.validator._validate_word_format([])

        assert result["score"] == 0.0
        assert result["details"]["valid_words"] == 0

    def test_validate_explanation_quality_good_explanation(self):
        """Test explanation quality validation with good explanation."""
        explanation = "All these words are types of fruits commonly found in grocery stores"
        result = self.validator._validate_explanation_quality(explanation)

        assert result["score"] > 0.5
        assert result["details"]["length"] == len(explanation)
        assert len(result["details"]["quality_indicators"]) > 0

    def test_validate_explanation_quality_no_explanation(self):
        """Test explanation quality validation with no explanation."""
        result = self.validator._validate_explanation_quality(None)

        assert result["score"] == 0.0
        assert result["details"]["length"] == 0

    def test_validate_explanation_quality_empty_explanation(self):
        """Test explanation quality validation with empty explanation."""
        result = self.validator._validate_explanation_quality("")

        assert result["score"] == 0.0
        assert result["details"]["length"] == 0

    def test_validate_explanation_quality_short_explanation(self):
        """Test explanation quality validation with short explanation."""
        result = self.validator._validate_explanation_quality("fruits")

        assert result["score"] == 0.5  # Base score only
        assert len(result["details"]["quality_indicators"]) == 0

    def test_validate_no_repetition_no_previous_guesses(self):
        """Test no repetition validation with no previous guesses."""
        result = self.validator._validate_no_repetition(["apple", "banana", "orange", "grape"], [])

        assert result["score"] == 1.0
        assert result["details"]["repeated_guesses"] == 0

    def test_validate_no_repetition_no_match(self):
        """Test no repetition validation with no matching previous guesses."""
        previous_guesses = [self._create_guess_attempt(["cat", "dog", "bird", "fish"])]
        result = self.validator._validate_no_repetition(["apple", "banana", "orange", "grape"], previous_guesses)

        assert result["score"] == 1.0
        assert result["details"]["repeated_guesses"] == 0

    def test_validate_no_repetition_exact_match(self):
        """Test no repetition validation with exact match."""
        previous_guesses = [self._create_guess_attempt(["apple", "banana", "orange", "grape"])]
        result = self.validator._validate_no_repetition(["apple", "banana", "orange", "grape"], previous_guesses)

        assert result["score"] < 1.0
        assert result["details"]["repeated_guesses"] == 1

    def test_validate_no_repetition_case_insensitive_match(self):
        """Test no repetition validation is case insensitive."""
        previous_guesses = [self._create_guess_attempt(["Apple", "Banana", "Orange", "Grape"])]
        result = self.validator._validate_no_repetition(["apple", "banana", "orange", "grape"], previous_guesses)

        assert result["score"] < 1.0
        assert result["details"]["repeated_guesses"] == 1

    def test_run_validation_rule_word_count(self):
        """Test running word count validation rule."""
        response = self._create_recommendation_response(["apple", "banana", "orange", "grape"])
        result = self.validator._run_validation_rule("word_count", response, [])

        assert result["score"] == 1.0

    def test_run_validation_rule_unknown_rule(self):
        """Test running unknown validation rule."""
        response = self._create_recommendation_response(["apple", "banana", "orange", "grape"])
        result = self.validator._run_validation_rule("unknown_rule", response, [])

        assert result["score"] == 1.0
        assert result["feedback"] == "Unknown rule"

    def test_validate_response_perfect_response(self):
        """Test validating a perfect response."""
        response = self._create_recommendation_response(
            ["apple", "banana", "orange", "grape"],
            "All these words are types of fruits commonly found in grocery stores",
        )

        result = self.validator.validate_response(response)

        assert result["valid"] is True
        assert result["overall_score"] > 0.6
        assert len(result["critical_failures"]) == 0
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["summary"], str)

    def test_validate_response_with_critical_failures(self):
        """Test validating a response with critical failures using direct method."""
        # Test word count validation directly since model validation prevents invalid models
        result = self.validator._validate_word_count(["apple", "banana", "orange"])  # Only 3 words

        assert result["score"] == 0.0
        assert result["details"]["word_count"] == 3

    def test_validate_response_with_duplicates(self):
        """Test validating duplicate words using direct method."""
        # Test uniqueness validation directly since model validation prevents invalid models
        result = self.validator._validate_word_uniqueness(["apple", "banana", "apple", "grape"])

        assert result["score"] == 0.0
        assert result["details"]["unique_count"] == 3

    def test_validate_response_with_previous_guesses(self):
        """Test validating response with previous guesses provided."""
        previous_guesses = [self._create_guess_attempt(["cat", "dog", "bird", "fish"])]
        response = self._create_recommendation_response(["apple", "banana", "orange", "grape"], "All are fruits")

        result = self.validator.validate_response(response, previous_guesses)

        assert result["valid"] is True
        assert "no_repetition" in result["rule_results"]

    def test_generate_recommendations(self):
        """Test generating improvement recommendations."""
        validation_results = {
            "word_count": {"score": 0.5},
            "word_uniqueness": {"score": 0.9},
            "explanation_quality": {"score": 0.3},
        }

        recommendations = self.validator._generate_recommendations(validation_results)

        assert len(recommendations) == 2  # word_count and explanation_quality
        assert any("word_count" in rec for rec in recommendations)
        assert any("explanation_quality" in rec for rec in recommendations)

    def test_generate_summary_valid_response(self):
        """Test generating summary for valid response."""
        summary = self.validator._generate_summary(True, 0.85, [])

        assert "valid" in summary.lower()
        assert "0.85" in summary

    def test_generate_summary_critical_failures(self):
        """Test generating summary with critical failures."""
        summary = self.validator._generate_summary(False, 0.4, ["word_count", "word_uniqueness"])

        assert "failed critical validations" in summary.lower()
        assert "word_count" in summary
        assert "word_uniqueness" in summary

    def test_generate_summary_low_quality(self):
        """Test generating summary for low quality response."""
        summary = self.validator._generate_summary(False, 0.4, [])

        assert "below quality threshold" in summary.lower()
        assert "0.40" in summary

    def test_quick_validate_valid_words(self):
        """Test quick validation with valid words."""
        result = self.validator.quick_validate(["apple", "banana", "orange", "grape"])

        assert result is True

    def test_quick_validate_wrong_count(self):
        """Test quick validation with wrong word count."""
        result = self.validator.quick_validate(["apple", "banana", "orange"])

        assert result is False

    def test_quick_validate_duplicates(self):
        """Test quick validation with duplicate words."""
        result = self.validator.quick_validate(["apple", "banana", "APPLE", "grape"])

        assert result is False

    def test_quick_validate_invalid_characters(self):
        """Test quick validation with invalid characters."""
        result = self.validator.quick_validate(["apple", "ban-ana", "orange", "grape"])

        assert result is False

    def test_quick_validate_too_short(self):
        """Test quick validation with too short words."""
        result = self.validator.quick_validate(["a", "banana", "orange", "grape"])

        assert result is False

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        summary = self.validator.get_validation_summary()

        assert "total_rules" in summary
        assert "critical_rules" in summary
        assert "validation_categories" in summary
        assert "common_words_count" in summary

        assert summary["total_rules"] > 0
        assert len(summary["critical_rules"]) > 0
        assert len(summary["validation_categories"]) > 0
        assert summary["common_words_count"] > 0
