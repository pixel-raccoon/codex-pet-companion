from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from queue import Queue, Empty
from typing import Any

from PySide6.QtCore import Qt, QTimer, QPoint, QObject, QEvent
from PySide6.QtGui import QAction, QColor, QCursor, QFont, QPainter, QPaintEvent, QPixmap, QRegion, QTextCursor
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QGridLayout, QMenu, QMessageBox, QPushButton, QTabWidget, QToolButton, QTextEdit, QVBoxLayout,
    QWidget, QSystemTrayIcon, QGroupBox, QFormLayout, QScrollArea, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon

from codex_pet_companion.core.bridge import CodexBridge
from codex_pet_companion.core.config import load_config, save_config, resolve_codex_home, resolve_state_dir, ui_default_config, data_dir
from codex_pet_companion.core.constants import ACHIEVEMENTS, STATES, TRAITS
from codex_pet_companion.core.pet_pack import export_pet_pack, import_pet_pack
from codex_pet_companion.core.pets import PetInfo, discover_pets, pet_trait_key
from codex_pet_companion.core.state import add_log, clear_runtime_logs, history_lines, load_state, now, save_state
from codex_pet_companion.core.tamagotchi import (
    apply_action, care_state, codex_session_lines, codex_status_line,
    codex_short_line, decayed, days_together, ensure_bond_state, friendship_progress_line,
    friendship_rank, friendship_title, maybe_mark_codex_silence,
    today_key,
    hint_line
)
from .sprites import SpriteFrames
from .widgets import StatRow

MINI_BUBBLE_THEME = "light"

STYLE = """
QWidget {
    background: #0f1116;
    color: #edf5ef;
    font-family: Segoe UI, Arial;
    font-size: 13px;
}
QWidget#CompactWindow {
    background: transparent;
}
QLabel#PetSprite {
    background: transparent;
    border: none;
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
QLabel#MiniName {
    color: #a7f2c3;
    font-weight: 700;
}
QLabel#MiniBar {
    background: rgba(11, 14, 20, 210);
    border: 1px solid #1f2930;
    border-radius: 10px;
    padding: 7px 10px;
}
QLabel#MiniBarCodex {
    background: rgba(11, 14, 20, 210);
    border: 1px solid #1f2930;
    border-radius: 10px;
    padding: 7px 10px;
    color: #f1d56e;
}
QLabel#MiniBarState {
    background: rgba(11, 14, 20, 210);
    border: 1px solid #1f2930;
    border-radius: 10px;
    padding: 7px 10px;
    color: #dce8e1;
}
QPushButton {
    background: #a7f2c3;
    color: #101318;
    border: 0;
    border-radius: 10px;
    padding: 8px 12px;
    font-weight: 700;
}
QPushButton:hover {
    background: #c9ffd9;
}
QPushButton#Secondary {
    background: #d9e0df;
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
    background: #10141a;
    border: 1px solid #28313a;
    border-radius: 12px;
    padding: 8px;
}
QComboBox, QLineEdit {
    background: #161a20;
    border: 1px solid #28313a;
    border-radius: 8px;
    padding: 7px;
}
QTabWidget::pane {
    border: 1px solid #28313a;
    border-radius: 12px;
}
QTabBar::tab {
    background: #161a20;
    color: #a9b5ad;
    padding: 7px 12px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}
QTabBar::tab:selected {
    color: #edf5ef;
    background: #28313a;
}
QGroupBox {
    border: 1px solid #28313a;
    border-radius: 12px;
    margin-top: 10px;
    padding: 10px;
    font-weight: 700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}
QCheckBox {
    padding: 4px;
}
"""


class SettingsWheelFilter(QObject):
    def __init__(self, scroll_area: QScrollArea):
        super().__init__(scroll_area)
        self.scroll_area = scroll_area

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y()
            if delta != 0:
                bar = self.scroll_area.verticalScrollBar()
                bar.setValue(bar.value() - delta)
                event.accept()
                return True
        return False


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

        self.value_label = QLabel(value)
        self.value_label.setObjectName("CardValue")
        self.value_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)


