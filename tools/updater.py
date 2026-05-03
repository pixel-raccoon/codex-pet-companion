#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

PROTECTED_TOP_LEVEL = {
    "data",
    "config.json",
    "state.json",
    "pets",
    "CodexPetCompanion.exe.bak",
    "CodexPetCompanion.exe.last_good.bak",
}
SKIP_FILE_NAMES = {
    "updater.exe",
    "updater",
}


def wait_until_replaceable(path: Path, timeout: float) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if path.exists():
                probe = path.with_suffix(path.suffix + ".replace_probe")
                path.rename(probe)
                probe.rename(path)
            return
        except OSError:
            time.sleep(0.35)
    raise RuntimeError(f"Timed out waiting for {path.name} to close.")


def extract_package(package: Path, extract_dir: Path) -> Path:
    if package.suffix.lower() == ".exe":
        single = extract_dir / "single-exe"
        single.mkdir(parents=True, exist_ok=True)
        shutil.copy2(package, single / "CodexPetCompanion.exe")
        return single

    if package.suffix.lower() != ".zip":
        raise RuntimeError(f"Unsupported update package: {package.name}")

    with zipfile.ZipFile(package) as z:
        z.extractall(extract_dir)

    folder_candidates = [
        path for path in extract_dir.iterdir()
        if path.is_dir() and (path / "CodexPetCompanion.exe").is_file()
    ]
    if folder_candidates:
        folder_candidates.sort(key=lambda p: p.name.lower())
        return folder_candidates[0]

    if (extract_dir / "CodexPetCompanion.exe").is_file():
        return extract_dir

    exe_candidates = list(extract_dir.rglob("CodexPetCompanion.exe"))
    if not exe_candidates:
        raise RuntimeError("Update package does not contain CodexPetCompanion.exe.")
    exe_candidates.sort(key=lambda p: len(p.parts))
    return exe_candidates[0].parent


def backup_app_exe(app_exe: Path) -> Path:
    backup = app_exe.with_suffix(app_exe.suffix + ".bak")
    old_backup = app_exe.with_suffix(app_exe.suffix + ".last_good.bak")
    try:
        if old_backup.exists():
            old_backup.unlink()
        if backup.exists():
            backup.unlink()
    except OSError:
        pass
    if app_exe.exists():
        shutil.copy2(app_exe, backup)
    return backup


def finish_backup(app_exe: Path, backup: Path) -> None:
    old_backup = app_exe.with_suffix(app_exe.suffix + ".last_good.bak")
    try:
        if old_backup.exists():
            old_backup.unlink()
        if backup.exists():
            backup.replace(old_backup)
    except OSError:
        pass


def should_skip(relative: Path) -> bool:
    if not relative.parts:
        return True
    first = relative.parts[0]
    if first in PROTECTED_TOP_LEVEL:
        return True
    if relative.name in SKIP_FILE_NAMES:
        return True
    if "__pycache__" in relative.parts:
        return True
    return False


def copy_update_tree(source_root: Path, app_dir: Path) -> None:
    for source in source_root.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(source_root)
        if should_skip(relative):
            continue
        target = app_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex Pet Companion updater")
    parser.add_argument("--app-exe", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--wait-timeout", type=float, default=30.0)
    args = parser.parse_args()

    app_exe = Path(args.app_exe).expanduser().resolve()
    app_dir = app_exe.parent
    package = Path(args.package).expanduser().resolve()

    try:
        if not package.is_file():
            raise RuntimeError(f"Update package not found: {package}")
        app_dir.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory(prefix="codex-pet-updater-") as temp_raw:
            temp = Path(temp_raw)
            new_root = extract_package(package, temp)
            new_exe = new_root / "CodexPetCompanion.exe"
            if not new_exe.is_file():
                raise RuntimeError("Update package does not contain CodexPetCompanion.exe.")

            wait_until_replaceable(app_exe, args.wait_timeout)
            backup = backup_app_exe(app_exe)
            try:
                copy_update_tree(new_root, app_dir)
                shutil.copy2(new_exe, app_exe)
                finish_backup(app_exe, backup)
            except Exception:
                if backup.exists():
                    shutil.copy2(backup, app_exe)
                raise

        if args.restart:
            subprocess.Popen([str(app_exe)], cwd=str(app_dir))
        return 0
    except Exception as exc:  # noqa: BLE001
        message = f"Codex Pet Companion update failed:\\n{exc}\\n\\nThe previous version should still be available."
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(None, message, "Update failed", 0x10)
            except Exception:
                print(message, file=sys.stderr)
        else:
            print(message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
