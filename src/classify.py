"""Классификация документа по содержимому."""
from __future__ import annotations

from typing import Tuple

from src.constants import AMBIGUITY_THRESHOLD, CLASSIFY_RULES


def _score(text: str) -> dict[str, float]:
    """Подсчитывает взвешенный скор для каждого класса."""
    t = text.lower()
    scores: dict[str, float] = {k: 0.0 for k in CLASSIFY_RULES}
    for cls, patterns in CLASSIFY_RULES.items():
        for pat, w in patterns:
            scores[cls] += w * t.count(pat)
    return scores


def classify(text: str) -> Tuple[str, float]:
    """Классифицирует тип документа.

    Args:
        text: Строка с текстом из документа.

    Returns:
        Кортеж (тип документа, уверенность).
        Тип: contract | spec | invoice | act | unknown.
        Если разрыв между 1-м и 2-м местом меньше AMBIGUITY_THRESHOLD —
        возвращается unknown.
    """
    if not isinstance(text, str) or not text.strip():
        return "unknown", 0.0

    scores = _score(text)
    total = sum(scores.values()) or 1.0
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    top_cls, top_raw = sorted_scores[0]
    second_raw = sorted_scores[1][1]

    if top_raw == 0:
        return "unknown", 0.0

    confidence = top_raw / total
    gap = (top_raw - second_raw) / total

    if gap < AMBIGUITY_THRESHOLD:
        return "unknown", round(min(confidence, 0.5), 3)

    return top_cls, round(min(confidence, 1.0), 3)