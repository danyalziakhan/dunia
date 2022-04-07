from __future__ import annotations

import os
import sys

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger


if TYPE_CHECKING:
    from typing import Final


def get_log_file(logs_dir: str) -> str:
    return os.path.join(logs_dir, f"{datetime.now().strftime('%Y%m%d')}.log")


logger.remove()

LOGGER_FORMAT_STR: Final[
    str
] = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line} [Process ID {extra[id]}]</cyan> - <level>{message}</level>"

logger.add(
    sys.stderr,
    format=LOGGER_FORMAT_STR,
    level="INFO",
    colorize=True,
    enqueue=True,
)

PROCESS_ID: Final[int] = os.getpid()

logger = logger.bind(id=PROCESS_ID).opt(colors=True)

logger.remove()
logger.add(sys.stderr, level="DEBUG", colorize=True, enqueue=True)

logger.add(
    get_log_file(os.path.join(Path().absolute(), "logs")),
    enqueue=True,
    encoding="utf-8-sig",
)

info = logger.info
debug = logger.debug
warning = logger.warning
error = logger.error
success = logger.success
