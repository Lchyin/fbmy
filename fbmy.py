"""透明浏览器：一个用于隐蔽浏览网页的 Python 桌面脚本。"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

DEFAULT_URL = "https://www.fenbi.com/"
DEFAULT_OPACITY = 88
MIN_OPACITY = 25
MAX_OPACITY = 100
RESIZE_MARGIN = 8


class BrowserPage(QWebEnginePage):
    """让 target=_blank / 新窗口链接在当前浏览器里打开。"""

    def createWindow(self, _type):
        return self


class FenbiBrowser(QMainWindow):
    """半透明通用网页浏览器主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("浏览器")
        self.resize(1160, 760)
        self.setMinimumSize(760, 480)
        self.setWindowOpacity(DEFAULT_OPACITY / 100)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._drag_position = None
        self._resize_edges = set()
        self._resize_start_geometry = QRect()
        self._resize_start_position = QPoint()
        self._normal_geometry = None
        self._normal_minimum_size = self.minimumSize()
        self._auto_hidden = False
        self._auto_hide_enabled = True
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self._collapse_for_moyu)

        self.browser = QWebEngineView(self)
        self.browser.setPage(BrowserPage(self.browser))
        self.browser.urlChanged.connect(self._sync_address_bar)
        self.browser.setUrl(QUrl(DEFAULT_URL))

        self._hide_when_collapsed = []
        self.toolbar = self._build_toolbar()
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.browser, 1)
        self.setCentralWidget(container)

        self._install_shortcuts()

    def _build_toolbar(self) -> QWidget:
        toolbar = QWidget(self)
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(72)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(8)

        brand = QLabel("浏览器\n透明窗口 · 任意网址 · 拖拽缩放", toolbar)
        brand.setObjectName("brand")
        layout.addWidget(brand, 1)

        self._track_control(self._add_button(layout, "←", self.browser.back, "后退"))
        self._track_control(self._add_button(layout, "→", self.browser.forward, "前进"))
        self.address_bar = self._track_control(QLineEdit(DEFAULT_URL, toolbar))
        self.address_bar.setObjectName("addressBar")
        self.address_bar.setClearButtonEnabled(True)
        self.address_bar.returnPressed.connect(self._load_address)
        layout.addWidget(self.address_bar, 2)

        self._track_control(self._add_button(layout, "打开", self._load_address, "打开地址栏网址"))
        self._track_control(self._add_button(layout, "首页", lambda: self._load_url(DEFAULT_URL), "打开默认网址"))
        self._track_control(self._add_button(layout, "刷新", self.browser.reload, "刷新"))
        self._track_control(self._add_button(layout, "居中", self._center_on_screen, "居中窗口"))

        self.top_button = self._track_control(self._add_button(layout, "置顶", self._toggle_always_on_top, "置顶窗口"))

        opacity_label = self._track_control(QLabel("透明度", toolbar))
        layout.addWidget(opacity_label)
        opacity = self._track_control(QSlider(Qt.Horizontal, toolbar))
        opacity.setRange(MIN_OPACITY, MAX_OPACITY)
        opacity.setValue(DEFAULT_OPACITY)
        opacity.setFixedWidth(120)
        opacity.valueChanged.connect(lambda value: self.setWindowOpacity(value / 100))
        layout.addWidget(opacity)

        self.auto_hide = self._track_control(QCheckBox("离开隐藏", toolbar))
        self.auto_hide.setChecked(True)
        self.auto_hide.toggled.connect(self._set_auto_hide)
        layout.addWidget(self.auto_hide)

        self.click_through = self._track_control(QCheckBox("穿透", toolbar))
        self.click_through.toggled.connect(self._toggle_click_through)
        layout.addWidget(self.click_through)

        self._track_control(self._add_button(layout, "隐藏", self._toggle_visible, "隐藏为小条"))
        close_button = self._add_button(layout, "退出", QApplication.instance().quit, "退出")
        close_button.setObjectName("danger")
        return toolbar

    def _track_control(self, widget):
        self._hide_when_collapsed.append(widget)
        return widget

    def _add_button(self, layout: QHBoxLayout, text: str, callback, tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setText(text)
        button.setToolTip(tooltip)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+Shift+H"), self, activated=self._toggle_visible)
        QShortcut(QKeySequence("Meta+Shift+H"), self, activated=self._toggle_visible)
        QShortcut(QKeySequence("Ctrl+Shift+Q"), self, activated=QApplication.instance().quit)
        QShortcut(QKeySequence("Meta+Shift+Q"), self, activated=QApplication.instance().quit)

    def _toggle_visible(self) -> None:
        if self._auto_hidden:
            self._restore_from_moyu()
            return
        self._collapse_for_moyu()

    def _toggle_always_on_top(self) -> None:
        enabled = not bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()
        self.top_button.setText("已置顶" if enabled else "置顶")

    def _set_auto_hide(self, enabled: bool) -> None:
        self._auto_hide_enabled = enabled
        if not enabled and self._auto_hidden:
            self._restore_from_moyu()

    def _toggle_click_through(self, enabled: bool) -> None:
        self.browser.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)
        self.browser.setFocusPolicy(Qt.NoFocus if enabled else Qt.StrongFocus)
        self.click_through.setText("已穿透" if enabled else "穿透")
        self.statusBar().showMessage("网页区域已开启鼠标穿透，工具栏仍可点击以便关闭。" if enabled else "网页区域鼠标穿透已关闭。", 5000)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(round(screen.width() * 0.72), round(screen.height() * 0.76))
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def _normalize_url(self, text: str) -> QUrl:
        value = text.strip()
        if not value:
            value = DEFAULT_URL
        if "://" not in value:
            value = f"https://{value}"
        return QUrl(value)

    def _load_url(self, url: str) -> None:
        self.browser.setUrl(self._normalize_url(url))

    def _load_address(self) -> None:
        self.browser.setUrl(self._normalize_url(self.address_bar.text()))

    def _sync_address_bar(self, url: QUrl) -> None:
        if not hasattr(self, "address_bar"):
            return
        self.address_bar.blockSignals(True)
        self.address_bar.setText(url.toString())
        self.address_bar.blockSignals(False)

    def _collapse_for_moyu(self) -> None:
        if self._auto_hidden:
            return
        self._normal_geometry = self.geometry()
        self.browser.setVisible(False)
        for widget in self._hide_when_collapsed:
            widget.setVisible(False)
        self.setMinimumSize(1, 1)
        self.toolbar.setFixedHeight(36)
        self.resize(220, 36)
        self.setWindowOpacity(0.18)
        self._auto_hidden = True

    def _restore_from_moyu(self) -> None:
        self._hide_timer.stop()
        if not self._auto_hidden:
            return
        self._auto_hidden = False
        self.setMinimumSize(self._normal_minimum_size)
        self.toolbar.setFixedHeight(72)
        for widget in self._hide_when_collapsed:
            widget.setVisible(True)
        self.browser.setVisible(True)
        if self._normal_geometry is not None:
            self.setGeometry(self._normal_geometry)
        self.setWindowOpacity(DEFAULT_OPACITY / 100)
        self.raise_()

    def enterEvent(self, event) -> None:
        self._restore_from_moyu()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self._auto_hide_enabled and not self._auto_hidden:
            self._hide_timer.start(650)
        super().leaveEvent(event)

    def _detect_resize_edges(self, position) -> set[str]:
        if self._auto_hidden:
            return set()
        x = position.x()
        y = position.y()
        width = self.width()
        height = self.height()
        edges = set()
        if x <= RESIZE_MARGIN:
            edges.add("left")
        elif x >= width - RESIZE_MARGIN:
            edges.add("right")
        if y <= RESIZE_MARGIN:
            edges.add("top")
        elif y >= height - RESIZE_MARGIN:
            edges.add("bottom")
        return edges

    def _update_resize_cursor(self, position) -> None:
        edges = self._detect_resize_edges(position)
        if {"left", "top"} <= edges or {"right", "bottom"} <= edges:
            self.setCursor(Qt.SizeFDiagCursor)
        elif {"right", "top"} <= edges or {"left", "bottom"} <= edges:
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges & {"left", "right"}:
            self.setCursor(Qt.SizeHorCursor)
        elif edges & {"top", "bottom"}:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.unsetCursor()

    def _resize_window(self, global_position: QPoint) -> None:
        delta = global_position - self._resize_start_position
        geometry = QRect(self._resize_start_geometry)
        minimum_width = self.minimumWidth()
        minimum_height = self.minimumHeight()

        if "left" in self._resize_edges:
            geometry.setLeft(min(geometry.left() + delta.x(), geometry.right() - minimum_width))
        if "right" in self._resize_edges:
            geometry.setRight(max(geometry.right() + delta.x(), geometry.left() + minimum_width))
        if "top" in self._resize_edges:
            geometry.setTop(min(geometry.top() + delta.y(), geometry.bottom() - minimum_height))
        if "bottom" in self._resize_edges:
            geometry.setBottom(max(geometry.bottom() + delta.y(), geometry.top() + minimum_height))

        self.setGeometry(geometry)

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.LeftButton:
            return super().mousePressEvent(event)

        self._resize_edges = self._detect_resize_edges(event.position())
        if self._resize_edges:
            self._resize_start_geometry = self.geometry()
            self._resize_start_position = event.globalPosition().toPoint()
            event.accept()
            return

        if event.position().y() <= self.toolbar.height():
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._resize_edges and event.buttons() & Qt.LeftButton:
            self._resize_window(event.globalPosition().toPoint())
            event.accept()
            return
        if self._drag_position is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        self._update_resize_cursor(event.position())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_position = None
        self._resize_edges = set()
        self._resize_start_geometry = QRect()
        self._resize_start_position = QPoint()
        self.unsetCursor()
        event.accept()


def load_stylesheet() -> str:
    return Path(__file__).with_name("style.qss").read_text(encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("浏览器")
    app.setStyleSheet(load_stylesheet())

    window = FenbiBrowser()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
