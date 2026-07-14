"""Проверка соответствия предмета оплаты льготной программе."""
from __future__ import annotations

import json
import os
from difflib import SequenceMatcher
from typing import Tuple

from src.constants import FUZZY_THRESHOLD, ALLOWED_CATEGORIES


def _keyword_match(subject: str) -> Tuple[bool, float, str]:
    """Локальная проверка через keyword + fuzzy matching."""
    s = subject.lower()
    best_cat, best_score, best_term = None, 0.0, ""

    for cat, terms in ALLOWED_CATEGORIES.items():
        for term in terms:
            if term in s:
                return True, 0.95, f"'{term}' относится к категории '{cat}'"
            ratio = SequenceMatcher(None, s, term).ratio()
            if ratio > best_score:
                best_score, best_cat, best_term = ratio, cat, term

    if best_score >= FUZZY_THRESHOLD and best_cat:
        return True, round(best_score, 2), f"'{best_term}' (похоже) относится к категории '{best_cat}'"

    return False, 0.9, "предмет не относится к разрешённым сельхоз-категориям"


def _llm_match(subject: str) -> Tuple[bool, float, str]:
    """Проверка через LangChain + OpenAI (fallback при ошибке)."""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
    except ImportError as e:
        raise RuntimeError(f"LangChain не установлен: {e}")

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Ты эксперт по льготным сельхоз-кредитам. Разрешённые категории: "
         + ", ".join(ALLOWED_CATEGORIES.keys())
         + ". Верни строго JSON вида "
         + "{\"matches\": bool, \"confidence\": float, \"reason\": str}."),
        ("human", "Предмет оплаты: {subject}"),
    ])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm
    resp = chain.invoke({"subject": subject})
    data = json.loads(resp.content)
    return bool(data["matches"]), float(data["confidence"]), str(data["reason"])


def check_subject(subject: str) -> Tuple[bool, float, str]:
    """Проверяет соответствие предмета оплаты программе.

    Args:
        subject: Строка с предметом оплаты.

    Returns:
        Кортеж (соответствует, уверенность_0_1, объяснение).
        По умолчанию — keyword + fuzzy matching.
        Если установлен OPENAI_API_KEY и langchain — используется LLM.
    """
    if not isinstance(subject, str) or not subject.strip():
        return False, 0.0, "предмет оплаты не указан"

    if os.getenv("OPENAI_API_KEY"):
        try:
            return _llm_match(subject)
        except Exception:
            return _keyword_match(subject)

    return _keyword_match(subject)