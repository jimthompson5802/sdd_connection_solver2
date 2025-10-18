#!/usr/bin/env python3
"""
Comprehensive fix script for all remaining e2e test issues
"""

import re


def fix_all_remaining_tests():
    """Apply all necessary fixes to the test file"""

    test_file = "backend/tests/e2e/test_quickstart_scenarios.py"

    with open(test_file, "r") as f:
        content = f.read()

    # 1. Fix all OpenAI tests to include provider factory mocking
    # Add provider factory mock to OpenAI tests that don't have it
    content = re.sub(
        r"(@patch\.object\(OpenAIService, \'generate_recommendation\'\)\s+def test_openai_provider_selection\(self, mock_openai, client, sample_puzzle_words\):)",
        r"@patch.object(LLMProviderFactory, \'get_available_providers\')\n    @patch.object(OpenAIService, \'generate_recommendation\')\n    def test_openai_provider_selection(self, mock_openai, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    content = re.sub(
        r"(@patch\.object\(OpenAIService, \'generate_recommendation\'\)\s+def test_openai_quality_comparison\(self, mock_openai, client, sample_puzzle_words\):)",
        r"@patch.object(LLMProviderFactory, \'get_available_providers\')\n    @patch.object(OpenAIService, \'generate_recommendation\')\n    def test_openai_quality_comparison(self, mock_openai, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    # 2. Add provider factory setup to OpenAI tests
    content = re.sub(
        r'(def test_openai_provider_selection\(self, mock_openai, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that openai provider can be selected and works"""\s+)(mock_openai\.return_value = MOCK_RECOMMENDATION_RESPONSES\["openai"\])',
        r'\1# Mock provider factory to make openai available\n        mock_provider_factory.return_value = {"simple": True, "ollama": False, "openai": True}\n        \2',
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    content = re.sub(
        r'(def test_openai_quality_comparison\(self, mock_openai, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that OpenAI provides higher quality recommendations"""\s+)(mock_openai\.return_value = MOCK_RECOMMENDATION_RESPONSES\["openai"\])',
        r'\1# Mock provider factory to make openai available\n        mock_provider_factory.return_value = {"simple": True, "ollama": False, "openai": True}\n        \2',
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 3. Fix mixed provider test with proper mocking and datetime serialization
    content = re.sub(
        r"(@patch\.object\(OllamaService, \'generate_recommendation\'\)\s+def test_mixed_provider_usage\(self, mock_ollama, client, sample_puzzle_words\):)",
        r"@patch.object(LLMProviderFactory, \'get_available_providers\')\n    @patch.object(OllamaService, \'generate_recommendation\')\n    def test_mixed_provider_usage(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    # 4. Add provider factory setup to mixed provider test and fix datetime
    content = re.sub(
        r'(def test_mixed_provider_usage\(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test using multiple providers in sequence"""\s+)(mock_ollama\.return_value = MOCK_RECOMMENDATION_RESPONSES\["ollama"\])',
        r'\1# Mock provider factory to make ollama available\n        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}\n        \2',
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 5. Fix datetime serialization in mixed provider test
    content = re.sub(
        r"(previous_guesses=\[attempt\.model_dump\(\)\])",
        r"previous_guesses=[attempt.model_dump(mode=\'json\')]",
        content,
    )

    # 6. Fix context awareness test
    content = re.sub(
        r"(@patch\.object\(OllamaService, \'generate_recommendation\'\)\s+def test_recommendation_quality_context_awareness\(self, mock_ollama, client, sample_puzzle_words\):)",
        r"@patch.object(LLMProviderFactory, \'get_available_providers\')\n    @patch.object(OllamaService, \'generate_recommendation\')\n    def test_recommendation_quality_context_awareness(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    content = re.sub(
        r'(def test_recommendation_quality_context_awareness\(self, mock_ollama, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that recommendations improve with context"""\s+)(mock_ollama\.side_effect)',
        r'\1# Mock provider factory to make ollama available\n        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": False}\n        \2',
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 7. Fix provider state isolation test
    content = re.sub(
        r"(@patch\.object\(OpenAIService, \'generate_recommendation\'\)\s+@patch\.object\(OllamaService, \'generate_recommendation\'\)\s+def test_provider_state_isolation\(self, mock_ollama, mock_openai, client, sample_puzzle_words\):)",
        r"@patch.object(LLMProviderFactory, \'get_available_providers\')\n    @patch.object(OpenAIService, \'generate_recommendation\')\n    @patch.object(OllamaService, \'generate_recommendation\')\n    def test_provider_state_isolation(self, mock_ollama, mock_openai, mock_provider_factory, client, sample_puzzle_words):",
        content,
    )

    content = re.sub(
        r'(def test_provider_state_isolation\(self, mock_ollama, mock_openai, mock_provider_factory, client, sample_puzzle_words\):\s+"""Test that different providers maintain separate state"""\s+)(mock_ollama\.return_value)',
        r'\1# Mock provider factory to make both providers available\n        mock_provider_factory.return_value = {"simple": True, "ollama": True, "openai": True}\n        \2',
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Write the fixed content back
    with open(test_file, "w") as f:
        f.write(content)

    print("Applied comprehensive fixes to e2e tests!")


if __name__ == "__main__":
    fix_all_remaining_tests()
