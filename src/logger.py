"""Centralized logging configuration for TranscribeMonkey."""

import logging
import os

LOG_FILE = 'app.log'

# Enable verbose logging when the DEBUG environment variable is set to "1".
LOG_LEVEL = logging.DEBUG if os.getenv("DEBUG") == "1" else logging.INFO

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger."""
    return logging.getLogger(name)
