"""
Pydantic models for API request/response validation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """Available operations for file processing."""

    TRIAGE = "triage"
    OCR = "ocr"
    SUMMARIZE = "summarize"
    LAB = "lab"


class ProcessFileRequest(BaseModel):
    """Request model for file processing."""

    file_path: str = Field(..., description="Path to the file to process")
    operation: OperationType = Field(..., description="Type of operation to perform")


class ProcessFileResponse(BaseModel):
    """Response model for file processing."""

    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Human-readable message")
    output_path: Optional[str] = Field(
        None, description="Path to output file if applicable"
    )
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TriageRequest(BaseModel):
    """Request model for triage operation."""

    file_path: str = Field(..., description="Path to the file to triage")


class TriageResponse(BaseModel):
    """Response model for triage operation."""

    destination: str = Field(..., description="Destination folder for the file")
    reason: str = Field(..., description="Reason for the triage decision")
    confidence: Optional[float] = Field(
        None, description="Confidence score for the decision"
    )


class OCRRequest(BaseModel):
    """Request model for OCR operation."""

    file_path: str = Field(..., description="Path to the file to OCR")
    language: Optional[str] = Field("eng", description="OCR language code")


class OCRResponse(BaseModel):
    """Response model for OCR operation."""

    status: str = Field(..., description="Status of the OCR operation")
    output_path: str = Field(..., description="Path to the OCR output file")
    pages_processed: Optional[int] = Field(
        None, description="Number of pages processed"
    )


class SummarizeRequest(BaseModel):
    """Request model for summarization."""

    file_path: str = Field(..., description="Path to the file to summarize")
    max_length: Optional[int] = Field(None, description="Maximum length of summary")


class SummarizeResponse(BaseModel):
    """Response model for summarization."""

    summary: str = Field(..., description="Generated summary")
    word_count: Optional[int] = Field(None, description="Word count of summary")
    source_pages: Optional[int] = Field(None, description="Number of source pages")


class ListFilesResponse(BaseModel):
    """Response model for listing files."""

    files: List[str] = Field(..., description="List of file names")
    total_count: int = Field(..., description="Total number of files")


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="Health status")
    version: Optional[str] = Field(None, description="API version")
    timestamp: Optional[str] = Field(None, description="Current timestamp")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
