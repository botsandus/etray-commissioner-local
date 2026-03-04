"""Logging utility for etray-commissioner."""

import logging
import os
from logging.handlers import RotatingFileHandler

from appdirs import AppDirs

MODULE_NAME = "etray-commissioner-local"
_data_dir = AppDirs(MODULE_NAME).user_data_dir
LOG_FILE = os.path.join(_data_dir, "etray-commissioner.log")
AUDIT_LOG_FILE = os.path.join(_data_dir, "audit.log")


def get_logger() -> logging.Logger:
    """Returns the application logger, initializing it if needed."""
    logger = logging.getLogger("etray-commissioner")
    if logger.handlers:
        return logger

    os.makedirs(_data_dir, exist_ok=True)

    logger.setLevel(logging.DEBUG)

    rotating_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    rotating_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
    )
    logger.addHandler(rotating_handler)

    audit_handler = logging.FileHandler(AUDIT_LOG_FILE, mode="a", encoding="utf-8")
    audit_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(module)s: %(message)s")
    )
    logger.addHandler(audit_handler)

    return logger


def get_audit_logger() -> logging.Logger:
    """Returns the audit logger for user action tracking."""
    audit_logger = logging.getLogger("etray-commissioner.audit")
    if audit_logger.handlers:
        return audit_logger

    os.makedirs(_data_dir, exist_ok=True)

    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False

    handler = logging.FileHandler(AUDIT_LOG_FILE, mode="a", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [AUDIT] %(message)s")
    )
    audit_logger.addHandler(handler)

    return audit_logger


def log_path() -> str:
    """Returns the path to the log file."""
    return LOG_FILE


def audit_log_path() -> str:
    """Returns the path to the audit log file."""
    return AUDIT_LOG_FILE
