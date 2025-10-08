"""
Minimal openai stub so tests can patch `openai.OpenAI` without requiring the OpenAI package.
This is a lightweight placeholder used during test execution.
"""


class OpenAI:
    def __init__(self, *args, **kwargs):
        class Chat:
            class Completions:
                def create(self, *args, **kwargs):
                    class Resp:
                        class Choice:
                            class Message:
                                content = ""

                        choices = [Choice()]

                    return Resp()

            completions = Completions()

        self.chat = Chat()
