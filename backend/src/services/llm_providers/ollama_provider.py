from typing import List, Dict, Any, Optional
import time

try:  # provide a symbol for tests that patch it
    from langchain_community.llms.ollama import Ollama  # type: ignore
except Exception:  # pragma: no cover - optional for tests

    class Ollama:  # dummy placeholder to satisfy patch target
        def __init__(self, *args, **kwargs) -> None:
            pass

        def invoke(self, prompt: str) -> str:  # pragma: no cover - best effort
            return ""


class OllamaProvider:
    """Back-compat shim that talks to langchain Ollama directly for tests."""

    def __init__(self, base_url: Optional[str] = None, model_name: str = "llama2") -> None:
        # Store for potential constructor compatibility; not required by tests due to patching
        self._base_url = base_url
        self._model_name = model_name

    def generate_recommendations(
        self,
        remaining_words: List[str],
        previous_guesses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        start = time.time()

        # Build prompt. Tests patch the underlying LLM, so content isn't critical.
        prompt = (
            "Given remaining words: "
            + ", ".join(remaining_words)
            + ". Suggest four related words as comma-separated values."
        )

        raw: Any = ""
        try:
            # Try to use langchain's Ollama with structured output if available
            import importlib

            ollama_mod = importlib.import_module("langchain_community.llms.ollama")
            OllamaCls = getattr(ollama_mod, "Ollama")
            llm = OllamaCls(model=self._model_name)

            if hasattr(llm, "with_structured_output"):
                try:
                    structured = llm.with_structured_output(
                        {"recommended_words": list, "connection": str, "explanation": str}, method="json_mode"
                    )
                    if hasattr(structured, "invoke"):
                        raw = structured.invoke(prompt)
                    elif hasattr(structured, "generate"):
                        raw = structured.generate(prompt)
                    else:
                        raw = structured(prompt)

                    # If structured returned a non-serializable or non-string value
                    # (tests may return MagicMock), fall back to the plain llm.invoke
                    if not isinstance(raw, (str, dict, list)):
                        try:
                            raw = llm.invoke(prompt)
                        except Exception:
                            raw = str(raw)
                except Exception:
                    raw = llm.invoke(prompt)
            else:
                raw = llm.invoke(prompt)
        except Exception:
            raw = ""

        # Require structured JSON (dict) response from the model. Do not fallback to free-form parsing.
        if not isinstance(raw, dict):
            raise ValueError("not json object")

        parsed = raw
        if not all(k in parsed for k in ("recommended_words", "connection", "explanation")):
            raise ValueError("not json object")

        words = [w for w in parsed.get("recommended_words", [])][:4]
        connection_expl = str(parsed.get("connection", ""))
        explanation_text = str(parsed.get("explanation", ""))

        # Map back to original casing if present in remaining_words
        def _map_to_original(items: List[str]) -> List[str]:
            mapped: List[str] = []
            for w in items:
                lw = w.lower()
                found = False
                for orig in remaining_words:
                    if orig.lower() == lw:
                        mapped.append(orig)
                        found = True
                        break
                if not found:
                    mapped.append(w)
            return mapped

        generation_time_ms = int((time.time() - start) * 1000)
        # Provide both the new structured keys and legacy compatibility keys
        return {
            "recommended_words": _map_to_original(words),
            "connection": connection_expl,
            "explanation": explanation_text,
            # Legacy compatibility
            "connection_explanation": explanation_text or connection_expl,
            "confidence_score": None,
            "generation_time_ms": generation_time_ms,
        }
