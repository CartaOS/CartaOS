from datetime import datetime, timezone
from typing import Optional, Any

from ..logging_config import logger

class AuditLogger:
    @staticmethod
    def log_security_event(
        event_type: str,
        user: Optional[str] = None,
        success: bool = True,
        **kwargs: Any
    ) -> None:
        """Log security-related events with redaction of sensitive data."""
        # Redact sensitive information
        redacted_kwargs = {
            k: "[REDACTED]" if any(s in k.lower() for s in ["key", "token", "secret", "password"]) 
            else v for k, v in kwargs.items()
        }
        
        # Create log record with extra fields
        log_record = {
            "event_type": event_type,
            "user": user,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **redacted_kwargs
        }
        
        # Log the security event
        logger.info("Security Event: %s - %s", 
                   event_type, 
                   "Succeeded" if success else "Failed",
                   extra={"security_event": log_record})
