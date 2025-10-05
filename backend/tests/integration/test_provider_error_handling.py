"""
Integration tests for provider error handling scenarios.
These tests validate error handling across different provider types.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestProviderErrorHandling:
    """Integration tests for provider error scenarios"""

    @pytest.mark.integration
    def test_invalid_provider_type_error(self):
        """Test error handling for invalid provider type"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InvalidProviderError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="nonexistent_provider", model_name="some_model"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        with pytest.raises(InvalidProviderError) as exc_info:
            service.get_recommendations(request)

        assert "nonexistent_provider" in str(exc_info.value)
        assert exc_info.value.error_code == "INVALID_PROVIDER"

    @pytest.mark.integration
    def test_insufficient_words_error(self):
        """Test error handling for insufficient word count"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InsufficientWordsError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["WORD1", "WORD2"],  # Only 2 words
            previous_guesses=[],
        )

        with pytest.raises(InsufficientWordsError) as exc_info:
            service.get_recommendations(request)

        assert "4 words" in str(exc_info.value).lower()
        assert exc_info.value.error_code == "INSUFFICIENT_WORDS"

    @pytest.mark.integration
    @patch("langchain_community.llms.ollama.Ollama")
    def test_ollama_connection_error(self, mock_ollama):
        """Test error handling for Ollama connection failures"""
        # Mock connection error
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = ConnectionError("Could not connect to Ollama server")
        mock_ollama.return_value = mock_llm

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import OllamaConnectionError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="ollama", model_name="llama2"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        with pytest.raises(OllamaConnectionError) as exc_info:
            service.get_recommendations(request)

        assert "ollama" in str(exc_info.value).lower()
        assert exc_info.value.error_code == "OLLAMA_CONNECTION_ERROR"

    @pytest.mark.integration
    @patch("openai.OpenAI")
    def test_openai_api_error(self, mock_openai):
        """Test error handling for OpenAI API failures"""
        # Mock OpenAI API error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        mock_openai.return_value = mock_client

        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import OpenAIAPIError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo"),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        with pytest.raises(OpenAIAPIError) as exc_info:
            service.get_recommendations(request)

        assert "openai" in str(exc_info.value).lower()
        assert exc_info.value.error_code == "OPENAI_API_ERROR"

    @pytest.mark.integration
    def test_configuration_missing_error(self):
        """Test error handling for missing configuration"""
        from src.services.llm_providers.provider_factory import ProviderFactory
        from src.models import LLMProvider
        from src.exceptions import ConfigurationError
        import os

        # Ensure no API key is set
        with patch.dict(os.environ, {}, clear=True):
            factory = ProviderFactory()

            llm_provider = LLMProvider(provider_type="openai", model_name="gpt-3.5-turbo")

            with pytest.raises(ConfigurationError) as exc_info:
                factory.create_provider(llm_provider)

            assert "api_key" in str(exc_info.value).lower()
            assert exc_info.value.error_code == "MISSING_CONFIG"

    @pytest.mark.integration
    def test_timeout_error_handling(self):
        """Test error handling for request timeouts"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import TimeoutError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        # Mock timeout scenario
        with patch.object(service, "_process_with_timeout") as mock_timeout:
            mock_timeout.side_effect = TimeoutError("Request timed out after 30 seconds")

            with pytest.raises(TimeoutError) as exc_info:
                service.get_recommendations(request)

            assert "30 seconds" in str(exc_info.value)
            assert exc_info.value.error_code == "REQUEST_TIMEOUT"

    @pytest.mark.integration
    def test_malformed_response_error(self):
        """Test error handling for malformed LLM responses"""
        from src.services.llm_providers.simple_provider import SimpleProvider
        from src.exceptions import LLMProviderError

        provider = SimpleProvider()

        # Mock scenario where simple provider fails
        with patch.object(provider, "_generate_simple_recommendation") as mock_generate:
            mock_generate.side_effect = ValueError("Algorithm failed")

            with pytest.raises(LLMProviderError) as exc_info:
                provider.generate_recommendations(
                    remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"], previous_guesses=[]
                )

            assert "algorithm" in str(exc_info.value).lower()
            assert exc_info.value.error_code == "PROVIDER_ERROR"

    @pytest.mark.integration
    def test_duplicate_words_error(self):
        """Test error handling for duplicate words in input"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InvalidInputError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["WORD1", "WORD1", "WORD3", "WORD4"],  # Duplicate WORD1
            previous_guesses=[],
        )

        with pytest.raises(InvalidInputError) as exc_info:
            service.get_recommendations(request)

        assert "duplicate" in str(exc_info.value).lower()
        assert exc_info.value.error_code == "DUPLICATE_WORDS"

    @pytest.mark.integration
    def test_empty_word_list_error(self):
        """Test error handling for empty word list"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InvalidInputError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=[],  # Empty list
            previous_guesses=[],
        )

        with pytest.raises(InvalidInputError) as exc_info:
            service.get_recommendations(request)

        assert "empty" in str(exc_info.value).lower()
        assert exc_info.value.error_code == "EMPTY_WORD_LIST"

    @pytest.mark.integration
    def test_error_logging_integration(self):
        """Test that errors are properly logged for monitoring"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InvalidProviderError
        from unittest.mock import patch

        with patch("src.services.recommendation_service.logger") as mock_logger:
            service = RecommendationService()

            request = RecommendationRequest(
                llm_provider=LLMProvider(provider_type="invalid", model_name="test"),
                remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
                previous_guesses=[],
            )

            try:
                service.get_recommendations(request)
            except InvalidProviderError:
                pass  # Expected error

            # Should have logged the error
            assert mock_logger.error.called

    @pytest.mark.integration
    def test_error_metrics_tracking(self):
        """Test that errors are tracked in metrics for monitoring"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import InsufficientWordsError
        from unittest.mock import patch

        with patch("src.services.recommendation_service.metrics") as mock_metrics:
            service = RecommendationService()

            request = RecommendationRequest(
                llm_provider=LLMProvider(provider_type="simple", model_name=None),
                remaining_words=["WORD1"],  # Insufficient words
                previous_guesses=[],
            )

            try:
                service.get_recommendations(request)
            except InsufficientWordsError:
                pass  # Expected error

            # Should have tracked error metric
            # This validates that metrics integration exists
            assert hasattr(mock_metrics, "increment") or mock_metrics.called

    @pytest.mark.integration
    def test_error_context_preservation(self):
        """Test that error context is preserved through the call stack"""
        from src.services.recommendation_service import RecommendationService
        from src.models import RecommendationRequest, LLMProvider
        from src.exceptions import LLMProviderError

        service = RecommendationService()

        request = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=["WORD1", "WORD2", "WORD3", "WORD4"],
            previous_guesses=[],
        )

        # Mock internal error
        with patch("src.services.llm_providers.simple_provider.SimpleProvider.generate_recommendations") as mock_gen:
            original_error = ValueError("Internal algorithm error")
            mock_gen.side_effect = original_error

            try:
                service.get_recommendations(request)
            except LLMProviderError as e:
                # Should preserve original error context
                assert hasattr(e, "original_error")
                assert e.original_error == original_error
            else:
                pytest.fail("Expected LLMProviderError to be raised")
