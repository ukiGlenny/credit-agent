"""Тесты для classify()."""
from src.classify import classify


def test_invoice_basic():
    doc_type, confidence = classify("Счёт на оплату №12 от 01.03.2025...")
    assert doc_type == "invoice"
    assert confidence > 0.5


def test_contract(sample_contract):
    doc_type, _ = classify(sample_contract)
    assert doc_type == "contract"


def test_spec():
    doc_type, _ = classify("Спецификация №3 к договору. Номенклатура товара...")
    assert doc_type == "spec"


def test_act():
    doc_type, _ = classify("Акт выполненных работ №18. Работы выполнены в полном объёме...")
    assert doc_type == "act"


def test_unknown_on_empty():
    doc_type, confidence = classify("")
    assert doc_type == "unknown"
    assert confidence == 0.0


def test_unknown_on_ambiguous():
    doc_type, _ = classify("Счёт. Договор. Акт. Спецификация.")
    assert doc_type == "unknown"


def test_confidence_range():
    _, conf = classify("Счёт на оплату №12 от 01.03.2025...")
    assert 0.0 <= conf <= 1.0