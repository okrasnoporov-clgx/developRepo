"""
SQLAlchemy ORM-модель для таблицы новостей.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base

import config

Base = declarative_base()


class News(Base):
    __tablename__ = "news"

    id        = Column(Integer,      primary_key=True, autoincrement=True)
    title     = Column(Text,         nullable=False)
    body      = Column(Text,         nullable=True)
    url       = Column(String(1000), unique=True, nullable=False)
    source    = Column(String(100),  default="ctrana.one")
    published = Column(DateTime,     nullable=True)
    fetched   = Column(DateTime,     default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<News id={self.id} title={self.title[:40]!r}>"


# ─── Engine ───────────────────────────────────────────────────────────────────

def get_engine():
    """Создаёт и возвращает SQLAlchemy engine для SQLite."""
    return create_engine(f"sqlite:///{config.DB_PATH}", echo=False)


def init_db() -> None:
    """Создаёт все таблицы (если ещё не существуют)."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
