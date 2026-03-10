Реализовано

Конфиг: при запуске проверяется наличие config.ini в каталоге скрипта; при отсутствии — выход с ошибкой.

CLI: аргумент — путь к файлу с командами; обрабатывается только команда inventory, остальные игнорируются.

Очереди: queue.Queue(maxsize=1000) для задач и инвентаризации — защита от переполнения; при переполнении задача отбрасывается с записью в лог.

Диспетчер: валидация команды, передача только разрешённых в очередь инвентаризации.

Инвентаризация: чтение HKEY_LOCAL_MACHINE\...\CurrentVersion, формирование JSON по заданной структуре, запись в payload.json в директории 
скрипта.

Логирование: log.txt по пути из конфига, режим append, уровни debug/info/warning/error из конфига.

Запуск проверен: агент успешно отработал с commands.txt, созданы log.txt и payload.json с данными ОС.

Запуск:

python main.py commands.txt
Проверка в venv:


python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py commands.txt
