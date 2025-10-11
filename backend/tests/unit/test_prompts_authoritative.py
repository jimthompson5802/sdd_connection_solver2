"""
Unit tests verifying prompt strengthening and server-authoritative remaining words.

These tests focus narrowly on the recent changes:
- Prompt contains explicit AVAILABLE WORDS and constraint instructions.
- RecommendationService builds an authoritative request using the active session's
  remaining words, ignoring client-sent remaining_words.
"""

from typing import List

from src.services.prompt_service import PromptTemplateService
from src.services.recommendation_service import RecommendationService
from src.llm_models.llm_provider import LLMProvider
from src.llm_models.recommendation_request import RecommendationRequest
from src.models import session_manager


def _make_session(words: List[str]):
    # Ensure a clean session context for this test
    # Create a new session with the provided words
    return session_manager.create_session(words)


def test_prompt_contains_available_words_and_constraints():
    service = PromptTemplateService()

    req = RecommendationRequest(
        llm_provider=LLMProvider(provider_type="openai", model_name="gpt-4o-mini"),
        remaining_words=["BASS", "FLOUNDER", "SALMON", "TROUT"],
        previous_guesses=[],
        puzzle_context=None,
    )

    prompt = service.generate_recommendation_prompt(req)

    # Core constraint lines
    assert "Use ONLY words from the AVAILABLE WORDS list" in prompt
    assert "Do NOT invent, modify, or reformat words" in prompt
    assert "AVAILABLE WORDS:" in prompt

    # The actual words must appear exactly as provided by the request
    for w in req.remaining_words:
        assert w in prompt


def test_service_uses_server_authoritative_remaining_words(monkeypatch):
    # Create a session with a known set of words
    session_words = [
        "BASS",
        "FLOUNDER",
        "SALMON",
        "TROUT",
        "PIANO",
        "GUITAR",
        "VIOLIN",
        "DRUMS",
        "RED",
        "BLUE",
        "GREEN",
        "YELLOW",
        "APPLE",
        "BANANA",
        "ORANGE",
        "GRAPE",
    ]
    _make_session(session_words)

    svc = RecommendationService()

    captured_request = {}

    def capture_simple_request(request):
        # Capture what the SimpleRecommendationService ultimately receives
        captured_request["remaining_words"] = list(request.remaining_words)
        # Return a minimal valid RecommendationResponse using simple provider
        from src.llm_models.recommendation_response import RecommendationResponse

        return RecommendationResponse(
            recommended_words=["bass", "flounder", "salmon", "trout"],
            connection_explanation=None,
            provider_used=LLMProvider(provider_type="simple", model_name=None),
            generation_time_ms=None,
        )

    # Force availability check to pass for simple
    monkeypatch.setattr(
        svc.provider_factory, "get_available_providers", lambda: {"simple": True, "ollama": False, "openai": False}
    )
    # Route will call .simple_service.generate_recommendation for provider "simple"; patch it
    monkeypatch.setattr(svc.simple_service, "generate_recommendation", capture_simple_request)

    # The client tries to send a different remaining_words list to simulate divergence
    client_supplied_words = ["X", "Y", "Z", "W"]

    req = RecommendationRequest(
        llm_provider=LLMProvider(provider_type="simple", model_name=None),
        remaining_words=client_supplied_words,
        previous_guesses=[],
        puzzle_context=None,
    )

    svc.generate_recommendation(req)

    # The service should have used session.get_remaining_words() not client_supplied_words
    # Session stores words lowercased; assert a subset check on known first group
    assert set(["bass", "flounder", "salmon", "trout"]).issubset(set(captured_request["remaining_words"]))
