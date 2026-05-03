from __future__ import annotations

from PySide6.QtCore import Qt
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
    def __init__(self, label: str):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)
        self.name = QLabel(label)
        self.name.setFixedWidth(86)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setTextVisible(False)
        self._bar_state = ""
        self.value = QLabel("0%")
        self.value.setFixedWidth(38)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
