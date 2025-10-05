#!/usr/bin/env python3
"""
Fix mock paths in e2e test file to properly mock service methods
"""

import re


def fix_mock_paths():
    """Fix all mock paths to target the service methods correctly"""

    test_file = "backend/tests/e2e/test_quickstart_scenarios.py"

    with open(test_file, "r") as f:
        content = f.read()

    # Fix ollama service patches - target the generate_recommendation method within the service instance
    content = re.sub(
        r"@patch\('src\.services\.recommendation_service\.RecommendationService\.ollama_service'\)",
        "@patch.object(OllamaService, 'generate_recommendation')",
        content,
    )

    # Fix openai service patches
    content = re.sub(
        r"@patch\('src\.services\.recommendation_service\.RecommendationService\.openai_service'\)",
        "@patch.object(OpenAIService, 'generate_recommendation')",
        content,
    )

    # Add necessary imports at the top
    import_lines = """from unittest.mock import patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from datetime import datetime
from src.main import app
from src.services.ollama_service import OllamaService
from src.services.openai_service import OpenAIService
from tests.mocks.llm_mocks import (
    MockProviderFactory,
    MOCK_RECOMMENDATION_RESPONSES
)"""

    # Replace the imports section
    content = re.sub(
        r"import pytest\nfrom unittest\.mock import patch\nfrom fastapi\.testclient import TestClient\nfrom httpx import AsyncClient\nfrom datetime import datetime\nfrom src\.main import app\nfrom tests\.mocks\.llm_mocks import \(\n    MockProviderFactory,\n    MOCK_RECOMMENDATION_RESPONSES\n\)",
        f"import pytest\n{import_lines}",
        content,
    )

    # Revert the mock usage patterns since we're using @patch.object now
    content = re.sub(
        r"mock_ollama\.generate_recommendation\.return_value = MOCK_RECOMMENDATION_RESPONSES\[\"ollama\"\]",
        'mock_ollama.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]',
        content,
    )

    content = re.sub(
        r"mock_openai\.generate_recommendation\.return_value = MOCK_RECOMMENDATION_RESPONSES\[\"openai\"\]",
        'mock_openai.return_value = MOCK_RECOMMENDATION_RESPONSES["openai"]',
        content,
    )

    # Revert assertion patterns
    content = re.sub(
        r"mock_ollama\.generate_recommendation\.assert_called_once\(\)",
        "mock_ollama.assert_called_once()",
        content,
    )

    content = re.sub(
        r"mock_ollama\.generate_recommendation\.call_args\[0\]\[0\]",
        "mock_ollama.call_args[0][0]",
        content,
    )

    content = re.sub(
        r"mock_openai\.generate_recommendation\.assert_called_once\(\)",
        "mock_openai.assert_called_once()",
        content,
    )

    # Write the fixed content back
    with open(test_file, "w") as f:
        f.write(content)

    print("Fixed mock paths with @patch.object!")


if __name__ == "__main__":
    fix_mock_paths()
