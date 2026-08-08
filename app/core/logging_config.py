"""
Centralized logging configuration for the FastAPI backend.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_PATH = os.getenv("LOG_FILE", os.path.join("logs", "app.log"))

handlers: list[logging.Handler] = [logging.StreamHandler()]

if LOG_FILE_PATH and LOG_FILE_PATH.upper() != "NUL":
    try:
        log_dir = os.path.dirname(LOG_FILE_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        handlers.insert(
            0,
            RotatingFileHandler(LOG_FILE_PATH, maxBytes=5_000_000, backupCount=5),
        )
    except OSError:
        # Fall back to console logging when the filesystem is unavailable.
        pass

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=handlers,
)

logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
