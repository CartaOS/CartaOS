import logging
import unittest
from cartaos.utils import WarningCaptureHandler

class TestWarningCaptureHandler(unittest.TestCase):
    """Unit tests for the WarningCaptureHandler class."""

    def test_emit(self):
        """
        Test that the emit method correctly appends the formatted log message
        to the provided messages list.
        """
        # Initialize an empty list to capture log messages
        messages_list = []

        # Create an instance of the WarningCaptureHandler with the messages list
        handler = WarningCaptureHandler(messages_list)

        # Create a log record with a test message
        record = logging.LogRecord(
            name='test', level=logging.WARNING, pathname="", lineno=0,
            msg='Test message', args=(), exc_info=None
        )

        # Emit the log record using the handler
        handler.emit(record)

        # Assert that the formatted log message is correctly appended to the list
        self.assertEqual([logging.Formatter().format(record)], messages_list)

