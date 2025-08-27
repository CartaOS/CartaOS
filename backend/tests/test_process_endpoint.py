"""
Test suite for the process file endpoint.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

# Import the app with the decorator patched
with patch("cartaos.processing.decorators.log_processing_stage", lambda x: lambda f: f):
    from cartaos.api.server import app

# Create test client
client = TestClient(app)

def test_process_file_endpoint(tmp_path):
    """Test the process file endpoint with proper decorator mocking."""
    # Setup test file
    test_file = tmp_path / "test.pdf"
    test_file.touch()

    # Import the OperationType enum
    from cartaos.api.models import OperationType

    # Mock the file processing
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("cartaos.api.server.AuditLogger") as mock_audit_logger, \
         patch("cartaos.api.server._process_with_processor") as mock_process:

        # Setup mocks
        mock_exists.return_value = True
        mock_process.return_value = {
            "status": "success",
            "message": "File processed",
            "output_path": str(test_file.with_suffix('.processed')),
            "metadata": {}
        }

        # Create a valid request payload using the OperationType enum
        payload = {
            "file_path": str(test_file),
            "operation": OperationType.TRIAGE.value
        }

        # Make the request with valid operation type
        response = client.post("/api/process", json=payload)

        # Verify the response
        if response.status_code != 200:
            print("Response content:", response.content)
        assert response.status_code == 200, f"Unexpected status code. Response: {response.content}"
        
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "File processed"
        assert data["output_path"] == str(test_file.with_suffix('.processed'))
        assert data["metadata"] == {}
