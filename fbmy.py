"""粉笔摸鱼浏览器：一个用于浏览粉笔网的 Python 桌面脚本。"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

HOME_URL = "https://www.fenbi.com/"
DEFAULT_OPACITY = 88
MIN_OPACITY = 25
MAX_OPACITY = 100


class FenbiBrowser(QMainWindow):
    """半透明粉笔网浏览器主窗口。"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("粉笔摸鱼浏览器")
        self.resize(1160, 760)
        self.setMinimumSize(760, 480)
        self.setWindowOpacity(DEFAULT_OPACITY / 100)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._drag_position = None
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl(HOME_URL))

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

        brand = QLabel("粉笔摸鱼浏览器\n透明窗口 · Python 脚本 · 专注刷题", toolbar)
        brand.setObjectName("brand")
        layout.addWidget(brand, 1)

        self._add_button(layout, "←", self.browser.back, "后退")
        self._add_button(layout, "→", self.browser.forward, "前进")
        self._add_button(layout, "粉笔", lambda: self.browser.setUrl(QUrl(HOME_URL)), "打开粉笔网")
        self._add_button(layout, "刷新", self.browser.reload, "刷新")
        self._add_button(layout, "居中", self._center_on_screen, "居中窗口")

        self.top_button = self._add_button(layout, "置顶", self._toggle_always_on_top, "置顶窗口")

        layout.addWidget(QLabel("透明度", toolbar))
        opacity = QSlider(Qt.Horizontal, toolbar)
        opacity.setRange(MIN_OPACITY, MAX_OPACITY)
        opacity.setValue(DEFAULT_OPACITY)
        opacity.setFixedWidth(120)
        opacity.valueChanged.connect(lambda value: self.setWindowOpacity(value / 100))
        layout.addWidget(opacity)

        self.click_through = QCheckBox("穿透", toolbar)
        self.click_through.toggled.connect(self._toggle_click_through)
        layout.addWidget(self.click_through)

        self._add_button(layout, "隐藏", self.showMinimized, "最小化")
        close_button = self._add_button(layout, "退出", QApplication.instance().quit, "退出")
        close_button.setObjectName("danger")
        return toolbar

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
        if self.isVisible() and not self.isMinimized():
            self.showMinimized()
            return
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _toggle_always_on_top(self) -> None:
        enabled = not bool(self.windowFlags() & Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()
        self.top_button.setText("已置顶" if enabled else "置顶")

    def _toggle_click_through(self, enabled: bool) -> None:
        if enabled:
            self.click_through.blockSignals(True)
            self.click_through.setChecked(False)
            self.click_through.blockSignals(False)
            self.statusBar().showMessage("Python/Qt 版本暂不启用全窗口鼠标穿透，避免无法点回窗口。", 5000)

    def _center_on_screen(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        self.resize(round(screen.width() * 0.72), round(screen.height() * 0.76))
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and event.position().y() <= self.toolbar.height():
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_position is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        self._drag_position = None
        event.accept()


def load_stylesheet() -> str:
    return Path(__file__).with_name("style.qss").read_text(encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("粉笔摸鱼浏览器")
    app.setStyleSheet(load_stylesheet())

    window = FenbiBrowser()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
