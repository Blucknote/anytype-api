"""Logging configuration for the application"""

import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """Configure application-wide logging"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    # Create formatters
    formatter = logging.Formatter(settings.log_format)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log file is specified
    if settings.log_file:
        log_file = Path(settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Parse rotation interval
        interval_mapping = {
            "day": "D",
            "hour": "H",
            "minute": "M",
            "second": "S",
        }
        rotation_interval = settings.log_rotation.split()
        if len(rotation_interval) == 2:
            count = int(rotation_interval[0])
            unit = interval_mapping.get(rotation_interval[1].lower(), "D")
        else:
            count, unit = 1, "D"

        # Create timed rotating file handler
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when=unit,
            interval=count,
            backupCount=int(settings.log_retention.split()[0]),
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.suffix = "%Y-%m-%d_%H-%M-%S"
        if settings.log_compression == "zip":
            file_handler.rotator = lambda source, dest: Path(source).rename(
                dest + ".zip"
            )
        logger.addHandler(file_handler)

    # Set logging levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
