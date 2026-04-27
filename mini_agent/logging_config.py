"""Centralized logging configuration for production deployments.

Provides structured JSON logging to stdout (12-factor app compatible)
alongside the existing file-based AgentLogger.
"""

import json
import logging
import sys
from datetime import UTC, datetime


class JSONFormatter(logging.Formatter):
    """JSON structured log formatter for production use."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        return json.dumps(log_entry, default=str, ensure_ascii=False)


def configure_logging(
    level: str = "INFO",
    json_output: bool = True,
    log_file: str | None = None,
):
    """Configure centralized logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, use JSON format to stdout (production).
                     If False, use human-readable format (development).
        log_file: Optional file path for additional file logging.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    root_logger.handlers.clear()

    stdout_handler = logging.StreamHandler(sys.stdout)
    if json_output:
        stdout_handler.setFormatter(JSONFormatter())
    else:
        stdout_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    root_logger.addHandler(stdout_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    for noisy_logger in ["httpx", "httpcore", "urllib3", "asyncio"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