class TextPanel(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setObjectName("InfoCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(title_label)
        layout.addWidget(self.text, 1)





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
        self.bubble.update_notification(notification, subtitle, show_bubble)
        self.follow_sprite()
        if self.sprite.isVisible():
            self.sprite.show()
        if self.bubble.isVisible():
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
        self.resize(900, 800)
        self.setMinimumSize(780, 700)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        top = QHBoxLayout()

        self.pet = QLabel()
        self.pet.setFixedSize(192 * 2, 208 * 2)
        self.pet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(self.pet)

        side_card = QFrame()
        side_card.setObjectName("Card")
        side = QVBoxLayout(side_card)
        side.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        self.title = QLabel("Pet")
        self.title.setObjectName("Title")
        header.addWidget(self.title, 1)

        self.mini_button = QToolButton()
        self.mini_button.setText("🐾")
        self.mini_button.setToolTip("Mini mode")
        self.mini_button.clicked.connect(self.controller.show_compact)

        header.addWidget(self.mini_button)
        side.addLayout(header)

        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setObjectName("Accent")

        self.codex = QLabel("")
        self.codex.setWordWrap(True)
        self.codex.setObjectName("Codex")

        self.state = QLabel("")
        self.state.setObjectName("Muted")

        side.addWidget(self.status)
        side.addWidget(self.codex)
        side.addWidget(self.state)

        self.stats = {
            "hunger": StatRow("Fullness"),
            "mood": StatRow("Mood"),
            "energy": StatRow("Energy"),
            "focus": StatRow("Focus"),
        }
        for row in self.stats.values():
            side.addWidget(row)

        self.level = QLabel("")
        self.level.setObjectName("Muted")
        side.addWidget(self.level)

        buttons = QHBoxLayout()
        for label, action in [("Feed", "feed"), ("Pet", "pet"), ("Play", "play"), ("Rest", "rest")]:
            b = QPushButton(label)
            b.clicked.connect(lambda _=False, a=action: self.controller.do_action(a))
            buttons.addWidget(b)
        side.addLayout(buttons)

        chat_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Talk to your pet...")
        self.chat_input.returnPressed.connect(self.send_chat)
        send = QPushButton("Talk")
        send.setObjectName("Secondary")
        send.clicked.connect(self.send_chat)
        chat_row.addWidget(self.chat_input)
        chat_row.addWidget(send)
        side.addLayout(chat_row)

        top.addWidget(side_card, 1)
        layout.addLayout(top)

        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(355)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        self.pet_tab = QWidget()
        self.build_pet_tab()

        self.codex_tab = QWidget()
        self.build_codex_tab()

        self.settings = QWidget()
        self.settings_scroll = QScrollArea()
        self.settings_scroll.setWidgetResizable(True)
        self.settings_scroll.setWidget(self.settings)
        self.build_settings()
        self.install_settings_wheel_filter()

        self.tabs.addTab(self.log, "General")
        self.tabs.addTab(self.pet_tab, "Pet")
        self.tabs.addTab(self.codex_tab, "Codex")
        self.tabs.addTab(self.settings_scroll, "Settings")

        layout.addWidget(self.tabs, 1)

    def build_pet_tab(self):
        layout = QVBoxLayout(self.pet_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        top_cards = QHBoxLayout()
        top_cards.setSpacing(10)

        self.today_care_card = InfoCard("Today")
        self.today_hint_card = InfoCard("Hint")

        top_cards.addWidget(self.today_care_card, 3)
        top_cards.addWidget(self.today_hint_card, 2)
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
        layout.addWidget(self.codex_history_panel, 1)

    def closeEvent(self, event):
        if bool(self.controller._really_quitting):
            event.accept()
            return
        event.ignore()
        self.controller.quit()

    def build_settings(self):
        layout = QVBoxLayout(self.settings)
        layout.setSpacing(12)

        window_box = QGroupBox("Window")
        window_layout = QFormLayout(window_box)

        self.start_mode_combo = QComboBox()
        self.start_mode_combo.addItem("Full mode", "full")
        self.start_mode_combo.addItem("Mini mode", "compact")

        self.always_top_check = QCheckBox("Mini stays on top")

        window_layout.addRow("Startup:", self.start_mode_combo)
        window_layout.addRow("", self.always_top_check)
        layout.addWidget(window_box)

        mini_box = QGroupBox("Mini mode")
        mini_layout = QFormLayout(mini_box)

        self.compact_size_combo = QComboBox()
        self.compact_size_combo.addItem("Small", 0.38)
        self.compact_size_combo.addItem("Normal", 0.50)
        self.compact_size_combo.addItem("Large", 0.65)

        mini_layout.addRow("Pet size:", self.compact_size_combo)
        layout.addWidget(mini_box)

        pet_box = QGroupBox("Pet")
        pet_layout = QFormLayout(pet_box)

        self.pet_combo = QComboBox()
        self.custom_name = QLineEdit()
        self.custom_name.setPlaceholderText("Display name")

        self.care_mode_combo = QComboBox()
        self.care_mode_combo.addItem("Soft", "soft")
        self.care_mode_combo.addItem("Normal", "normal")
        self.care_mode_combo.addItem("Strict", "strict")

        self.care_mode_hint = QLabel("Controls how quickly pet stats decay: soft is slower, strict is faster.")
        self.care_mode_hint.setObjectName("Muted")
        self.care_mode_hint.setWordWrap(True)

        pet_layout.addRow("Choice:", self.pet_combo)
        pet_layout.addRow("Name:", self.custom_name)
        pet_layout.addRow("Care mode:", self.care_mode_combo)
        pet_layout.addRow("", self.care_mode_hint)
        layout.addWidget(pet_box)

        files_box = QGroupBox("Files")
        files_layout = QVBoxLayout(files_box)

        packs = QHBoxLayout()
        imp = QPushButton("Adopt pet")
        exp = QPushButton("Send as guest")
        imp.setObjectName("Secondary")
        exp.setObjectName("Secondary")
        imp.clicked.connect(self.controller.import_pet_pack)
        exp.clicked.connect(self.controller.export_pet_pack)
        packs.addWidget(imp)
        packs.addWidget(exp)
        files_layout.addLayout(packs)

        tools = QHBoxLayout()
        choose_codex = QPushButton("Choose Codex folder")
        choose_codex.setObjectName("Secondary")
        choose_codex.clicked.connect(self.controller.choose_codex_home)
        open_state = QPushButton("Open data folder")
        open_state.setObjectName("Secondary")
        open_state.clicked.connect(self.controller.open_state_dir)
        tools.addWidget(choose_codex)
        tools.addWidget(open_state)
        files_layout.addLayout(tools)

        self.path_info = QLabel("")
        self.path_info.setObjectName("Muted")
        self.path_info.setWordWrap(True)
        files_layout.addWidget(self.path_info)

        layout.addWidget(files_box)

        buttons = QHBoxLayout()
        apply = QPushButton("Apply")
        apply.clicked.connect(self.controller.apply_settings_from_ui)
        reset_ui = QPushButton("Reset settings")
        reset_ui.setObjectName("Secondary")
        reset_ui.clicked.connect(self.controller.reset_ui_settings)
        refresh = QPushButton("Refresh pets")
        refresh.setObjectName("Secondary")
        refresh.clicked.connect(self.controller.reload_pets)
        reset_state = QPushButton("Reset state")
        reset_state.setObjectName("Danger")
        reset_state.clicked.connect(self.controller.reset_state)

        buttons.addWidget(apply)
        buttons.addWidget(reset_ui)
        buttons.addWidget(refresh)
        buttons.addWidget(reset_state)
        layout.addLayout(buttons)

        layout.addStretch(1)

    def install_settings_wheel_filter(self):
        self.settings_wheel_filter = SettingsWheelFilter(self.settings_scroll)
        self.settings.installEventFilter(self.settings_wheel_filter)
        self.settings_scroll.viewport().installEventFilter(self.settings_wheel_filter)
        for child in self.settings.findChildren(QWidget):
            child.installEventFilter(self.settings_wheel_filter)

    def send_chat(self):
        text = self.chat_input.text().strip()
        if text:
            self.chat_input.clear()
            self.controller.do_action("chat", text)

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

    def update_view(self, pixmap, data: dict[str, Any]):
        self.pet.setPixmap(pixmap)
        self.title.setText(data["pet_name"])
        self.status.setText(data["status"])
        self.codex.setText(data["codex"])
        self.state.setText(data["state"])
        for key, row in self.stats.items():
            row.set_value(data[key])
        self.level.setText(data["level"])

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
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 2)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.frame_index = 0
        self.anim_name = "idle"
        self.next_frame_at = 0.0
        self.compact_dragging = False
        self.compact_drag_animation = "running"
        self.queue: Queue = Queue()
        self._really_quitting = False
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
        else:
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
            action = action_map.get(action, action)
            self.add_bridge_debug(
                f"queue received: {action} title={event.get('notification_title') or ''} subtitle={event.get('notification_subtitle') or ''}"
            )
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
        if self.codex_home is None:
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
        hunger = float(self.state.get("hunger", 50) or 0)
        mood = float(self.state.get("mood", 50) or 0)
        energy = float(self.state.get("energy", 50) or 0)
        focus = float(self.state.get("focus", 50) or 0)
        flags = self.state.get("recovery_flags") if isinstance(self.state.get("recovery_flags"), dict) else {}
        pet_id = self.current_pet.id

        if bool(flags.get("hunger", False)):
            return hint_line(pet_id, "recovery_hunger")
        if bool(flags.get("energy", False)):
            return hint_line(pet_id, "recovery_energy")
        if bool(flags.get("mood", False)):
            return hint_line(pet_id, "recovery_mood")
        if bool(flags.get("focus", False)):
            return hint_line(pet_id, "recovery_focus")
        if hunger < 30:
            return hint_line(pet_id, "low_hunger")
        if energy < 30:
            return hint_line(pet_id, "low_energy")
        if mood < 35:
            return hint_line(pet_id, "low_mood")
        if focus < 25:
            return hint_line(pet_id, "low_focus")
        record = self.today_record()
        if int(record.get("feed", 0) or 0) <= 0:
            return hint_line(pet_id, "not_fed_today")
        if int(record.get("rest", 0) or 0) <= 0 and energy < 65:
            return hint_line(pet_id, "no_rest_today")
        return hint_line(pet_id, "ok")


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
        self.set_combo_value(self.full.care_mode_combo, str(self.config.get("careMode") or "normal"))

        self.full.path_info.setText(f"Codex: {self.codex_home or 'not found'}\nData: {self.state_dir}")

    def apply_settings_from_ui(self):
        pet_id = self.full.pet_combo.currentData()
        self.config["selectedPetId"] = pet_id or "lumisprout"
        self.config["customDisplayName"] = self.full.custom_name.text().strip()
        self.config["startMode"] = self.full.start_mode_combo.currentData() or "full"
        if self.config["startMode"] == "tray":
            self.config["startMode"] = "full"
        self.config["compactScale"] = compact_scale_value(self.full.compact_size_combo.currentData() or 0.50)
        self.config["miniAlwaysOnTop"] = bool(self.full.always_top_check.isChecked())
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
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 2)))
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
        save_config(self.config)

        self.full.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.full.setWindowOpacity(1.0)
        self.compact.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, bool(self.config.get("miniAlwaysOnTop", True)))
        if self.full.isVisible():
            self.full.show()
        if self.compact.isVisible():
            self.compact.show()

        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 2)))
        self.compact_frames = SpriteFrames(self.current_pet.spritesheet_path, compact_scale_value(self.config.get("compactScale", 0.50)))
        self.reload_pet_combo()
        self.refresh()

    def reload_pets(self):
        self.pets = discover_pets(self.codex_home)
        self.current_pet = self.resolve_pet()
        self.trait_key = pet_trait_key(self.current_pet)
        self.full_frames = SpriteFrames(self.current_pet.spritesheet_path, float(self.config.get("fullScale", 2)))
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
        if self.codex_home is None:
            QMessageBox.warning(self.full, "Adopt pet", "Choose a Codex folder first.")
            return
        path, _ = QFileDialog.getOpenFileName(self.full, "Adopt pet", "", "Zip (*.zip)")
        if not path:
            return
        try:
            pet_id = import_pet_pack(Path(path), self.codex_home)
            self.config["selectedPetId"] = pet_id
            save_config(self.config)
            self.reload_pets()
        except Exception as exc:
            QMessageBox.critical(self.full, "Adopt pet", str(exc))

    def export_pet_pack(self):
        pet = self.current_pet
        if pet.folder is None:
            message = "Built-in pets already live here. Only custom pets can be sent as guest packs."
            add_log(self.state, message)
            self.state["event_status"] = message
            self.state["current_event"] = "waving"
            self.state["event_until"] = now() + 4.0
            save_state(self.state_path, self.state)
            self.refresh()
            return
        path, _ = QFileDialog.getSaveFileName(self.full, "Send as guest", f"{pet.id}_guest_pack.zip", "Zip (*.zip)")
        if not path:
            return
        try:
            export_pet_pack(pet.folder, pet.id, Path(path))
            add_log(self.state, f"Pet guest pack ready: {Path(path).name}")
            save_state(self.state_path, self.state)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(self.full, "Send as guest", str(exc))

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
    font = app.font()
    if font.pointSize() <= 0:
        font.setPointSize(10)
        app.setFont(font)

    config = load_config()
    guard = SingleInstanceGuard("codex_pet_companion_v11")
    if bool(config.get("singleInstance", True)) and not guard.acquire():
        print("Codex Pet Companion is already running.")
        return

    app.setStyleSheet(STYLE)
    app.aboutToQuit.connect(guard.release)

    controller = CompanionController(app)
    if str(controller.config.get("startMode") or "full").lower() == "tray":
        controller.config["startMode"] = "full"
    controller.start()
    sys.exit(app.exec())
