from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QWidget, QHBoxLayout

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
        self.value = QLabel("0%")
        self.value.setFixedWidth(38)
        self.value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.name)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.value)

    def set_value(self, value: int) -> None:
        self.bar.setValue(max(0, min(100, int(value))))
        self.value.setText(f"{int(value)}%")
