"""
Stub submodule for langchain_community.llms.ollama to support tests that patch Ollama.
"""


class Ollama:
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, prompt: str) -> str:
        return ""

    def with_structured_output(self, *args, **kwargs):
        # Return self for simple chaining in tests; tests will patch methods as needed.
        return self
