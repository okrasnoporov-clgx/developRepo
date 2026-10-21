"""
Парсер ctrana.one.

fetch_news_list() → список {'title': str, 'url': str}
fetch_article(url) → {'title': str, 'body': str, 'published': str | None}
"""
from __future__ import annotations

import time

import requests
from bs4 import BeautifulSoup

import config
from parser.cleaner import clean_body


def _get(url: str) -> BeautifulSoup | None:
    """HTTP GET с корректной обработкой кодировки."""
    try:
        resp = requests.get(
            url,
            headers=config.REQUEST_HEADERS,
            timeout=config.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        # Ключевой момент для кириллицы: доверяем chardet, а не заголовку
        resp.encoding = resp.apparent_encoding
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(f"[scraper] Ошибка запроса {url}: {exc}")
        return None


# ─── Список новостей ──────────────────────────────────────────────────────────

def fetch_news_list() -> list[dict[str, str]]:
    """
    Загружает главную страницу и извлекает ссылки на статьи из ленты новостей.
    Возвращает список уникальных {'title': ..., 'url': ...}.
    """
    soup = _get(config.NEWS_LIST_URL)
    if soup is None:
        return []

    seen: set[str] = set()
    items: list[dict[str, str]] = []

    for a in soup.select("ul.list-newsfeed li a.article"):
        href: str = a.get("href", "").strip()
        if not href or href in seen:
            continue
        seen.add(href)

        # Очищаем заголовок от текста иконок (fa-icons не имеют текста, но на всякий случай)
        for icon in a.select("i"):
            icon.decompose()
        title = a.get_text(" ", strip=True)

        url = href if href.startswith("http") else config.BASE_URL + href
        items.append({"title": title, "url": url})

    return items


# ─── Отдельная статья ─────────────────────────────────────────────────────────

def fetch_article(url: str) -> dict[str, str | None] | None:
    """
    Загружает страницу статьи и извлекает заголовок, дату и текст.
    Возвращает {'title', 'body', 'published'} или None при ошибке.
    """
    time.sleep(config.DELAY_BETWEEN_REQUESTS)   # вежливая пауза
    soup = _get(url)
    if soup is None:
        return None

    # Заголовок
    h1 = soup.select_one("h1.article")
    title: str = h1.get_text(strip=True) if h1 else ""

    # Дата публикации из атрибута data-time
    date_el = soup.select_one("span.strana-adate")
    published: str | None = date_el.get("data-time") if date_el else None

    # Если нет — пробуем JSON-LD
    if not published:
        import json, re
        ld = soup.find("script", type="application/ld+json")
        if ld:
            try:
                data = json.loads(ld.string)
                published = data.get("datePublished", "")[:19].replace("T", " ")
            except (json.JSONDecodeError, AttributeError):
                pass

    # Тело статьи
    body_el = soup.select_one("div#article-body")
    body: str = clean_body(body_el) if body_el else ""

    return {"title": title, "body": body, "published": published}
