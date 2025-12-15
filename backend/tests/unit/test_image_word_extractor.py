"""
Unit tests for ImageWordExtractor service.

Tests the LLM-based word extraction logic with mocked dependencies.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.image_word_extractor import ImageWordExtractor
from src.models import ImageSetupRequest, ExtractedWords


class TestImageWordExtractor:
    """Test suite for ImageWordExtractor service."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.extractor = ImageWordExtractor()

        self.valid_request = ImageSetupRequest(
            image_base64="dGVzdCBpbWFnZSBkYXRh",  # "test image data" in base64
            image_mime="image/png",
            provider_type="openai",
            model_name="gpt-4-vision-preview"
        )

        self.expected_words = [
            "apple", "banana", "cherry", "date",
            "elderberry", "fig", "grape", "honeydew",
            "kiwi", "lemon", "mango", "nectarine",
            "orange", "papaya", "quince", "raspberry"
        ]

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_success(self, mock_factory_class):
        """Test successful word extraction from image."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider

        mock_llm = MagicMock()
        mock_provider.llm = mock_llm

        # Mock the structured output response
        mock_extracted = ExtractedWords(words=self.expected_words, grid_detected=True)
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_extracted

        # Act
        result = await self.extractor.extract_words(self.valid_request)

        # Assert
        assert result == self.expected_words
        assert len(result) == 16

        # Verify factory was called with correct provider details
        mock_factory.create_provider.assert_called_once()
        call_args = mock_factory.create_provider.call_args
        provider_model = call_args[0][0]  # First argument should be LLMProvider model
        assert provider_model.provider_type == "openai"
        assert provider_model.model_name == "gpt-4-vision-preview"

        # Verify structured output was configured
        mock_llm.with_structured_output.assert_called_once_with(ExtractedWords)

        # Verify the invoke call was made
        mock_llm.with_structured_output.return_value.invoke.assert_called_once()

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_wrong_count_raises_error(self, mock_factory_class):
        """Test extraction with wrong word count raises ValueError."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider

        mock_llm = MagicMock()
        mock_provider.llm = mock_llm

        # Mock response with wrong number of words
        wrong_words = ["apple", "banana", "cherry"]  # Only 3 words instead of 16
        mock_extracted = MagicMock()
        mock_extracted.words = wrong_words
        mock_extracted.grid_detected = True
        mock_llm.with_structured_output.return_value.invoke.return_value = mock_extracted

        # Act & Assert
        with pytest.raises(ValueError, match="Expected 16 words"):
            await self.extractor.extract_words(self.valid_request)

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_no_vision_support_raises_error(self, mock_factory_class):
        """Test extraction with non-vision model raises RuntimeError."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider

        mock_llm = MagicMock()
        mock_provider.llm = mock_llm

        # Mock no vision support - with_structured_output doesn't exist
        mock_llm.with_structured_output = None

        # Act & Assert
        with pytest.raises(RuntimeError, match="does not support.*with_structured_output"):
            await self.extractor.extract_words(self.valid_request)

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_provider_creation_fails(self, mock_factory_class):
        """Test extraction with provider creation failure."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        # Mock provider creation failure
        mock_factory.create_provider.side_effect = Exception("Provider creation failed")

        # Act & Assert
        with pytest.raises(Exception, match="Provider creation failed"):
            await self.extractor.extract_words(self.valid_request)

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_llm_invocation_fails(self, mock_factory_class):
        """Test extraction with LLM invocation failure."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider

        mock_llm = MagicMock()
        mock_provider.llm = mock_llm

        # Mock LLM invocation failure
        mock_llm.with_structured_output.return_value.invoke.side_effect = Exception("LLM call failed")

        # Act & Assert
        with pytest.raises(Exception, match="LLM call failed"):
            await self.extractor.extract_words(self.valid_request)

    @patch('src.services.image_word_extractor.LLMProviderFactory')
    async def test_extract_words_empty_response_raises_error(self, mock_factory_class):
        """Test extraction with empty LLM response raises ValueError."""
        # Arrange
        mock_factory = MagicMock()
        mock_factory_class.return_value = mock_factory

        mock_provider = MagicMock()
        mock_factory.create_provider.return_value = mock_provider

        mock_llm = MagicMock()
        mock_provider.llm = mock_llm

        # Mock empty response
        mock_llm.with_structured_output.return_value.invoke.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="No words extracted"):
            await self.extractor.extract_words(self.valid_request)

    def test_vision_prompt_construction(self):
        """Test that vision prompts are constructed correctly."""
        # This test validates the 4-strategy prompt approach mentioned in the spec
        # We'll implement this as part of the actual implementation
        # For now, just verify the extractor can be instantiated
        extractor = ImageWordExtractor()
        assert extractor is not None

    async def test_base64_image_handling(self):
        """Test that base64 image data is handled correctly."""
        # This test will verify proper image data handling
        # Implementation will be added with the actual extract_words method
        extractor = ImageWordExtractor()
        assert extractor is not None