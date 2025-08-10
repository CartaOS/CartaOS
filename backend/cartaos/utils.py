import logging
from typing import List

class WarningCaptureHandler(logging.Handler):
    """
    A custom logging handler that captures log records into a list
    instead of emitting them to a stream.
    """
    def __init__(self, messages_list: List[str]):
        """
        Initializes the handler.

        Args:
            messages_list (List[str]): The list to which log messages will be appended.
        """
        super().__init__()
        self.messages_list = messages_list

    def emit(self, record: logging.LogRecord):
        """Captures the formatted log message in the list."""
        self.messages_list.append(self.format(record))