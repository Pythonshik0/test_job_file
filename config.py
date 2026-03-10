# -*- coding: utf-8 -*-
"""Загрузка конфигурации из config.ini."""

import os
from configparser import ConfigParser

# Директория скрипта (для поиска config.ini рядом с исполняемым файлом)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILENAME = "config.ini"
CONFIG_PATH = os.path.join(SCRIPT_DIR, CONFIG_FILENAME)


def load_config():
    """Читает config.ini из директории скрипта. Возвращает None, если файл отсутствует."""
    if not os.path.isfile(CONFIG_PATH):
        return None
    parser = ConfigParser()
    parser.read(CONFIG_PATH, encoding="utf-8")
    return parser


def get_config_value(parser, section, key, default=None):
    """Безопасное получение значения из конфига."""
    if parser is None:
        return default
    try:
        return parser.get(section, key, fallback=default)
    except Exception:
        return default
