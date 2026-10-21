"""
Точка входа в приложение.

Запуск:
    python main.py
"""
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from db.models import init_db
from ui.app import MainWindow


def main() -> None:
    # Инициализируем БД (создаёт таблицы, если их ещё нет)
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Страна — Читалка новостей")
    app.setOrganizationName("strana-news-parser")

    # Шрифт по умолчанию с поддержкой кириллицы
    font = QFont("Segoe UI", 12)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
