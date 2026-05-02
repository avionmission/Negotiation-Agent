import logging
import sys
from typing import Any

from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    settings = get_settings()

    logger = logging.getLogger("negotiation_agent")
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()


def get_logger(name: str | None = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"negotiation_agent.{name}")
    return logger
