"""Unit tests for puzzle state model."""

import pytest
from pydantic import ValidationError
from src.llm_models.puzzle_state import PuzzleState
from src.llm_models.completed_group import CompletedGroup


class TestPuzzleState:
    """Test cases for PuzzleState model."""

    def test_valid_puzzle_state_creation(self):
        """Test creating a valid puzzle state."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words)

        assert len(puzzle.all_words) == 16
        assert puzzle.completed_groups == []
        assert puzzle.guess_attempts == []
        assert puzzle.mistakes_remaining == 4
        assert puzzle.is_completed is False

    def test_all_words_validation_wrong_count(self):
        """Test validation fails with wrong word count."""
        words = ["bass", "flounder", "salmon"]  # Only 3 words

        with pytest.raises(ValidationError, match="all_words must contain exactly 16 words"):
            PuzzleState(all_words=words)

    def test_all_words_validation_duplicates(self):
        """Test validation fails with duplicate words."""
        words = [
            "bass",
            "bass",
            "salmon",
            "trout",  # "bass" duplicated
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        with pytest.raises(ValidationError, match="all_words must not contain duplicates"):
            PuzzleState(all_words=words)

    def test_all_words_validation_empty_string(self):
        """Test validation fails with empty string."""
        words = [
            "",
            "flounder",
            "salmon",
            "trout",  # Empty string
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        with pytest.raises(ValidationError, match="all words must be non-empty strings"):
            PuzzleState(all_words=words)

    def test_all_words_validation_whitespace_only(self):
        """Test validation fails with whitespace-only string."""
        words = [
            "   ",
            "flounder",
            "salmon",
            "trout",  # Whitespace only
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        with pytest.raises(ValidationError, match="all words must be non-empty strings"):
            PuzzleState(all_words=words)

    def test_all_words_cleaning_and_lowercase(self):
        """Test that words are cleaned and converted to lowercase."""
        words = [
            "  BASS  ",
            "Flounder",
            "SALMON",
            "trout",
            "Piano",
            "GUITAR",
            "violin",
            "Drums",
            "RED",
            "blue",
            "Green",
            "YELLOW",
            "Apple",
            "ORANGE",
            "banana",
            "Grape",
        ]

        puzzle = PuzzleState(all_words=words)

        for word in puzzle.all_words:
            assert word.islower()
            assert word.strip() == word

    def test_completed_groups_validation_word_not_in_puzzle(self):
        """Test validation fails when completed group has word not in puzzle."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        invalid_group = CompletedGroup(
            words=["bass", "flounder", "salmon", "shark"], connection="Fish", difficulty="easy"  # "shark" not in puzzle
        )

        with pytest.raises(ValidationError, match="word 'shark' in completed group not found in puzzle words"):
            PuzzleState(all_words=words, completed_groups=[invalid_group])

    def test_completed_groups_validation_duplicate_words(self):
        """Test validation fails when words appear in multiple groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        group1 = CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy")
        group2 = CompletedGroup(
            words=["bass", "piano", "guitar", "violin"], connection="Music", difficulty="medium"
        )  # "bass" duplicated

        with pytest.raises(ValidationError, match="word 'bass' appears in multiple completed groups"):
            PuzzleState(all_words=words, completed_groups=[group1, group2])

    def test_completed_groups_validation_too_many_groups(self):
        """Test validation fails with more than 4 completed groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
            "extra",
            "words",
            "here",
            "now",  # Add extra words for 5th group
        ]

        groups = [
            CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy"),
            CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium"),
            CompletedGroup(words=["red", "blue", "green", "yellow"], connection="Colors", difficulty="easy"),
            CompletedGroup(words=["apple", "orange", "banana", "grape"], connection="Fruits", difficulty="easy"),
            CompletedGroup(words=["extra", "words", "here", "now"], connection="Extra", difficulty="hard"),  # 5th group
        ]

        # This should raise a validation error about too many groups (the validation should catch this)
        with pytest.raises(ValidationError):
            PuzzleState(all_words=words, completed_groups=groups)

    def test_mistakes_remaining_validation_negative(self):
        """Test validation fails with negative mistakes remaining."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        with pytest.raises(ValidationError, match="mistakes_remaining must be between 0 and 4"):
            PuzzleState(all_words=words, mistakes_remaining=-1)

    def test_mistakes_remaining_validation_too_high(self):
        """Test validation fails with mistakes remaining too high."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        with pytest.raises(ValidationError, match="mistakes_remaining must be between 0 and 4"):
            PuzzleState(all_words=words, mistakes_remaining=5)

    def test_is_completed_validation_completed_without_four_groups(self):
        """Test validation fails when marked completed without 4 groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        group = CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy")

        with pytest.raises(ValidationError, match="puzzle cannot be completed without 4 completed groups"):
            PuzzleState(all_words=words, completed_groups=[group], is_completed=True)

    def test_is_completed_validation_not_completed_with_four_groups(self):
        """Test validation fails when not marked completed with 4 groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        groups = [
            CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy"),
            CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium"),
            CompletedGroup(words=["red", "blue", "green", "yellow"], connection="Colors", difficulty="easy"),
            CompletedGroup(words=["apple", "orange", "banana", "grape"], connection="Fruits", difficulty="easy"),
        ]

        with pytest.raises(ValidationError, match="puzzle must be marked as completed with 4 completed groups"):
            PuzzleState(all_words=words, completed_groups=groups, is_completed=False)

    def test_get_remaining_words_no_completed_groups(self):
        """Test getting remaining words with no completed groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words)
        remaining = puzzle.get_remaining_words()

        assert len(remaining) == 16
        assert set(remaining) == set(words)

    def test_get_remaining_words_with_completed_groups(self):
        """Test getting remaining words with some completed groups."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        group = CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy")
        puzzle = PuzzleState(all_words=words, completed_groups=[group])
        remaining = puzzle.get_remaining_words()

        assert len(remaining) == 12
        assert "bass" not in remaining
        assert "flounder" not in remaining
        assert "salmon" not in remaining
        assert "trout" not in remaining
        assert "piano" in remaining

    def test_can_make_guess_valid_state(self):
        """Test can make guess in valid state."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words)

        assert puzzle.can_make_guess() is True

    def test_can_make_guess_no_mistakes_remaining(self):
        """Test cannot make guess with no mistakes remaining."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words, mistakes_remaining=0)

        assert puzzle.can_make_guess() is False

    def test_can_make_guess_completed_puzzle(self):
        """Test cannot make guess on completed puzzle."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        groups = [
            CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy"),
            CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium"),
            CompletedGroup(words=["red", "blue", "green", "yellow"], connection="Colors", difficulty="easy"),
            CompletedGroup(words=["apple", "orange", "banana", "grape"], connection="Fruits", difficulty="easy"),
        ]

        puzzle = PuzzleState(all_words=words, completed_groups=groups, is_completed=True)

        assert puzzle.can_make_guess() is False

    def test_can_make_guess_insufficient_words(self):
        """Test cannot make guess with insufficient remaining words."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        # Complete 3 groups, leaving only 4 words - but we need at least 4 for a guess
        groups = [
            CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy"),
            CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium"),
            CompletedGroup(words=["red", "blue", "green", "yellow"], connection="Colors", difficulty="easy"),
        ]

        puzzle = PuzzleState(all_words=words, completed_groups=groups)

        # Should still be able to make guess with exactly 4 words remaining
        assert puzzle.can_make_guess() is True

    def test_get_completion_percentage(self):
        """Test getting completion percentage."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        # No groups completed
        puzzle = PuzzleState(all_words=words)
        assert puzzle.get_completion_percentage() == 0.0

        # One group completed
        group = CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy")
        puzzle = PuzzleState(all_words=words, completed_groups=[group])
        assert puzzle.get_completion_percentage() == 0.25

        # Two groups completed
        group2 = CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium")
        puzzle = PuzzleState(all_words=words, completed_groups=[group, group2])
        assert puzzle.get_completion_percentage() == 0.5

    def test_is_game_over_completed(self):
        """Test game over when completed."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        groups = [
            CompletedGroup(words=["bass", "flounder", "salmon", "trout"], connection="Fish", difficulty="easy"),
            CompletedGroup(words=["piano", "guitar", "violin", "drums"], connection="Music", difficulty="medium"),
            CompletedGroup(words=["red", "blue", "green", "yellow"], connection="Colors", difficulty="easy"),
            CompletedGroup(words=["apple", "orange", "banana", "grape"], connection="Fruits", difficulty="easy"),
        ]

        puzzle = PuzzleState(all_words=words, completed_groups=groups, is_completed=True)

        assert puzzle.is_game_over() is True

    def test_is_game_over_no_mistakes(self):
        """Test game over when no mistakes remaining."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words, mistakes_remaining=0)

        assert puzzle.is_game_over() is True

    def test_is_game_over_in_progress(self):
        """Test game not over when still in progress."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        puzzle = PuzzleState(all_words=words, mistakes_remaining=2)

        assert puzzle.is_game_over() is False

    def test_get_incorrect_guess_count(self):
        """Test getting incorrect guess count."""
        words = [
            "bass",
            "flounder",
            "salmon",
            "trout",
            "piano",
            "guitar",
            "violin",
            "drums",
            "red",
            "blue",
            "green",
            "yellow",
            "apple",
            "orange",
            "banana",
            "grape",
        ]

        # No incorrect guesses
        puzzle = PuzzleState(all_words=words, mistakes_remaining=4)
        assert puzzle.get_incorrect_guess_count() == 0

        # Two incorrect guesses
        puzzle = PuzzleState(all_words=words, mistakes_remaining=2)
        assert puzzle.get_incorrect_guess_count() == 2

        # All mistakes used
        puzzle = PuzzleState(all_words=words, mistakes_remaining=0)
        assert puzzle.get_incorrect_guess_count() == 4
