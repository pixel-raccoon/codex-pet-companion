from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QProgressBar, QWidget, QHBoxLayout

BAR_STYLE_BY_STATE = {
    "good": """
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
    """,
    "mid": """
        QProgressBar {
            background: #20252d;
            border: 0;
            border-radius: 5px;
            height: 10px;
        }
        QProgressBar::chunk {
            background: #f1d56e;
            border-radius: 5px;
        }
    """,
    "low": """
        QProgressBar {
            background: #20252d;
            border: 0;
            border-radius: 5px;
            height: 10px;
        }
        QProgressBar::chunk {
            background: #ff9b71;
            border-radius: 5px;
        }
    """,
    "critical": """
        QProgressBar {
            background: #20252d;
            border: 0;
            border-radius: 5px;
            height: 10px;
        }
        QProgressBar::chunk {
            background: #ffa6a6;
            border-radius: 5px;
        }
    """,
}

class StatRow(QWidget):
    def __init__(self, label: str, icon_path: Path | None = None):
        super().__init__()
        self.setObjectName("StatRow")
        self.setStyleSheet(
            """
            QWidget#StatRow,
            QWidget#StatRow QLabel {
                background: transparent;
                border: none;
            }
            QLabel#StatName {
                color: #d8eee1;
                font-weight: 700;
            }
            QLabel#StatValue {
                color: #a9b5ad;
                font-weight: 700;
            }
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        self.icon = QLabel()
        self.icon.setFixedSize(20, 20)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_path is not None:
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                self.icon.setPixmap(
                    pixmap.scaled(
                        self.icon.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        self.name = QLabel(label)
        self.name.setObjectName("StatName")
        self.name.setFixedWidth(64)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self._bar_state = ""
        self.value = QLabel("0%")
        self.value.setObjectName("StatValue")
        self.value.setFixedWidth(38)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.icon)
        layout.addWidget(self.name)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.value)

    def _state_for_value(self, value: int) -> str:
        if value <= 20:
            return "critical"
        if value <= 40:
            return "low"
        if value <= 65:
            return "mid"
        return "good"

    def set_value(self, value: int) -> None:
        safe_value = max(0, min(100, int(value)))
        self.bar.setValue(safe_value)
        self.value.setText(f"{safe_value}%")
        bar_state = self._state_for_value(safe_value)
        if bar_state != self._bar_state:
            self._bar_state = bar_state
            self.bar.setStyleSheet(BAR_STYLE_BY_STATE[bar_state])
