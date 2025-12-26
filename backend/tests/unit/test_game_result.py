"""
Unit tests for GameResult Pydantic model.

Tests cover validation rules and constraints:
- Field type validation
- Range constraints (count_groups_found: 0-4, count_mistakes: 0-4, total_guesses: minimum 1)
- puzzle_id UUID format validation
- puzzle_solved string validation ('true' or 'false')
- Optional field handling (LLM provider/model, result_id, created_at)
"""

import pytest
from pydantic import ValidationError

from src.game_result import GameResult


class TestGameResultValidation:
    """Test GameResult model validation rules."""

    def test_valid_game_result_with_all_fields(self):
        """Test creating a valid GameResult with all fields."""
        result = GameResult(
            result_id=1,
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="true",
            count_groups_found=4,
            count_mistakes=2,
            total_guesses=8,
            llm_provider_name="openai",
            llm_model_name="gpt-4",
            created_at="2025-12-24T15:30:05+00:00"
        )

        assert result.result_id == 1
        assert result.puzzle_id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.puzzle_solved == "true"
        assert result.count_groups_found == 4
        assert result.count_mistakes == 2
        assert result.total_guesses == 8
        assert result.llm_provider_name == "openai"
        assert result.llm_model_name == "gpt-4"

    def test_valid_game_result_without_optional_fields(self):
        """Test creating a valid GameResult without optional fields."""
        result = GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=2,
            count_mistakes=4,
            total_guesses=6
        )

        assert result.result_id is None
        assert result.llm_provider_name is None
        assert result.llm_model_name is None
        assert result.created_at is None

    def test_puzzle_solved_must_be_true_or_false_string(self):
        """Test that puzzle_solved only accepts 'true' or 'false'."""
        # Valid values
        GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="true",
            count_groups_found=4,
            count_mistakes=0,
            total_guesses=5
        )

        GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=2,
            count_mistakes=4,
            total_guesses=6
        )

        # Invalid values should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="yes",
                count_groups_found=4,
                count_mistakes=0,
                total_guesses=5
            )
        assert "puzzle_solved must be 'true' or 'false'" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="True",  # Capital T not allowed
                count_groups_found=4,
                count_mistakes=0,
                total_guesses=5
            )
        assert "puzzle_solved must be 'true' or 'false'" in str(exc_info.value)

    def test_count_groups_found_range_validation(self):
        """Test that count_groups_found must be between 0 and 4."""
        # Valid values: 0-4
        for count in range(5):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=count,
                count_mistakes=0,
                total_guesses=1
            )

        # Invalid: negative
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=-1,
                count_mistakes=0,
                total_guesses=1
            )

        # Invalid: > 4
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=5,
                count_mistakes=0,
                total_guesses=1
            )

    def test_count_mistakes_range_validation(self):
        """Test that count_mistakes must be between 0 and 4."""
        # Valid values: 0-4
        for count in range(5):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=count,
                total_guesses=1
            )

        # Invalid: negative
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=-1,
                total_guesses=1
            )

        # Invalid: > 4
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=5,
                total_guesses=1
            )

    def test_total_guesses_minimum_validation(self):
        """Test that total_guesses must be at least 1."""
        # Valid: minimum 1
        GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=0,
            count_mistakes=0,
            total_guesses=1
        )

        # Valid: larger values
        GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=0,
            count_mistakes=0,
            total_guesses=100
        )

        # Invalid: 0
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=0
            )

        # Invalid: negative
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=-1
            )

    def test_puzzle_id_must_be_valid_uuid(self):
        """Test that puzzle_id must be a valid UUID string."""
        # Valid UUID
        GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=0,
            count_mistakes=0,
            total_guesses=1
        )

        # Invalid UUID format (correct length but not valid UUID format)
        # UUID has format: 8-4-4-4-12 (36 chars with dashes)
        with pytest.raises(ValidationError) as exc_info:
            GameResult(
                puzzle_id="notvalid-uuid-format-36chars-xxxxxxx",  # Exactly 36 chars
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )
        assert "puzzle_id must be a valid UUID string" in str(exc_info.value)

    def test_puzzle_id_length_validation(self):
        """Test that puzzle_id must be exactly 36 characters."""
        # Too short
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )

        # Too long
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000-extra",
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )

    def test_required_fields_validation(self):
        """Test that required fields cannot be omitted."""
        # Missing puzzle_id
        with pytest.raises(ValidationError):
            GameResult(
                game_date="2025-12-24T15:30:00+00:00",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )

        # Missing game_date
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                puzzle_solved="false",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )

        # Missing puzzle_solved
        with pytest.raises(ValidationError):
            GameResult(
                puzzle_id="550e8400-e29b-41d4-a716-446655440000",
                game_date="2025-12-24T15:30:00+00:00",
                count_groups_found=0,
                count_mistakes=0,
                total_guesses=1
            )

    def test_game_result_serialization(self):
        """Test that GameResult can be serialized to dict."""
        result = GameResult(
            result_id=1,
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="true",
            count_groups_found=4,
            count_mistakes=2,
            total_guesses=8,
            llm_provider_name="openai",
            llm_model_name="gpt-4",
            created_at="2025-12-24T15:30:05+00:00"
        )

        data = result.model_dump()

        assert data["result_id"] == 1
        assert data["puzzle_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert data["puzzle_solved"] == "true"
        assert data["count_groups_found"] == 4
        assert data["count_mistakes"] == 2
        assert data["total_guesses"] == 8

    def test_game_result_json_serialization(self):
        """Test that GameResult can be serialized to JSON."""
        result = GameResult(
            result_id=1,
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="true",
            count_groups_found=4,
            count_mistakes=2,
            total_guesses=8,
            llm_provider_name="openai",
            llm_model_name="gpt-4"
        )

        json_str = result.model_dump_json()

        assert "550e8400-e29b-41d4-a716-446655440000" in json_str
        assert "true" in json_str
        assert "openai" in json_str

    def test_llm_fields_can_be_none(self):
        """Test that LLM provider and model fields can be None."""
        result = GameResult(
            puzzle_id="550e8400-e29b-41d4-a716-446655440000",
            game_date="2025-12-24T15:30:00+00:00",
            puzzle_solved="false",
            count_groups_found=2,
            count_mistakes=3,
            total_guesses=5,
            llm_provider_name=None,
            llm_model_name=None
        )

        assert result.llm_provider_name is None
        assert result.llm_model_name is None

    def test_game_result_example_schema(self):
        """Test that the example in Config is valid."""
        example = GameResult.model_config["json_schema_extra"]["example"]

        # Should be able to create a GameResult from the example
        result = GameResult(**example)

        assert result.result_id == 1
        assert result.puzzle_id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.puzzle_solved == "true"
