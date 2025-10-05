#!/usr/bin/env python3
"""
Fix mocks to return proper RecommendationResponse objects instead of raw dicts
"""


def fix_mock_responses():
    """Update mocks to return proper RecommendationResponse objects"""

    test_file = "backend/tests/mocks/llm_mocks.py"

    with open(test_file, "r") as f:
        content = f.read()

    # Add proper imports at the top
    import_section = '''"""
Comprehensive LLM Provider Mocks for Testing

This module provides consistent mock responses for all LLM providers
to ensure reproducible testing across the application.
"""

from unittest.mock import Mock
from typing import Dict, Any, Optional
import json
from datetime import datetime
from src.llm_models.recommendation_response import RecommendationResponse
from src.llm_models.llm_provider import LLMProvider'''

    content = content.replace(
        '''"""
Comprehensive LLM Provider Mocks for Testing

This module provides consistent mock responses for all LLM providers
to ensure reproducible testing across the application.
"""

from unittest.mock import Mock
from typing import Dict, Any, Optional
import json
from datetime import datetime''',
        import_section,
    )

    # Create a function to build proper response objects
    builder_function = '''

def create_mock_response(response_data: Dict[str, Any]) -> RecommendationResponse:
    """Create a proper RecommendationResponse object from mock data."""
    provider_type = response_data["provider_used"]
    provider = LLMProvider(provider_type=provider_type, model_name="test-model")
    
    return RecommendationResponse(
        recommended_words=response_data["recommended_words"],
        connection_explanation=response_data.get("connection_explanation"),
        confidence_score=response_data["confidence_score"],
        provider_used=provider,
        generation_time_ms=response_data.get("generation_time_ms"),
    )'''

    # Insert the builder function after the imports
    content = content.replace(
        "from datetime import datetime",
        f"from datetime import datetime{builder_function}",
    )

    # Update the MOCK_RECOMMENDATION_RESPONSES to use the builder
    responses_section = """

# Create proper response objects for mocking
MOCK_RECOMMENDATION_RESPONSES = {
    "simple": create_mock_response({
        "recommended_words": ["BASS", "PIKE", "SOLE", "CARP"],
        "connection_explanation": None,  # Simple provider has no explanation
        "confidence_score": 0.8,
        "provider_used": "simple",
        "generation_time_ms": None,  # Simple provider has no timing
    }),
    "ollama": create_mock_response({
        "recommended_words": ["BASS", "PIKE", "SOLE", "CARP"],
        "connection_explanation": (
            "These words are all types of fish. Bass and pike are freshwater fish "
            "commonly found in lakes and rivers, while sole and carp are also fish species."
        ),
        "confidence_score": 0.92,
        "provider_used": "ollama",
        "generation_time_ms": 2340,
    }),
    "openai": create_mock_response({
        "recommended_words": ["APPLE", "BANANA", "CHERRY", "GRAPE"],
        "connection_explanation": (
            "These are all fruits. They are common fruits that people eat "
            "and are found in grocery stores and orchards."
        ),
        "confidence_score": 0.95,
        "provider_used": "openai",
        "generation_time_ms": 1850,
    })
}"""

    # Replace the existing MOCK_RECOMMENDATION_RESPONSES section
    # Find the start and end of the current responses section
    start_marker = "# Mock response data for consistent testing"
    end_marker = "# Mock error responses for testing error scenarios"

    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)

    if start_pos != -1 and end_pos != -1:
        content = content[:start_pos] + responses_section + "\n\n" + content[end_pos:]

    # Write the fixed content back
    with open(test_file, "w") as f:
        f.write(content)

    print("Fixed mock responses to return proper RecommendationResponse objects!")


if __name__ == "__main__":
    fix_mock_responses()
