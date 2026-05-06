from __future__ import annotations

import os
import sys
import time
import subprocess
import tempfile
import threading
import webbrowser
from pathlib import Path
from queue import Queue, Empty
from typing import Any

from PySide6.QtCore import Qt, QTimer, QPoint, QObject, QEvent, QUrl, QRect, QSize
from PySide6.QtGui import QAction, QColor, QCursor, QFont, QPainter, QPaintEvent, QPainterPath, QPen, QPixmap, QRegion, QTextCursor, QDesktopServices
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QGridLayout, QMenu, QMessageBox, QPushButton, QSizePolicy, QTabWidget, QToolButton, QTextEdit, QVBoxLayout,
    QWidget, QSystemTrayIcon, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon

from codex_pet_companion.core.bridge import CodexBridge
from codex_pet_companion.core.config import load_config, save_config, resolve_codex_home, resolve_state_dir, ui_default_config, data_dir
from codex_pet_companion.core.constants import ACHIEVEMENTS, APP_VERSION, APP_NAME_DISPLAY, STATES, TRAITS
from codex_pet_companion.core.daily_activities import ensure_activity_state as _ensure_activity_state, activity_text as _activity_text
from codex_pet_companion.core.pet_pack import export_pet_pack, import_pet_pack
from codex_pet_companion.core.pets import PetInfo, discover_pets, pet_trait_key
from codex_pet_companion.core.phrases import hint_line
from codex_pet_companion.core.state import add_log, clear_runtime_logs, history_lines, load_state, now, save_state
from codex_pet_companion.core.virtual_pet import (
    apply_action, care_state, codex_session_lines, codex_status_line,
    codex_short_line, decayed, days_together, ensure_bond_state, friendship_progress_line,
    friendship_rank, friendship_title, maybe_mark_codex_silence,
    today_key,
)
from codex_pet_companion.core.text_profiles import text_profile_id
from codex_pet_companion.core.update_checker import UpdateInfo, check_for_update, download_update
from .sprites import SpriteFrames
from .widgets import StatRow

MINI_BUBBLE_THEME = "light"

STYLE = """
QWidget {
    color: #edf5ef;
    font-family: Segoe UI, Arial;
    font-size: 13px;
}
QMainWindow,
QWidget#AppRoot {
    background: #0f1116;
}
QWidget#CompactWindow {
    background: transparent;
}
QLabel,
QCheckBox {
    background: transparent;
}
QLabel#PetSprite {
    background: transparent;
    border: none;
}
QFrame#SpriteCard {
    background: rgba(12, 16, 22, 110);
    border: 1px solid #202a33;
    border-radius: 18px;
}
QFrame#Card {
    background: rgba(22, 26, 32, 238);
    border: 1px solid #28313a;
    border-radius: 16px;
}
QFrame#InfoCard {
    background: rgba(16, 20, 26, 245);
    border: 1px solid #28313a;
    border-radius: 14px;
}
QLabel#CardTitle {
    color: #a9b5ad;
    font-size: 12px;
    font-weight: 700;
}
QLabel#CardValue {
    color: #edf5ef;
    font-size: 16px;
    font-weight: 700;
}
QLabel#Title {
    font-size: 22px;
    font-weight: 700;
}
QLabel#Relationship {
    color: #d8eee1;
    font-size: 14px;
    font-weight: 700;
}
QLabel#Muted {
    color: #a9b5ad;
}
QLabel#Accent {
    color: #a7f2c3;
    font-weight: 700;
}
QLabel#Codex {
    color: #f1d56e;
}
QLabel#StatusLine,
QLabel#CodexLine,
QLabel#StateLine {
    background: transparent;
    padding-left: 6px;
    padding-right: 6px;
}
QLabel#StatusLine {
    color: #a7f2c3;
    font-weight: 700;
}
QLabel#CodexLine {
    color: #f1d56e;
}
QLabel#StateLine {
    color: #a9b5ad;
}
QFrame#SoftDivider {
    background: #28313a;
    border: none;
    min-height: 1px;
    max-height: 1px;
}
QLabel#MiniName {
    color: #a7f2c3;
    font-weight: 700;
}
QLabel#MiniBar {
    background: transparent;
    border: none;
    padding: 7px 10px;
}
QLabel#MiniBarCodex {
    background: transparent;
    border: none;
    padding: 7px 10px;
    color: #f1d56e;
}
QLabel#MiniBarState {
    background: transparent;
    border: none;
    padding: 7px 10px;
    color: #dce8e1;
}
QPushButton {
    background: #2bdc84;
    color: #08170f;
    border: 1px solid #64f4ae;
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 700;
}
QPushButton:hover {
    background: #64f4ae;
    border: 1px solid #a8ffd0;
}
QPushButton#Secondary {
    background: #151d25;
    color: #d8eee1;
    border: 1px solid #2a3843;
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 700;
}
QPushButton#Danger {
    background: #ffa6a6;
}
QToolButton {
    background: rgba(22, 26, 32, 230);
    color: #edf5ef;
    border: 1px solid #28313a;
    border-radius: 10px;
    padding: 4px 7px;
    font-weight: 700;
}
QToolButton:hover {
    background: #28313a;
}
QProgressBar {
    background: #20252d;
    border: 0;
    border-radius: 5px;
    height: 10px;
}
QProgressBar::chunk {
    background: #a7f2c3;
    border-radius: 5px;
}
QTextEdit {
    background: rgba(16, 20, 26, 180);
    border: 1px solid #28313a;
    border-radius: 12px;
    padding: 8px;
}
QTextEdit#PlainTextPanel {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 0;
}
QComboBox, QLineEdit {
    background: #161a20;
    border: 1px solid #28313a;
    border-radius: 8px;
    padding: 7px;
}
QComboBox {
    padding-right: 28px;
}
QComboBox::drop-down {
    background: transparent;
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
}
QComboBox::down-arrow {
    image: url(__COMBO_ARROW__);
    width: 12px;
    height: 12px;
    margin-right: 9px;
}
QComboBox QAbstractItemView {
    background: #161a20;
    color: #edf5ef;
    border: 1px solid #28313a;
    selection-background-color: #28313a;
    selection-color: #edf5ef;
    outline: 0;
}
QTabWidget::pane {
    background: transparent;
    border: none;
    top: 8px;
}
QTabWidget::tab-bar {
    alignment: left;
}
QTabBar::tab {
    background: transparent;
    color: #a9b5ad;
    border: none;
    border-radius: 9px;
    padding: 7px 14px;
    margin-right: 6px;
    min-width: 104px;
}
QTabBar::tab:selected {
    color: #edf5ef;
    background: rgba(40, 49, 58, 190);
}
QTabBar::tab:hover:!selected {
    color: #edf5ef;
    background: rgba(40, 49, 58, 105);
}
QGroupBox {
    background: transparent;
    border: 1px solid #28313a;
    border-radius: 12px;
    margin-top: 10px;
    padding: 10px;
    font-weight: 700;
}
QGroupBox::title {
    background: transparent;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QCheckBox {
    background: transparent;
    padding: 4px;
}

QPushButton#AccentButton {
    background: #1a2a22;
    color: #a7f2c3;
    border: 1px solid #31503f;
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 700;
}
QPushButton#AccentButton:hover {
    background: #21382d;
    border: 1px solid #5fcf91;
}
QPushButton#Secondary:hover {
    background: #1c2831;
    border: 1px solid #40525d;
}
QPushButton#PngActionButton,
QPushButton#PngActionButton:hover,
QPushButton#PngActionButton:pressed,
QPushButton#PngActionButton:disabled {
    background: transparent;
    border: none;
    padding: 0;
}
"""



