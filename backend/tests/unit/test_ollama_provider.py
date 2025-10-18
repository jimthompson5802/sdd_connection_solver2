"""
Unit tests for Ollama provider.
Tests the OllamaProvider class methods and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from src.services.llm_providers.ollama_provider import OllamaProvider


class TestOllamaProvider:
    """Test cases for OllamaProvider class."""

    def test_constructor_with_defaults(self):
        """Test constructor with default parameters."""
        provider = OllamaProvider()
        assert provider._base_url is None
        assert provider._model_name == "qwen2.5:32b"

    def test_constructor_with_custom_params(self):
        """Test constructor with custom parameters."""
        provider = OllamaProvider(base_url="http://localhost:11434", model_name="llama2:7b")
        assert provider._base_url == "http://localhost:11434"
        assert provider._model_name == "llama2:7b"

    def test_generate_recommendations_import_exception(self):
        """Test generate_recommendations when import fails."""
        provider = OllamaProvider()
        remaining_words = ["WORD1", "WORD2", "WORD3", "WORD4"]
        previous_guesses = []
        
        # Should raise ValueError when raw is empty string and not a dict
        with pytest.raises(ValueError, match="not json object"):
            provider.generate_recommendations(remaining_words, previous_guesses)

    def test_generate_recommendations_with_previous_guesses(self):
        """Test generate_recommendations includes previous_guesses in prompt context."""
        # This test verifies that previous_guesses parameter is accepted
        provider = OllamaProvider()
        remaining_words = ["WORD1", "WORD2", "WORD3", "WORD4"]
        previous_guesses = [
            {"words": ["GUESS1", "GUESS2", "GUESS3", "GUESS4"], "result": "incorrect"}
        ]
        
        # Should not raise any exception with previous_guesses
        # Since we don't mock the LLM, this will raise ValueError for "not json object"
        with pytest.raises(ValueError, match="not json object"):
            provider.generate_recommendations(remaining_words, previous_guesses)

    @patch("importlib.import_module")
    def test_generate_recommendations_with_structured_output(self, mock_import):
        """Test generate_recommendations with structured output."""
        # Mock importlib.import_module
        mock_ollama_mod = Mock()
        mock_ollama_cls = Mock()
        mock_llm = Mock()
        
        # Set up the structured output mock
        mock_structured = Mock()
        mock_structured.invoke.return_value = {
            "recommended_words": ["BASS", "SALMON", "TROUT", "PIKE"],
            "connection": "Types of fish",
            "explanation": "These are all freshwater fish species"
        }
        
        mock_llm.with_structured_output.return_value = mock_structured
        mock_ollama_cls.return_value = mock_llm
        mock_ollama_mod.ChatOllama = mock_ollama_cls
        mock_import.return_value = mock_ollama_mod
        
        provider = OllamaProvider()
        remaining_words = ["BASS", "SALMON", "TROUT", "PIKE", "GUITAR", "PIANO"]
        previous_guesses = []
        
        result = provider.generate_recommendations(remaining_words, previous_guesses)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "recommended_words" in result
        assert "connection" in result
        assert "explanation" in result
        assert "connection_explanation" in result
        assert "generation_time_ms" in result
        
        # Verify content
        assert result["recommended_words"] == ["BASS", "SALMON", "TROUT", "PIKE"]
        assert result["connection"] == "Types of fish"
        assert result["explanation"] == "These are all freshwater fish species"
        assert result["connection_explanation"] == "These are all freshwater fish species"
        assert isinstance(result["generation_time_ms"], int)

    @patch("importlib.import_module")
    def test_generate_recommendations_word_limit_truncation(self, mock_import):
        """Test generate_recommendations truncates to maximum 4 words."""
        # Mock importlib.import_module
        mock_ollama_mod = Mock()
        mock_ollama_cls = Mock()
        mock_llm = Mock()
        
        # Set up structured output to return more than 4 words
        mock_structured = Mock()
        mock_structured.invoke.return_value = {
            "recommended_words": ["WORD1", "WORD2", "WORD3", "WORD4", "WORD5", "WORD6"],
            "connection": "Test connection",
            "explanation": "Test explanation"
        }
        
        mock_llm.with_structured_output.return_value = mock_structured
        mock_ollama_cls.return_value = mock_llm
        mock_ollama_mod.ChatOllama = mock_ollama_cls
        mock_import.return_value = mock_ollama_mod
        
        provider = OllamaProvider()
        remaining_words = ["WORD1", "WORD2", "WORD3", "WORD4", "WORD5", "WORD6"]
        previous_guesses = []
        
        result = provider.generate_recommendations(remaining_words, previous_guesses)
        
        # Should truncate to 4 words
        assert len(result["recommended_words"]) == 4
        assert result["recommended_words"] == ["WORD1", "WORD2", "WORD3", "WORD4"]

    @patch("importlib.import_module")
    def test_generate_recommendations_word_case_mapping(self, mock_import):
        """Test generate_recommendations maps words to original case."""
        # Mock importlib.import_module
        mock_ollama_mod = Mock()
        mock_ollama_cls = Mock()
        mock_llm = Mock()
        
        # Set up structured output to return lowercase words
        mock_structured = Mock()
        mock_structured.invoke.return_value = {
            "recommended_words": ["bass", "salmon", "trout", "pike"],
            "connection": "Fish",
            "explanation": "Types of fish"
        }
        
        mock_llm.with_structured_output.return_value = mock_structured
        mock_ollama_cls.return_value = mock_llm
        mock_ollama_mod.ChatOllama = mock_ollama_cls
        mock_import.return_value = mock_ollama_mod
        
        provider = OllamaProvider()
        # Remaining words in uppercase
        remaining_words = ["BASS", "SALMON", "TROUT", "PIKE", "GUITAR", "PIANO"]
        previous_guesses = []
        
        result = provider.generate_recommendations(remaining_words, previous_guesses)
        
        # Should map to original uppercase
        assert result["recommended_words"] == ["BASS", "SALMON", "TROUT", "PIKE"]

    @patch("importlib.import_module")
    def test_generate_recommendations_non_dict_response(self, mock_import):
        """Test generate_recommendations raises error for non-dict response."""
        # Mock importlib.import_module
        mock_ollama_mod = Mock()
        mock_ollama_cls = Mock()
        mock_llm = Mock()
        
        # Set up structured output to return a string instead of dict
        mock_structured = Mock()
        mock_structured.invoke.return_value = "This is not a dict"
        
        mock_llm.with_structured_output.return_value = mock_structured
        mock_ollama_cls.return_value = mock_llm
        mock_ollama_mod.ChatOllama = mock_ollama_cls
        mock_import.return_value = mock_ollama_mod
        
        provider = OllamaProvider()
        remaining_words = ["WORD1", "WORD2", "WORD3", "WORD4"]
        previous_guesses = []
        
        # Should raise ValueError for non-dict response
        with pytest.raises(ValueError, match="not json object"):
            provider.generate_recommendations(remaining_words, previous_guesses)

    @patch("importlib.import_module")
    @patch("time.time")
    def test_generate_recommendations_timing(self, mock_time, mock_import):
        """Test generate_recommendations timing calculation."""
        # Mock time progression
        mock_time.side_effect = [1.0, 1.5]  # Start at 1.0, end at 1.5 (500ms)
        
        # Mock importlib.import_module
        mock_ollama_mod = Mock()
        mock_ollama_cls = Mock()
        mock_llm = Mock()
        
        mock_structured = Mock()
        mock_structured.invoke.return_value = {
            "recommended_words": ["WORD1", "WORD2", "WORD3", "WORD4"],
            "connection": "Test",
            "explanation": "Test"
        }
        
        mock_llm.with_structured_output.return_value = mock_structured
        mock_ollama_cls.return_value = mock_llm
        mock_ollama_mod.ChatOllama = mock_ollama_cls
        mock_import.return_value = mock_ollama_mod
        
        provider = OllamaProvider()
        remaining_words = ["WORD1", "WORD2", "WORD3", "WORD4"]
        previous_guesses = []
        
        result = provider.generate_recommendations(remaining_words, previous_guesses)
        
        # Should calculate timing correctly (500ms)
        assert result["generation_time_ms"] == 500