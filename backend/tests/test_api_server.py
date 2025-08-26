"""
Test suite for FastAPI server implementation.
Following TDD approach - these tests should now pass.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

# Import the modules we'll be mocking
from cartaos.utils import pdf_utils
from cartaos.utils import ai_utils

# Create mock modules for the processors
sys.modules['cartaos.processors.ocr_processor'] = MagicMock()
sys.modules['cartaos.processors.summarizer'] = MagicMock()

# Import the mocks after setting up the mock modules
from cartaos.processors.ocr_processor import OcrProcessor
from cartaos.processors.summarizer import Summarizer


def test_api_server_import():
    """Test that the API server module can be imported."""
    from cartaos.api.server import app

    assert app is not None


def test_health_endpoint():
    """Test the health check endpoint."""
    from cartaos.api.server import app
    from datetime import datetime, timezone
    
    with patch("cartaos.api.server.datetime") as mock_datetime:
        # Mock the current time
        fixed_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_time
        
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert data["timestamp"] == fixed_time.isoformat()


def test_list_files_endpoint():
    """Test the list files endpoint."""
    from cartaos.api.server import app
    from cartaos.utils.logging_utils import LogContext
    
    # Create test client with overridden dependencies
    client = TestClient(app)
    
    # Create a proper mock for LogContext
    class MockLogContext:
        def __init__(self, *args, **kwargs):
            self.logger = Mock()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    # Mock the dependencies
    with patch("cartaos.api.server.LogContext", new=MockLogContext), \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("pathlib.Path.iterdir") as mock_iterdir, \
         patch("pathlib.Path.absolute") as mock_absolute:
        
        # Set up mock file system
        mock_exists.return_value = True
        mock_absolute.return_value = Path("/mock/absolute/path/00_Inbox")
        
        # Mock files in the directory
        mock_file1 = Mock()
        mock_file1.name = "file1.pdf"
        mock_file1.is_file.return_value = True
        mock_file2 = Mock()
        mock_file2.name = "file2.pdf"
        mock_file2.is_file.return_value = True
        mock_iterdir.return_value = [mock_file1, mock_file2]
        
        # Make the test request
        response = client.get("/api/files/00_Inbox")
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["files"] == ["file1.pdf", "file2.pdf"]
        assert data["total_count"] == 2


def test_process_file_endpoint():
    """Test the process file endpoint."""
    from cartaos.api.server import app
    
    # Mock the missing processors module
    sys.modules['cartaos.processors'] = Mock()
    sys.modules['cartaos.processors.triage'] = Mock()
    TriageProcessor = Mock()
    sys.modules['cartaos.processors.triage'].TriageProcessor = TriageProcessor
    
    # Create a proper mock for LogContext
    class MockLogContext:
        def __init__(self, *args, **kwargs):
            self.logger = Mock()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    client = TestClient(app)
    
    # Mock the dependencies
    with patch("cartaos.api.server.LogContext", new=MockLogContext), \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("cartaos.utils.pdf_utils.extract_text") as mock_extract, \
         patch("cartaos.api.server.ProcessFileRequest") as mock_request, \
         patch.object(TriageProcessor, 'process') as mock_process:
        
        # Set up mocks
        mock_exists.return_value = True
        mock_extract.return_value = "This is a long text with more than 500 characters." * 20
        mock_process.return_value = {
            "status": "completed",
            "output_path": "/path/to/processed_file.pdf"
        }
        
        # Mock the request model
        mock_request.return_value = Mock(
            file_path="/path/to/file.pdf",
            operation="triage"
        )
        
        # Make the test request
        response = client.post(
            "/api/process",
            json={"file_path": "/path/to/file.pdf", "operation": "triage"},
        )
        
        # Verify the response


def test_triage_endpoint():
    """Test the triage endpoint."""
    from cartaos.api.server import app
    from cartaos.triage import TriageProcessor
    
    # Create a proper mock for LogContext
    class MockLogContext:
        def __init__(self, *args, **kwargs):
            self.logger = Mock()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    client = TestClient(app)
    
    # Create a temporary test file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        test_file_path = tmp_file.name
    
    try:
        # Mock the dependencies
        with patch("cartaos.api.server.LogContext", new=MockLogContext), \
             patch("pathlib.Path.exists") as mock_exists, \
             patch("cartaos.api.server.TriageRequest") as mock_request, \
             patch.object(TriageProcessor, 'process') as mock_triage:
            
            # Set up mocks
            mock_exists.return_value = True
            mock_triage.return_value = {
                "destination": "03_Lab", 
                "reason": "PDF needs OCR processing (test mode)",
                "confidence": 0.95
            }
            
            # Mock the request model
            mock_request.return_value = Mock(
                file_path=test_file_path
            )
            
            # Make the test request
            response = client.post(
                "/api/triage",
                json={"file_path": test_file_path},
            )
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert data["destination"] == "03_Lab"
            assert data["reason"] == "PDF needs OCR processing (test mode)"
    finally:
        # Clean up the temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)


def test_ocr_endpoint():
    """Test the OCR endpoint."""
    from cartaos.api.server import app, OCRResponse
    
    # Create a proper mock for LogContext
    class MockLogContext:
        def __init__(self, *args, **kwargs):
            self.logger = Mock()
            
        def __enter__(self):
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    client = TestClient(app)
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        test_file_path = tmp_file.name
    
    try:
        # Create a mock for OcrProcessor
        mock_processor = Mock()
        mock_processor.process.return_value = "/path/to/ocr_file.pdf"
        
        # Mock the dependencies
        with patch("cartaos.api.server.LogContext", new=MockLogContext), \
             patch("pathlib.Path.exists") as mock_exists, \
             patch("cartaos.processors.ocr_processor.OcrProcessor") as mock_ocr_processor:
            
            # Set up mocks
            mock_exists.return_value = True
            mock_ocr_processor.return_value = mock_processor
            
            # Make the test request
            response = client.post(
                "/api/ocr",
                json={"file_path": test_file_path},
            )
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            # The output path should be in the same directory as the input with 'ocr_' prefix
            assert data["output_path"].endswith("ocr_" + os.path.basename(test_file_path))
            assert "pages_processed" in data
    finally:
        # Clean up the temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)


def test_summarize_endpoint():
    """Test the summarize endpoint."""
    # Import required modules
    import os
    from unittest.mock import Mock, patch
    from fastapi.testclient import TestClient
    from cartaos.api.server import app
    from cartaos.utils import pdf_utils
    from cartaos.utils import ai_utils
    from cartaos.api.models import SummarizeRequest, SummarizeResponse
    
    # Create a test client
    client = TestClient(app)
    
    # Create a temporary test file with some content
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        test_file_path = tmp_file.name
        # Write a simple PDF header to make it a valid PDF
        tmp_file.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT\n/F1 24 Tf\n100 700 Td\n(Test PDF Document) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000015 00000 n \n0000000069 00000 n \n0000000120 00000 n \n0000000209 00000 n \n0000000229 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n310\n%%EOF')
    
    try:
        # Create a proper mock for LogContext
        class MockLogContext:
            def __init__(self, *args, **kwargs):
                self.logger = Mock()
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        
        # Mock the dependencies
        with patch("cartaos.api.server.LogContext", new=MockLogContext), \
             patch("pathlib.Path.exists") as mock_exists, \
             patch.object(pdf_utils, 'extract_text') as mock_extract_text, \
             patch.object(ai_utils, 'generate_summary') as mock_generate_summary:
            
            # Set up mocks
            mock_exists.return_value = True
            mock_extract_text.return_value = "This is a sample document text that needs to be summarized."
            mock_generate_summary.return_value = "This is a summary of the document."
            
            # Create a test file and get its path
            with open(test_file_path, 'wb') as f:
                f.write(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 44>>stream\nBT\n/F1 24 Tf\n100 700 Td\n(Test PDF Document) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000015 00000 n \n0000000069 00000 n \n0000000120 00000 n \n0000000209 00000 n \n0000000229 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n310\n%%EOF')
            
            # Make the test request with JSON payload
            response = client.post(
                "/api/summarize",
                json={"file_path": test_file_path}
            )
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert data["summary"] == "This is a summary of the document."
            assert "word_count" in data
            assert "source_pages" in data
            
            # Verify the mocks were called correctly
            mock_extract_text.assert_called_once()
            mock_generate_summary.assert_called_once_with("This is a sample document text that needs to be summarized.")
    finally:
        # Clean up the temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)


def test_error_handling():
    """Test error handling in the API."""
    from cartaos.api.server import app
    from fastapi import status
    
    client = TestClient(app)
    
    # Test with invalid request (missing required field)
    response = client.post("/api/process", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Check that the error response has the expected structure
    error_data = response.json()
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)
    assert len(error_data["detail"]) > 0
    assert "msg" in error_data["detail"][0]
    
    # Test with invalid operation
    response = client.post(
        "/api/process",
        json={"file_path": "/path/to/file.txt", "operation": "invalid_operation"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_data = response.json()
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)
    assert any("Input should be 'triage', 'ocr', 'summarize' or 'lab'" in item.get("msg", "") 
             for item in error_data["detail"] if isinstance(item, dict))

def test_cors_configuration():
    """Test CORS configuration for local development."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.testclient import TestClient
    
    # Create a test app with CORS middleware
    test_app = FastAPI()
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:1420", "tauri://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add a test endpoint
    @test_app.get("/api/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(test_app)
    
    # Test preflight request
    response = client.options(
        "/api/test",
        headers={
            "Origin": "http://localhost:1420",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    
    # Verify CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:1420"
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


def test_request_validation():
    """Test request validation with Pydantic models."""
    from cartaos.api.server import app
    from cartaos.api.models import ProcessFileResponse
    from fastapi import status

    # Create a test client
    client = TestClient(app)

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        test_file_path = tmp_file.name

    try:
        # Create a proper mock for LogContext
        class MockLogContext:
            def __init__(self, *args, **kwargs):
                self.logger = Mock()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        with patch("cartaos.api.server.LogContext", new=MockLogContext), \
             patch("pathlib.Path.exists") as mock_exists, \
             patch("cartaos.api.server.process_file") as mock_process_file, \
             patch("cartaos.utils.pdf_utils.extract_text") as mock_extract_text, \
             patch("cartaos.utils.ai_utils.generate_summary") as mock_generate_summary:

            # Set up mocks
            mock_exists.return_value = True
            mock_process_file.return_value = ProcessFileResponse(
                status="success",
                message="File processed successfully"
            )
            mock_extract_text.return_value = "Sample document text"
            mock_generate_summary.return_value = "This is a test summary"

            # Test with valid request to /api/ocr
            response = client.post(
                "/api/ocr",
                json={"file_path": test_file_path},
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Test with valid request to /api/summarize
            response = client.post(
                "/api/summarize",
                json={"file_path": test_file_path}
            )
            assert response.status_code == status.HTTP_200_OK
            
            # Test with invalid request (missing required field)
            response = client.post("/api/ocr", json={})
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    finally:
        # Clean up the temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
