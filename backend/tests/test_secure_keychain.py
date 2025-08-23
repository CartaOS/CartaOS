"""
Test suite for secure keychain implementation.
Following TDD approach - these tests should fail initially.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


def test_keychain_module_import():
    """Test that the keychain module can be imported."""
    from cartaos.utils.keychain import SecureKeychain

    assert SecureKeychain is not None


def test_keychain_store_key():
    """Test storing a key in the OS keychain."""
    from cartaos.utils.keychain import SecureKeychain

    keychain = SecureKeychain()

    # Mock the keyring operations
    with patch("keyring.set_password") as mock_set:
        result = keychain.store_key("GEMINI_API_KEY", "test-api-key-123")
        assert result is True
        mock_set.assert_called_once_with(
            "CartaOS", "GEMINI_API_KEY", "test-api-key-123"
        )


def test_keychain_retrieve_key():
    """Test retrieving a key from the OS keychain."""
    from cartaos.utils.keychain import SecureKeychain

    keychain = SecureKeychain()

    # Mock the keyring operations
    with patch("keyring.get_password") as mock_get:
        mock_get.return_value = "test-api-key-123"
        result = keychain.get_key("GEMINI_API_KEY")
        assert result == "test-api-key-123"
        mock_get.assert_called_once_with("CartaOS", "GEMINI_API_KEY")


def test_keychain_delete_key():
    """Test deleting a key from the OS keychain."""
    from cartaos.utils.keychain import SecureKeychain

    keychain = SecureKeychain()

    # Mock the keyring operations
    with patch("keyring.delete_password") as mock_delete:
        result = keychain.delete_key("GEMINI_API_KEY")
        assert result is True
        mock_delete.assert_called_once_with("CartaOS", "GEMINI_API_KEY")


def test_keychain_key_not_found():
    """Test handling when a key is not found in keychain."""
    from cartaos.utils.keychain import SecureKeychain

    keychain = SecureKeychain()

    # Mock keyring to return None (key not found)
    with patch("keyring.get_password") as mock_get:
        mock_get.return_value = None
        result = keychain.get_key("NONEXISTENT_KEY")
        assert result is None


def test_keychain_error_handling():
    """Test error handling in keychain operations."""
    from cartaos.utils.keychain import SecureKeychain

    keychain = SecureKeychain()

    # Mock keyring to raise an exception
    with patch("keyring.get_password") as mock_get:
        mock_get.side_effect = Exception("Keychain access denied")
        result = keychain.get_key("GEMINI_API_KEY")
        assert result is None


def test_ai_utils_keychain_integration():
    """Test that ai_utils integrates with keychain for API key retrieval."""
    # Reset the global client to force re-initialization
    import cartaos.utils.ai_utils

    cartaos.utils.ai_utils._CLIENT = None

    from cartaos.utils.ai_utils import get_client

    # Mock keychain to return API key
    with patch("cartaos.utils.ai_utils.get_secure_api_key") as mock_get_key, patch(
        "cartaos.utils.ai_utils.Client"
    ) as mock_client:
        mock_get_key.return_value = "secure-api-key-from-keychain"
        mock_client.return_value = MagicMock()

        # Should try keychain first, then fall back to .env
        client = get_client()
        mock_get_key.assert_called_with("GEMINI_API_KEY")


def test_env_fallback_when_keychain_unavailable():
    """Test fallback to .env when keychain is unavailable."""
    # Reset the global client to force re-initialization
    import cartaos.utils.ai_utils

    cartaos.utils.ai_utils._CLIENT = None

    from cartaos.utils.ai_utils import get_client

    # Mock keychain to be unavailable and .env to have key
    with patch("cartaos.utils.ai_utils.get_secure_api_key") as mock_get_key, patch(
        "cartaos.utils.ai_utils.Client"
    ) as mock_client:

        mock_get_key.return_value = "env-api-key"  # Fallback to env
        mock_client.return_value = MagicMock()

        client = get_client()
        mock_get_key.assert_called_with("GEMINI_API_KEY")


def test_migration_from_env_to_keychain():
    """Test migration of API key from .env to keychain."""
    from cartaos.utils.keychain import migrate_env_to_keychain

    # Mock .env file with API key
    with patch("cartaos.utils.keychain.load_dotenv"), patch.dict(
        os.environ, {"GEMINI_API_KEY": "env-api-key"}
    ), patch("cartaos.utils.keychain.SecureKeychain") as mock_keychain_class:

        mock_keychain = Mock()
        mock_keychain.store_key.return_value = True
        mock_keychain_class.return_value = mock_keychain

        result = migrate_env_to_keychain()
        assert result is True
        mock_keychain.store_key.assert_called_with("GEMINI_API_KEY", "env-api-key")


def test_keychain_cross_platform_compatibility():
    """Test that keychain works across different platforms."""
    from cartaos.utils.keychain import SecureKeychain

    # Test different platform scenarios
    platforms = ["darwin", "win32", "linux"]

    for platform in platforms:
        with patch("sys.platform", platform), patch("keyring.get_password") as mock_get:
            mock_get.return_value = f"key-for-{platform}"

            keychain = SecureKeychain()
            result = keychain.get_key("GEMINI_API_KEY")
            assert result == f"key-for-{platform}"
