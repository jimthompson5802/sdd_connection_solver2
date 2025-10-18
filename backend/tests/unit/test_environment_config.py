"""Unit tests for environment configuration loader."""

import os
from unittest.mock import patch
from src.config.environment import EnvironmentLoader


class TestEnvironmentLoader:
    """Test cases for EnvironmentLoader."""

    def test_init_with_default_env_file(self):
        """Test initialization with default .env file."""
        loader = EnvironmentLoader()
        assert loader.env_file == ".env"

    def test_init_with_custom_env_file(self):
        """Test initialization with custom .env file."""
        custom_file = "/path/to/custom.env"
        loader = EnvironmentLoader(custom_file)
        assert loader.env_file == custom_file

    @patch("src.config.environment.os.path.exists")
    @patch("src.config.environment.load_dotenv")
    def test_load_env_file_exists(self, mock_load_dotenv, mock_exists):
        """Test loading env file when it exists."""
        mock_exists.return_value = True
        EnvironmentLoader()  # This will call _load_env_file
        mock_load_dotenv.assert_called_once_with(".env")

    @patch("src.config.environment.os.path.exists")
    @patch("src.config.environment.load_dotenv")
    def test_load_env_file_not_exists(self, mock_load_dotenv, mock_exists):
        """Test loading env file when it doesn't exist."""
        mock_exists.return_value = False
        EnvironmentLoader()  # This will call _load_env_file
        mock_load_dotenv.assert_not_called()

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "sk-test_fake_key_for_testing_only_1234567890abcdef",
            "OPENAI_MODEL_NAME": "gpt-4",
            "OPENAI_TIMEOUT": "600",
        },
    )
    def test_load_openai_config_complete(self):
        """Test loading complete OpenAI configuration."""
        loader = EnvironmentLoader()
        config = loader.load_openai_config()

        assert config["api_key"] == "sk-test_fake_key_for_testing_only_1234567890abcdef"
        assert config["model_name"] == "gpt-4"
        assert config["timeout"] == 600

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test_fake_key_for_testing_only_abcdef1234567890"})
    def test_load_openai_config_defaults(self):
        """Test loading OpenAI configuration with defaults."""
        loader = EnvironmentLoader()
        config = loader.load_openai_config()

        assert config["api_key"] == "sk-test_fake_key_for_testing_only_abcdef1234567890"
        assert config["model_name"] == "gpt-4o-mini"
        assert config["timeout"] == 300

    @patch.dict(os.environ, {}, clear=True)
    @patch("src.config.environment.os.path.exists")
    @patch("src.config.environment.load_dotenv")
    def test_load_openai_config_no_api_key(self, mock_load_dotenv, mock_exists):
        """Test loading OpenAI configuration without API key."""
        mock_exists.return_value = False  # No .env file
        loader = EnvironmentLoader()
        config = loader.load_openai_config()

        assert config == {}

    @patch.dict(
        os.environ,
        {"OLLAMA_BASE_URL": "http://localhost:11434", "OLLAMA_MODEL_NAME": "llama2", "OLLAMA_TIMEOUT": "400"},
    )
    def test_load_ollama_config_complete(self):
        """Test loading complete Ollama configuration."""
        loader = EnvironmentLoader()
        config = loader.load_ollama_config()

        assert config["base_url"] == "http://localhost:11434"
        assert config["model_name"] == "llama2"
        assert config["timeout"] == 400

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://localhost:11434"})
    def test_load_ollama_config_defaults(self):
        """Test loading Ollama configuration with defaults."""
        loader = EnvironmentLoader()
        config = loader.load_ollama_config()

        assert config["base_url"] == "http://localhost:11434"
        assert config["model_name"] == "qwen2.5:32b"
        assert config["timeout"] == 300

    @patch.dict(os.environ, {}, clear=True)
    def test_load_ollama_config_no_base_url(self):
        """Test loading Ollama configuration without base URL."""
        loader = EnvironmentLoader()
        config = loader.load_ollama_config()

        assert config == {}

    @patch.dict(
        os.environ,
        {"DEBUG": "true", "LOG_LEVEL": "DEBUG", "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"},
    )
    def test_load_application_config_complete(self):
        """Test loading complete application configuration."""
        loader = EnvironmentLoader()
        config = loader.load_application_config()

        assert config["debug"] is True
        assert config["log_level"] == "DEBUG"
        assert config["cors_origins"] == ["http://localhost:3000", "http://localhost:8080"]

    @patch.dict(os.environ, {}, clear=True)
    def test_load_application_config_defaults(self):
        """Test loading application configuration with defaults."""
        loader = EnvironmentLoader()
        config = loader.load_application_config()

        assert config["debug"] is False
        assert config["log_level"] == "INFO"
        assert config["cors_origins"] == ["http://localhost:3000"]

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_load_application_config_debug_false(self):
        """Test loading application configuration with debug=false."""
        loader = EnvironmentLoader()
        config = loader.load_application_config()

        assert config["debug"] is False

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_get_env_var_exists(self):
        """Test getting environment variable that exists."""
        loader = EnvironmentLoader()
        value = loader.get_env_var("TEST_VAR")

        assert value == "test_value"

    @patch.dict(os.environ, {}, clear=True)
    def test_get_env_var_not_exists_no_default(self):
        """Test getting environment variable that doesn't exist without default."""
        loader = EnvironmentLoader()
        value = loader.get_env_var("NON_EXISTENT_VAR")

        assert value is None

    @patch.dict(os.environ, {}, clear=True)
    def test_get_env_var_not_exists_with_default(self):
        """Test getting environment variable that doesn't exist with default."""
        loader = EnvironmentLoader()
        value = loader.get_env_var("NON_EXISTENT_VAR", "default_value")

        assert value == "default_value"

    @patch.dict(
        os.environ,
        {
            "REQUIRED_VAR_1": "value1",
            "REQUIRED_VAR_2": "",
        },
    )
    def test_validate_required_vars(self):
        """Test validating required environment variables."""
        loader = EnvironmentLoader()
        result = loader.validate_required_vars(["REQUIRED_VAR_1", "REQUIRED_VAR_2", "MISSING_VAR"])

        assert result["REQUIRED_VAR_1"] is True
        assert result["REQUIRED_VAR_2"] is True  # Empty string is still "set"
        assert result["MISSING_VAR"] is False

    @patch.dict(os.environ, {"VAR1": "value1", "VAR2": "value2"})
    def test_get_all_env_vars(self):
        """Test getting all environment variables."""
        loader = EnvironmentLoader()
        env_vars = loader.get_all_env_vars()

        assert "VAR1" in env_vars
        assert "VAR2" in env_vars
        assert env_vars["VAR1"] == "value1"
        assert env_vars["VAR2"] == "value2"

    def test_mask_sensitive_vars_with_sensitive_keys(self):
        """Test masking sensitive environment variables."""
        loader = EnvironmentLoader()
        env_vars = {
            "API_KEY": "fake_test_api_key_12345678901234567890",
            "PASSWORD": "fake_test_password_abcdefghijklmnop",
            "SECRET_TOKEN": "fake_test_secret_token_xyz123456789",
            "NORMAL_VAR": "normalvalue",
        }

        masked = loader.mask_sensitive_vars(env_vars)

        assert masked["API_KEY"] == "fa******..."
        assert masked["PASSWORD"] == "fa******..."
        assert masked["SECRET_TOKEN"] == "fa******..."
        assert masked["NORMAL_VAR"] == "normalvalue"

    def test_mask_sensitive_vars_short_values(self):
        """Test masking sensitive environment variables with short values."""
        loader = EnvironmentLoader()
        env_vars = {
            "API_KEY": "abc",  # Less than 4 characters
            "SECRET": "",  # Empty string
        }

        masked = loader.mask_sensitive_vars(env_vars)

        assert masked["API_KEY"] == "****"
        assert masked["SECRET"] == "[EMPTY]"

    def test_mask_sensitive_vars_case_insensitive(self):
        """Test masking sensitive environment variables is case insensitive."""
        loader = EnvironmentLoader()
        env_vars = {
            "api_key": "fake_test_api_key_12345678901234567890",
            "USER_PASSWORD": "fake_test_password_abcdefghijklmnop",
            "Auth_Token": "fake_test_token_xyz123456789abcdef",
        }

        masked = loader.mask_sensitive_vars(env_vars)

        assert masked["api_key"] == "fa******..."
        assert masked["USER_PASSWORD"] == "fa******..."
        assert masked["Auth_Token"] == "fa******..."


