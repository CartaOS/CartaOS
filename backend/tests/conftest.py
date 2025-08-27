"""
Test configuration and fixtures for the CartaOS backend tests.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from cartaos.app_config import AppConfig, get_config
from cartaos.api.server import app


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch, tmp_path):
    """Set up test environment with necessary configurations."""
    # Set environment variables
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(tmp_path / "vault"))
    
    # Clear any existing config instance
    if hasattr(get_config, "_instance"):
        delattr(get_config, "_instance")


@pytest.fixture
def mock_config(monkeypatch, tmp_path):
    """Create a mock AppConfig for testing."""
    # Create test directories
    test_dirs = {
        "00_Inbox": tmp_path / "00_Inbox",
        "02_Triage": tmp_path / "02_Triage",
        "03_Lab": tmp_path / "03_Lab",
        "04_ReadyForOCR": tmp_path / "04_ReadyForOCR",
        "05_ReadyForSummary": tmp_path / "05_ReadyForSummary",
        "06_TooLarge": tmp_path / "06_TooLarge",
        "07_Processed": tmp_path / "07_Processed",
        "vault": tmp_path / "vault"
    }
    
    # Create directories
    for dir_path in test_dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create a new config instance with test settings
    config = AppConfig()
    
    # Update the config with test paths
    config.pipeline_dirs = {
        stage: path for stage, path in test_dirs.items() 
        if stage != "vault"
    }
    config.obsidian_vault_path = test_dirs["vault"]
    config.gemini_api_key = "test_api_key"
    
    # Clear any existing instance and patch get_config
    if hasattr(get_config, "_instance"):
        delattr(get_config, "_instance")
    
    # Patch get_config to return our test config
    with patch('cartaos.get_config', return_value=config):
        yield config


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_pdf_utils():
    """Mock the pdf_utils module."""
    with patch("cartaos.utils.pdf_utils") as mock:
        yield mock


@pytest.fixture
def mock_ai_utils():
    """Mock the ai_utils module."""
    with patch("cartaos.utils.ai_utils") as mock:
        yield mock


@pytest.fixture
def test_pdf_file(tmp_path):
    """Create a test PDF file."""
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        # Minimal PDF content
        f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n" +
                b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n" +
                b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n" +
                b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n" +
                b"5 0 obj<</Length 44>>stream\nBT\n/F1 24 Tf\n100 700 Td\n(Test PDF Document) Tj\nET\nendstream\nendobj\n" +
                b"xref\n0 6\n0000000000 65535 f \n0000000015 00000 n \n0000000069 00000 n \n0000000120 00000 n \n0000000209 00000 n \n0000000229 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n310\n%%EOF")
    return pdf_path
