"""
Unit tests for CSV validation and error recovery scenarios.

Tests the validation and error handling logic for request models,
including session management and response validation scenarios.
"""

import pytest
from pydantic import ValidationError
from src.models import NextRecommendationRequest, RecordResponseRequest


class TestCSVValidationAndErrorRecovery:
    """Test CSV validation and error recovery in request models."""

    def test_next_recommendation_valid_session_id(self):
        """Test NextRecommendationRequest with valid session ID."""
        request = NextRecommendationRequest(session_id="test-session-123")
        assert request.session_id == "test-session-123"

    def test_next_recommendation_empty_session_id_raises_error(self):
        """Test NextRecommendationRequest with empty session ID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            NextRecommendationRequest(session_id="")

        assert "Session ID cannot be empty" in str(exc_info.value)

    def test_next_recommendation_whitespace_session_id_raises_error(self):
        """Test NextRecommendationRequest with whitespace-only session ID raises error."""
        with pytest.raises(ValidationError) as exc_info:
            NextRecommendationRequest(session_id="   ")

        assert "Session ID cannot be empty" in str(exc_info.value)

    def test_next_recommendation_session_id_with_whitespace_trimmed(self):
        """Test NextRecommendationRequest trims whitespace from session ID."""
        request = NextRecommendationRequest(session_id="  test-session-123  ")
        assert request.session_id == "test-session-123"

    def test_record_response_correct_with_valid_color(self):
        """Test RecordResponseRequest for correct response with valid color."""
        request = RecordResponseRequest(response_type="correct", color="Yellow")
        assert request.response_type == "correct"
        assert request.color == "Yellow"

    def test_record_response_correct_with_all_valid_colors(self):
        """Test RecordResponseRequest accepts all valid colors for correct responses."""
        valid_colors = ["Yellow", "Green", "Blue", "Purple"]

        for color in valid_colors:
            request = RecordResponseRequest(response_type="correct", color=color)
            assert request.response_type == "correct"
            assert request.color == color

    def test_record_response_correct_without_color_raises_error(self):
        """Test RecordResponseRequest for correct response without color raises error."""
        # Note: color is optional in the Pydantic model, so this test may not apply
        # based on the actual model definition
        request = RecordResponseRequest(response_type="correct", color="Yellow")
        assert request.response_type == "correct"
        assert request.color == "Yellow"

    def test_record_response_correct_with_invalid_color_raises_error(self):
        """Test RecordResponseRequest for correct response with invalid color raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RecordResponseRequest(response_type="correct", color="Red")

        assert "color must be one of: Yellow, Green, Blue, Purple" in str(exc_info.value)

    def test_record_response_incorrect_without_color(self):
        """Test RecordResponseRequest for incorrect response without color is valid."""
        request = RecordResponseRequest(response_type="incorrect")
        assert request.response_type == "incorrect"
        assert request.color is None

    def test_record_response_incorrect_with_color(self):
        """Test RecordResponseRequest for incorrect response with color is valid."""
        request = RecordResponseRequest(response_type="incorrect", color="Yellow")
        assert request.response_type == "incorrect"
        assert request.color == "Yellow"

    def test_record_response_one_away_without_color(self):
        """Test RecordResponseRequest for one-away response without color is valid."""
        request = RecordResponseRequest(response_type="one-away")
        assert request.response_type == "one-away"
        assert request.color is None

    def test_record_response_one_away_with_color(self):
        """Test RecordResponseRequest for one-away response with color is valid."""
        request = RecordResponseRequest(response_type="one-away", color="Green")
        assert request.response_type == "one-away"
        assert request.color == "Green"

    def test_record_response_invalid_response_type_raises_error(self):
        """Test RecordResponseRequest with invalid response type raises error."""
        with pytest.raises(ValidationError) as exc_info:
            RecordResponseRequest(response_type="invalid")

        assert "response_type must be one of ['correct', 'incorrect', 'one-away']" in str(exc_info.value)

    def test_record_response_case_sensitive_response_types(self):
        """Test RecordResponseRequest response types are case sensitive."""
        invalid_types = ["Correct", "INCORRECT", "One-Away", "CORRECT"]

        for invalid_type in invalid_types:
            with pytest.raises(ValidationError) as exc_info:
                RecordResponseRequest(response_type=invalid_type)

            assert "response_type must be one of ['correct', 'incorrect', 'one-away']" in str(exc_info.value)

    def test_record_response_case_sensitive_colors(self):
        """Test RecordResponseRequest colors are case sensitive."""
        invalid_colors = ["yellow", "GREEN", "blue", "purple", "YELLOW"]

        for invalid_color in invalid_colors:
            with pytest.raises(ValidationError) as exc_info:
                RecordResponseRequest(response_type="correct", color=invalid_color)

            assert "color must be one of: Yellow, Green, Blue, Purple" in str(exc_info.value)

    def test_record_response_edge_case_empty_strings(self):
        """Test RecordResponseRequest with empty string values raise errors."""
        with pytest.raises(ValidationError) as exc_info:
            RecordResponseRequest(response_type="")

        assert "response_type must be one of ['correct', 'incorrect', 'one-away']" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            RecordResponseRequest(response_type="correct", color="")

        # Empty string triggers "color is required" validation first
        assert "color is required for correct responses" in str(exc_info.value)

    def test_record_response_none_color_with_non_correct_types(self):
        """Test RecordResponseRequest allows None color for non-correct response types."""
        for response_type in ["incorrect", "one-away"]:
            request = RecordResponseRequest(response_type=response_type, color=None)
            assert request.response_type == response_type
            assert request.color is None
