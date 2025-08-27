# -*- coding: utf-8 -*-
# backend/tests/test_ai_utils.py

import os
import logging
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch, PropertyMock

import pytest

from cartaos import get_config
from cartaos.app_config import AppConfig
from cartaos.utils import ai_utils
from cartaos.config import settings


@pytest.fixture(autouse=True)
def reset_client():
    """Reset the client singleton and app config before each test."""
    ai_utils._CLIENT = None
    # Reset the app config singleton
    if hasattr(AppConfig, "_instance"):
        delattr(AppConfig, "_instance")
    # Reset the logger
    logging.getLogger().handlers = []
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def mock_app_config(monkeypatch):
    """Create a test app config with default values."""
    # Create a test config
    test_config = AppConfig()
    test_config.gemini_api_key = "test_api_key"
    test_config.obsidian_vault_path = Path("/test/vault")
    
    # Patch get_config to return our test config
    with patch('cartaos.get_config', return_value=test_config):
        yield test_config


@patch("cartaos.utils.ai_utils.Client")
def test_get_client_success(mock_gemini_client, mock_app_config):
    """Test that get_client returns a client when API key is present in config."""
    # Call the function
    client = ai_utils.get_client()
    
    # Assertions
    assert client is not None
    mock_gemini_client.assert_called_once_with(api_key="test_api_key")


@patch("cartaos.utils.ai_utils.Client")
def test_get_client_singleton(mock_gemini_client, mock_app_config):
    """Test that get_client returns the same client instance on subsequent calls."""
    # Setup mock client
    mock_client_instance = MagicMock()
    mock_gemini_client.return_value = mock_client_instance
    
    # Call the function multiple times
    client1 = ai_utils.get_client()
    client2 = ai_utils.get_client()
    
    # Assertions
    assert client1 is client2
    mock_gemini_client.assert_called_once_with(api_key="test_api_key")
    
    # Reset call count
    mock_gemini_client.reset_mock()
    
    # Second call should return the cached client
    assert client1 is client2
    
    # The client constructor should not be called again
    mock_gemini_client.assert_not_called()


@patch.dict('os.environ', {'GEMINI_API_KEY': ''}, clear=True)
@patch('cartaos.utils.ai_utils.logger')
def test_get_client_no_api_key(mock_logger):
    """Test that get_client raises ValueError if API key is not configured."""
    # Save the original client and reset it
    original_client = ai_utils._CLIENT
    ai_utils._CLIENT = None
    
    # Clear the config cache to ensure we get a fresh config
    if hasattr(get_config, '_instance'):
        delattr(get_config, '_instance')
    
    # Test that the function raises ValueError
    with pytest.raises(ValueError, match="API key is not configured in application settings"):
        ai_utils.get_client()
    
    # Verify the error was logged
    mock_logger.error.assert_called_once_with(
        "GEMINI_API_KEY is not configured in AppConfig"
    )
    
    # Restore the original client
    ai_utils._CLIENT = original_client


@patch("cartaos.utils.ai_utils.get_client")
@patch("builtins.open", new_callable=mock_open, read_data="Test prompt with {text}")
@patch("pathlib.Path.exists")
@patch("cartaos.utils.ai_utils.settings")
def test_generate_summary_success(mock_settings, mock_path_exists, mock_file_open, mock_get_client, tmp_path):
    """Test successful summary generation."""
    # Setup mocks
    mock_path_exists.return_value = True
    mock_client_instance = MagicMock()
    mock_client_instance.models.generate_content.return_value.text = "Generated summary"
    mock_get_client.return_value = mock_client_instance
    
    # Create a test prompt file
    prompt_file = tmp_path / "prompts" / "summary_prompt.md"
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text("Test prompt with {text}")
    
    # Mock settings
    mock_settings.PROMPTS_DIR = tmp_path / "prompts"
    
    # Call the function
    result = ai_utils.generate_summary("Test text")
    
    # Assertions
    assert result == "Generated summary"
    mock_file_open.assert_called_once()
    mock_client_instance.models.generate_content.assert_called_once()


@patch("cartaos.utils.ai_utils.get_client")
@patch("cartaos.utils.ai_utils.logging")
def test_generate_summary_client_error(mock_logging, mock_get_client, mock_app_config):
    """Test summary generation when the client fails to initialize."""
    # Setup mock to raise an error
    mock_get_client.side_effect = ValueError("API key not found")
    
    # Reset the mock logging
    mock_logging.reset_mock()
    
    # Call the function
    result = ai_utils.generate_summary("Test text")
    
    # Assertions
    assert result is None
    
    # Get the actual call arguments
    args, _ = mock_logging.error.call_args
    
    # Check the error message format
    assert len(args) == 2
    assert args[0] == "Failed to generate summary due to configuration error: %s"
    assert str(args[1]) == "API key not found"  # Check the string representation of the exception


@patch("pathlib.Path.exists")
@patch("cartaos.utils.ai_utils.get_client")
@patch("cartaos.utils.ai_utils.settings")
@patch("cartaos.utils.ai_utils.logging")
def test_generate_summary_no_prompt_file(mock_logging, mock_settings, mock_get_client, mock_path_exists, tmp_path):
    """Test summary generation when the prompt file is missing."""
    # Setup mocks
    mock_path_exists.return_value = False
    mock_client_instance = MagicMock()
    mock_get_client.return_value = mock_client_instance
    
    # Reset the mock logging
    mock_logging.reset_mock()
    
    # Mock settings
    mock_settings.PROMPTS_DIR = tmp_path / "prompts"
    
    # Create the prompts directory but not the file
    (tmp_path / "prompts").mkdir(parents=True, exist_ok=True)
    
    # Call the function
    result = ai_utils.generate_summary("Test text")
    
    # Assertions
    assert result is None
    
    # Get the actual call arguments
    args, _ = mock_logging.error.call_args
    
    # Check the error message format
    assert len(args) == 2
    assert args[0] == "Prompt file not found at: %s"
    assert str(args[1]).endswith("prompts/summary_prompt.md")  # Check the path ends correctly
