"""Logging configuration for the CartaOS API."""

import logging
import sys
from pathlib import Path

# Create a custom formatter
class CustomFormatter(logging.Formatter):
    """Custom log formatter that includes timestamp and module information."""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: grey + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)

# Configure the root logger
def setup_logging(log_level=logging.INFO, log_file=None):
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (default: logging.INFO)
        log_file: Optional path to log file. If None, logs to stderr.
    """
    # Create logger
    logger = logging.getLogger('cartaos')
    logger.setLevel(log_level)
    
    # Prevent adding multiple handlers if already configured
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CustomFormatter())
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Initialize logger with default configuration
logger = setup_logging()
