"""Unit tests for OpenAI Service."""

import pytest
from unittest.mock import Mock, patch
from src.services.openai_service import OpenAIService
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider, LLMRecommendationResponse
from src.exceptions import LLMProviderError


class TestOpenAIService:
    """Test cases for OpenAI Service."""

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_initialization(self, mock_prompt_service, mock_get_provider_factory):
        """Test OpenAI service initialization."""
        mock_factory = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt = Mock()
        mock_prompt_service.return_value = mock_prompt

        service = OpenAIService()

        assert service.provider_factory is mock_factory
        assert service.prompt_service is mock_prompt

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    @patch("time.time")
    def test_generate_recommendation_success(self, mock_time, mock_prompt_service, mock_get_provider_factory):
        """Test successful recommendation generation."""
        # Setup mocks
        mock_time.side_effect = [1000, 1002]  # 2 second generation time
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider

        # Mock LLM response
        mock_llm_response = LLMRecommendationResponse(
            recommendations=["bass", "flounder", "salmon", "trout"],
            connection="Types of fish",
            explanation="These are all types of fish commonly found in waters.",
        )
        mock_provider.generate_recommendation.return_value = mock_llm_response

        # Mock prompt service
        mock_prompt_svc.generate_recommendation_prompt.return_value = "base prompt"
        mock_prompt_svc.add_provider_specific_instructions.return_value = "enhanced prompt"

        service = OpenAIService()
        request = RecommendationRequest(
            remaining_words=["bass", "flounder", "salmon", "trout", "guitar", "piano"],
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
        )

        result = service.generate_recommendation(request)

        assert isinstance(result, RecommendationResponse)
        assert result.recommended_words == ["bass", "flounder", "salmon", "trout"]
        assert result.connection_explanation == "Types of fish"
        assert result.provider_used.provider_type == "openai"
        assert result.generation_time_ms == 2000

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_generate_recommendation_provider_error(self, mock_prompt_service, mock_get_provider_factory):
        """Test recommendation generation with provider error."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider to raise ValueError
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider
        mock_provider.generate_recommendation.side_effect = ValueError("Invalid response format")

        # Mock prompt service
        mock_prompt_svc.generate_recommendation_prompt.return_value = "base prompt"
        mock_prompt_svc.add_provider_specific_instructions.return_value = "enhanced prompt"

        service = OpenAIService()
        request = RecommendationRequest(
            remaining_words=["bass", "flounder", "salmon", "trout"],
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
        )

        with pytest.raises(LLMProviderError) as exc_info:
            service.generate_recommendation(request)

        assert "OpenAI provider returned malformed response" in str(exc_info.value)
        assert exc_info.value.provider_type == "openai"
        assert exc_info.value.error_code == "MALFORMED_PROVIDER_RESPONSE"

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    @patch("os.getenv")
    def test_generate_recommendation_factory_fallback(
        self, mock_getenv, mock_prompt_service, mock_get_provider_factory
    ):
        """Test recommendation generation with factory fallback."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc
        mock_getenv.return_value = "test_api_key"

        # Mock factory to raise RuntimeError
        mock_factory.create_provider.side_effect = RuntimeError("Provider not configured")

        # Mock OpenAI provider
        with patch("src.services.llm_providers.openai_provider.OpenAIProvider") as mock_openai_provider:
            mock_provider = Mock()
            mock_openai_provider.return_value = mock_provider

            mock_llm_response = LLMRecommendationResponse(
                recommendations=["bass", "flounder", "salmon", "trout"],
                connection="Types of fish",
                explanation="These are all types of fish commonly found in waters.",
            )
            mock_provider.generate_recommendation.return_value = mock_llm_response

            # Mock prompt service
            mock_prompt_svc.generate_recommendation_prompt.return_value = "base prompt"
            mock_prompt_svc.add_provider_specific_instructions.return_value = "enhanced prompt"

            service = OpenAIService()
            request = RecommendationRequest(
                remaining_words=["bass", "flounder", "salmon", "trout"],
                llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
            )

            result = service.generate_recommendation(request)

            assert isinstance(result, RecommendationResponse)
            mock_openai_provider.assert_called_once_with(api_key="test_api_key", model_name="gpt-4o-mini")

    def test_add_structured_output_request(self):
        """Test adding structured output request to prompt."""
        service = OpenAIService()
        base_prompt = "This is a test prompt"

        result = service._add_structured_output_request(base_prompt)

        assert "This is a test prompt" in result
        assert "IMPORTANT: Format your response as follows:" in result
        assert "bass, flounder, salmon, trout" in result

    def test_extract_words_flexible_with_comma_pattern(self):
        """Test flexible word extraction with comma-separated pattern."""
        service = OpenAIService()
        # Create a response with few enough words that the word pattern doesn't match
        response = "bass, flounder, salmon, trout"

        result = service._extract_words_flexible(response)

        assert result == ["bass", "flounder", "salmon", "trout"]

    def test_extract_words_flexible_with_word_pattern(self):
        """Test flexible word extraction with word pattern."""
        service = OpenAIService()
        response = "The words are bass flounder salmon trout and they are fish"

        result = service._extract_words_flexible(response)

        assert result == ["the", "words", "are", "bass"]  # First 4 words, lowercased

    def test_extract_words_flexible_fallback(self):
        """Test flexible word extraction fallback."""
        service = OpenAIService()
        # Response with fewer than 4 words and no comma pattern
        response = "No valid"

        result = service._extract_words_flexible(response)

        assert result == ["bass", "flounder", "salmon", "trout"]  # Fallback

    def test_extract_explanation_basic(self):
        """Test explanation extraction."""
        service = OpenAIService()
        response = "These are all types of fish.\nbass, flounder, salmon, trout"
        words = ["bass", "flounder", "salmon", "trout"]

        result = service._extract_explanation(response, words)

        assert "These are all types of fish." in result
        assert "bass, flounder, salmon, trout" not in result

    def test_extract_explanation_with_cleanup(self):
        """Test explanation extraction with cleanup."""
        service = OpenAIService()
        response = """Format: Please answer this
        These are all types of fish.
        They swim in water.
        Example: Like this
        bass, flounder, salmon, trout"""
        words = ["bass", "flounder", "salmon", "trout"]

        result = service._extract_explanation(response, words)

        assert "Format:" not in result
        assert "Example:" not in result
        assert "These are all types of fish" in result

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_generate_detailed_explanation_success(self, mock_prompt_service, mock_get_provider_factory):
        """Test successful detailed explanation generation."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider
        mock_provider.generate_recommendation.return_value = "Detailed explanation about fish"

        # Mock prompt service
        mock_prompt_svc.generate_explanation_prompt.return_value = "explanation prompt"

        service = OpenAIService()
        words = ["bass", "flounder", "salmon", "trout"]
        connection = "Types of fish"

        result = service.generate_detailed_explanation(words, connection)

        assert result == "Detailed explanation about fish"
        mock_prompt_svc.generate_explanation_prompt.assert_called_once_with(words, connection)

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_generate_detailed_explanation_error(self, mock_prompt_service, mock_get_provider_factory):
        """Test detailed explanation generation with error."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider to raise error
        mock_factory.create_provider.side_effect = Exception("Provider error")

        service = OpenAIService()
        words = ["bass", "flounder", "salmon", "trout"]
        connection = "Types of fish"

        result = service.generate_detailed_explanation(words, connection)

        assert "Unable to generate detailed explanation" in result
        assert "Provider error" in result

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_validate_connection_success(self, mock_prompt_service, mock_get_provider_factory):
        """Test successful connection validation."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider
        mock_provider = Mock()
        mock_factory.create_provider.return_value = mock_provider
        mock_provider.generate_recommendation.return_value = "RATING: 8/10\nREASONING: Good connection\nVALID: YES"

        # Mock prompt service
        mock_prompt_svc.generate_validation_prompt.return_value = "validation prompt"

        service = OpenAIService()
        words = ["bass", "flounder", "salmon", "trout"]

        result = service.validate_connection(words)

        assert result["valid"] is True
        assert result["score"] == 0.8
        assert "Good connection" in result["explanation"]

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_validate_connection_error(self, mock_prompt_service, mock_get_provider_factory):
        """Test connection validation with error."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock provider to raise error
        mock_factory.create_provider.side_effect = Exception("Validation error")

        service = OpenAIService()
        words = ["bass", "flounder", "salmon", "trout"]

        result = service.validate_connection(words)

        assert result["valid"] is False
        assert result["score"] == 0.0
        assert "Validation failed" in result["explanation"]

    def test_parse_validation_response_complete(self):
        """Test parsing complete validation response."""
        service = OpenAIService()
        response = "RATING: 7/10\nREASONING: These are all fish species\nVALID: YES"

        result = service._parse_validation_response(response)

        assert result["valid"] is True
        assert result["score"] == 0.7
        assert "These are all fish species" in result["explanation"]

    def test_parse_validation_response_partial(self):
        """Test parsing partial validation response."""
        service = OpenAIService()
        response = "RATING: 3/10\nSome reasoning here"

        result = service._parse_validation_response(response)

        assert result["valid"] is False  # Score < 0.6
        assert result["score"] == 0.3

    def test_parse_validation_response_invalid(self):
        """Test parsing invalid validation response."""
        service = OpenAIService()
        response = "Invalid response format"

        result = service._parse_validation_response(response)

        assert result["valid"] is False
        assert result["score"] == 0.5  # Default score when no rating found
        assert result["explanation"] == "Invalid response format"

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    @patch("os.getenv")
    def test_generate_recommendation_factory_fallback_exception(
        self, mock_getenv, mock_prompt_service, mock_get_provider_factory
    ):
        """Test recommendation generation with factory fallback exception."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc
        mock_getenv.return_value = "test_api_key"

        # Mock factory to raise RuntimeError
        mock_factory.create_provider.side_effect = RuntimeError("Provider not configured")

        # Mock OpenAI provider to raise an exception during instantiation
        with patch("src.services.llm_providers.openai_provider.OpenAIProvider") as mock_openai_provider:
            mock_openai_provider.side_effect = Exception("Provider instantiation failed")

            service = OpenAIService()
            request = RecommendationRequest(
                remaining_words=["bass", "flounder", "salmon", "trout"],
                llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
            )

            with pytest.raises(Exception, match="Provider instantiation failed"):
                service.generate_recommendation(request)

    def test_extract_words_flexible_with_actual_comma_pattern(self):
        """Test flexible word extraction with comma pattern when word pattern insufficient."""
        service = OpenAIService()
        # Response with only 1 regular word but valid comma pattern
        response = ": bass,flounder,salmon,trout"

        result = service._extract_words_flexible(response)

        assert result == ["bass", "flounder", "salmon", "trout"]

    def test_parse_validation_response_exception(self):
        """Test parsing validation response with exception."""
        service = OpenAIService()

        # Mock re.search to raise an exception
        with patch("re.search") as mock_search:
            mock_search.side_effect = Exception("Regex error")

            result = service._parse_validation_response("some response")

            assert result["valid"] is False
            assert result["score"] == 0.0
            assert result["explanation"] == "Unable to parse validation response"

    @patch("src.services.openai_service.get_provider_factory")
    @patch("src.services.openai_service.PromptTemplateService")
    def test_generate_recommendation_non_openai_provider_error(self, mock_prompt_service, mock_get_provider_factory):
        """Test recommendation generation with non-openai provider error."""
        # Setup mocks
        mock_factory = Mock()
        mock_prompt_svc = Mock()
        mock_get_provider_factory.return_value = mock_factory
        mock_prompt_service.return_value = mock_prompt_svc

        # Mock factory to raise RuntimeError with different message
        mock_factory.create_provider.side_effect = RuntimeError("Different error")

        service = OpenAIService()
        request = RecommendationRequest(
            remaining_words=["bass", "flounder", "salmon", "trout"],
            llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
        )

        with pytest.raises(RuntimeError, match="Different error"):
            service.generate_recommendation(request)

    def test_get_service_info(self):
        """Test getting service information."""
        service = OpenAIService()

        result = service.get_service_info()

        assert result["service_type"] == "openai_llm"
        assert result["version"] == "1.0"
        assert "high_quality_recommendations" in result["capabilities"]
        assert result["requires_api_key"] is True
        assert result["supports_offline"] is False
        assert result["expected_response_time"] == "fast"
