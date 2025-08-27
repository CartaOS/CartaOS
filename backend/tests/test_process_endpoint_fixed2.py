"""
Test the process file endpoint with proper decorator mocking.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute

# Mock the decorator before importing the app
with patch("cartaos.processing.decorators.log_processing_stage", lambda x: lambda f: f):
    # Now import the app with the mocked decorator
    from cartaos.api.server import app as original_app, process_file
    from fastapi.testclient import TestClient
    from cartaos.api.models import ProcessFileRequest, OperationType, ProcessFileResponse

# Create a new FastAPI instance for testing
app = FastAPI()

# Copy all routes except the process_file endpoint
for route in original_app.routes:
    if not (isinstance(route, APIRoute) and route.name == 'process_file'):
        app.router.routes.append(route)

# Add the process_file route with our implementation
@app.post("/api/process", response_model=ProcessFileResponse)
async def process_file_route(request: ProcessFileRequest):
    return await process_file(request)

# Create test client
client = TestClient(app)

def test_process_file_endpoint(tmp_path):
    """Test the process file endpoint with proper decorator mocking."""
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
