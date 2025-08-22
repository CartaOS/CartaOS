"""
External call management with timeout, retry, and circuit breaker functionality.
Provides robust handling of external API calls with configurable resilience patterns.
"""
import asyncio
import logging
import os
import random
from typing import Callable, Optional, Any, Awaitable
from dataclasses import dataclass
from enum import Enum

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class TimeoutError(Exception):
    """Custom timeout error for external calls."""
    pass


class CircuitBreakerError(Exception):
    """Error raised when circuit breaker is open."""
    pass


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3


class CircuitBreaker:
    """Circuit breaker implementation for external calls."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_calls = 0
        
    def can_execute(self) -> bool:
        """Check if call can be executed based on circuit breaker state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if asyncio.get_event_loop().time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        else:  # HALF_OPEN
            return self.half_open_calls < self.config.half_open_max_calls
    
    def record_success(self):
        """Record successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
    
    def record_failure(self):
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
        elif self.failure_count >= self.config.threshold:
            self.state = CircuitBreakerState.OPEN


class ExternalCallManager:
    """Manager for external calls with timeout, retry, and circuit breaker."""
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_recovery_timeout: float = 60.0,
        progress_callback: Optional[Callable[[int, int, float], None]] = None
    ):
        """Initialize ExternalCallManager with configuration."""
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        if max_retries <= 0:
            raise ValueError("Max retries must be positive")
        if base_delay <= 0:
            raise ValueError("Base delay must be positive")
            
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.progress_callback = progress_callback
        
        circuit_config = CircuitBreakerConfig(
            threshold=circuit_breaker_threshold,
            recovery_timeout=circuit_breaker_recovery_timeout
        )
        self.circuit_breaker = CircuitBreaker(circuit_config)
    
    @classmethod
    def from_env(cls) -> 'ExternalCallManager':
        """Create ExternalCallManager from environment variables."""
        return cls(
            timeout=float(os.getenv('CARTAOS_EXTERNAL_CALL_TIMEOUT', '30.0')),
            max_retries=int(os.getenv('CARTAOS_MAX_RETRIES', '3')),
            base_delay=float(os.getenv('CARTAOS_BASE_DELAY', '1.0')),
            max_delay=float(os.getenv('CARTAOS_MAX_DELAY', '60.0')),
            circuit_breaker_threshold=int(os.getenv('CARTAOS_CIRCUIT_BREAKER_THRESHOLD', '5')),
            circuit_breaker_recovery_timeout=float(os.getenv('CARTAOS_CIRCUIT_BREAKER_RECOVERY', '60.0'))
        )
    
    async def call_with_retry(
        self,
        func: Callable[[], Awaitable[Any]],
        timeout_override: Optional[float] = None
    ) -> Any:
        """Execute function with timeout, retry, and circuit breaker protection."""
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerError("Circuit breaker is open")
        
        timeout = timeout_override or self.timeout
        attempt = 0
        last_exception = None
        
        while attempt <= self.max_retries:
            try:
                # Execute with timeout
                result = await asyncio.wait_for(func(), timeout=timeout)
                self.circuit_breaker.record_success()
                return result
                
            except asyncio.TimeoutError as e:
                last_exception = TimeoutError(f"Call timed out after {timeout} seconds")
                if attempt == self.max_retries:
                    break
                
            except (httpx.RequestError, Exception) as e:
                last_exception = e
                if attempt == self.max_retries:
                    break
            
            # Calculate delay with exponential backoff and jitter
            delay = min(
                self.base_delay * (2 ** attempt),
                self.max_delay
            )
            # Add jitter (±25% of delay)
            jitter = delay * 0.25 * (2 * random.random() - 1)
            actual_delay = max(0, delay + jitter)
            
            # Call progress callback if provided
            if self.progress_callback:
                self.progress_callback(attempt + 1, self.max_retries + 1, actual_delay)
            
            logger.warning(
                f"External call failed (attempt {attempt + 1}/{self.max_retries + 1}), "
                f"retrying in {actual_delay:.2f}s"
            )
            
            await asyncio.sleep(actual_delay)
            attempt += 1
        
        # All retries exhausted - record failure for circuit breaker
        self.circuit_breaker.record_failure()
        
        if isinstance(last_exception, TimeoutError):
            raise last_exception
        else:
            raise RetryError(f"Max retries ({self.max_retries}) exceeded") from last_exception


# Global instance for convenience
_default_manager: Optional[ExternalCallManager] = None


def get_default_manager() -> ExternalCallManager:
    """Get or create the default ExternalCallManager instance."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ExternalCallManager.from_env()
    return _default_manager


async def call_with_retries(
    func: Callable[[], Awaitable[Any]],
    timeout: Optional[float] = None,
    max_retries: Optional[int] = None
) -> Any:
    """Convenience function for calling external functions with retries."""
    manager = get_default_manager()
    if max_retries is not None:
        # Create temporary manager with custom retry count
        manager = ExternalCallManager(
            timeout=manager.timeout,
            max_retries=max_retries,
            base_delay=manager.base_delay,
            max_delay=manager.max_delay
        )
    
    return await manager.call_with_retry(func, timeout_override=timeout)
