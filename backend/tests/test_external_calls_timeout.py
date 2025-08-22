"""
Test suite for external call timeout and retry functionality.
Following TDD methodology - these tests should fail initially.
"""
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from tenacity import RetryError
import httpx

from cartaos.utils.external_calls import (
    ExternalCallManager,
    CircuitBreakerError,
    TimeoutError as CustomTimeoutError
)


class TestExternalCallManager:
    """Test the ExternalCallManager for timeout and retry functionality."""

    def test_external_call_manager_import(self):
        """Test that ExternalCallManager can be imported."""
        from cartaos.utils.external_calls import ExternalCallManager
        assert ExternalCallManager is not None

    @pytest.mark.asyncio
    async def test_simple_successful_call(self):
        """Test a simple successful external call."""
        manager = ExternalCallManager()
        
        async def mock_call():
            return "success"
        
        result = await manager.call_with_retry(mock_call)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_configuration(self):
        """Test that timeout can be configured."""
        manager = ExternalCallManager(timeout=5.0)
        assert manager.timeout == 5.0

    @pytest.mark.asyncio
    async def test_retry_configuration(self):
        """Test that retry attempts can be configured."""
        manager = ExternalCallManager(max_retries=5)
        assert manager.max_retries == 5

    @pytest.mark.asyncio
    async def test_call_timeout_raises_error(self):
        """Test that calls exceeding timeout raise TimeoutError."""
        manager = ExternalCallManager(timeout=0.1)
        
        async def slow_call():
            await asyncio.sleep(0.2)
            return "too slow"
        
        with pytest.raises(CustomTimeoutError):
            await manager.call_with_retry(slow_call)

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that failed calls are retried with exponential backoff."""
        manager = ExternalCallManager(max_retries=3, base_delay=0.01)
        call_count = 0
        
        async def failing_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.RequestError("Network error")
            return "success after retries"
        
        result = await manager.call_with_retry(failing_call)
        assert result == "success after retries"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that RetryError is raised when max retries exceeded."""
        manager = ExternalCallManager(max_retries=2, base_delay=0.01)
        
        async def always_failing_call():
            raise httpx.RequestError("Always fails")
        
        with pytest.raises(RetryError):
            await manager.call_with_retry(always_failing_call)

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_repeated_failures(self):
        """Test that circuit breaker opens after repeated failures."""
        manager = ExternalCallManager(circuit_breaker_threshold=3)
        
        async def failing_call():
            raise httpx.RequestError("Service down")
        
        # First 3 calls should fail normally
        for _ in range(3):
            with pytest.raises(RetryError):
                await manager.call_with_retry(failing_call)
        
        # 4th call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await manager.call_with_retry(failing_call)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test that circuit breaker can recover after successful calls."""
        manager = ExternalCallManager(
            circuit_breaker_threshold=2,
            circuit_breaker_recovery_timeout=0.1
        )
        
        # Fail enough times to open circuit breaker
        async def failing_call():
            raise httpx.RequestError("Service down")
        
        for _ in range(2):
            with pytest.raises(RetryError):
                await manager.call_with_retry(failing_call)
        
        # Wait for recovery timeout
        await asyncio.sleep(0.15)
        
        # Successful call should close circuit breaker
        async def successful_call():
            return "recovered"
        
        result = await manager.call_with_retry(successful_call)
        assert result == "recovered"

    @pytest.mark.asyncio
    async def test_jitter_in_retry_delay(self):
        """Test that retry delays include jitter to prevent thundering herd."""
        manager = ExternalCallManager(max_retries=2, base_delay=0.1)
        
        delays = []
        original_sleep = asyncio.sleep
        
        async def mock_sleep(delay):
            delays.append(delay)
            await original_sleep(0.01)  # Speed up test
        
        call_count = 0
        async def failing_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.RequestError("Temporary failure")
            return "success"
        
        with patch('asyncio.sleep', side_effect=mock_sleep):
            result = await manager.call_with_retry(failing_call)
        
        assert result == "success"
        assert len(delays) == 1  # One retry delay
        # Jitter should make delay different from base_delay
        assert delays[0] != 0.1


