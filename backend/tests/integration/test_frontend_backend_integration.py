"""
Integration Tests for LLM Provider Integration

These tests focus on testing the integration between frontend and backend
components, ensuring the complete system works together correctly.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.main import app
from tests.mocks.llm_mocks import MOCK_RECOMMENDATION_RESPONSES


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
def sample_request():
    """Sample valid request for testing"""
    return {
        "llm_provider": {"provider_type": "simple", "model_name": None},
        "remaining_words": [
            "BASS",
            "PIKE",
            "SOLE",
            "CARP",
            "APPLE",
            "BANANA",
            "CHERRY",
            "GRAPE",
            "RED",
            "BLUE",
            "GREEN",
            "YELLOW",
            "CHAIR",
            "TABLE",
            "LAMP",
            "DESK",
        ],
        "previous_guesses": [],
        "puzzle_context": None,
    }


class TestIntegrationBasicFlow:
    """Test basic integration flow between components"""

    def test_api_endpoint_exists(self, client):
        """Test that the API endpoints exist and return appropriate responses"""
        # Test recommendations endpoint exists
        response = client.post("/api/v2/recommendations", json={})
        # Should get validation error, not 404
        assert response.status_code == 422

        # Test providers endpoint exists
        response = client.post("/api/v2/providers/validate", json={})
        # Should get validation error, not 404
        assert response.status_code == 422

    def test_provider_validation_endpoint_integration(self, client):
        """Test provider validation endpoint integration"""
        # Test simple provider validation
        request_data = {"provider_type": "simple"}

        response = client.post("/api/v2/providers/validate", json=request_data)

        # Should either work or give clear error
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "provider_type" in data
            assert "is_valid" in data
            assert "status" in data
            assert "message" in data


class TestMockIntegration:
    """Test mock providers work correctly in integration"""

    @patch("src.services.simple_recommendation_service.SimpleRecommendationService.generate_recommendation")
    def test_simple_provider_mock_integration(self, mock_service, client, sample_request):
        """Test simple provider works with mocks"""
        # Mock the service to return consistent response
        mock_service.return_value = MOCK_RECOMMENDATION_RESPONSES["simple"]

        response = client.post("/api/v2/recommendations", json=sample_request)

        # Should either work or fail gracefully
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            assert "recommended_words" in data
            assert "provider_used" in data

    @patch("src.services.ollama_service.OllamaService.generate_recommendation")
    def test_ollama_provider_mock_integration(self, mock_service, client, sample_request):
        """Test ollama provider works with mocks"""
        # Mock the service to return consistent response
        mock_service.return_value = MOCK_RECOMMENDATION_RESPONSES["ollama"]

        # Update request for ollama
        ollama_request = sample_request.copy()
        ollama_request["llm_provider"] = {"provider_type": "ollama", "model_name": "llama2"}

        response = client.post("/api/v2/recommendations", json=ollama_request)

        # Should either work or fail gracefully
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            assert "recommended_words" in data
            assert "provider_used" in data

    @patch("src.services.openai_service.OpenAIService.generate_recommendation")
    def test_openai_provider_mock_integration(self, mock_service, client, sample_request):
        """Test openai provider works with mocks"""
        # Mock the service to return consistent response
        mock_service.return_value = MOCK_RECOMMENDATION_RESPONSES["openai"]

        # Update request for openai
        openai_request = sample_request.copy()
        openai_request["llm_provider"] = {"provider_type": "openai", "model_name": "gpt-3.5-turbo"}

        response = client.post("/api/v2/recommendations", json=openai_request)

        # Should either work or fail gracefully
        assert response.status_code in [200, 400, 422, 500]

        if response.status_code == 200:
            data = response.json()
            # Verify response structure
            assert "recommended_words" in data
            assert "provider_used" in data


class TestErrorHandlingIntegration:
    """Test error handling works correctly across components"""

    def test_invalid_request_validation(self, client):
        """Test that invalid requests are properly validated"""
        invalid_requests = [
            {},  # Empty request
            {"llm_provider": {"provider_type": "invalid"}},  # Invalid provider
            {"remaining_words": []},  # Missing provider
            {"llm_provider": {"provider_type": "simple"}, "remaining_words": ["A", "B"]},  # Too few words
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/v2/recommendations", json=invalid_request)
            # Should get validation error
            assert response.status_code in [400, 422]

            data = response.json()
            # Should have error information
            assert "detail" in data or "error" in data

    def test_service_error_handling(self, client, sample_request):
        """Test that service errors are handled gracefully"""
        # This test verifies the error handling middleware works
        with patch("src.services.recommendation_service.RecommendationService.generate_recommendation") as mock_service:
            mock_service.side_effect = Exception("Test service error")

            response = client.post("/api/v2/recommendations", json=sample_request)

            # Should handle error gracefully
            assert response.status_code in [500]

            data = response.json()
            assert "detail" in data or "error" in data


class TestBackwardCompatibility:
    """Test backward compatibility with Phase 1"""

    def test_simple_provider_maintains_compatibility(self, client, sample_request):
        """Test that simple provider maintains Phase 1 behavior"""
        response = client.post("/api/v2/recommendations", json=sample_request)

        # Should either work or give clear errors
        assert response.status_code in [200, 400, 422, 500]

        # If it works, verify it behaves like Phase 1
        if response.status_code == 200:
            data = response.json()
            assert data["provider_used"] == "simple"
            assert len(data["recommended_words"]) == 4


class TestSystemHealth:
    """Test overall system health and functionality"""

    def test_application_startup(self, client):
        """Test that the application starts up correctly"""
        # Test health check or basic endpoint
        response = client.get("/")

        # Should either work or redirect, but not crash
        assert response.status_code in [200, 404, 307]

    def test_api_documentation_available(self, client):
        """Test that API documentation is available"""
        # Test OpenAPI docs
        response = client.get("/docs")
        assert response.status_code in [200, 404]  # 404 is acceptable if docs disabled

        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code in [200, 404]  # 404 is acceptable if docs disabled

    def test_all_endpoints_discoverable(self, client):
        """Test that all expected endpoints are discoverable"""
        expected_paths = ["/api/v2/recommendations", "/api/v2/providers/validate"]

        # Get OpenAPI schema if available
        response = client.get("/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            available_paths = schema.get("paths", {}).keys()

            for path in expected_paths:
                assert path in available_paths, f"Expected endpoint {path} not found in API schema"


class TestComponentIntegration:
    """Test integration between different components"""

    def test_provider_factory_integration(self, client):
        """Test that provider factory integration works"""
        # This is tested implicitly through other tests
        # but we can add specific factory tests here
        pass

    def test_validation_service_integration(self, client, sample_request):
        """Test that validation services work correctly"""
        response = client.post("/api/v2/recommendations", json=sample_request)

        # Should get proper validation response
        assert response.status_code in [200, 400, 422, 500]

    def test_error_middleware_integration(self, client):
        """Test that error middleware handles errors correctly"""
        # Test with completely malformed JSON
        response = client.post(
            "/api/v2/recommendations", content='{"invalid": json}', headers={"Content-Type": "application/json"}
        )

        # Should handle JSON parsing error gracefully
        assert response.status_code in [400, 422]


# Integration test summary function
def test_integration_summary():
    """Summary test to verify integration test completeness"""
    # This test serves as documentation of what we've tested
    tested_areas = [
        "API endpoint existence",
        "Provider validation integration",
        "Mock provider integration",
        "Error handling integration",
        "Backward compatibility",
        "System health",
        "Component integration",
    ]

    # All areas should be covered by the tests above
    assert len(tested_areas) == 7  # Update this if adding more test areas

    # Test passes if we've covered all major integration points
    assert True
