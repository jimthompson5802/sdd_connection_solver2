"""
Contract tests for POST /api/v2/setup_puzzle_from_image endpoint.

These tests validate the API contract for image-based puzzle setup,
ensuring proper request validation and response format.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import base64
import json

from src.main import app
from src.models import ImageSetupResponse


client = TestClient(app)


class TestSetupPuzzleFromImageContract:
    """Test suite for image puzzle setup API contract."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Valid test image (minimal PNG in base64)
        self.valid_image_base64 = base64.b64encode(b"valid_png_data_here").decode('utf-8')
        self.valid_request = {
            "image_base64": self.valid_image_base64,
            "image_mime": "image/png",
            "provider_type": "openai", 
            "model_name": "gpt-4-vision-preview"
        }
        
        # Expected successful response
        self.expected_words = [
            "apple", "banana", "cherry", "date",
            "elderberry", "fig", "grape", "honeydew", 
            "kiwi", "lemon", "mango", "nectarine",
            "orange", "papaya", "quince", "raspberry"
        ]
    
    @patch('src.services.image_word_extractor.ImageWordExtractor.extract_words')
    def test_successful_image_setup(self, mock_extract_words):
        """Test successful image setup returns 200 with correct response structure."""
        # Arrange
        mock_extract_words.return_value = self.expected_words
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=self.valid_request)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure matches ImageSetupResponse model
        assert "remaining_words" in data
        assert "status" in data
        assert data["status"] == "success"
        assert len(data["remaining_words"]) == 16
        assert data["remaining_words"] == self.expected_words
        assert "message" not in data or data["message"] is None
        
        # Verify the mock was called with correct arguments
        mock_extract_words.assert_called_once()
        call_args = mock_extract_words.call_args[0][0]  # First positional argument
        assert call_args.image_base64 == self.valid_image_base64
        assert call_args.image_mime == "image/png"
        assert call_args.provider_type == "openai"
        assert call_args.model_name == "gpt-4-vision-preview"

    def test_missing_image_base64_returns_422(self):
        """Test missing image_base64 field returns 422 validation error."""
        # Arrange
        invalid_request = {
            "image_mime": "image/png",
            "provider_type": "openai",
            "model_name": "gpt-4-vision-preview"
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
    def test_missing_image_mime_returns_422(self):
        """Test missing image_mime field returns 422 validation error."""
        # Arrange
        invalid_request = {
            "image_base64": self.valid_image_base64,
            "provider_type": "openai", 
            "model_name": "gpt-4-vision-preview"
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_missing_provider_type_returns_422(self):
        """Test missing provider_type field returns 422 validation error."""
        # Arrange  
        invalid_request = {
            "image_base64": self.valid_image_base64,
            "image_mime": "image/png",
            "model_name": "gpt-4-vision-preview"
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_missing_model_name_returns_422(self):
        """Test missing model_name field returns 422 validation error."""
        # Arrange
        invalid_request = {
            "image_base64": self.valid_image_base64,
            "image_mime": "image/png", 
            "provider_type": "openai"
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
    
    def test_invalid_mime_type_returns_422(self):
        """Test invalid MIME type returns 422 validation error."""
        # Arrange
        invalid_request = {
            **self.valid_request,
            "image_mime": "text/plain"  # Invalid MIME type
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
    def test_invalid_provider_type_returns_422(self):
        """Test invalid provider type returns 422 validation error.""" 
        # Arrange
        invalid_request = {
            **self.valid_request,
            "provider_type": "invalid_provider"
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_oversized_image_returns_422(self):
        """Test oversized image (>5MB) returns 422 validation error."""
        # Arrange - create image that exceeds base64 size limit
        large_data = b"x" * 7000000  # > 6.67MB base64 limit
        large_image_base64 = base64.b64encode(large_data).decode('utf-8')
        
        invalid_request = {
            **self.valid_request,
            "image_base64": large_image_base64
        }
        
        # Act  
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
    @patch('src.services.image_word_extractor.ImageWordExtractor.extract_words')
    def test_extraction_failure_returns_400(self, mock_extract_words):
        """Test LLM extraction failure returns 400 with error message."""
        # Arrange
        mock_extract_words.side_effect = ValueError("Could not extract 16 words from image")
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=self.valid_request)
        
        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data

    @patch('src.services.image_word_extractor.ImageWordExtractor.extract_words')
    def test_provider_failure_returns_500(self, mock_extract_words):
        """Test LLM provider failure returns 500 with error message."""
        # Arrange
        mock_extract_words.side_effect = RuntimeError("LLM provider unavailable")
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=self.valid_request)
        
        # Assert
        assert response.status_code == 500
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data

    def test_payload_too_large_returns_413(self):
        """Test HTTP 413 for extremely large payload (simulated)."""
        # Arrange - create extremely large payload that would exceed server limits
        massive_data = b"x" * 10000000  # 10MB raw data
        massive_image_base64 = base64.b64encode(massive_data).decode('utf-8')
        
        invalid_request = {
            **self.valid_request,
            "image_base64": massive_image_base64
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert - should return 413 or 422 for validation failure
        assert response.status_code in [413, 422]
        
    @patch('src.services.image_word_extractor.ImageWordExtractor.extract_words')
    def test_wrong_word_count_returns_400(self, mock_extract_words):
        """Test HTTP 400 when LLM extracts wrong number of words."""
        # Arrange
        mock_extract_words.return_value = ["word1", "word2", "word3"]  # Only 3 words instead of 16
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=self.valid_request)
        
        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data
        
    def test_model_no_vision_returns_400(self):
        """Test HTTP 400 for non-vision model selection."""
        # Arrange
        invalid_request = {
            **self.valid_request,
            "model_name": "gpt-3.5-turbo"  # Non-vision model
        }
        
        # Act
        response = client.post("/api/v2/setup_puzzle_from_image", json=invalid_request)
        
        # Assert
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data