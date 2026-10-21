"""
Главное окно приложения (PyQt6).
Левая панель — таблица новостей, правая — текст выбранной статьи.
"""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QThread, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

import config
from db import repository
from parser import scraper


# ─── Цветовая схема ───────────────────────────────────────────────────────────
PALETTE = {
    "bg":           "#1a1a2a",
    "bg_panel":     "#22223a",
    "bg_toolbar":   "#16162a",
    "accent":       "#8b1a35",
    "accent_hover": "#a82040",
    "text":         "#e8e6f0",
    "text_dim":     "#8884a0",
    "row_even":     "#1e1e30",
    "row_odd":      "#252538",
    "row_sel":      "#3a1830",
    "border":       "#2e2e4a",
    "time":         "#c0a060",
}

APP_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {PALETTE['bg']};
    color: {PALETTE['text']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}

/* ── Toolbar ── */
#toolbar {{
    background-color: {PALETTE['bg_toolbar']};
    border-bottom: 1px solid {PALETTE['border']};
    padding: 6px 12px;
}}

#app_title {{
    font-size: 17px;
    font-weight: 700;
    color: {PALETTE['text']};
    letter-spacing: 0.5px;
}}

#app_subtitle {{
    font-size: 11px;
    color: {PALETTE['text_dim']};
}}

/* ── Кнопка обновления ── */
#btn_refresh {{
    background-color: {PALETTE['accent']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 600;
}}
#btn_refresh:hover {{
    background-color: {PALETTE['accent_hover']};
}}
#btn_refresh:disabled {{
    background-color: #444455;
    color: #777788;
}}

/* ── Поиск ── */
#search_box {{
    background-color: {PALETTE['bg_panel']};
    color: {PALETTE['text']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    min-width: 220px;
}}
#search_box:focus {{
    border: 1px solid {PALETTE['accent']};
}}

