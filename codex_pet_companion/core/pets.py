from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .config import ROOT, data_dir
from .constants import ATLAS_SIZE, TRAITS

@dataclass
class PetInfo:
    id: str
    display_name: str
    description: str
    spritesheet_path: Path
    source: str
    folder: Path | None = None
    background_path: Path | None = None

    @property
    def label(self) -> str:
        return f"{self.display_name} ({self.id})"

def valid_spritesheet(path: Path) -> bool:
    try:
        with Image.open(path) as img:
            return img.size == ATLAS_SIZE and img.format in {"WEBP", "PNG"}
    except Exception:
        return False

def load_pet_from_folder(folder: Path, source: str) -> PetInfo | None:
    manifest_path = folder / "pet.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    pet_id = str(manifest.get("id") or folder.name).strip() or folder.name
    display = str(manifest.get("displayName") or pet_id).strip() or pet_id
    desc = str(manifest.get("description") or "").strip()
    sheet = folder / str(manifest.get("spritesheetPath") or "spritesheet.webp")
    if not valid_spritesheet(sheet):
        return None
    background_raw = str(manifest.get("backgroundPath") or "").strip()
    background = folder / background_raw if background_raw else folder / f"{pet_id}_background.jpg"
    return PetInfo(
        pet_id,
        display,
        desc,
        sheet,
        source,
        folder,
        background if background.is_file() else None,
    )


def builtin_pets() -> list[PetInfo]:
    pets: list[PetInfo] = []
    builtins_root = ROOT / "builtin_pets"
    if not builtins_root.is_dir():
        return pets
    for folder in sorted(path for path in builtins_root.iterdir() if path.is_dir()):
        pet = load_pet_from_folder(folder, "built-in")
        if pet is not None:
            pets.append(pet)
    return pets

def discover_pets(_codex_home: Path | None = None) -> list[PetInfo]:
    pets: list[PetInfo] = builtin_pets()
    pets_root = data_dir() / "pets"
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