class TestEnvironmentLoaderSecurity:
    """Security-focused test cases for EnvironmentLoader."""

    def test_get_safe_env_vars_excludes_sensitive_data(self):
        """Test that get_safe_env_vars excludes sensitive environment variables."""
        loader = EnvironmentLoader()

        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "fake_test_key_123",
                "DATABASE_PASSWORD": "fake_test_password",
                "NORMAL_VAR": "safe_value",
                "DEBUG": "true",
                "SECRET_TOKEN": "fake_secret",
            },
        ):
            safe_vars = loader.get_safe_env_vars()

            # Should exclude sensitive variables
            assert "OPENAI_API_KEY" not in safe_vars
            assert "DATABASE_PASSWORD" not in safe_vars
            assert "SECRET_TOKEN" not in safe_vars

            # Should include non-sensitive variables
            assert "NORMAL_VAR" in safe_vars
            assert "DEBUG" in safe_vars
            assert safe_vars["NORMAL_VAR"] == "safe_value"

    def test_mask_sensitive_vars_prevents_info_leakage(self):
        """Test that masking doesn't leak too much information for short secrets."""
        loader = EnvironmentLoader()
        env_vars = {"API_KEY": "short123", "SECRET": "tiny", "PASSWORD": "ab"}  # 8 chars or less  # 4 chars  # 2 chars

        masked = loader.mask_sensitive_vars(env_vars)

        # Should not reveal any characters for short secrets
        assert masked["API_KEY"] == "****"
        assert masked["SECRET"] == "****"
        assert masked["PASSWORD"] == "****"

        # Ensure no original characters are visible
        for key, original in env_vars.items():
            assert original not in masked[key]

    def test_mask_sensitive_vars_handles_edge_cases(self):
        """Test masking handles various edge cases securely."""
        loader = EnvironmentLoader()
        env_vars = {
            "API_KEY": "verylongfaketestapikey123456789012345",  # Very long
            "SECRET": None,  # None value
            "PASSWORD": "",  # Empty string
            "TOKEN": "a",  # Single character
        }

        # Handle None values gracefully
        env_vars_safe = {k: v for k, v in env_vars.items() if v is not None}

        masked = loader.mask_sensitive_vars(env_vars_safe)

        assert masked["API_KEY"] == "ve******..."
        assert masked["PASSWORD"] == "[EMPTY]"
        assert masked["TOKEN"] == "****"

    def test_enhanced_sensitive_keyword_detection(self):
        """Test that enhanced sensitive keyword list detects more patterns."""
        loader = EnvironmentLoader()
        env_vars = {
            "AUTH_HEADER": "fake_auth_value_123456789",
            "CREDENTIAL_FILE": "fake_credential_path_123456789",
            "CLIENT_SECRET": "fake_client_secret_123456789",
            "BEARER_TOKEN": "fake_bearer_token_123456789",
            "NORMAL_CONFIG": "safe_value",
        }

        masked = loader.mask_sensitive_vars(env_vars)

        # Should mask auth/credential related variables
        assert masked["AUTH_HEADER"] == "fa******..."
        assert masked["CREDENTIAL_FILE"] == "fa******..."
        assert masked["CLIENT_SECRET"] == "fa******..."
        assert masked["BEARER_TOKEN"] == "fa******..."

        # Should not mask normal config
        assert masked["NORMAL_CONFIG"] == "safe_value"

    @patch.dict(os.environ, {"TEST_API_KEY": "fake_test_key_should_not_be_used", "ENVIRONMENT": "test"})
    def test_no_real_credentials_in_test_environment(self):
        """Test that we don't accidentally use real credentials in tests."""
        loader = EnvironmentLoader()

        # Verify test environment is properly isolated
        env_value = loader.get_env_var("ENVIRONMENT")
        assert env_value == "test"

        # Verify test key patterns are clearly fake
        test_key = loader.get_env_var("TEST_API_KEY")
        assert test_key is not None
        assert "fake" in test_key.lower() or "test" in test_key.lower()

        # Should not contain patterns that look like real keys
        assert not test_key.startswith("sk-") or "fake" in test_key.lower()
        assert not test_key.startswith("ak-") or "fake" in test_key.lower()
