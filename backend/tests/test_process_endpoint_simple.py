"""
Simple test for the process file endpoint with module-level decorator mocking.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Mock the decorator at module level
original_log_processing_stage = None

def mock_log_processing_stage(stage_name):
    def decorator(f):
        return f
    return decorator

# Apply the mock before importing the app
import cartaos.processing.decorators
original_log_processing_stage = cartaos.processing.decorators.log_processing_stage
cartaos.processing.decorators.log_processing_stage = mock_log_processing_stage

# Now import the app with the mocked decorator
from cartaos.api.server import app
from fastapi.testclient import TestClient
from cartaos.api.models import ProcessFileRequest, OperationType

# Create test client
client = TestClient(app)

def test_process_file_endpoint_simple(tmp_path):
    """Test the process file endpoint with module-level decorator mocking."""
    # Setup test file
    test_file = tmp_path / "test.pdf"
    test_file.touch()

    # Mock the file processing
    with patch("pathlib.Path.exists") as mock_exists, \
         patch("cartaos.security.audit_logger.AuditLogger") as mock_audit_logger, \
         patch("cartaos.api.server._process_with_processor") as mock_process:

        # Setup mocks
        mock_exists.return_value = True
        mock_process.return_value = {
            "status": "success",
            "message": "File processed",
            "output_path": str(test_file.with_suffix('.processed')),
            "metadata": {}
        }

        # Create a valid request payload
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

# Restore the original decorator after tests
def teardown_module():
    if original_log_processing_stage is not None:
        import cartaos.processing.decorators
        cartaos.processing.decorators.log_processing_stage = original_log_processing_stage
