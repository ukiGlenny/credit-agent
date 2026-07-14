"""Тесты для extract()."""
import pytest

from src.extract import extract


def test_amount_space_format():
    assert extract("Сумма: 1 250 000,00 руб.")["amount"] == 1_250_000.0


def test_amount_ruble_sign():
    assert extract("К оплате: 850000.00 ₽")["amount"] == 850_000.0


def test_amount_usd_format():
    assert extract("Сумма 1,250,000.00 RUB")["amount"] == 1_250_000.0


def test_amount_with_kopecks():
    assert extract("320500.75 руб.")["amount"] == 320_500.75


def test_no_amount():
    assert extract("без цифр")["amount"] is None


def test_inn_10_digits():
    assert extract("ИНН 7701234567")["inn"] == "7701234567"


def test_inn_12_digits():
    assert extract("ИНН 503456789012")["inn"] == "503456789012"


def test_date_dot_format():
    assert extract("от 01.03.2025")["date"] == "2025-03-01"


def test_date_text_format():
    assert extract("1 марта 2025 г.")["date"] == "2025-03-01"


def test_date_short_year():
    assert extract("03/01/25")["date"] == "2025-01-03"


def test_contractor():
    r = extract("Поставщик: ООО \"АгроТех\"")
    assert r["contractor"] and "АгроТех" in r["contractor"]


def test_subject():
    r = extract("Предмет: поставка удобрений")
    assert r["subject"] and "удобрений" in r["subject"]


def test_empty_text():
    r = extract("")
    assert all(v is None for v in r.values())


def test_full_document(sample_contract):
    r = extract(sample_contract)
    assert r["amount"] == 1_250_000.0
    assert r["date"] == "2025-03-01"
    assert r["inn"] == "7701234567"
    assert "АгроТех" in r["contractor"]
    assert "удобрений" in r["subject"]