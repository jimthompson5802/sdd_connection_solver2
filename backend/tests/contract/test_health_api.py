"""
Contract tests for GET /api/v2/health endpoint.
These tests validate health check API contract compliance.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthContract:
    """Contract tests for /api/v2/health endpoint"""

    @pytest.fixture
    def client(self):
        """Test client fixture - will fail until FastAPI app exists"""
        # This will need to import the actual FastAPI app when implemented
        from src.main import app

        return TestClient(app)

    @pytest.mark.contract
    def test_health_check_contract(self, client):
        """Test that health check endpoint follows expected contract"""
        # This should fail until implementation exists
        response = client.get("/api/v2/health")

        # Expected contract behavior (will fail initially)
        assert response.status_code == 200
        data = response.json()

        # Validate response schema
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "providers_available" in data

        # Validate providers_available structure
        providers = data["providers_available"]
        assert isinstance(providers, list)

        # Should at least have simple provider
        provider_types = [p["provider_type"] for p in providers]
        assert "simple" in provider_types

        for provider in providers:
            assert "provider_type" in provider
            assert "available" in provider
            assert isinstance(provider["available"], bool)
            if "error_message" in provider:
                assert isinstance(provider["error_message"], (str, type(None)))

    @pytest.mark.contract
    def test_health_response_format(self, client):
        """Test that health response format is consistent"""
        response = client.get("/api/v2/health")

        if response.status_code == 200:
            data = response.json()

            # Required fields
            required_fields = ["status", "timestamp", "version", "providers_available"]
            for field in required_fields:
                assert field in data, f"Health response missing required field: {field}"

            # Timestamp should be ISO format
            import datetime

            try:
                datetime.datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
            except ValueError:
                pytest.fail("timestamp field is not in valid ISO format")

            # Version should be string
            assert isinstance(data["version"], str)

            # Status should be specific value
            assert data["status"] in ["healthy", "degraded", "unhealthy"]
