# AI-агент проверки льготных кредитов

Модуль обработки документов для автоматизации проверки извлечения данных.

## Технологии
- **Python 3.11+**
- **pytest** — тестирование
- **python-dateutil** — парсинг дат
- **difflib** (стандартная библиотека) — нечёткое сопоставление
- **LangChain + OpenAI** — опциональный LLM-путь (fallback на keyword matching без API-ключа)

## Архитектура
```
src/
  constants.py       — константы (пороги, словари, правила)
  extract.py         — извлечение amount/date/inn/contractor/subject
  classify.py        — классификация типа документа
  check_subject.py   — проверка соответствия предмета оплаты
  run.py             — скрипт запуска пайплайна
dataset/             — тестовые документы и предметы оплаты
tests/               — pytest-тесты
```

**Пайплайн:** текст → `extract` (поля) + `classify` (тип) → `check_subject` (целевое назначение) → отчёт.

## Запуск (3 команды)
```bash
pip install -r requirements.txt
pytest -v
python -m src.run
```

## Примеры
```python
from src.extract import extract
from src.classify import classify
from src.check_subject import check_subject

extract("Сумма: 1 250 000,00 руб., дата 01.03.2025, ИНН 7701234567")
# {'amount': 1250000.0, 'date': '2025-03-01', 'inn': '7701234567', ...}

classify("Счёт на оплату №12 от 01.03.2025...")
# ('invoice', 0.82)

check_subject("покупка минеральных удобрений")
# (True, 0.95, "'удобрения' относятся к категории 'агрохимия'")
```