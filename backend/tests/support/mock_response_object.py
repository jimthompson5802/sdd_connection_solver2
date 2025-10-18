class MockResponseObject:
    def __init__(self, data):
        # data is expected to be a dict with keys like recommended_words and connection_explanation
        # Normalize to attributes used by services
        self.recommendations = data.get("recommended_words")
        # support both 'connection_explanation' and 'connection'
        self.connection = data.get("connection_explanation") or data.get("connection") or data.get("explanation")
