# -*- coding: utf-8 -*-
"""Сервис инвентаризации: сбор данных об ОС из реестра Windows, запись в payload.json."""

import json
import os
import sys

# Реестр доступен только на Windows
if sys.platform == "win32":
    import winreg

REG_PATH = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
KEYS = ("ProductName", "DisplayVersion", "CurrentBuild", "UBR", "InstallDate", "EditionID")


def _read_registry():
    """Читает параметры ОС из HKEY_LOCAL_MACHINE\\...\\CurrentVersion."""
    result = {}
    if sys.platform != "win32":
        return result
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_PATH,
            0,
            winreg.KEY_READ,
        )
        for name in KEYS:
            try:
                value, _ = winreg.QueryValueEx(key, name)
                result[name] = str(value) if value is not None else ""
            except FileNotFoundError:
                result[name] = ""
        winreg.CloseKey(key)
    except OSError:
        raise
    return result


def run_inventory(script_dir, logger=None):
    """
    Выполняет сбор информации об ОС и записывает результат в payload.json
    в директории script_dir. Возвращает True при успехе.
    """
    try:
        raw = _read_registry()
    except OSError as e:
        if logger:
            logger.error("Ошибка чтения реестра: %s", e)
        raise

    # Формируем структуру по заданному формату (без InstallDate в JSON по примеру)
    payload = {
        "os": {
            "ProductName": raw.get("ProductName", ""),
            "CurrentBuild": raw.get("CurrentBuild", ""),
            "DisplayVersion": raw.get("DisplayVersion", ""),
            "EditionID": raw.get("EditionID", ""),
        }
    }

    payload_path = os.path.join(script_dir, "payload.json")
    with open(payload_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    if logger:
        logger.info("Инвентаризация выполнена, записано в %s", payload_path)
    return True


def inventory_worker_loop(inventory_queue, script_dir, logger=None):
    """
    Цикл воркера: берёт задачи из inventory_queue и выполняет run_inventory.
    Остановка: получить sentinel None.
    """
    while True:
        try:
            task = inventory_queue.get()
            if task is None:
                inventory_queue.task_done()
                break
            try:
                run_inventory(script_dir, logger=logger)
            except Exception as e:
                if logger:
                    logger.error("Ошибка инвентаризации: %s", e)
            finally:
                inventory_queue.task_done()
        except Exception as e:
            if logger:
                logger.error("Ошибка воркера инвентаризации: %s", e)
