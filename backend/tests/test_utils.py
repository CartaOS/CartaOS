# -*- coding: utf-8 -*-
# backend/tests/test_utils.py

import logging
import pytest

from cartaos.utils.utils import WarningCaptureHandler


def test_warning_capture_handler():
    """Test that the WarningCaptureHandler correctly captures log messages."""
    # 1. Setup
    log_messages = []
    handler = WarningCaptureHandler(log_messages)
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.WARNING)
    logger.addHandler(handler)

    # Ensure the logger doesn't propagate to the root logger, which might print to console
    logger.propagate = False

    # 2. Action
    test_message = "This is a test warning."
    logger.warning(test_message)

    # 3. Assertion
    assert len(log_messages) == 1
    assert log_messages[0] == test_message

    # Test with another message
    another_message = "Another warning."
    logger.warning(another_message)
    assert len(log_messages) == 2
    assert log_messages[1] == another_message

    # Test that non-warning messages are ignored
    logger.info("This should not be captured.")
    assert len(log_messages) == 2

    # Clean up the handler to avoid side effects in other tests
    logger.removeHandler(handler)