/* ── Таблица ── */
QTableWidget {{
    background-color: {PALETTE['bg']};
    gridline-color: {PALETTE['border']};
    border: none;
    outline: 0;
    selection-background-color: {PALETTE['row_sel']};
}}
QTableWidget::item {{
    padding: 4px 8px;
    border-bottom: 1px solid {PALETTE['border']};
}}
QTableWidget::item:selected {{
    background-color: {PALETTE['row_sel']};
    color: {PALETTE['text']};
}}
QHeaderView::section {{
    background-color: {PALETTE['bg_toolbar']};
    color: {PALETTE['text_dim']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid {PALETTE['border']};
    border-right: 1px solid {PALETTE['border']};
}}
QScrollBar:vertical {{
    background: {PALETTE['bg']};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {PALETTE['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── Панель текста статьи ── */
QTextBrowser {{
    background-color: {PALETTE['bg_panel']};
    color: {PALETTE['text']};
    border: none;
    border-left: 1px solid {PALETTE['border']};
    padding: 20px 24px;
    font-size: 14px;
    line-height: 1.7;
    selection-background-color: {PALETTE['accent']};
}}

/* ── Статус-бар ── */
QStatusBar {{
    background-color: {PALETTE['bg_toolbar']};
    color: {PALETTE['text_dim']};
    border-top: 1px solid {PALETTE['border']};
    font-size: 12px;
    padding: 2px 8px;
}}
QStatusBar::item {{
    border: none;
}}

/* ── Разделитель ── */
QSplitter::handle {{
    background-color: {PALETTE['border']};
    width: 1px;
}}
"""


# ─── Фоновый поток загрузки ───────────────────────────────────────────────────

class FetchWorker(QThread):
    """Загружает список и статьи в фоне, не блокируя UI."""

    progress = pyqtSignal(str)          # сообщение о текущей операции
    finished = pyqtSignal(int)          # кол-во новых статей
    error    = pyqtSignal(str)          # текст ошибки

    def run(self) -> None:
        try:
            self.progress.emit("Загрузка ленты новостей…")
            news_list = scraper.fetch_news_list()

            if not news_list:
                self.error.emit("Не удалось получить список новостей.")
                return

            existing_urls = repository.get_existing_urls()
            new_items = [it for it in news_list if it["url"] not in existing_urls]

            if not new_items:
                self.progress.emit("Новых статей нет.")
                self.finished.emit(0)
                return

            new_count = 0
            for i, item in enumerate(new_items, 1):
                if self.isInterruptionRequested():
                    break
                short_title = item["title"][:55] + ("…" if len(item["title"]) > 55 else "")
                self.progress.emit(f"[{i}/{len(new_items)}] {short_title}")

                article = scraper.fetch_article(item["url"])
                if article:
                    saved = repository.save_news(
                        url=item["url"],
                        title=article["title"] or item["title"],
                        body=article["body"],
                        published=article["published"],
                    )
                    if saved:
                        new_count += 1

            self.finished.emit(new_count)

        except Exception as exc:                        # pylint: disable=broad-except
            self.error.emit(str(exc))


# ─── Главное окно ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Страна — Читалка новостей")
        self.setMinimumSize(1100, 650)
        self.resize(1280, 760)

        self._worker: FetchWorker | None = None
        self._all_news: list[dict] = []

        self._build_ui()
        self._apply_style()
        self._setup_auto_refresh()

        # Загружаем из БД при старте
        self._reload_table()

    # ── Построение UI ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Toolbar
        root_layout.addWidget(self._make_toolbar())

        # Splitter: таблица | текст
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        splitter.addWidget(self._make_news_table())
        splitter.addWidget(self._make_article_panel())
        splitter.setSizes([460, 820])

        root_layout.addWidget(splitter, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._lbl_count  = QLabel()
        self._lbl_status = QLabel("Готово")
        self.status_bar.addWidget(self._lbl_status, 1)
        self.status_bar.addPermanentWidget(self._lbl_count)

    def _make_toolbar(self) -> QWidget:
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)

        # Логотип / название
        title_block = QVBoxLayout()
        title_block.setSpacing(1)
        lbl_title    = QLabel("📰  Страна — Читалка")
        lbl_subtitle = QLabel("ctrana.one  ·  локальная база новостей")
        lbl_title.setObjectName("app_title")
        lbl_subtitle.setObjectName("app_subtitle")
        title_block.addWidget(lbl_title)
        title_block.addWidget(lbl_subtitle)
        layout.addLayout(title_block)

        layout.addStretch()

        # Поиск
        self._search = QLineEdit()
        self._search.setObjectName("search_box")
        self._search.setPlaceholderText("🔍  Поиск по заголовкам…")
        self._search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search)

        # Кнопка обновления
        self._btn_refresh = QPushButton("⟳  Обновить")
        self._btn_refresh.setObjectName("btn_refresh")
        self._btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_refresh.clicked.connect(self.start_fetch)
        layout.addWidget(self._btn_refresh)

        return toolbar

    def _make_news_table(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Дата / Время", "Заголовок"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.setWordWrap(False)
        self._table.verticalHeader().setDefaultSectionSize(34)
        self._table.itemSelectionChanged.connect(self._on_row_selected)

        layout.addWidget(self._table)
        return container

    def _make_article_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._article_title = QLabel("Выберите новость из списка")
        self._article_title.setWordWrap(True)
        self._article_title.setStyleSheet(
            f"font-size:16px; font-weight:700; color:{PALETTE['text']};"
            f"background:{PALETTE['bg_panel']};"
            f"padding:16px 24px 10px 24px;"
            f"border-left:1px solid {PALETTE['border']};"
            f"border-bottom:1px solid {PALETTE['border']};"
        )

        self._article_meta = QLabel("")
        self._article_meta.setStyleSheet(
            f"font-size:11px; color:{PALETTE['text_dim']};"
            f"background:{PALETTE['bg_panel']};"
            f"padding:0 24px 12px 24px;"
            f"border-left:1px solid {PALETTE['border']};"
            f"border-bottom:1px solid {PALETTE['border']};"
        )

        self._article_body = QTextBrowser()
        self._article_body.setOpenExternalLinks(True)
        font = QFont("Segoe UI", 13)
        self._article_body.setFont(font)

        layout.addWidget(self._article_title)
        layout.addWidget(self._article_meta)
        layout.addWidget(self._article_body, 1)
        return container

    # ── Стиль ─────────────────────────────────────────────────────────────────

    def _apply_style(self) -> None:
        self.setStyleSheet(APP_STYLE)

    # ── Автообновление ────────────────────────────────────────────────────────

    def _setup_auto_refresh(self) -> None:
        interval_ms = config.AUTO_REFRESH_MINUTES * 60 * 1000
        self._auto_timer = QTimer(self)
        self._auto_timer.timeout.connect(self.start_fetch)
        self._auto_timer.start(interval_ms)

    # ── Загрузка данных ───────────────────────────────────────────────────────

    def start_fetch(self) -> None:
        """Запускает фоновую загрузку (только если нет активного worker'а)."""
        if self._worker and self._worker.isRunning():
            return

        self._btn_refresh.setEnabled(False)
        self._btn_refresh.setText("⏳  Загрузка…")

        self._worker = FetchWorker(self)
        self._worker.progress.connect(self._on_fetch_progress)
        self._worker.finished.connect(self._on_fetch_done)
        self._worker.error.connect(self._on_fetch_error)
        self._worker.start()

    def _on_fetch_progress(self, msg: str) -> None:
        self._lbl_status.setText(msg)

    def _on_fetch_done(self, new_count: int) -> None:
        self._btn_refresh.setEnabled(True)
        self._btn_refresh.setText("⟳  Обновить")
        now = datetime.now().strftime("%H:%M:%S")
        if new_count:
            self._lbl_status.setText(f"✓ Добавлено {new_count} новых статей  [{now}]")
        else:
            self._lbl_status.setText(f"Нет новых статей  [{now}]")
        self._reload_table()

    def _on_fetch_error(self, msg: str) -> None:
        self._btn_refresh.setEnabled(True)
        self._btn_refresh.setText("⟳  Обновить")
        self._lbl_status.setText(f"⚠ Ошибка: {msg}")

    # ── Таблица ───────────────────────────────────────────────────────────────

    def _reload_table(self, search: str = "") -> None:
        """Перезагружает таблицу из БД."""
        self._all_news = repository.get_all(search=search)
        self._populate_table(self._all_news)
        count = repository.get_count()
        self._lbl_count.setText(f"  Всего в БД: {count}  ")

    def _populate_table(self, news_list: list[dict]) -> None:
        self._table.setUpdatesEnabled(False)
        self._table.setRowCount(0)

        for row_idx, news in enumerate(news_list):
            self._table.insertRow(row_idx)

            # Колонка: дата/время
            dt = news.get("published") or news.get("fetched")
            if isinstance(dt, datetime):
                dt_str = dt.strftime("%d.%m  %H:%M")
            elif isinstance(dt, str):
                dt_str = dt[:16]
            else:
                dt_str = "—"

            dt_item = QTableWidgetItem(dt_str)
            dt_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            dt_item.setForeground(QColor(PALETTE["time"]))
            dt_item.setData(Qt.ItemDataRole.UserRole, row_idx)  # индекс в списке

            # Колонка: заголовок
            title_item = QTableWidgetItem(news["title"])
            title_item.setToolTip(news["title"])

            # Чередование строк
            bg = QColor(PALETTE["row_even"] if row_idx % 2 == 0 else PALETTE["row_odd"])
            for item in (dt_item, title_item):
                item.setBackground(bg)

            self._table.setItem(row_idx, 0, dt_item)
            self._table.setItem(row_idx, 1, title_item)

        self._table.setUpdatesEnabled(True)

    # ── Выбор строки ──────────────────────────────────────────────────────────

    def _on_row_selected(self) -> None:
        selected = self._table.selectedItems()
        if not selected:
            return
        row = self._table.currentRow()
        if row < 0 or row >= len(self._all_news):
            return

        news = self._all_news[row]
        self._show_article(news)

    def _show_article(self, news: dict) -> None:
        """Отображает заголовок и текст выбранной новости."""
        self._article_title.setText(news["title"])

        # Мета-строка: дата + источник + ссылка
        dt = news.get("published") or news.get("fetched")
        if isinstance(dt, datetime):
            dt_str = dt.strftime("%d %B %Y,  %H:%M")
        else:
            dt_str = str(dt)[:16] if dt else "—"

        url = news.get("url", "")
        accent_color = PALETTE["accent"]
        self._article_meta.setText(
            f"🕐 {dt_str}   ·   <a href='{url}' style='color:{accent_color}'>"
            f"Открыть в браузере</a>"
        )
        self._article_meta.setOpenExternalLinks(True)

        # Тело
        body = news.get("body", "") or "Текст статьи недоступен."
        # Форматируем: параграфы через HTML
        html_body = "".join(
            f"<p style='margin:0 0 12px 0'>{para}</p>"
            for para in body.split("\n\n")
            if para.strip()
        )
        self._article_body.setHtml(
            f"""
            <html><body style="
                font-family:'Segoe UI',Arial,sans-serif;
                font-size:14px;
                color:{PALETTE['text']};
                background:{PALETTE['bg_panel']};
                line-height:1.75;
            ">
            {html_body}
            </body></html>
            """
        )

    # ── Поиск ─────────────────────────────────────────────────────────────────

    def _on_search_changed(self, text: str) -> None:
        self._reload_table(search=text.strip())

    # ── Закрытие ──────────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(3000)
        event.accept()
