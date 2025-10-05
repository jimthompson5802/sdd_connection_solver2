"""
Contract tests for configuration validation functionality.
These tests validate configuration loading and provider availability checking.
"""

import pytest
from unittest.mock import patch
import os


class TestConfigurationContract:
    """Contract tests for configuration validation"""

    @pytest.mark.contract
    def test_configuration_service_exists(self):
        """Test that configuration service can be imported and instantiated"""
        # This will fail until implementation exists
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()
        assert config_service is not None

    @pytest.mark.contract
    def test_load_configuration_method_exists(self):
        """Test that load_configuration method exists and returns expected format"""
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()

        # Should have load_configuration method
        assert hasattr(config_service, "load_configuration")

        # Method should be callable
        assert callable(getattr(config_service, "load_configuration"))

    @pytest.mark.contract
    def test_validate_providers_method_exists(self):
        """Test that validate_providers method exists and returns expected format"""
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()

        # Should have validate_providers method
        assert hasattr(config_service, "validate_providers")

        # Method should be callable
        assert callable(getattr(config_service, "validate_providers"))

    @pytest.mark.contract
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key", "OLLAMA_BASE_URL": "http://localhost:11434"})
    def test_configuration_loading_contract(self):
        """Test that configuration loading follows expected contract"""
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()
        config = config_service.load_configuration()

        # Expected configuration structure
        assert isinstance(config, dict)

        # Should contain provider configurations
        expected_keys = ["openai", "ollama", "simple"]
        for key in expected_keys:
            assert key in config, f"Configuration missing provider: {key}"

        # OpenAI config should include API key
        assert "api_key" in config["openai"]
        assert config["openai"]["api_key"] == "test_openai_key"

        # Ollama config should include base URL
        assert "base_url" in config["ollama"]
        assert config["ollama"]["base_url"] == "http://localhost:11434"

        # Simple provider should not require external config
        assert isinstance(config["simple"], dict)

    @pytest.mark.contract
    def test_provider_validation_contract(self):
        """Test that provider validation follows expected contract"""
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()
        validation_results = config_service.validate_providers()

        # Expected validation results structure
        assert isinstance(validation_results, list)

        # Should validate at least simple provider
        provider_types = [result["provider_type"] for result in validation_results]
        assert "simple" in provider_types

        # Each validation result should have required fields
        for result in validation_results:
            assert "provider_type" in result
            assert "available" in result
            assert isinstance(result["available"], bool)

            if not result["available"]:
                assert "error_message" in result
                assert isinstance(result["error_message"], str)

    @pytest.mark.contract
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_configuration_handling(self):
        """Test that missing configuration is handled gracefully"""
        from src.services.configuration_service import ConfigurationService

        config_service = ConfigurationService()

        # Should not raise exception with missing environment variables
        config = config_service.load_configuration()
        validation_results = config_service.validate_providers()

        # Should still return valid structures
        assert isinstance(config, dict)
        assert isinstance(validation_results, list)

        # Simple provider should still be available
        simple_result = next((r for r in validation_results if r["provider_type"] == "simple"), None)
        assert simple_result is not None
        assert simple_result["available"] is True

    @pytest.mark.contract
    def test_configuration_service_singleton_behavior(self):
        """Test that configuration service behaves appropriately for repeated access"""
        from src.services.configuration_service import ConfigurationService

        # Should be able to create multiple instances without error
        config_service1 = ConfigurationService()
        config_service2 = ConfigurationService()

        # Both should provide consistent results
        config1 = config_service1.load_configuration()
        config2 = config_service2.load_configuration()

        assert config1.keys() == config2.keys()
