from typing import List, Dict, Any
from src.services.simple_recommendation_service import SimpleRecommendationService
from src.llm_models.recommendation_request import RecommendationRequest
from src.llm_models.llm_provider import LLMProvider


class SimpleProvider:
    """Back-compat shim exposing generate_recommendations that returns dicts."""

    def __init__(self) -> None:
        self._svc = SimpleRecommendationService()

    def generate_recommendations(
        self,
        remaining_words: List[str],
        previous_guesses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        # Build a RecommendationRequest; previous_guesses from older tests are raw dicts, so let Pydantic coerce
        req = RecommendationRequest(
            llm_provider=LLMProvider(provider_type="simple", model_name=None),
            remaining_words=remaining_words,
            previous_guesses=previous_guesses,  # type: ignore[arg-type]
        )
        resp = self._svc.generate_recommendation(req)

        # Map words back to original casing based on remaining_words input
        def _map_to_original(words: List[str]) -> List[str]:
            mapped: List[str] = []
            for lw in words:
                found = False
                for orig in remaining_words:
                    if orig.lower() == lw.lower():
                        mapped.append(orig)
                        found = True
                        break
                if not found:
                    mapped.append(lw)
            return mapped

        return {
            "recommended_words": _map_to_original(resp.recommended_words),
            "connection_explanation": resp.connection_explanation,
            "generation_time_ms": resp.generation_time_ms,
        }
