# -*- coding: utf-8 -*-
"""Сервис диспетчеризации: управление очередью, валидация команд, передача в сервисы."""

import queue
import threading

ALLOWED_COMMANDS = frozenset({"inventory"})
QUEUE_MAX_SIZE = 1000


def dispatcher_loop(task_queue, inventory_queue, logger=None):
    """
    Цикл диспетчера: берёт задачу из task_queue, проверяет по списку разрешённых
    команд и кладёт в соответствующую очередь сервиса (inventory). Остальные команды игнорируются.
    Остановка: получить sentinel None из task_queue.
    """
    while True:
        try:
            cmd = task_queue.get()
            if cmd is None:
                task_queue.task_done()
                break
            cmd = (cmd or "").strip().lower()
            if cmd in ALLOWED_COMMANDS:
                if cmd == "inventory":
                    try:
                        inventory_queue.put_nowait("inventory")
                    except queue.Full:
                        if logger:
                            logger.warning("Очередь инвентаризации переполнена, задача отброшена")
            else:
                if logger:
                    logger.debug("Команда игнорируется: %s", cmd)
            task_queue.task_done()
        except Exception as e:
            if logger:
                logger.error("Ошибка диспетчера: %s", e)
            try:
                task_queue.task_done()
            except ValueError:
                pass
