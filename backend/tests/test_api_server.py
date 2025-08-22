"""
Test suite for FastAPI server implementation.
Following TDD approach - these tests should now pass.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
import tempfile
import os
from pathlib import Path


def test_api_server_import():
    """Test that the API server module can be imported."""
    from cartaos.api.server import app
    assert app is not None


def test_health_endpoint():
    """Test the health check endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_list_files_endpoint():
    """Test the list files endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.iterdir') as mock_iterdir:
        mock_exists.return_value = True
        mock_file1 = Mock()
        mock_file1.name = "file1.pdf"
        mock_file1.is_file.return_value = True
        mock_file2 = Mock()
        mock_file2.name = "file2.pdf"
        mock_file2.is_file.return_value = True
        mock_iterdir.return_value = [mock_file1, mock_file2]
        
        response = client.get("/api/files/00_Inbox")
        assert response.status_code == 200
        data = response.json()
        assert data["files"] == ["file1.pdf", "file2.pdf"]
        assert data["total_count"] == 2


def test_process_file_endpoint():
    """Test the process file endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('cartaos.utils.pdf_utils.extract_text') as mock_extract:
        mock_exists.return_value = True
        mock_extract.return_value = "This is a long text with more than 500 characters." * 20
        
        response = client.post("/api/process", json={
            "file_path": "/path/to/file.pdf",
            "operation": "triage"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data


def test_triage_endpoint():
    """Test the triage endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    with patch('cartaos.triage.TriageProcessor.process') as mock_triage, \
         patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        mock_triage.return_value = {"destination": "03_Lab", "reason": "Needs OCR"}
        
        response = client.post("/api/triage", json={
            "file_path": "/path/to/file.pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["destination"] == "03_Lab"
        assert data["reason"] == "PDF needs OCR processing"


def test_ocr_endpoint():
    """Test the OCR endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    with patch('cartaos.ocr.OcrProcessor.process') as mock_ocr, \
         patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        mock_ocr.return_value = True
        
        response = client.post("/api/ocr", json={
            "file_path": "/path/to/file.pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["output_path"] == "/path/to/ocr_file.pdf"


def test_summarize_endpoint():
    """Test the summarize endpoint."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    with patch('cartaos.utils.ai_utils.generate_summary') as mock_summarize, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('cartaos.utils.pdf_utils.extract_text') as mock_extract:
        mock_exists.return_value = True
        mock_extract.return_value = "Sample text content"
        mock_summarize.return_value = "This is a summary of the document."
        
        response = client.post("/api/summarize", json={
            "file_path": "/path/to/file.pdf"
        })
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert len(data["summary"]) > 0
        assert data["word_count"] > 0


def test_error_handling():
    """Test error handling in API endpoints."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    # Test invalid file path - should return 500 due to exception handling
    response = client.post("/api/process", json={
        "file_path": "/nonexistent/file.pdf",
        "operation": "triage"
    })
    assert response.status_code == 500
    data = response.json()
    assert "error" in data


def test_cors_configuration():
    """Test CORS configuration for local development."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    # Test preflight request
    response = client.options("/api/files/00_Inbox", headers={
        "Origin": "http://localhost:1420",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_request_validation():
    """Test request validation with Pydantic models."""
    from cartaos.api.server import app
    client = TestClient(app)
    
    # Test missing required fields
    response = client.post("/api/process", json={})
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
