# -*- coding: utf-8 -*-
"""Настройка журналирования: файл log.txt, уровень из config."""

import logging
import os

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}


def setup_logging(log_path_dir, level_name="info"):
    """
    Настраивает логгер: запись в log.txt в указанной директории.
    При перезапуске файл не перезаписывается (режим append).
    """
    level = LEVELS.get(level_name.lower(), logging.INFO)
    log_file = os.path.join(log_path_dir, "log.txt")

    logger = logging.getLogger("agent")
    logger.setLevel(level)
    logger.handlers.clear()

    handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
