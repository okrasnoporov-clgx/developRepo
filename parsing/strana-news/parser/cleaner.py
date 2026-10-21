"""
Очистка HTML-текста статьи: удаление рекламы, лишних тегов,
нормализация пробелов.
"""
from __future__ import annotations

import re

from bs4 import Tag


# Классы/id блоков, которые нужно удалить из тела статьи
_REMOVE_SELECTORS = [
    ".mob-ban",
    ".article-afterbody",
    ".sunsite_actions",
    ".video-icon",
    ".article-image",     # главная картинка статьи
    ".caption",           # подпись к фото
    "script",
    "style",
    "iframe",
    ".fa",                # иконки FontAwesome
]


def clean_body(element: Tag) -> str:
    """
    Принимает bs4-элемент div#article-body,
    возвращает чистый текст с переносами между абзацами.
    """
    # Клонируем, чтобы не портить оригинальное дерево
    el = element.__copy__()

    # Удаляем нежелательные блоки
    for selector in _REMOVE_SELECTORS:
        for node in el.select(selector):
            node.decompose()

    # Собираем текст по абзацам
    paragraphs: list[str] = []
    for tag in el.find_all(["p", "h2", "h3", "h4", "li", "blockquote"]):
        text = tag.get_text(" ", strip=True)
        text = _normalize_whitespace(text)
        if text:
            paragraphs.append(text)

    if paragraphs:
        return "\n\n".join(paragraphs)

    # Фолбэк: весь текст блока
    return _normalize_whitespace(el.get_text(" ", strip=True))


def _normalize_whitespace(text: str) -> str:
    """Схлопывает множественные пробелы и nbsp."""
    text = text.replace("\xa0", " ")          # &nbsp; → пробел
    text = re.sub(r"[ \t]+", " ", text)       # множественные пробелы
    text = re.sub(r"\n{3,}", "\n\n", text)    # больше 2 переносов — в два
    return text.strip()
