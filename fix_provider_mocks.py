#!/usr/bin/env python3
"""
Fix test file to properly mock both the services and the provider availability check
"""

import re


def fix_test_with_provider_factory():
    """Add provider factory mocking to make providers available"""

    test_file = "backend/tests/e2e/test_quickstart_scenarios.py"

    with open(test_file, "r") as f:
        content = f.read()

    # Add additional import for the provider factory
    content = re.sub(
        r"from src\.services\.openai_service import OpenAIService",
        "from src.services.openai_service import OpenAIService\nfrom src.services.llm_provider_factory import LLMProviderFactory",
        content,
    )

    # Update the ollama test to include provider factory mock
    ollama_test_pattern = r"(@patch\.object\(OllamaService, 'generate_recommendation'\)\s+def test_ollama_provider_selection\(self, mock_ollama, client, sample_puzzle_words\):)"

    replacement = """@patch.object(LLMProviderFactory, 'get_available_providers')
    @patch.object(OllamaService, 'generate_recommendation')
    def test_ollama_provider_selection(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):"""

    content = re.sub(
        ollama_test_pattern, replacement, content, flags=re.MULTILINE | re.DOTALL
    )

    # Update the test body to set up the provider factory mock
    test_body_pattern = r'(def test_ollama_provider_selection\(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that ollama provider can be selected and works"""\s+)(mock_ollama\.return_value = MOCK_RECOMMENDATION_RESPONSES\["ollama"\])'

    replacement_body = r"""\1# Mock provider factory to make ollama available
        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}
        \2"""

    content = re.sub(
        test_body_pattern, replacement_body, content, flags=re.MULTILINE | re.DOTALL
    )

    # Update other ollama tests similarly
    content = re.sub(
        r"@patch\.object\(OllamaService, 'generate_recommendation'\)\s+def test_ollama_contextual_recommendation\(self, mock_ollama, client, sample_puzzle_words\):",
        "@patch.object(LLMProviderFactory, 'get_available_providers')\n    @patch.object(OllamaService, 'generate_recommendation')\n    def test_ollama_contextual_recommendation(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    # Add provider factory setup to contextual test
    content = re.sub(
        r'(def test_ollama_contextual_recommendation\(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that ollama considers previous guesses in context"""\s+# First call returns fish suggestion\s+)(mock_ollama\.return_value = MOCK_RECOMMENDATION_RESPONSES\["ollama"\])',
        r"""\1# Mock provider factory to make ollama available
        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}
        # First call returns fish suggestion
        \2""",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Update OpenAI tests similarly
    content = re.sub(
        r"@patch\.object\(OpenAIService, 'generate_recommendation'\)",
        "@patch.object(LLMProviderFactory, 'get_available_providers')\n    @patch.object(OpenAIService, 'generate_recommendation')",
        content,
    )

    # Add OpenAI provider factory setups
    content = re.sub(
        r'(def test_openai_provider_selection\(self, mock_openai, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that openai provider can be selected and works"""\s+)(mock_openai\.return_value = MOCK_RECOMMENDATION_RESPONSES\["openai"\])',
        r"""\1# Mock provider factory to make openai available
        mock_provider_factory.return_value = {"simple": True, "ollama": False, "openai": True}
        \2""",
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Write fixed content back
    with open(test_file, "w") as f:
        f.write(content)

    print("Added provider factory mocking to tests!")


if __name__ == "__main__":
    fix_test_with_provider_factory()
