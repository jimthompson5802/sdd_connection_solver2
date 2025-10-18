#!/usr/bin/env python3
"""
Fix mock paths in e2e test file to properly mock service instances
"""

import re


def fix_mock_paths():
    """Fix all mock paths to target the service instances in RecommendationService"""

    test_file = "backend/tests/e2e/test_quickstart_scenarios.py"

    with open(test_file, "r") as f:
        content = f.read()

    # Fix ollama service patches
    content = re.sub(
        r"@patch\('src\.services\.ollama_service\.OllamaService\.generate_recommendation'\)",
        "@patch('src.services.recommendation_service.RecommendationService.ollama_service')",
        content,
    )

    # Fix openai service patches
    content = re.sub(
        r"@patch\('src\.services\.openai_service\.OpenAIService\.generate_recommendation'\)",
        "@patch('src.services.recommendation_service.RecommendationService.openai_service')",
        content,
    )

    # Fix mock usage patterns - update the mock calls
    # Change mock.return_value to mock.generate_recommendation.return_value
    content = re.sub(
        r"mock_ollama\.return_value = MOCK_RECOMMENDATION_RESPONSES\[\"ollama\"\]",
        'mock_ollama.generate_recommendation.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]',
        content,
    )

    content = re.sub(
        r"mock_openai\.return_value = MOCK_RECOMMENDATION_RESPONSES\[\"openai\"\]",
        'mock_openai.generate_recommendation.return_value = MOCK_RECOMMENDATION_RESPONSES["openai"]',
        content,
    )

    # Fix assertion patterns
    content = re.sub(
        r"mock_ollama\.assert_called_once\(\)",
        "mock_ollama.generate_recommendation.assert_called_once()",
        content,
    )

    content = re.sub(
        r"mock_ollama\.call_args\[0\]\[0\]",
        "mock_ollama.generate_recommendation.call_args[0][0]",
        content,
    )

    content = re.sub(
        r"mock_openai\.assert_called_once\(\)",
        "mock_openai.generate_recommendation.assert_called_once()",
        content,
    )

    # Write the fixed content back
    with open(test_file, "w") as f:
        f.write(content)

    print("Fixed mock paths in test file!")


if __name__ == "__main__":
    fix_mock_paths()