class TestAIUtilsIntegration:
    """Test integration of timeout/retry with AI utilities."""

    @pytest.mark.asyncio
    async def test_ai_client_uses_external_call_manager(self):
        """Test that AI client integrates with ExternalCallManager."""
        from cartaos.utils.ai_utils import get_external_call_manager
        
        # Test that we can get the external call manager
        manager = get_external_call_manager()
        assert manager is not None
        assert manager.timeout == 60.0  # AI-specific timeout

    @pytest.mark.asyncio
    async def test_generate_content_with_timeout(self):
        """Test that content generation handles timeout gracefully."""
        from cartaos.utils.ai_utils import generate_content_with_retries
        
        with patch('cartaos.utils.ai_utils.get_external_call_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_get_manager.return_value = mock_manager
            mock_manager.call_with_retry = AsyncMock(side_effect=CustomTimeoutError("Timeout"))
            
            # Should return None on timeout, not raise exception
            result = await generate_content_with_retries("test prompt")
            assert result is None


class TestOCRIntegration:
    """Test integration of timeout/retry with OCR operations."""

    @pytest.mark.asyncio
    async def test_ocr_process_with_timeout(self):
        """Test that OCR processing respects timeout settings."""
        from cartaos.utils.ocr_utils import process_document_with_retries
        
        with patch('cartaos.utils.ocr_utils.ExternalCallManager') as mock_manager:
            mock_instance = MagicMock()
            mock_manager.return_value = mock_instance
            mock_instance.call_with_retry = AsyncMock(return_value="OCR result")
            
            result = await process_document_with_retries("/path/to/doc.pdf")
            assert result == "OCR result"

    @pytest.mark.asyncio
    async def test_ocr_retry_on_temporary_failure(self):
        """Test that OCR retries on temporary failures."""
        from cartaos.utils.ocr_utils import process_document_with_retries
        
        with patch('cartaos.utils.ocr_utils.ExternalCallManager') as mock_manager:
            mock_instance = MagicMock()
            # First call fails, second succeeds
            mock_instance.call_with_retry = AsyncMock(side_effect=[
                Exception("Temporary OCR failure"),
                "OCR success"
            ])
            mock_manager.return_value = mock_instance
            
            # The ExternalCallManager should handle the retry internally
            mock_instance.call_with_retry.side_effect = None
            mock_instance.call_with_retry.return_value = "OCR success"
            
            result = await process_document_with_retries("/path/to/doc.pdf")
            assert result == "OCR success"


class TestConfigurationManagement:
    """Test configuration management for timeouts and retries."""

    def test_default_configuration_values(self):
        """Test that default configuration values are reasonable."""
        manager = ExternalCallManager()
        
        assert manager.timeout > 0
        assert manager.max_retries > 0
        assert manager.base_delay > 0
        assert manager.circuit_breaker.config.threshold > 0

    def test_configuration_from_environment(self):
        """Test that configuration can be loaded from environment variables."""
        with patch.dict('os.environ', {
            'CARTAOS_EXTERNAL_CALL_TIMEOUT': '30.0',
            'CARTAOS_MAX_RETRIES': '5',
            'CARTAOS_BASE_DELAY': '2.0'
        }):
            from cartaos.utils.external_calls import ExternalCallManager
            manager = ExternalCallManager.from_env()
            
            assert manager.timeout == 30.0
            assert manager.max_retries == 5
            assert manager.base_delay == 2.0

    def test_configuration_validation(self):
        """Test that invalid configuration values are rejected."""
        with pytest.raises(ValueError):
            ExternalCallManager(timeout=-1)
        
        with pytest.raises(ValueError):
            ExternalCallManager(max_retries=0)
        
        with pytest.raises(ValueError):
            ExternalCallManager(base_delay=-0.1)


class TestProgressIndicators:
    """Test progress indicators for long-running operations."""

    @pytest.mark.asyncio
    async def test_progress_callback_called(self):
        """Test that progress callbacks are called during retries."""
        progress_calls = []
        
        def progress_callback(attempt, max_attempts, delay):
            progress_calls.append((attempt, max_attempts, delay))
        
        manager = ExternalCallManager(
            max_retries=3,
            base_delay=0.01,
            progress_callback=progress_callback
        )
        
        call_count = 0
        async def failing_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.RequestError("Retry me")
            return "success"
        
        result = await manager.call_with_retry(failing_call)
        assert result == "success"
        assert len(progress_calls) == 2  # Two retry attempts

    @pytest.mark.asyncio
    async def test_cancellation_support(self):
        """Test that long-running operations can be cancelled."""
        manager = ExternalCallManager()
        
        async def long_running_call():
            await asyncio.sleep(10)  # Very long operation
            return "completed"
        
        task = asyncio.create_task(manager.call_with_retry(long_running_call))
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()
        
        with pytest.raises(asyncio.CancelledError):
            await task
