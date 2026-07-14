import pytest

from src.check_subject import check_subject


def test_pass_fertilizer():
    ok, conf, reason = check_subject("покупка минеральных удобрений")
    assert ok is True
    assert conf > 0.8
    assert "агрохимия" in reason.lower() or "удобрен" in reason.lower()


def test_pass_fuel():
    ok, _, _ = check_subject("поставка дизельного топлива")
    assert ok is True


def test_pass_seeds():
    ok, _, _ = check_subject("семена пшеницы яровой")
    assert ok is True


def test_fail_office():
    ok, conf, reason = check_subject("аренда офиса в Москве")
    assert ok is False
    assert conf > 0.8


def test_fail_corporate_event():
    ok, _, _ = check_subject("оплата корпоратива")
    assert ok is False


def test_empty_subject():
    ok, conf, _ = check_subject("")
    assert ok is False
    assert conf == 0.0


@pytest.mark.parametrize("subject,expected", [
    ("покупка трактора МТЗ-82", True),
    ("ветеринарные препараты для КРС", True),
    ("услуги клининга", False),
    ("ГСМ для сельхозтехники", True),
    ("покупка легкового автомобиля", False),
])
def test_parametrized(subject, expected):
    ok, _, _ = check_subject(subject)
    assert ok is expected