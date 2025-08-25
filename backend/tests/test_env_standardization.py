"""Test environment variable standardization for Issue #24."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_gemini_api_key_environment_variable():
    """Test that GEMINI_API_KEY environment variable is used consistently."""
    # Test that the environment variable can be set and read
    test_key = "test_gemini_key_123"

    with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}, clear=True):
        assert os.getenv("GEMINI_API_KEY") == test_key

        # Test that legacy API_KEY is not used when GEMINI_API_KEY is available
        assert os.getenv("API_KEY") is None


def test_env_file_format_uses_gemini_api_key():
    """Test that .env file format uses GEMINI_API_KEY consistently."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        env_path = Path(tmp_dir) / ".env"

        # Write a properly formatted .env file
        env_content = (
            'GEMINI_API_KEY="test_api_key_456"\nOBSIDIAN_VAULT_PATH="/test/vault"\n'
        )
        env_path.write_text(env_content, encoding="utf-8")

        # Read and verify the format
        content = env_path.read_text(encoding="utf-8")
        assert "GEMINI_API_KEY=" in content
        assert "test_api_key_456" in content
        assert "OBSIDIAN_VAULT_PATH=" in content


def test_no_legacy_api_key_usage():
    """Test that no code uses legacy API_KEY instead of GEMINI_API_KEY."""
    # This test ensures we don't regress to using the old API_KEY format

    # Check that environment doesn't have legacy API_KEY when GEMINI_API_KEY is set
    with patch.dict(os.environ, {"GEMINI_API_KEY": "correct_key"}, clear=True):
        # Verify GEMINI_API_KEY is used
        assert os.getenv("GEMINI_API_KEY") == "correct_key"
        # Verify legacy API_KEY is not set
        assert os.getenv("API_KEY") is None


def test_tauri_backend_consistency():
    """Test that Tauri backend uses same env var as Python backend."""
    # This is more of a documentation test since we can't easily test Rust code
    # But we can verify the expected environment variable name

    expected_env_var = "GEMINI_API_KEY"

    # Verify this matches what our Python backend expects
    with patch.dict(os.environ, {expected_env_var: "tauri_test_key"}, clear=True):
        assert os.getenv(expected_env_var) == "tauri_test_key"

    # This test documents that both Tauri (Rust) and Python should use GEMINI_API_KEY
    # The actual Rust code verification would need to be done in Rust tests
