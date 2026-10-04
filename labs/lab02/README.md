# Lab 02

## Встановлення
Всі команди виконуються з кореня репозиторію
```
source venv/bin/activate
pip install -r requirements.txt
```

Структура файлів:
```
labs/lab02/
├── README.md
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-314.pyc
│   ├── main.cpython-314.pyc
│   ├── task1.cpython-314.pyc
│   └── task2.cpython-314.pyc
├── _manifest.json
├── data
│   ├── arp_audit.log
│   ├── arp_security_alerts.json
│   └── arp_table.csv
├── main.py
├── task1.py
└── task2.py

3 directories, 13 files
```

# Запуск

## Завдання 1
```bash
python -m labs.lab02.main demo
```

## Завдання 2
```bash
python -m labs.lab02.main analyze \
    --arp-file labs/lab02/data/arp_table.csv \
    --detect-spoofing \ 
    --output-json labs/lab02/data/arp_security_alerts.json \
    --log_file labs/lab02/data/arp_audit.log
```

# Вхідні дані

Файл `labs/lab02/data/arp_table.csv` має колонки IP Address, Mac Address, Interface, Type

Утиліта приймає CSV (з комами) або текстовий файл, де поля розділені пробілами. Рядок-заголовок пропускається автоматично

# Параметри командного рядка

| Параметр | Опис |
|---|---|
| `--arp-file` | Обов'язковий. Шлях до файлу ARP-таблиці. |
| `--output-json` | Шлях до JSON-звіту. Якщо не вказано, звіт не зберігається. |
| `--detect-spoofing` | Прапорець. Вмикає пошук MAC-адрес, пов'язаних із кількома IP. |
| `--log-file` | Шлях до файлу журналу. Якщо не вказано, журнал виводиться лише в консоль. |
 
## Що перевіряє утиліта
 
1. **Валідація** IPv4 (кожен октет 0–255) та MAC (шість пар hex-символів, роздільник `:` або `-`) за допомогою регулярних виразів `re`. MAC-адреси нормалізуються до нижнього регістру з `:`.
2. **Пошук дублікатів:** `collections.defaultdict` групує IP-адреси за MAC. Якщо один MAC пов'язаний з кількома IP, це можлива ARP-spoofing / Man-in-the-Middle атака.
3. **Клас даних** `Conflict` (`@dataclass`) зберігає MAC та список IP-адрес, що йому відповідають.
4. **Журналювання** (`logging`): `INFO` для ходу роботи, `WARNING` для некоректних рядків, `CRITICAL` для виявленого spoofing, `ERROR` для помилок читання й запису.
5. **Звіт у JSON:** кількість коректних і некоректних записів та список конфліктів.
## Поведінка при помилках
 
| Ситуація | Поведінка |
|---|---|
| Файл не знайдено або недоступний | `ERROR` у журналі, код завершення `1`, без traceback. |
| Некоректний IP або MAC у рядку | `WARNING`, рядок пропускається та рахується як `Invalid Syntax`. |
| Не вдалося записати JSON-звіт | `ERROR` у журналі, код завершення `1`. |
| Виявлено spoofing | `CRITICAL` у журналі та блок `[ALERT]` у консолі, код завершення `0`. |
| Не вказано команду або `--arp-file` | Повідомлення `argparse`, код завершення `2`. |
 
MAC у форматі `0011.2233.4455` (крапки, формат Cisco) не відповідає заданому шаблону з шести пар, тому вважається некоректним.
 
## Приклад результату
 
```
[INFO] Parsing ARP table snapshot from labs/lab02/data/arp_table.csv...
[WARNING] Invalid entry skipped: ['999.168.1.30', 'AA:BB:CC:DD:EE:30', 'eth0', 'dynamic']
[WARNING] Invalid entry skipped: ['192.168.1.31', 'GG:11:22:33:44:55', 'eth0', 'dynamic']
[WARNING] Invalid entry skipped: ['192.168.1.32', '0011.2233.4455', 'eth0', 'dynamic']
[INFO] Validated 11 IP/MAC entries.
 
=== Validated Entries Summary ===
Valid IP/MAC Pairs : 8
Invalid Syntax     : 3
 
=== CRITICAL SECURITY ALERTS: ARP-SPOOFING DETECTED ===
[ALERT] MAC de:ad:be:ef:00:01 associated with MULTIPLE IP addresses:
  - 192.168.1.20
  - 192.168.1.21
  - 192.168.1.22
```
 
Підсумок за переглянутими даними: MAC `de:ad:be:ef:00:01` використовується трьома IP-адресами, одна з яких на інтерфейсі `wlan0`. Це ознака ARP-spoofing.
 
## Перевірка коду
 
```bash
ruff check .
ruff format --check .
```
 
