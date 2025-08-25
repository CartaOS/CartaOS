# -*- coding: utf-8 -*-
# backend/tests/test_ai_utils.py

from unittest.mock import MagicMock, mock_open, patch

import pytest

from cartaos.utils import ai_utils


@pytest.fixture(autouse=True)
def reset_client():
    ai_utils._CLIENT = None


@patch("cartaos.utils.ai_utils.Client")
@patch("cartaos.utils.ai_utils.get_secure_api_key")
def test_get_client_success(mock_get_key, mock_gemini_client):
    """Test that get_client returns a client when API key is present via keychain."""
    mock_get_key.return_value = "FAKE_API_KEY"
    client = ai_utils.get_client()
    assert client is not None
    mock_gemini_client.assert_called_once_with(api_key="FAKE_API_KEY")


@patch("cartaos.utils.ai_utils.Client")
@patch("cartaos.utils.ai_utils.get_secure_api_key")
def test_get_client_singleton(mock_get_key, mock_gemini_client):
    """Test that get_client returns the same client instance on subsequent calls."""
    mock_get_key.return_value = "FAKE_API_KEY"
    client1 = ai_utils.get_client()  # First call initializes the client
    mock_gemini_client.assert_called_once_with(api_key="FAKE_API_KEY")

    client2 = ai_utils.get_client()  # Second call should return the cached client
    assert client1 is client2

    # The client constructor should still be called only once due to singleton caching
    mock_gemini_client.assert_called_once()


@patch("cartaos.utils.ai_utils.get_secure_api_key")
def test_get_client_no_api_key(mock_get_key):
    """Test that get_client raises ValueError if API key is not found."""
    mock_get_key.return_value = None
    with pytest.raises(ValueError, match="API key is not configured."):
        ai_utils.get_client()


@patch("cartaos.utils.ai_utils.get_client")
@patch("builtins.open", new_callable=mock_open, read_data="Test prompt with {text}")
@patch("pathlib.Path.exists")
def test_generate_summary_success(mock_path_exists, mock_file_open, mock_get_client):
    """Test successful summary generation."""
    mock_path_exists.return_value = True
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a summary."
    mock_client.models.generate_content.return_value = mock_response
    mock_get_client.return_value = mock_client

    summary = ai_utils.generate_summary("Some text to summarize.")

    assert summary == "This is a summary."
    mock_client.models.generate_content.assert_called_once()


@patch("cartaos.utils.ai_utils.get_client")
def test_generate_summary_client_error(mock_get_client):
    """Test summary generation when the client fails to initialize."""
    mock_get_client.side_effect = ValueError("API key error")
    summary = ai_utils.generate_summary("Some text.")
    assert summary is None


@patch("cartaos.utils.ai_utils.get_client")
@patch("pathlib.Path.exists")
def test_generate_summary_no_prompt_file(mock_path_exists, mock_get_client):
    """Test summary generation when the prompt file is missing."""
    mock_path_exists.return_value = False
    mock_get_client.return_value = MagicMock()

    summary = ai_utils.generate_summary("Some text.")
    assert summary is None
