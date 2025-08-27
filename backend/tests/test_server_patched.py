"""
Patched version of the server module for testing.
"""

import traceback
from pathlib import Path
from unittest.mock import MagicMock
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from cartaos.api.server import app as original_app, ProcessFileRequest, ProcessFileResponse, _process_with_processor, _process_summarization
from cartaos.security.audit_logger import AuditLogger
from cartaos.api.models import OperationType

# Mock CartaOSProcessor class
class MockCartaOSProcessor:
    def __init__(self, *args, **kwargs):
        self.process = MagicMock(return_value=True)

# Patch the CartaOSProcessor in the server module
import sys
import importlib
sys.modules['cartaos.processor'] = MagicMock()
sys.modules['cartaos.processor'].CartaOSProcessor = MockCartaOSProcessor

# Reload the server module to apply the patch
import cartaos.api.server as server_module
importlib.reload(server_module)

# Create a new FastAPI instance for testing
app = FastAPI()

# Copy all routes except the process_file endpoint
for route in original_app.routes:
    if not (isinstance(route, APIRoute) and route.name == 'process_file'):
        app.router.routes.append(route)

# Add the process_file route with our custom implementation

# Re-add the route without the decorator
@app.post("/api/process", response_model=ProcessFileResponse)
async def process_file(
    request: ProcessFileRequest,
    file_path: str = None  # Keep for compatibility
):
    """Process a file with the specified operation (patched version)."""
    # Log the processing start
    AuditLogger.log_security_event(
        event_type="file_processing_started",
        file_path=str(request.file_path),
        operation=request.operation
    )
    
    try:
        file_path = Path(request.file_path)
        if not file_path.exists():
            error_msg = f"File not found: {request.file_path}"
            AuditLogger.log_security_event(
                event_type="file_not_found",
                file_path=str(file_path),
                success=False,
                error=error_msg
            )
            raise HTTPException(status_code=404, detail=error_msg)

        # Process based on operation type
        if request.operation == OperationType.TRIAGE:
            result = await _process_with_processor(file_path, OperationType.TRIAGE)
        elif request.operation == OperationType.OCR:
            result = await _process_with_processor(file_path, OperationType.OCR)
        elif request.operation == OperationType.SUMMARIZE:
            result = await _process_summarization(file_path, request)
        else:
            error_msg = f"Unsupported operation: {request.operation}"
            AuditLogger.log_security_event(
                event_type="processing_failed",
                file_path=str(file_path),
                operation=request.operation,
                success=False,
                error=error_msg
            )
            raise HTTPException(status_code=400, detail=error_msg)

        # Log successful completion
        AuditLogger.log_security_event(
            event_type="processing_completed",
            file_path=str(file_path),
            operation=request.operation,
            success=True,
            result=str(result.get("output_path", ""))
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing file: {str(e)}"
        AuditLogger.log_security_event(
            event_type="processing_error",
            file_path=str(file_path) if 'file_path' in locals() else 'unknown',
            operation=request.operation if 'request' in locals() else 'unknown',
            success=False,
            error=error_msg,
            stack_trace=traceback.format_exc()
        )
        raise HTTPException(status_code=500, detail=error_msg)
