# -*- coding: utf-8 -*-
"""
Агент сбора информации об ОС Windows (микросервисная архитектура).
Запуск: python main.py <путь_к_файлу_команд>
"""

import argparse
import os
import sys
import threading
import queue

from config import CONFIG_PATH, load_config, get_config_value, SCRIPT_DIR
from logger_setup import setup_logging
from dispatcher import dispatcher_loop, QUEUE_MAX_SIZE
from inventory_service import inventory_worker_loop


def main():
    parser = argparse.ArgumentParser(description="Агент сбора информации об ОС Windows")
    parser.add_argument("command_file", help="Путь к файлу с командами")
    args = parser.parse_args()

    # Проверка наличия конфигурационного файла
    config = load_config()
    if config is None:
        print("Ошибка: конфигурационный файл не найден:", CONFIG_PATH, file=sys.stderr)
        sys.exit(1)

    log_path = get_config_value(config, "logging", "log_path", ".")
    log_path = os.path.abspath(log_path) if not os.path.isabs(log_path) else log_path
    if not os.path.isdir(log_path):
        os.makedirs(log_path, exist_ok=True)

    log_level = get_config_value(config, "logging", "log_level") or get_config_value(config, "logging", "level", "info")
    logger = setup_logging(log_path, log_level)
    logger.info("Запуск агента")

    num_inventory_workers = int(get_config_value(config, "workers", "InventoryWorkers", "1") or "1")
    num_inventory_workers = max(1, min(num_inventory_workers, 16))

    task_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)
    inventory_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)

    # Запуск диспетчера
    dispatcher = threading.Thread(
        target=dispatcher_loop,
        args=(task_queue, inventory_queue),
        kwargs={"logger": logger},
        daemon=False,
    )
    dispatcher.start()

    # Запуск воркеров инвентаризации
    workers = []
    for _ in range(num_inventory_workers):
        t = threading.Thread(
            target=inventory_worker_loop,
            args=(inventory_queue, SCRIPT_DIR),
            kwargs={"logger": logger},
            daemon=False,
        )
        t.start()
        workers.append(t)

    # Чтение файла команд и постановка в очередь
    cmd_path = os.path.abspath(args.command_file)
    if not os.path.isfile(cmd_path):
        logger.error("Файл команд не найден: %s", cmd_path)
        sys.exit(1)

    try:
        with open(cmd_path, "r", encoding="utf-8") as f:
            for line in f:
                cmd = line.strip()
                if not cmd:
                    continue
                try:
                    task_queue.put_nowait(cmd)
                except queue.Full:
                    logger.warning("Очередь задач переполнена, команда отброшена: %s", cmd)
    except OSError as e:
        logger.error("Ошибка чтения файла команд: %s", e)
        sys.exit(1)

    # Сигнал завершения диспетчеру
    try:
        task_queue.put_nowait(None)
    except queue.Full:
        task_queue.put(None)

    task_queue.join()
    # Сигнал завершения каждому воркеру инвентаризации
    for _ in workers:
        try:
            inventory_queue.put_nowait(None)
        except queue.Full:
            inventory_queue.put(None)
    inventory_queue.join()

    dispatcher.join()
    for t in workers:
        t.join()

    logger.info("Агент завершил работу")


if __name__ == "__main__":
    main()
