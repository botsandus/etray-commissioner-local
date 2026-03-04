"""Logging utility for etray-commissioner."""

import logging
import os
from logging.handlers import RotatingFileHandler

from appdirs import AppDirs

MODULE_NAME = "etray-commissioner-local"
LOG_FILE = os.path.join(AppDirs(MODULE_NAME).user_data_dir, "etray-commissioner.log")


def get_logger() -> logging.Logger:
    """Returns the application logger, initializing it if needed."""
    logger = logging.getLogger("etray-commissioner")
    if logger.handlers:
        return logger

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
    )
    logger.addHandler(handler)
    return logger


def log_path() -> str:
    """Returns the path to the log file."""
    return LOG_FILE
