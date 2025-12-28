"""Logging configuration."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import app_config


def setup_logging() -> None:
    """Configure application logging."""
    log_dir = Path(app_config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, app_config.log_level.upper(), logging.INFO)
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"

    handlers = [
        RotatingFileHandler(log_dir / "backend.log", maxBytes=5_000_000, backupCount=3),
        RotatingFileHandler(log_dir / "errors.log", maxBytes=5_000_000, backupCount=3),
    ]
    handlers[1].setLevel(logging.ERROR)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers + [logging.StreamHandler()],
    )
