from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .config import DEFAULT_PET_JSON_PATH, DEFAULT_SPRITESHEET_PATH, ROOT
from .constants import ATLAS_SIZE, TRAITS

@dataclass
class PetInfo:
    id: str
    display_name: str
    description: str
    spritesheet_path: Path
    source: str
    folder: Path | None = None

    @property
    def label(self) -> str:
        return f"{self.display_name} ({self.id})"

def valid_spritesheet(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            return img.size == ATLAS_SIZE and img.format in {"WEBP", "PNG"}
    except Exception:
        return False

def builtin_pets() -> list[PetInfo]:
    pets: list[PetInfo] = []
    if valid_spritesheet(DEFAULT_SPRITESHEET_PATH):
        pets.append(PetInfo(
            "lumisprout",
            "Lumisprout",
            "Built-in default companion.",
            DEFAULT_SPRITESHEET_PATH,
            "built-in",
            None,
        ))

    vikamon_sheet = ROOT / "builtin_pets" / "vikamon" / "spritesheet.webp"
    if valid_spritesheet(vikamon_sheet):
        pets.append(PetInfo(
            "vikamon",
            "Vikamon",
            "A mischievous chibi mascot in a green monster hoodie.",
            vikamon_sheet,
            "built-in",
            None,
        ))
    return pets

def discover_pets(codex_home: Path | None) -> list[PetInfo]:
    pets: list[PetInfo] = builtin_pets()

    if codex_home is not None:
        pets_root = codex_home / "pets"
        if pets_root.is_dir():
            for folder in sorted(p for p in pets_root.iterdir() if p.is_dir()):
                manifest_path = folder / "pet.json"
                if not manifest_path.is_file():
                    continue
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                except Exception:
                    continue
                pet_id = str(manifest.get("id") or folder.name).strip() or folder.name
                display = str(manifest.get("displayName") or pet_id).strip() or pet_id
                desc = str(manifest.get("description") or "").strip()
                sheet = folder / str(manifest.get("spritesheetPath") or "spritesheet.webp")
                if valid_spritesheet(sheet):
                    pets.append(PetInfo(pet_id, display, desc, sheet, str(folder), folder))
    return pets

def load_companion_data(pet: PetInfo | None) -> dict:
    if pet is None or pet.folder is None:
        return {}
    path = pet.folder / "companion.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def pet_trait_key(pet: PetInfo | None) -> str:
    data = load_companion_data(pet)
    raw = str(data.get("trait") or data.get("personality") or "neutral").strip().lower()
    return raw if raw in TRAITS else "neutral"
