"""
Minimal llms stubs for tests.
Provides FakeListLLM and a minimal Ollama placeholder to be patched by tests.
"""

from typing import List


class FakeListLLM:
    def __init__(self, responses: List[str]):
        self.responses = responses
        self._idx = 0

    def invoke(self, prompt: str) -> str:
        if not self.responses:
            return ""
        resp = self.responses[self._idx % len(self.responses)]
        self._idx += 1
        return resp


class Ollama:
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, prompt: str) -> str:
        return ""
