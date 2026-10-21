"""
CRUD-операции над таблицей news.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from .models import News, get_engine

# Кэшируем один engine на весь жизненный цикл приложения
_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


# ─── Запись ───────────────────────────────────────────────────────────────────

def save_news(
    url: str,
    title: str,
    body: str = "",
    published: str | None = None,
    source: str = "ctrana.one",
) -> bool:
    """
    Сохраняет новость в БД.
    Возвращает True если новость добавлена, False если URL уже существует.
    """
    engine = _get_engine()
    with Session(engine) as session:
        if session.query(News).filter_by(url=url).first():
            return False  # дубль — пропускаем

        pub_dt: datetime | None = None
        if published:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
                try:
                    pub_dt = datetime.strptime(published[:19], fmt[:len(published[:19])])
                    break
                except ValueError:
                    continue

        news = News(
            title=title,
            body=body,
            url=url,
            source=source,
            published=pub_dt,
            fetched=datetime.utcnow(),
        )
        session.add(news)
        session.commit()
        return True


# ─── Чтение ───────────────────────────────────────────────────────────────────

def get_all(search: str = "") -> list[dict[str, Any]]:
    """
    Возвращает список новостей (новейшие первыми).
    Опциональный параметр search фильтрует по заголовку.
    """
    engine = _get_engine()
    with Session(engine) as session:
        q = session.query(News).order_by(News.fetched.desc())
        if search:
            q = q.filter(News.title.contains(search))
        return [
            {
                "id":        n.id,
                "title":     n.title,
                "body":      n.body or "",
                "url":       n.url,
                "published": n.published,
                "fetched":   n.fetched,
            }
            for n in q.all()
        ]


def get_existing_urls() -> set[str]:
    """Быстро возвращает множество всех URL, уже сохранённых в БД."""
    engine = _get_engine()
    with Session(engine) as session:
        rows = session.query(News.url).all()
        return {r[0] for r in rows}


def get_count() -> int:
    """Общее количество новостей в БД."""
    engine = _get_engine()
    with Session(engine) as session:
        return session.query(News).count()
