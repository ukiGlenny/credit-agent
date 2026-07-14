"""Извлечение структурированных полей из текста документа."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as dateutil_parser

from src.constants import INN_LENGTHS, DATE_ISO_FORMAT


_AMOUNT_PATTERN = re.compile(
    r"(?P<amount>"
    r"(?:\d{1,3}(?:[ \u00A0]\d{3})+(?:[.,]\d{1,2})?)"
    r"|(?:\d+[.,]\d{1,2})"
    r"|(?:\d+)"
    r")\s*(?:руб\.?|₽|RUB|рублей|RUR)",
    re.IGNORECASE,
)


def _normalize_amount(raw: str) -> float:
    """Переводит строку с суммой в float."""
    s = raw.replace("\u00A0", " ").strip()
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    s = s.replace(" ", "")
    return float(s)


def _extract_amount(text: str) -> Optional[float]:
    m = _AMOUNT_PATTERN.search(text)
    if not m:
        return None
    try:
        return _normalize_amount(m.group("amount"))
    except ValueError:
        return None


_MONTHS_RU = {
    "января": "01", "февраля": "02", "марта": "03", "апреля": "04",
    "мая": "05", "июня": "06", "июля": "07", "августа": "08",
    "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12",
}

_DATE_TEXT_PATTERN = re.compile(
    r"(?P<d>\d{1,2})\s+(?P<m>" + "|".join(_MONTHS_RU) + r")\s+(?P<y>\d{4})\s*г\.?",
    re.IGNORECASE,
)
_DATE_DOT_PATTERN = re.compile(r"\b(\d{2})\.(\d{2})\.(\d{4})\b")
_DATE_SLASH_PATTERN = re.compile(r"\b(\d{2})/(\d{2})/(\d{2,4})\b")


def _extract_date(text: str) -> Optional[str]:
    """Извлекает дату в формате ISO (YYYY-MM-DD)."""
    m = _DATE_TEXT_PATTERN.search(text)
    if m:
        d = m.group("d").zfill(2)
        mon = _MONTHS_RU[m.group("m").lower()]
        y = m.group("y")
        return datetime(int(y), int(mon), int(d)).date().isoformat()

    m = _DATE_DOT_PATTERN.search(text)
    if m:
        d, mo, y = m.groups()
        try:
            return datetime(int(y), int(mo), int(d)).date().isoformat()
        except ValueError:
            pass

    m = _DATE_SLASH_PATTERN.search(text)
    if m:
        d, mo, y = m.groups()
        y = int(y) + 2000 if len(y) == 2 else int(y)
        try:
            return datetime(y, int(mo), int(d)).date().isoformat()
        except ValueError:
            pass

    try:
        return dateutil_parser.parse(text, dayfirst=True, fuzzy=True).date().isoformat()
    except (ValueError, OverflowError):
        return None


_INN_PATTERN = re.compile(
    r"\b(?:ИНН[:\s#№]*)?(?P<inn>\d{" + str(INN_LENGTHS[0]) + r"}|\d{" + str(INN_LENGTHS[1]) + r"})\b"
)


def _extract_inn(text: str) -> Optional[str]:
    m = _INN_PATTERN.search(text)
    return m.group("inn") if m else None


_CONTRACTOR_PATTERN = re.compile(
    r"(?:Контрагент|Поставщик|Покупатель|Исполнитель|Заказчик|Продавец|Наименование)"
    r"[:\s#№]+(?P<val>[^\n,;]{3,80})",
    re.IGNORECASE,
)


def _extract_contractor(text: str) -> Optional[str]:
    m = _CONTRACTOR_PATTERN.search(text)
    return m.group("val").strip() if m else None


_SUBJECT_PATTERN = re.compile(
    r"(?:Предмет(?:\s+оплаты|\s+договора)?|Назначение платежа|За|Оплата\s+за)"
    r"[:\s#№\-]+(?P<val>[^\n]{3,200})",
    re.IGNORECASE,
)


def _extract_subject(text: str) -> Optional[str]:
    m = _SUBJECT_PATTERN.search(text)
    return m.group("val").strip() if m else None


def extract(text: str) -> dict:
    """Извлекает amount, date, inn, contractor, subject.

    Args:
        text: Строка с текстом из документа.

    Returns:
        Словарь с полями amount, date, inn, contractor, subject.
        Поля, которые не удалось найти — None.
    """
    if not isinstance(text, str):
        return {
            "amount": None, "date": None, "inn": None,
            "contractor": None, "subject": None,
        }

    return {
        "amount": _extract_amount(text),
        "date": _extract_date(text),
        "inn": _extract_inn(text),
        "contractor": _extract_contractor(text),
        "subject": _extract_subject(text),
    }