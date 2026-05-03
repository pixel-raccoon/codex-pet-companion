from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

def import_pet_pack(zip_path: Path, data_root: Path) -> str:
    pets_root = data_root / "pets"
    pets_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        pet_json_candidates = [name for name in names if name.endswith("pet.json")]
        if not pet_json_candidates:
            raise ValueError("Archive does not contain pet.json.")
        manifest_name = pet_json_candidates[0]
        manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
        pet_id = str(manifest.get("id") or Path(manifest_name).parent.name).strip()
        if not pet_id:
            raise ValueError("pet.json does not contain id.")
        target = pets_root / pet_id
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)
        root_prefix = str(Path(manifest_name).parent).replace("\\", "/")
        for name in names:
            normalized = name.replace("\\", "/")
            if root_prefix not in {"", "."}:
                if not normalized.startswith(root_prefix + "/"):
                    continue
                rel = normalized[len(root_prefix) + 1:]
            else:
                rel = normalized
            if not rel or rel.startswith("../") or "/../" in rel:
                continue
            out = target / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(archive.read(name))
    return pet_id

def export_pet_pack(folder: Path, pet_id: str, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in folder.rglob("*"):
            if file.is_file():
                archive.write(file, arcname=str(Path(pet_id) / file.relative_to(folder)))
