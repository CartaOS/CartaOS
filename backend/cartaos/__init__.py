"""
CartaOS - A document processing and management system.

This package provides the backend functionality for the CartaOS application,
including document processing, OCR, and AI-powered summarization.
"""

__version__ = "0.1.0"

# Import key components for easier access
from cartaos.app_config import AppConfig, get_config
from cartaos.api.server import app
from cartaos.api.models import (
    ProcessFileRequest, ProcessFileResponse,
    TriageRequest, TriageResponse,
    OCRRequest, OCRResponse,
    SummarizeRequest, SummarizeResponse,
    OperationType
)

__all__ = [
    # Core components
    "AppConfig",
    "get_config",
    "app",
    
    # Models
    "ProcessFileRequest",
    "ProcessFileResponse",
    "TriageRequest",
    "TriageResponse",
    "OCRRequest",
    "OCRResponse",
    "SummarizeRequest",
    "SummarizeResponse",
    "OperationType",
    
    # Version
    "__version__"
]