class SingleInstanceGuard:
    def __init__(self, name: str):
        self.name = name
        self.server: QLocalServer | None = None

    def acquire(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(self.name)
        if socket.waitForConnected(120):
            socket.disconnectFromServer()
            return False

        QLocalServer.removeServer(self.name)
        self.server = QLocalServer()
        return self.server.listen(self.name)

    def release(self) -> None:
        if self.server is not None:
            self.server.close()
            QLocalServer.removeServer(self.name)
            self.server = None




class InfoCard(QFrame):
    def __init__(self, title: str, value: str = ""):
        super().__init__()
        self.setObjectName("InfoCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("CardTitle")
        self.title_label.setFixedHeight(18)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        self.value_label.setWordWrap(True)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)
        self.value_label.setToolTip(value)


class TextPanel(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("PlainSection")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        self.text = QTextEdit()
        self.text.setObjectName("PlainTextPanel")
        self.text.setReadOnly(True)

        layout.addWidget(title_label)
        layout.addWidget(self.text, 1)





class PetBackdropFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("SpriteCard")
        self._background = QPixmap()
        self._background_path = ""
        self._radius = 18

    def set_background_path(self, path: str) -> None:
        path = str(path or "")
        if path == self._background_path:
            return
        self._background_path = path
        self._background = QPixmap(path) if path else QPixmap()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect().adjusted(0, 0, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, self._radius, self._radius)

        painter.setClipPath(path)
        painter.fillRect(rect, QColor(12, 16, 22, 110))

        if not self._background.isNull():
            overfill = 1.10
            target_w = max(1, int(rect.width() * overfill))
            target_h = max(1, int(rect.height() * overfill))
            scaled = self._background.scaled(
                target_w,
                target_h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = rect.center().x() - scaled.width() // 2
            y = rect.center().y() - scaled.height() // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillRect(rect, QColor(2, 6, 7, 46))

        painter.setClipping(False)
        painter.setPen(QPen(QColor("#202a33"), 1))
        painter.drawRoundedRect(rect, self._radius, self._radius)


class PngActionButton(QPushButton):
    TARGET_HEIGHT = 42

    def __init__(self, label: str, icon_path: Path):
        super().__init__("")
        self._label = label
        self._pixmap = QPixmap(str(icon_path))
        self._pressed = False
        self.setToolTip(label)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setText("")
        self.setObjectName("PngActionButton")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(self.TARGET_HEIGHT)
        self.setMinimumWidth(88)

    def sizeHint(self) -> QSize:
        if self._pixmap.isNull():
            return QSize(96, self.TARGET_HEIGHT)
        width = round(self.TARGET_HEIGHT * self._pixmap.width() / max(1, self._pixmap.height()))
        return QSize(max(88, width), self.TARGET_HEIGHT)

    def minimumSizeHint(self) -> QSize:
        return QSize(88, self.TARGET_HEIGHT)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        self._pressed = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._pixmap.isNull():
            return

        y_offset = 1 if self._pressed and self.isEnabled() else 0
        available = self.rect().adjusted(0, 0, 0, -1)
        scaled = self._pixmap.scaled(
            available.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = available.center().x() - scaled.width() // 2
        y = available.center().y() - scaled.height() // 2 + y_offset
        target = QRect(x, y, scaled.width(), scaled.height())

        painter.setOpacity(0.50 if not self.isEnabled() else 1.0)
        painter.drawPixmap(target, scaled)

        if not self.isEnabled():
            return

        if self._pressed:
            painter.setOpacity(0.16)
            painter.fillRect(target, QColor(0, 0, 0))
        elif self.underMouse():
            painter.setOpacity(0.12)
            painter.fillRect(target, QColor(255, 255, 255))


def app_icon_path(name: str) -> Path:
    filename = name if Path(name).suffix else f"{name}.png"
    return Path(__file__).resolve().parents[2] / "icons" / filename


def icon_for(name: str) -> QIcon:
    return QIcon(str(app_icon_path(name)))


def add_button_icon(button: QPushButton, icon_name: str, minimum_width: int | None = None) -> None:
    button.setIcon(icon_for(icon_name))
    button.setIconSize(QSize(20, 20))
    if minimum_width is not None:
        button.setMinimumWidth(minimum_width)


def soft_divider() -> QFrame:
    line = QFrame()
    line.setObjectName("SoftDivider")
    line.setFrameShape(QFrame.Shape.NoFrame)
    return line


def compact_scale_value(raw_value) -> float:
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return 0.50
    return max(0.25, min(0.65, value))

def disable_windows_backdrop(widget: QWidget) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        hwnd = wintypes.HWND(int(widget.winId()))
        dwmapi = ctypes.windll.dwmapi

        def set_dwm_attr(attr: int, value: int) -> None:
            raw = ctypes.c_uint(value)
            dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(raw), ctypes.sizeof(raw))

        # Windows 11 DWM can draw a rounded translucent host surface even for
        # frameless translucent Qt tool windows. Disable that surface explicitly.
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_DONOTROUND = 1
        DWMWA_BORDER_COLOR = 34
        DWMWA_CAPTION_COLOR = 35
        DWMWA_SYSTEMBACKDROP_TYPE = 38
        DWMSBT_NONE = 1
        DWMWA_COLOR_NONE = 0xFFFFFFFE

        set_dwm_attr(DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_DONOTROUND)
        set_dwm_attr(DWMWA_SYSTEMBACKDROP_TYPE, DWMSBT_NONE)
        set_dwm_attr(DWMWA_BORDER_COLOR, DWMWA_COLOR_NONE)
        set_dwm_attr(DWMWA_CAPTION_COLOR, DWMWA_COLOR_NONE)
    except Exception:
        return

class MiniSpriteWindow(QWidget):
    def __init__(self, controller: "CompanionController"):
        super().__init__()
        self.controller = controller
        self.drag_pos: QPoint | None = None
        self._pixmap = QPixmap()
        self.setWindowTitle("Codex Pet Companion")
        self.setObjectName("MiniSpriteWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setStyleSheet("background: transparent; border: none;")

    def showEvent(self, event):
        super().showEvent(event)
        disable_windows_backdrop(self)

    def update_pixmap(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self.setFixedSize(pixmap.size())
        if not pixmap.isNull():
            self.setMask(QRegion(pixmap.mask()))
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        if self._pixmap.isNull():
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.controller.begin_compact_drag()
        elif event.button() == Qt.MouseButton.RightButton:
            self.controller.show_context_menu(QCursor.pos())

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            previous_x = self.x()
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            self.controller.update_compact_drag_direction(self.x() - previous_x)
            self.controller.follow_compact_sprite()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.controller.end_compact_drag()

    def mouseDoubleClickEvent(self, event):
        self.controller.show_full()


class ClickableSpriteLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.clicked_callback = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.clicked_callback is not None:
            self.clicked_callback()
            event.accept()
            return
        super().mousePressEvent(event)


class MiniBubbleWindow(QWidget):
    BUBBLE_WIDTH = 330

    def __init__(self, controller: "CompanionController"):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Codex Pet Companion Notification")
        self.setObjectName("MiniBubbleWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)
        self.setAutoFillBackground(False)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.SplashScreen
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setStyleSheet("""
QWidget#MiniBubbleWindow { background: transparent; border: none; }
QFrame#MiniBubble {
    background: rgba(255, 255, 255, 238);
    border: 1px solid rgba(0, 0, 0, 28);
    border-radius: 18px;
}
QLabel#MiniBubbleTitle {
    background: transparent;
    border: none;
    color: #1f2328;
    font-weight: 700;
    font-size: 13px;
}
QLabel#MiniBubbleSubtitle {
    background: transparent;
    border: none;
    color: #5d6670;
    font-size: 12px;
}
QLabel#MiniBubbleActivity {
    background: transparent;
    border: none;
    color: #5d6670;
    font-size: 18px;
}
""")

        self.card = QFrame(self)
        self.card.setObjectName("MiniBubble")
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 35))
        self.card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(14, 9, 12, 9)
        card_layout.setSpacing(12)

        text_box = QVBoxLayout()
        text_box.setContentsMargins(0, 0, 0, 0)
        text_box.setSpacing(2)

        self.title = QLabel("")
        self.title.setObjectName("MiniBubbleTitle")
        self.title.setFixedWidth(self.BUBBLE_WIDTH - 58)
        self.title.setWordWrap(False)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("MiniBubbleSubtitle")
        self.subtitle.setFixedWidth(self.BUBBLE_WIDTH - 58)
        self.subtitle.setWordWrap(False)

        text_box.addWidget(self.title)
        text_box.addWidget(self.subtitle)

        self.activity = QLabel("◌")
        self.activity.setObjectName("MiniBubbleActivity")
        self.activity.setFixedWidth(24)
        self.activity.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addLayout(text_box, 1)
        card_layout.addWidget(self.activity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.card)

        self.setFixedWidth(self.BUBBLE_WIDTH)
        self.hide()

    def showEvent(self, event):
        super().showEvent(event)
        disable_windows_backdrop(self)

    def update_notification(self, title: str, subtitle: str, visible: bool) -> None:
        title = title.strip()
        subtitle = subtitle.strip()
        if len(title) > 44:
            title = title[:41].rstrip() + "…"
        if len(subtitle) > 78:
            subtitle = subtitle[:75].rstrip() + "…"
        self.title.setText(title)
        self.subtitle.setText(subtitle)
        self.setVisible(visible and bool(title))
        self.adjustSize()

    def mouseDoubleClickEvent(self, event):
        self.controller.show_full()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.controller.show_context_menu(QCursor.pos())


class CompactWindow(QObject):
    def __init__(self, controller: "CompanionController"):
        super().__init__()
        self.controller = controller
        self.sprite = MiniSpriteWindow(controller)
        self.bubble = MiniBubbleWindow(controller)

    def show(self) -> None:
        self.sprite.show()
        disable_windows_backdrop(self.sprite)
        self.sprite.raise_()
        self.follow_sprite()
        if self.bubble.isVisible():
            self.bubble.show()
            disable_windows_backdrop(self.bubble)
            self.bubble.raise_()

    def hide(self) -> None:
        self.sprite.hide()
        self.bubble.hide()

    def isVisible(self) -> bool:
        return self.sprite.isVisible()

    def raise_(self) -> None:
        self.sprite.raise_()
        if self.bubble.isVisible():
            self.bubble.raise_()

    def setWindowFlag(self, flag, enabled: bool = True) -> None:
        self.sprite.setWindowFlag(flag, enabled)
        self.bubble.setWindowFlag(flag, enabled)

    def update_view(self, pixmap, pet_name: str, notification: str, show_bubble: bool = False, subtitle: str = ""):
        self.sprite.update_pixmap(pixmap)
        sprite_visible = self.sprite.isVisible()
        self.bubble.update_notification(notification, subtitle, show_bubble and sprite_visible)
        self.follow_sprite()
        if sprite_visible:
            self.sprite.show()
        else:
            self.bubble.hide()
        if sprite_visible and self.bubble.isVisible():
            self.bubble.show()
            disable_windows_backdrop(self.bubble)
            self.bubble.raise_()

    def follow_sprite(self) -> None:
        geo = self.sprite.frameGeometry()
        screen = QApplication.screenAt(geo.center()) or QApplication.primaryScreen()
        available = screen.availableGeometry() if screen is not None else None
        x = geo.x() + 18
        y = geo.y() + max(0, geo.height() - 10)

        if available is not None:
            if x + self.bubble.width() > available.right():
                x = max(available.left(), available.right() - self.bubble.width())
            if y + self.bubble.height() > available.bottom():
                y = max(available.top(), geo.y() - self.bubble.height() - 8)

        self.bubble.move(x, y)


class FullWindow(QMainWindow):
    def __init__(self, controller: "CompanionController"):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Codex Pet Companion")
        self.resize(900, 900)
        self.setMinimumSize(780, 820)

        root = QWidget()
        root.setObjectName("AppRoot")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(12)

        pet_column = QVBoxLayout()
        pet_column.setSpacing(8)

        pet_header = QGridLayout()
        pet_header.setContentsMargins(0, 0, 0, 0)
        pet_header.setHorizontalSpacing(8)

        self.header_spacer = QWidget()
        self.header_spacer.setFixedWidth(38)
        pet_header.addWidget(self.header_spacer, 0, 0)

        self.title = QLabel("Pet")
        self.title.setObjectName("Title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pet_header.addWidget(self.title, 0, 1)

        self.mini_button = QToolButton()
        self.mini_button.setText("🐾")
        self.mini_button.setToolTip("Mini mode")
        self.mini_button.clicked.connect(self.controller.show_compact)
        self.mini_button.setFixedWidth(38)
        pet_header.addWidget(self.mini_button, 0, 2, Qt.AlignmentFlag.AlignRight)
        pet_header.setColumnStretch(1, 1)
        pet_column.addLayout(pet_header)

        self.relationship = QLabel("")
        self.relationship.setObjectName("Relationship")
        self.relationship.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.relationship.setWordWrap(False)
        pet_column.addWidget(self.relationship)

        self.sprite_card = PetBackdropFrame()
        sprite_card = self.sprite_card
        sprite_layout = QVBoxLayout(sprite_card)
        sprite_layout.setContentsMargins(16, 12, 16, 14)
        sprite_layout.setSpacing(0)

        self.pet = ClickableSpriteLabel()
        self.pet.setFixedSize(300, 320)
        self.pet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.pet.setObjectName("PetSprite")
        self.pet.setToolTip("Click to pet")
        self.pet.clicked_callback = lambda: self.controller.do_action("pet")
        sprite_layout.addWidget(self.pet, 0, Qt.AlignmentFlag.AlignCenter)

        pet_buttons = QHBoxLayout()
        pet_buttons.setSpacing(8)
        icons_dir = Path(__file__).resolve().parents[2] / "icons"
        for label, action in [("Feed", "feed"), ("Play", "play"), ("Rest", "rest")]:
            button = PngActionButton(label, icons_dir / f"{action}.png")
            button.clicked.connect(lambda _=False, a=action: self.controller.do_action(a))
            pet_buttons.addWidget(button)
        pet_column.addWidget(sprite_card)
        pet_column.addLayout(pet_buttons)
        top.addLayout(pet_column)

        side_card = QFrame()
        side_card.setObjectName("Card")
        side = QVBoxLayout(side_card)
        side.setContentsMargins(14, 14, 14, 14)
        side.setSpacing(7)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setObjectName("StatusLine")

        self.codex = QLabel("")
        self.codex.setWordWrap(True)
        self.codex.setObjectName("CodexLine")

        self.state = QLabel("")
        self.state.setObjectName("StateLine")
        self.state.setWordWrap(True)

        side.addWidget(self.status)
        side.addSpacing(2)
        side.addWidget(self.codex)
        side.addSpacing(2)
        side.addWidget(self.state)
        side.addSpacing(3)
        side.addWidget(soft_divider())
        side.addSpacing(3)

        self.stats = {
            "hunger": StatRow("Fullness", app_icon_path("fullness")),
            "mood": StatRow("Mood", app_icon_path("mood")),
            "energy": StatRow("Energy", app_icon_path("energy")),
            "focus": StatRow("Focus", app_icon_path("focus")),
        }
        for row in self.stats.values():
            side.addWidget(row)

        side.addSpacing(3)
        side.addWidget(soft_divider())
        side.addSpacing(3)
        self.activity_card = InfoCard("Today's activity")
        self.activity_card.setMinimumHeight(92)
        side.addWidget(self.activity_card)

        top.addWidget(side_card, 1)
        layout.addLayout(top)

        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(440)
        self.tabs.setIconSize(QSize(20, 20))

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.pet_tab = QWidget()
        self.build_pet_tab()

        self.codex_tab = QWidget()
        self.build_codex_tab()

        self.settings = QWidget()
        self.build_settings()

        self.tabs.addTab(self.log, icon_for("general"), "General")
        self.tabs.addTab(self.pet_tab, icon_for("pet"), "Pet")
        self.tabs.addTab(self.codex_tab, icon_for("codex"), "Codex")
        self.tabs.addTab(self.settings, icon_for("settings"), "Settings")

        layout.addWidget(self.tabs, 1)

    def build_pet_tab(self):
        layout = QVBoxLayout(self.pet_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        top_cards = QHBoxLayout()
        top_cards.setSpacing(10)

        self.today_care_card = InfoCard("Today")
        self.today_hint_card = InfoCard("Hint")

        top_cards.addWidget(self.today_care_card, 2)
        top_cards.addWidget(self.today_hint_card, 3)
        layout.addLayout(top_cards)

        self.pet_history_panel = TextPanel("Pet history")
        layout.addWidget(self.pet_history_panel, 1)

    def build_codex_tab(self):
        layout = QVBoxLayout(self.codex_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.codex_error_card = InfoCard("Last error")
        layout.addWidget(self.codex_error_card)

        self.codex_history_panel = TextPanel("Codex events")
        self.codex_history_panel.text.setPlaceholderText("No Codex events yet.")
        layout.addWidget(self.codex_history_panel, 1)

    def closeEvent(self, event):
        if bool(self.controller._really_quitting):
            event.accept()
            return
        event.ignore()
        self.controller.quit()

    def build_settings(self):
        layout = QVBoxLayout(self.settings)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 2)
        grid.setColumnStretch(4, 0)

        # Row 1: Startup [dropdown]        [x] Mini stays on top
        grid.addWidget(QLabel("Startup:"), 0, 0)
        self.start_mode_combo = QComboBox()
        self.start_mode_combo.addItem("Full window", "full")
        self.start_mode_combo.addItem("Mini mode", "compact")
        self.start_mode_combo.setMinimumWidth(170)
        grid.addWidget(self.start_mode_combo, 0, 1)

        self.always_top_check = QCheckBox("Mini stays on top")
        self.always_top_check.setToolTip("Keep the mini pet above other windows.")
        grid.addWidget(self.always_top_check, 0, 2, 1, 3, Qt.AlignmentFlag.AlignLeft)

        # Row 2: Care mode [dropdown wide]  Hint: ...
        grid.addWidget(QLabel("Care mode:"), 1, 0)
        self.care_mode_combo = QComboBox()
        self.care_mode_combo.addItem("Soft", "soft")
        self.care_mode_combo.addItem("Normal", "normal")
        self.care_mode_combo.addItem("Strict", "strict")
        self.care_mode_combo.setMinimumWidth(170)
        grid.addWidget(self.care_mode_combo, 1, 1)

        self.care_mode_hint = QLabel("Soft is more relaxed. Strict needs attention more often.")
        self.care_mode_hint.setObjectName("Muted")
        self.care_mode_hint.setWordWrap(True)
        grid.addWidget(self.care_mode_hint, 1, 2, 1, 3)

        # Row 3: Pet [dropdown]  Display name [input]
        grid.addWidget(QLabel("Pet:"), 2, 0)
        self.pet_combo = QComboBox()
        self.pet_combo.setMinimumWidth(170)
        grid.addWidget(self.pet_combo, 2, 1)

        grid.addWidget(QLabel("Display name:"), 2, 2)
        self.custom_name = QLineEdit()
        self.custom_name.setPlaceholderText("Display name")
        grid.addWidget(self.custom_name, 2, 3, 1, 2)

        # Row 4: Mini size [dropdown]
        grid.addWidget(QLabel("Mini size:"), 3, 0)
        self.compact_size_combo = QComboBox()
        self.compact_size_combo.addItem("Small", 0.38)
        self.compact_size_combo.addItem("Normal", 0.50)
        self.compact_size_combo.addItem("Large", 0.65)
        self.compact_size_combo.setMinimumWidth(170)
        grid.addWidget(self.compact_size_combo, 3, 1)

        # Row 5: Codex sources: [path/info] [Choose]
        grid.addWidget(QLabel("Codex sources:"), 4, 0)
        self.path_info_codex = QLabel("not found")
        self.path_info_codex.setObjectName("Muted")
        self.path_info_codex.setWordWrap(True)
        grid.addWidget(self.path_info_codex, 4, 1, 1, 3)

        choose_codex = QPushButton("Choose")
        choose_codex.setObjectName("Secondary")
        choose_codex.setFixedWidth(112)
        choose_codex.clicked.connect(self.controller.choose_codex_home)
        grid.addWidget(choose_codex, 4, 4, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(grid)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(6)

        apply = QPushButton("Apply settings")
        apply.setMinimumWidth(154)
        apply.clicked.connect(self.controller.apply_settings_from_ui)

        reset_ui = QPushButton("Reset UI")
        reset_ui.setObjectName("Secondary")
        reset_ui.setMinimumWidth(124)
        reset_ui.clicked.connect(self.controller.reset_ui_settings)

        reset_state = QPushButton("Reset state")
        reset_state.setObjectName("Danger")
        reset_state.setMinimumWidth(132)
        reset_state.clicked.connect(self.controller.reset_state)

        buttons_row.addWidget(apply, 2)
        buttons_row.addWidget(reset_ui, 1)
        buttons_row.addWidget(reset_state, 1)
        layout.addLayout(buttons_row)

        file_buttons = QHBoxLayout()
        file_buttons.setSpacing(6)
        imp = QPushButton("Import / adopt pet")
        imp.setObjectName("AccentButton")
        add_button_icon(imp, "pet", 178)
        exp = QPushButton("Export / share pet")
        exp.setObjectName("AccentButton")
        add_button_icon(exp, "pet", 178)
        refresh = QPushButton("Refresh pets")
        refresh.setObjectName("Secondary")
        refresh.setMinimumWidth(142)
        refresh.clicked.connect(self.controller.reload_pets)

        for button in [imp, exp, refresh]:
            file_buttons.addWidget(button)

        imp.clicked.connect(self.controller.import_pet_pack)
        exp.clicked.connect(self.controller.export_pet_pack)
        layout.addLayout(file_buttons)

        updates_row = QHBoxLayout()
        updates_row.setSpacing(6)
        updates_row.addWidget(QLabel("Updates:"))
        self.check_updates = QPushButton("Check now")
        self.check_updates.setObjectName("Secondary")
        self.check_updates.setMinimumWidth(126)
        self.check_updates.clicked.connect(lambda: self.controller.check_updates(manual=True))
        self.auto_update_check = QCheckBox("Check automatically")
        updates_row.addWidget(self.check_updates)
        updates_row.addWidget(self.auto_update_check)
        updates_row.addStretch(1)
        layout.addLayout(updates_row)

        self.version_label = QLabel(f"Version {APP_VERSION}")
        self.version_label.setObjectName("Muted")
        layout.addWidget(self.version_label)
        layout.addStretch(1)

    def set_text_if_changed(self, box: QTextEdit, text: str) -> None:
        if box.toPlainText() == text:
            return
        bar = box.verticalScrollBar()
        old_value = bar.value()
        old_max = bar.maximum()
        cursor = box.textCursor()
        anchor = cursor.anchor()
        position = cursor.position()
        box.setPlainText(text)
        new_max = bar.maximum()
        if old_max > 0:
            ratio = old_value / old_max
            bar.setValue(round(new_max * ratio))
        else:
            bar.setValue(0)
        if position >= 0:
            cursor = box.textCursor()
            max_pos = len(box.toPlainText())
            cursor.setPosition(min(position, max_pos))
            if anchor != position:
                cursor.setPosition(min(anchor, max_pos), QTextCursor.MoveMode.KeepAnchor)
            box.setTextCursor(cursor)

    def format_relationship_line(self, text: str) -> str:
        # Give the relationship line a little more presence without changing the saved state text.
        return str(text or "").replace("♡", "♡ ")

    def update_view(self, pixmap, data: dict[str, Any]):
        self.sprite_card.set_background_path(str(data.get("pet_background_path") or ""))
        self.pet.setPixmap(pixmap)
        self.title.setText(data["pet_name"])
        self.status.setText(data["status"])
        self.codex.setText(data["codex"])
        self.state.setText(data["state"])
        for key, row in self.stats.items():
            row.set_value(data[key])
        self.relationship.setText(self.format_relationship_line(data["level"]))
        self.relationship.setToolTip(data["level"])
        self.activity_card.set_value(data["activity"])

        self.set_text_if_changed(self.log, "\n".join(data["log"]))
        self.today_care_card.set_value(data["today_care"])
        self.today_hint_card.set_value(data["today_hint"])
        self.set_text_if_changed(self.pet_history_panel.text, "\n".join(data["history"]))

        self.codex_error_card.set_value(data["codex_last_error"])
        self.set_text_if_changed(self.codex_history_panel.text, "\n".join(data["codex_log"]))


class CompanionController:
    def __init__(self, app: QApplication):
        self.app = app
        self.config = load_config()
        self.codex_home = resolve_codex_home(self.config)
        self.state_dir = resolve_state_dir(self.config, self.codex_home)
        self.state_path = self.state_dir / "state.json"
        self.state = load_state(self.state_path)
        self.state["codex_status"] = "idle"
        self.state["codex_last_event"] = ""
        self.state["codex_last_note"] = ""
        self.state["codex_last_time"] = 0
        self.state["codex_status_until"] = 0
        self.state["codex_notification"] = ""
        self.state["codex_notification_title"] = ""
        self.state["codex_notification_subtitle"] = ""
        self.state["codex_notification_until"] = 0
        self.state["codex_detection_status"] = "checking"
        self.state["codex_active_source_label"] = ""
        self.state["codex_active_session_file"] = ""
        self.state["codex_active_session_count"] = 0
        self.state["codex_active_source_kind"] = "none"
        self.state["codex_active_codex_home"] = ""
        self.state["codex_found_source_labels"] = []
        if self.config.get("clearLogsOnStart", True):
            clear_runtime_logs(self.state)
        else:
            self.state["codex_status"] = "idle"
            self.state["codex_last_event"] = ""
            self.state["codex_last_note"] = ""
            self.state["codex_last_time"] = 0
        self.pets = discover_pets(self.codex_home)
        self.current_pet = self.resolve_pet()
        ensure_bond_state(self.state, self.current_pet.id)
        self.trait_key = pet_trait_key(self.current_pet)
        self.ensure_activity_state()
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 1.0)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.frame_index = 0
        self.anim_name = "idle"
        self.next_frame_at = 0.0
        self.compact_dragging = False
        self.compact_drag_animation = "running"
        self.queue: Queue = Queue()
        self._really_quitting = False
        self._update_check_running = False
        self._download_running = False
        self._pending_update_info: UpdateInfo | None = None
        self.bridge = CodexBridge(self.codex_home, self.config, self.queue)
        self.bridge.start()

        self.compact = CompactWindow(self)
        self.full = FullWindow(self)
        self.full.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.full.setWindowOpacity(1.0)
        self.reload_pet_combo()

        self.tray = None
        if bool(self.config.get("enableTray", False)):
            self.tray = QSystemTrayIcon(self.app)
            self.tray.setIcon(QIcon(self.compact_frames.get("idle", 0)))
            self.tray.setToolTip("Codex Pet Companion")
            self.tray.activated.connect(lambda reason: self.show_full() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
            self.tray.setContextMenu(self.context_menu())
            self.tray.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)
        QTimer.singleShot(1200, self.maybe_check_updates_on_startup)

    def start(self):
        mode = str(self.config.get("startMode") or "full").lower()
        if mode == "compact":
            self.show_compact()
        else:
            self.show_full()

    def context_menu(self) -> QMenu:
        menu = QMenu()
        open_action = QAction("Open")
        compact_action = QAction("Mini mode")
        refresh_action = QAction("Refresh pets")
        quit_action = QAction("Quit")
        open_action.triggered.connect(self.show_full)
        compact_action.triggered.connect(self.show_compact)
        refresh_action.triggered.connect(self.reload_pets)
        quit_action.triggered.connect(self.quit)
        menu.addAction(open_action)
        menu.addAction(compact_action)
        menu.addAction(refresh_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        return menu

    def show_context_menu(self, pos):
        self.context_menu().exec(pos)

    def resolve_pet(self) -> PetInfo:
        selected = str(self.config.get("selectedPetId") or "lumisprout")
        for pet in self.pets:
            if pet.id == selected:
                return pet
        return self.pets[0]

    def pet_name(self) -> str:
        return str(self.config.get("customDisplayName") or "").strip() or self.current_pet.display_name

    def show_full(self):
        self.compact.hide()
        self.full.show()
        self.full.raise_()
        self.full.activateWindow()

    def show_compact(self):
        self.full.hide()
        self.compact.show()
        self.compact.raise_()

    def follow_compact_sprite(self):
        self.compact.follow_sprite()

    def begin_compact_drag(self):
        self.compact_dragging = True
        self.compact_drag_animation = "running"
        self.force_animation("running")
        self.advance_animation_frame()
        self.refresh_compact_sprite_only()

    def update_compact_drag_direction(self, dx: int):
        if not self.compact_dragging:
            return
        if dx > 1:
            self.compact_drag_animation = "running-right"
        elif dx < -1:
            self.compact_drag_animation = "running-left"
        elif self.compact_drag_animation not in STATES:
            self.compact_drag_animation = "running"
        self.force_animation(self.compact_drag_animation)
        self.advance_animation_frame()
        self.refresh_compact_sprite_only()

    def end_compact_drag(self):
        self.compact_dragging = False
        self.compact_drag_animation = "running"
        wanted = self.current_animation()
        self.force_animation(wanted)

    def advance_animation_frame(self):
        if self.anim_name not in STATES:
            return
        row, durations = STATES[self.anim_name]
        t = now() * 1000
        if self.next_frame_at <= 0:
            self.frame_index = 0
            self.next_frame_at = t + durations[self.frame_index]
        elif t >= self.next_frame_at:
            self.frame_index = (self.frame_index + 1) % len(durations)
            self.next_frame_at = t + durations[self.frame_index]

    def force_animation(self, animation: str):
        if animation not in STATES:
            return
        if animation != self.anim_name:
            self.anim_name = animation
            self.frame_index = 0
            self.next_frame_at = 0

    def quit(self):
        self._really_quitting = True
        if hasattr(self, "timer"):
            self.timer.stop()
        self.bridge.stop()
        if self.bridge.is_alive():
            self.bridge.join(timeout=1.0)
        save_state(self.state_path, self.state)
        if self.tray is not None:
            self.tray.hide()
        self.compact.hide()
        self.full.hide()
        self.app.quit()

    def add_bridge_debug(self, message: str) -> None:
        if not bool(self.config.get("debugBridge", False)):
            return
        log = self.state.get("bridge_debug_log")
        if not isinstance(log, list):
            log = []
            self.state["bridge_debug_log"] = log
        log.insert(0, f"{int(now())}: {message}")
        max_lines = int(self.config.get("debugBridgeMaxLines", 160) or 160)
        del log[max_lines:]
        codex_log = self.state.get("codex_log")
        if isinstance(codex_log, list):
            codex_log.insert(0, f"bridge: {message}")
            del codex_log[max_lines:]

    def apply_bridge_source_metadata(self, event: dict[str, Any]) -> None:
        keys = (
            "codex_detection_status",
            "codex_active_source_label",
            "codex_active_session_file",
            "codex_active_session_count",
            "codex_active_source_kind",
            "codex_active_codex_home",
            "codex_found_source_labels",
        )
        for key in keys:
            if key in event:
                self.state[key] = event.get(key)

    def do_action(
        self,
        action: str,
        note: str = "",
        session_file: str = "",
        notification_title: str = "",
        notification_subtitle: str = "",
        task_title: str = "",
    ):
        self.state = decayed(self.state, self.config, self.trait_key)
        apply_action(
            self.state,
            action,
            note,
            self.pet_name(),
            self.current_pet.id,
            self.trait_key,
            session_file or getattr(self.bridge, "active_session_file", ""),
            self.config,
        )
        if task_title:
            self.state["codex_current_task_title"] = task_title
        if notification_title:
            self.state["codex_notification_title"] = notification_title
            self.state["codex_notification"] = notification_title
        if notification_subtitle:
            self.state["codex_notification_subtitle"] = notification_subtitle
        self.add_bridge_debug(f"applied event: {action} note={note}")
        save_state(self.state_path, self.state)
        self.refresh()

    def process_queue(self):
        action_map = {
            "codex": "codex_running",
            "function_call": "codex_running",
            "task_started": "codex_running",
            "review": "review_ready",
            "final_answer": "review_ready",
            "fail": "error",
            "failed": "error",
            "codex_error": "error",
        }
        while True:
            try:
                event = self.queue.get_nowait()
            except Empty:
                break
            action = str(event.get("action") or "")
            if action == "__bridge_debug__":
                self.add_bridge_debug(str(event.get("note") or ""))
                continue
            if action == "__bridge_source__":
                self.apply_bridge_source_metadata(event)
                continue
            if action == "__update_check_result__":
                self.handle_update_check_result(event)
                continue
            if action == "__update_download_result__":
                self.handle_update_download_result(event)
                continue
            action = action_map.get(action, action)
            self.add_bridge_debug(
                f"queue received: {action} title={event.get('notification_title') or ''} subtitle={event.get('notification_subtitle') or ''}"
            )
            self.apply_bridge_source_metadata(event)
            self.do_action(
                action,
                str(event.get("note") or ""),
                str(event.get("session_file") or ""),
                str(event.get("notification_title") or ""),
                str(event.get("notification_subtitle") or ""),
                str(event.get("task_title") or ""),
            )

    def current_animation(self) -> str:
        if self.compact_dragging and self.compact_drag_animation in STATES:
            return self.compact_drag_animation

        current_time = now()
        if float(self.state.get("event_until", 0) or 0) > current_time and str(self.state.get("current_event") or "") in STATES:
            return str(self.state["current_event"])

        if int(self.state.get("hunger", 0)) < 20 or int(self.state.get("mood", 0)) < 18:
            return "failed"

        # Quiet desktop mode should be calm. High focus is a stat, not a reason to
        # bounce forever after Codex has gone quiet.
        codex_status = str(self.state.get("codex_status") or "idle")
        codex_fresh = float(self.state.get("codex_status_until", 0) or 0) > current_time
        if codex_fresh and codex_status == "running":
            return "review"
        if codex_fresh and codex_status == "review":
            return "review"
        if codex_fresh and codex_status == "error":
            return "failed"

        if int(self.state.get("energy", 0)) < 25:
            return "waiting"
        return "idle"

    def status_text(self) -> str:
        if float(self.state.get("event_until", 0) or 0) > now() and self.state.get("event_status"):
            return str(self.state["event_status"])
        name = self.pet_name()
        if self.codex_home is None and getattr(self.bridge, "active_codex_home", None) is None:
            return "Codex folder not found. Open settings."
        icon, label = care_state(self.state)
        if label == "Hungry":
            return f"{name} wants food, politely."
        if label == "Tired":
            return f"{name} is saving battery."
        if label == "Grumpy":
            return f"{name} is offended by the quality of reality."
        return f"{name} is waiting for the next strange task."

    def today_record(self) -> dict[str, Any]:
        records = self.state.get("daily_care")
        if not isinstance(records, dict):
            return {}
        record = records.get(today_key())
        return record if isinstance(record, dict) else {}

    def today_care_text(self) -> str:
        record = self.today_record()
        return (
            f"Food {int(record.get('feed', 0) or 0)} · "
            f"Care {int(record.get('pet', 0) or 0)} · "
            f"Play {int(record.get('play', 0) or 0)} · "
            f"Rest {int(record.get('rest', 0) or 0)}"
        )


    def today_hint_text(self) -> str:
        def stable_hint(key: str) -> str:
            scoped_key = f"{self.current_pet.id}:{key}"
            if self.state.get("last_hint_key") == scoped_key and self.state.get("last_hint_text"):
                return str(self.state["last_hint_text"])
            text = hint_line(self.current_pet.id, key, self.state)
            self.state["last_hint_key"] = scoped_key
            self.state["last_hint_text"] = text
            return text

        hunger = float(self.state.get("hunger", 50) or 0)
        mood = float(self.state.get("mood", 50) or 0)
        energy = float(self.state.get("energy", 50) or 0)
        focus = float(self.state.get("focus", 50) or 0)
        flags = self.state.get("recovery_flags") if isinstance(self.state.get("recovery_flags"), dict) else {}

        if bool(flags.get("hunger", False)):
            return stable_hint("recovery_hunger")
        if bool(flags.get("energy", False)):
            return stable_hint("recovery_energy")
        if bool(flags.get("mood", False)):
            return stable_hint("recovery_mood")
        if bool(flags.get("focus", False)):
            return stable_hint("recovery_focus")
        record = self.today_record()
        fed_today = int(record.get("feed", 0) or 0) > 0
        rested_today = int(record.get("rest", 0) or 0) > 0

        if hunger < 30:
            return stable_hint("low_hunger")
        if not fed_today and hunger < 70:
            return stable_hint("not_fed_today")
        if energy < 30:
            return stable_hint("low_energy")
        if not rested_today and energy < 58:
            return stable_hint("no_rest_today")
        if mood < 35:
            return stable_hint("low_mood")
        if focus < 25:
            return stable_hint("low_focus")
        return stable_hint("ok")

    def ensure_activity_state(self) -> None:
        _ensure_activity_state(self.state, self.current_pet.id, str(self.state.get("codex_status") or "idle"))

    def activity_text(self) -> str:
        return _activity_text(self.state, self.current_pet.id, self.pet_name())

    def view_data(self) -> dict[str, Any]:
        ensure_bond_state(self.state, self.current_pet.id)
        icon, label = care_state(self.state)
        bond_line = friendship_progress_line(self.state, self.current_pet.id)
        bond_title = friendship_title(self.state, self.current_pet.id)
        days = days_together(self.state)
        codex_counters = self.state.get("codex_counters") if isinstance(self.state.get("codex_counters"), dict) else {}
        codex_status = str(self.state.get("codex_status") or "idle")
        codex_last_event = str(self.state.get("codex_last_event") or "—")
        codex_last_note = str(self.state.get("codex_last_note") or "").strip()
        codex_last_time = float(self.state.get("codex_last_time") or 0)
        codex_age = int(max(0, now() - codex_last_time)) if codex_last_time else 0

        event_names = {
            "final_answer": "ready to review",
            "task_started": "task started",
            "function_call": "working",
            "error": "error",
            "long_silence": "quiet for a while",
        }
        status_names = {
            "idle": "calm",
            "running": "working",
            "review": "review ready",
            "error": "error",
            "waiting": "maybe waiting",
        }
        care_names = {
            "soft": "Soft",
            "normal": "Normal",
            "strict": "Strict",
        }

        history = history_lines(self.state)
        data_hearts = "♡♡♡♡♡"
        bond_parts = bond_line.split("\n")
        if len(bond_parts) > 1:
            data_hearts = bond_parts[1].strip() or data_hearts
        if days == 1:
            days_together_text = "1 day together"
        else:
            days_together_text = f"{days} days together"
        pet_recent = "Quiet for now."
        for line in history:
            stripped = str(line).strip()
            if stripped and not stripped.startswith("20"):
                pet_recent = stripped
                break

        last_error = "No errors yet."
        for line in list(self.state.get("codex_log", [])):
            low = str(line).lower()
            if "error" in low or "failed" in low:
                last_error = str(line)
                break

        codex_counts = (
            f"Events: {codex_counters.get('events', 0)}\n"
            f"Tasks: {codex_counters.get('task_started', 0)}\n"
            f"Tools: {codex_counters.get('function_call', 0)}\n"
            f"Errors: {codex_counters.get('error', 0)}"
        )
        codex_last = "No activity."
        if codex_last_time:
            codex_last = f"{event_names.get(codex_last_event, codex_last_event)} · {codex_age}s ago"
            if codex_last_note:
                codex_last += f"\n{codex_last_note}"

        return {
            "pet_name": self.pet_name(),
            "pet_background_path": str(self.current_pet.background_path or ""),
            "status": self.status_text(),
            "codex": codex_status_line(self.state),
            "compact_notification": str(self.state.get("codex_notification_title") or self.state.get("codex_notification") or self.state.get("event_status") or ""),
            "compact_notification_subtitle": str(self.state.get("codex_notification_subtitle") or ""),
            "codex_short": codex_short_line(self.state),
            "state": f"{icon} {label}",
            "level": f"{bond_title} · {data_hearts} · {days_together_text}",
            "friendship": bond_line,
            "friendship_title": bond_title,
            "days_together": f"{days} d.",
            "care_mode": care_names.get(str(self.config.get("careMode") or "normal"), "Normal"),
            "pet_recent": pet_recent,
            "today_care": self.today_care_text(),
            "today_hint": self.today_hint_text(),
            "activity": self.activity_text(),
            "hunger": round(float(self.state.get("hunger", 0) or 0)),
            "mood": round(float(self.state.get("mood", 0) or 0)),
            "energy": round(float(self.state.get("energy", 0) or 0)),
            "focus": round(float(self.state.get("focus", 0) or 0)),
            "log": list(self.state.get("log", []))[:80],
            "codex_log": list(self.state.get("codex_log", []))[:80],
            "codex_session": codex_session_lines(self.state),
            "history": history,
            "codex_status_short": status_names.get(codex_status, codex_status),
            "codex_last": codex_last,
            "codex_last_error": last_error,
            "codex_counts": codex_counts,
        }

    def tick(self):
        self.process_queue()
        self.state = decayed(self.state, self.config, self.trait_key)
        maybe_mark_codex_silence(self.state, self.config)
        self.ensure_activity_state()

        wanted = self.current_animation()
        self.force_animation(wanted)

        self.advance_animation_frame()
        t = now() * 1000

        self.refresh()
        if int(t) % 15000 < 140:
            save_state(self.state_path, self.state)

    def should_show_compact_bubble(self) -> bool:
        return now() < float(self.state.get("codex_notification_until", 0.0) or 0.0)

    def refresh_compact_sprite_only(self):
        pixmap = self.compact_frames.get(self.anim_name, self.frame_index)
        data = self.view_data()
        self.compact.update_view(
            pixmap,
            data["pet_name"],
            data.get("compact_notification", str(self.state.get("codex_notification") or self.state.get("event_status") or "")),
            self.should_show_compact_bubble(),
            data.get("compact_notification_subtitle", ""),
        )

    def refresh(self):
        compact_pixmap = self.compact_frames.get(self.anim_name, self.frame_index)
        full_pixmap = self.full_frames.get(self.anim_name, self.frame_index)
        data = self.view_data()
        self.compact.update_view(
            compact_pixmap,
            data["pet_name"],
            data.get("compact_notification", str(self.state.get("codex_notification") or self.state.get("event_status") or "")),
            self.should_show_compact_bubble(),
            data.get("compact_notification_subtitle", ""),
        )
        self.full.update_view(full_pixmap, data)
        self.full.path_info_codex.setText(self.codex_source_label())
        if self.tray is not None:
            self.tray.setToolTip(f"{data['pet_name']} — {data['codex']}")

    def set_combo_value(self, combo: QComboBox, value):
        for index in range(combo.count()):
            if combo.itemData(index) == value:
                combo.setCurrentIndex(index)
                return
        try:
            wanted = float(value)
            for index in range(combo.count()):
                try:
                    if abs(float(combo.itemData(index)) - wanted) < 0.001:
                        combo.setCurrentIndex(index)
                        return
                except Exception:
                    pass
        except Exception:
            pass

    def reload_pet_combo(self):
        self.full.pet_combo.blockSignals(True)
        self.full.pet_combo.clear()
        for pet in self.pets:
            self.full.pet_combo.addItem(pet.label, pet.id)
            if pet.id == self.current_pet.id:
                self.full.pet_combo.setCurrentIndex(self.full.pet_combo.count() - 1)
        self.full.pet_combo.blockSignals(False)

        self.full.custom_name.setText(str(self.config.get("customDisplayName") or ""))

        start_mode = str(self.config.get("startMode") or "full")
        if start_mode == "tray":
            start_mode = "full"
        self.set_combo_value(self.full.start_mode_combo, start_mode)
        self.set_combo_value(self.full.compact_size_combo, compact_scale_value(self.config.get("compactScale", 0.50)))

        self.full.always_top_check.setChecked(bool(self.config.get("miniAlwaysOnTop", True)))
        self.full.auto_update_check.setChecked(bool(self.config.get("checkUpdatesOnStartup", True)))
        self.set_combo_value(self.full.care_mode_combo, str(self.config.get("careMode") or "normal"))

        self.full.path_info_codex.setText(self.codex_source_label())

    def codex_source_label(self) -> str:
        active = getattr(self.bridge, "active_codex_home", None)
        state_label = str(self.state.get("codex_active_source_label") or "").strip()
        detection = str(self.state.get("codex_detection_status") or "").strip()
        configured = str(self.config.get("codexHome") or "auto").strip()
        custom = configured and configured.lower() != "auto"
        active_label = state_label if state_label and state_label != "not found" else ""
        found = self.state.get("codex_found_source_labels")
        if not isinstance(found, list):
            found = []
        found_labels = [str(label).strip() for label in found if str(label).strip()]
        if active is not None:
            active_path = Path(active)
            active_label = active_label or self.codex_source_name(active_path)
        elif self.codex_home is not None and detection != "checking":
            active_label = active_label or self.codex_source_name(self.codex_home)
        if detection == "checking":
            active_text = "looking for sessions..."
            found_text = "checking"
        else:
            active_text = active_label or "not found"
            if not found_labels and active_label:
                found_labels = [active_label]
            found_text = ", ".join(found_labels) if found_labels else "none"
        if custom:
            custom_text = configured
        else:
            custom_text = "not set"
        return f"Active: {active_text}\nFound: {found_text}\nCustom: {custom_text}"

    def codex_source_name(path: Path) -> str:
        text = str(path)
        normalized = text.replace("/", "\\")
        lowered = normalized.lower()
        for prefix in ("\\\\wsl.localhost\\", "\\\\wsl$\\"):
            if lowered.startswith(prefix.lower()):
                rest = normalized[len(prefix):].split("\\")
                distro = rest[0] if rest and rest[0] else "WSL"
                return f"WSL {distro}"
        if sys.platform == "linux" and os.environ.get("WSL_DISTRO_NAME"):
            try:
                if path == Path.home() / ".codex":
                    return f"WSL {os.environ.get('WSL_DISTRO_NAME') or 'local'}"
            except Exception:
                pass
            if text.startswith("/mnt/c/Users/") or text.startswith("/mnt/c/users/"):
                return "Windows .codex"
        try:
            if sys.platform == "win32" and path.resolve() == (Path.home() / ".codex").resolve():
                return "Windows .codex"
        except Exception:
            pass
        return str(path)

    def apply_settings_from_ui(self):
        pet_id = self.full.pet_combo.currentData()
        self.config["selectedPetId"] = pet_id or "lumisprout"
        self.config["customDisplayName"] = self.full.custom_name.text().strip()
        self.config["startMode"] = self.full.start_mode_combo.currentData() or "full"
        if self.config["startMode"] == "tray":
            self.config["startMode"] = "full"
        self.config["compactScale"] = compact_scale_value(self.full.compact_size_combo.currentData() or 0.50)
        self.config["miniAlwaysOnTop"] = bool(self.full.always_top_check.isChecked())
        self.config["checkUpdatesOnStartup"] = bool(self.full.auto_update_check.isChecked())
        self.config["windowOpacity"] = 1.0
        self.config["careMode"] = self.full.care_mode_combo.currentData() or "normal"
        # Advanced values are intentionally kept out of the normal UI.
        self.config["decayEnabled"] = True
        self.config["closeToCompact"] = False

        save_config(self.config)

        self.full.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.full.setWindowOpacity(1.0)
        self.compact.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(self.config.get("miniAlwaysOnTop", True)))
        if self.full.isVisible():
            self.full.show()
        if self.compact.isVisible():
            self.compact.show()

        self.pets = discover_pets(self.codex_home)
        self.current_pet = self.resolve_pet()
        self.trait_key = pet_trait_key(self.current_pet)
        self.ensure_activity_state()
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 1.0)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.reload_pet_combo()
        self.refresh()

    def reset_ui_settings(self):
        defaults = ui_default_config()
        selected_pet = self.config.get("selectedPetId", "lumisprout")
        codex_home = self.config.get("codexHome", "auto")
        state_dir = self.config.get("stateDir", "auto")
        self.config.update(defaults)
        self.config["selectedPetId"] = selected_pet
        self.config["codexHome"] = codex_home
        self.config["stateDir"] = state_dir
        self.config["enableTray"] = False
        self.config["closeToCompact"] = False
        self.config["checkUpdatesOnStartup"] = bool(self.config.get("checkUpdatesOnStartup", True))
        save_config(self.config)

        self.full.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.full.setWindowOpacity(1.0)
        self.compact.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(self.config.get("miniAlwaysOnTop", True)))
        if self.full.isVisible():
            self.full.show()
        if self.compact.isVisible():
            self.compact.show()

        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 1.0)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.reload_pet_combo()
        self.refresh()

    def reload_pets(self):
        self.pets = discover_pets(self.codex_home)
        self.current_pet = self.resolve_pet()
        self.trait_key = pet_trait_key(self.current_pet)
        self.ensure_activity_state()
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 1.0)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.reload_pet_combo()
        self.refresh()

    def choose_codex_home(self):
        selected = QFileDialog.getExistingDirectory(self.full, "Choose .codex folder")
        if not selected:
            return
        self.config["codexHome"] = selected.replace("\\", "/")
        save_config(self.config)
        self.codex_home = resolve_codex_home(self.config)
        self.state_dir = resolve_state_dir(self.config, self.codex_home)
        self.state_path = self.state_dir / "state.json"
        self.state = load_state(self.state_path)
        self.state["codex_status"] = "idle"
        self.state["codex_last_event"] = ""
        self.state["codex_last_note"] = ""
        self.state["codex_last_time"] = 0
        self.state["codex_status_until"] = 0
        self.state["codex_notification"] = ""
        self.state["codex_notification_title"] = ""
        self.state["codex_notification_subtitle"] = ""
        self.state["codex_notification_until"] = 0
        self.state["codex_detection_status"] = "checking"
        self.state["codex_active_source_label"] = ""
        self.state["codex_active_session_file"] = ""
        self.state["codex_active_session_count"] = 0
        self.state["codex_active_source_kind"] = "none"
        self.state["codex_active_codex_home"] = ""
        self.state["codex_found_source_labels"] = []
        self.bridge.stop()
        self.bridge = CodexBridge(self.codex_home, self.config, self.queue)
        self.bridge.start()
        self.reload_pets()

    def open_state_dir(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(self.state_dir))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{self.state_dir}"')
        else:
            os.system(f'xdg-open "{self.state_dir}"')

    def import_pet_pack(self):
        path, _ = QFileDialog.getOpenFileName(self.full, "Import / adopt pet", "", "Zip (*.zip)")
        if not path:
            return
        try:
            pet_id = import_pet_pack(Path(path), self.state_dir)
            self.config["selectedPetId"] = pet_id
            save_config(self.config)
            self.reload_pets()
        except Exception as exc:
            QMessageBox.critical(self.full, "Import / adopt pet", str(exc))

    def export_pet_pack(self):
        pet = self.current_pet
        if pet.folder is None:
            message = "Built-in pets already live here. Only custom pets can be exported as shareable packs."
            add_log(self.state, message)
            self.state["event_status"] = message
            self.state["current_event"] = "waving"
            self.state["event_until"] = now() + 4.0
            save_state(self.state_path, self.state)
            self.refresh()
            return
        path, _ = QFileDialog.getSaveFileName(self.full, "Export / share pet", f"{pet.id}_pet_pack.zip", "Zip (*.zip)")
        if not path:
            return
        try:
            export_pet_pack(pet.folder, pet.id, Path(path))
            add_log(self.state, f"Pet pack ready: {Path(path).name}")
            save_state(self.state_path, self.state)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self.full, "Export / share pet", str(exc))

    def maybe_check_updates_on_startup(self):
        if not bool(self.config.get("checkUpdatesOnStartup", True)):
            return
        try:
            last = float(self.config.get("lastUpdateCheck", 0) or 0)
        except (TypeError, ValueError):
            last = 0
        if now() - last < 24 * 60 * 60:
            return
        self.check_updates(manual=False)

    def check_updates(self, manual: bool = False):
        if self._update_check_running:
            if manual:
                QMessageBox.information(self.full, "Updates", "Update check is already running.")
            return
        self._update_check_running = True
        if manual:
            self.full.check_updates.setEnabled(False)
            self.full.check_updates.setText("Checking...")

        def worker():
            info = check_for_update(APP_VERSION)
            self.queue.put({
                "action": "__update_check_result__",
                "manual": manual,
                "info": info.to_dict(),
            })

        threading.Thread(target=worker, daemon=True).start()

    def handle_update_check_result(self, event: dict[str, Any]):
        self._update_check_running = False
        if hasattr(self.full, "check_updates"):
            self.full.check_updates.setEnabled(True)
            self.full.check_updates.setText("Check now")

        manual = bool(event.get("manual", False))
        raw = event.get("info") if isinstance(event.get("info"), dict) else {}
        info = UpdateInfo(**raw)
        if info.ok:
            self.config["lastUpdateCheck"] = now()
            save_config(self.config)

        if not info.ok:
            if manual:
                QMessageBox.warning(self.full, "Updates", f"Could not check for updates.\n\n{info.error}")
            return

        if not info.update_available:
            if manual:
                QMessageBox.information(self.full, "Updates", f"{APP_NAME_DISPLAY} is up to date.\n\nCurrent version: {APP_VERSION}")
            return

        ignored = str(self.config.get("ignoredUpdateVersion") or "")
        if not manual and ignored and ignored == info.latest_version:
            return
        self.show_update_dialog(info)

    def show_update_dialog(self, info: UpdateInfo):
        self._pending_update_info = info
        notes = (info.release_notes or "").strip()
        if len(notes) > 900:
            notes = notes[:900].rstrip() + "..."
        if not notes:
            notes = "No release notes provided."

        asset_line = f"\n\nAsset: {info.asset_name}" if info.asset_name else "\n\nNo installable Windows asset was found."
        message = (
            f"Version {info.latest_version} is available.\n\n"
            f"{notes}"
            f"{asset_line}"
        )
        box = QMessageBox(self.full)
        box.setWindowTitle("Update available")
        box.setText(message)
        install = box.addButton("Install update", QMessageBox.ButtonRole.AcceptRole)
        later = box.addButton("Later", QMessageBox.ButtonRole.RejectRole)
        skip = box.addButton("Skip this version", QMessageBox.ButtonRole.DestructiveRole)
        open_page = box.addButton("Open release page", QMessageBox.ButtonRole.ActionRole)
        if not info.install_available:
            install.setEnabled(False)
        box.exec()

        clicked = box.clickedButton()
        if clicked == install:
            self.install_update(info)
        elif clicked == skip:
            self.config["ignoredUpdateVersion"] = info.latest_version
            save_config(self.config)
        elif clicked == open_page:
            if info.release_url:
                QDesktopServices.openUrl(QUrl(info.release_url))
        else:
            _ = later

    def install_update(self, info: UpdateInfo):
        if self._download_running:
            QMessageBox.information(self.full, "Updates", "An update download is already running.")
            return
        if not info.install_available:
            if info.release_url:
                QDesktopServices.openUrl(QUrl(info.release_url))
            return
        updater = self.updater_exe_path()
        if not updater.exists():
            QMessageBox.warning(
                self.full,
                "Updates",
                f"updater.exe was not found next to the app.\n\nExpected:\n{updater}\n\nOpen the release page and download the update manually."
            )
            if info.release_url:
                QDesktopServices.openUrl(QUrl(info.release_url))
            return

        self._download_running = True
        if hasattr(self.full, "check_updates"):
            self.full.check_updates.setEnabled(False)
            self.full.check_updates.setText("Downloading...")

        def worker():
            try:
                target_dir = Path(tempfile.mkdtemp(prefix="codex-pet-update-"))
                package = download_update(info, target_dir)
                self.queue.put({
                    "action": "__update_download_result__",
                    "ok": True,
                    "package": str(package),
                    "latest_version": info.latest_version,
                })
            except Exception as exc:  # noqa: BLE001
                self.queue.put({
                    "action": "__update_download_result__",
                    "ok": False,
                    "error": str(exc),
                })

        threading.Thread(target=worker, daemon=True).start()

    def handle_update_download_result(self, event: dict[str, Any]):
        self._download_running = False
        if hasattr(self.full, "check_updates"):
            self.full.check_updates.setEnabled(True)
            self.full.check_updates.setText("Check now")

        if not bool(event.get("ok", False)):
            QMessageBox.warning(self.full, "Updates", f"Could not download update.\n\n{event.get('error') or 'Unknown error'}")
            return

        package = Path(str(event.get("package") or ""))
        updater = self.updater_exe_path()
        app_exe = self.app_exe_path()
        if not package.is_file() or not updater.exists() or not app_exe.exists():
            QMessageBox.warning(self.full, "Updates", "Downloaded update is not ready. Please try again.")
            return

        answer = QMessageBox.question(
            self.full,
            "Install update",
            "The update has been downloaded. Install it now?\n\nThe app will close and restart.",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            subprocess.Popen(
                [
                    str(updater),
                    "--app-exe",
                    str(app_exe),
                    "--package",
                    str(package),
                    "--restart",
                ],
                cwd=str(app_exe.parent),
                close_fds=False,
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self.full, "Updates", f"Could not start updater.\n\n{exc}")
            return

        self.quit()

    def app_exe_path(self) -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve()
        return Path(sys.argv[0]).resolve()

    def updater_exe_path(self) -> Path:
        base = self.app_exe_path().parent
        return base / ("updater.exe" if os.name == "nt" else "updater")

    def reset_state(self):
        if QMessageBox.question(self.full, "Reset", "Reset pet state?") != QMessageBox.StandardButton.Yes:
            return
        from codex_pet_companion.core.state import DEFAULT_STATE
        self.state = dict(DEFAULT_STATE)
        self.state["last_update"] = now()
        ensure_bond_state(self.state, self.current_pet.id)
        save_state(self.state_path, self.state)
        self.refresh()

def run_app():
    app = QApplication(sys.argv)
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)
    font = app.font()
    if font.pointSize() <= 0:
        font.setPointSize(10)
        app.setFont(font)

    config = load_config()
    guard = SingleInstanceGuard("codex_pet_companion_v11")
    if bool(config.get("singleInstance", True)) and not guard.acquire():
        print("Codex Pet Companion is already running.")
        return

    combo_arrow = str(app_icon_path("chevron-down.svg").resolve()).replace("\\", "/")
    app.setStyleSheet(STYLE.replace("__COMBO_ARROW__", combo_arrow))
    app.aboutToQuit.connect(guard.release)

    controller = CompanionController(app)
    if str(controller.config.get("startMode") or "full").lower() == "tray":
        controller.config["startMode"] = "full"
    controller.start()
    sys.exit(app.exec())
