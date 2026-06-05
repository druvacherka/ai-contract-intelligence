"""
Centralized logging module using Loguru.

Provides structured, rotating file logs and colorized console output
for the entire Data + OCR pipeline.
"""

import sys
from pathlib import Path

from loguru import logger

from src.utils.config import Config


def _setup_logger() -> None:
    """
    Configure loguru with console + rotating file sinks.
    Called once at module import time.
    """
    # Remove the default stderr handler
    logger.remove()

    # --- Console Sink (colorized) ---
    logger.add(
        sys.stderr,
        level=Config.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # --- File Sink (rotating, structured) ---
    log_file = Path(Config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_file),
        level=Config.LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
        rotation=Config.LOG_ROTATION,
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
    )

    logger.info("Logger initialized | level={} | file={}", Config.LOG_LEVEL, log_file)


# Initialize on import
_setup_logger()

# Re-export logger for convenience
__all__ = ["logger"]
