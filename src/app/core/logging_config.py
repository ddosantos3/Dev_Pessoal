import logging
import sys
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: Any = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.log(level, record.getMessage())


def configurar_logging() -> None:
    logger.remove()
    logger.add(sys.stdout, serialize=True, enqueue=True, backtrace=False, diagnose=False)
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
