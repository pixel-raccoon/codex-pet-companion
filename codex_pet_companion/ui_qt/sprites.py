from __future__ import annotations

from pathlib import Path

from PIL import Image
from PySide6.QtGui import QImage, QPixmap

from codex_pet_companion.core.constants import CELL_H, CELL_W, STATES

def pil_to_pixmap(image: Image.Image) -> QPixmap:
    rgba = image.convert("RGBA")
    data = rgba.tobytes("raw", "RGBA")
    qimg = QImage(data, rgba.width, rgba.height, QImage.Format.Format_RGBA8888)
    # copy needed because data buffer belongs to temporary object
    return QPixmap.fromImage(qimg.copy())

class SpriteFrames:
    def __init__(self, path: Path, scale: float = 2.0):
        self.path = path
        self.scale = max(0.25, min(4.0, float(scale)))
        self.frames: dict[str, list[QPixmap]] = {}
        self.load()

    def load(self) -> None:
        with Image.open(self.path) as opened:
            atlas = opened.convert("RGBA")
        self.frames = {}
        for name, (row, durations) in STATES.items():
            row_frames: list[QPixmap] = []
            for col in range(len(durations)):
                crop = atlas.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H)).convert("RGBA")
                if self.scale != 1:
                    crop = crop.resize((max(1, round(CELL_W * self.scale)), max(1, round(CELL_H * self.scale))), Image.Resampling.NEAREST)
                row_frames.append(pil_to_pixmap(crop))
            self.frames[name] = row_frames

    def get(self, state: str, index: int) -> QPixmap:
        frames = self.frames.get(state) or self.frames["idle"]
        return frames[index % len(frames)]
