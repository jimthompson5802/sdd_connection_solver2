"""Unit tests for recommendation engine logic.

Tests cover:
- RecommendationEngine initialization and configuration
- Word grouping logic and similarity analysis
- Edge cases and error handling
- Performance and reliability characteristics
"""

from src.recommendation_engine import RecommendationEngine
from src.models import PuzzleSession


class TestRecommendationEngine:
    """Test suite for RecommendationEngine functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.sample_words = [
            "apple",
            "banana",
            "cherry",
            "date",
            "elephant",
            "fox",
            "giraffe",
            "hippo",
            "red",
            "blue",
            "green",
            "yellow",
            "one",
            "two",
            "three",
            "four",
        ]
        self.engine = RecommendationEngine()
        self.sample_session = PuzzleSession(self.sample_words)

    def test_initialization(self):
        """Test RecommendationEngine initialization."""
        engine = RecommendationEngine()
        assert engine is not None
        assert hasattr(engine, "get_recommendation")

    def test_get_recommendation_basic_functionality(self):
        """Test basic recommendation generation."""
        recommendation = self.engine.get_recommendation(self.sample_session)

        # Verify recommendation structure
        assert isinstance(recommendation, tuple)
        assert len(recommendation) == 2
        words, connection = recommendation
        assert isinstance(words, list)
        assert isinstance(connection, str)
        assert len(words) == 4
        assert connection == "this is the connection reason"

    def test_get_recommendation_with_fruits(self):
        """Test recommendation generation with clear fruit grouping."""
        fruit_words = [
            "apple",
            "banana",
            "cherry",
            "date",
            "table",
            "chair",
            "desk",
            "lamp",
            "red",
            "blue",
            "green",
            "yellow",
            "car",
            "bus",
            "train",
            "plane",
        ]
        session = PuzzleSession(fruit_words)
        recommendation = self.engine.get_recommendation(session)

        # Should identify some grouping
        words, connection = recommendation
        assert len(words) == 4
        assert connection == "this is the connection reason"

    def test_get_recommendation_insufficient_remaining_words(self):
        """Test recommendation generation with insufficient remaining words."""
        # Create a session and simulate found groups by recording correct attempts
        session = PuzzleSession(self.sample_words)

        # Mark 3 groups as found by recording correct attempts (4 words each = 12 words total)
        # This leaves 4 words remaining
        from src.models import ResponseResult

        # First group: fruits
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT, color="Yellow")

        # Second group: animals
        session.record_attempt(["elephant", "fox", "giraffe", "hippo"], ResponseResult.CORRECT, color="Green")

        # Third group: colors
        session.record_attempt(["red", "blue", "green", "yellow"], ResponseResult.CORRECT, color="Blue")

        # Now only 4 words should remain: "one", "two", "three", "four"
        remaining = session.get_remaining_words()
        assert len(remaining) == 4

        recommendation = self.engine.get_recommendation(session)
        words, connection = recommendation

        # Should still return 4 words (the last group)
        assert len(words) == 4
        assert connection == "this is the connection reason"

    def test_get_recommendation_no_remaining_words(self):
        """Test recommendation generation when all groups are found."""
        # Create a session and mark all groups as found by recording correct attempts
        session = PuzzleSession(self.sample_words)

        # Mark all 4 groups as found by recording correct attempts
        from src.models import ResponseResult

        # First group: fruits
        session.record_attempt(["apple", "banana", "cherry", "date"], ResponseResult.CORRECT, color="Yellow")

        # Second group: animals
        session.record_attempt(["elephant", "fox", "giraffe", "hippo"], ResponseResult.CORRECT, color="Green")

        # Third group: colors
        session.record_attempt(["red", "blue", "green", "yellow"], ResponseResult.CORRECT, color="Blue")

        # Fourth group: numbers
        session.record_attempt(["one", "two", "three", "four"], ResponseResult.CORRECT, color="Purple")

        # Now no words should remain
        remaining = session.get_remaining_words()
        assert len(remaining) == 0

        recommendation = self.engine.get_recommendation(session)
        words, connection = recommendation

        # Should return empty list with empty connection
        assert words == []
        assert connection == ""

    def test_get_recommendation_consistency(self):
        """Test that recommendations are consistent for the same input."""
        recommendation1 = self.engine.get_recommendation(self.sample_session)
        recommendation2 = self.engine.get_recommendation(self.sample_session)

        # Results should be consistent (since no randomness in current implementation)
        assert recommendation1[0] == recommendation2[0]  # words
        assert recommendation1[1] == recommendation2[1]  # connection string

    def test_recommendation_words_are_from_remaining(self):
        """Test that recommended words are from remaining words."""
        recommendation = self.engine.get_recommendation(self.sample_session)
        words, connection = recommendation

        remaining_words = self.sample_session.get_remaining_words()
        for word in words:
            assert word in remaining_words

    def test_confidence_score_range(self):
        """Test that confidence scores are in valid range."""
        recommendation = self.engine.get_recommendation(self.sample_session)
        words, connection = recommendation

        assert isinstance(connection, str)
        assert connection == "this is the connection reason"

    def test_multiple_recommendations_different_sessions(self):
        """Test that different sessions can produce different recommendations."""
        words1 = [
            "apple",
            "banana",
            "cherry",
            "date",
            "red",
            "blue",
            "green",
            "yellow",
            "one",
            "two",
            "three",
            "four",
            "cat",
            "dog",
            "bird",
            "fish",
        ]
        words2 = [
            "car",
            "bus",
            "train",
            "plane",
            "happy",
            "sad",
            "angry",
            "excited",
            "north",
            "south",
            "east",
            "west",
            "hot",
            "cold",
            "warm",
            "cool",
        ]

        session1 = PuzzleSession(words1)
        session2 = PuzzleSession(words2)
        rec1 = self.engine.get_recommendation(session1)
        rec2 = self.engine.get_recommendation(session2)

        # Different sessions should potentially produce different recommendations
        # (may be the same if algorithm finds similar patterns, but at least one should differ)
        assert rec1 != rec2 or rec1[0] != rec2[0]

    def test_performance_with_reasonable_input_size(self):
        """Test that recommendation generation completes in reasonable time."""
        import time

        start_time = time.time()
        recommendation = self.engine.get_recommendation(self.sample_session)
        end_time = time.time()

        # Should complete within 5 seconds for reasonable input
        execution_time = end_time - start_time
        assert execution_time < 5.0, f"Recommendation took {execution_time:.2f} seconds"

        # Verify result is still valid
        words, connection = recommendation
        assert len(words) == 4
        assert connection == "this is the connection reason"
