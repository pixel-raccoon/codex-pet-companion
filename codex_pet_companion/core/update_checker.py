from __future__ import annotations

import json
import re
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import GITHUB_REPO


LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
PREFERRED_ASSETS = [
    "Codex-Pet-Companion-windows-x64.zip",
    "CodexPetCompanion-windows-x64.zip",
    "CodexPetCompanion.zip",
    "CodexPetCompanion.exe",
]


@dataclass
class UpdateInfo:
    ok: bool
    update_available: bool
    install_available: bool
    current_version: str
    latest_version: str = ""
    release_url: str = ""
    release_notes: str = ""
    published_at: str = ""
    asset_name: str = ""
    asset_download_url: str = ""
    asset_size: int = 0
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "update_available": self.update_available,
            "install_available": self.install_available,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "release_url": self.release_url,
            "release_notes": self.release_notes,
            "published_at": self.published_at,
            "asset_name": self.asset_name,
            "asset_download_url": self.asset_download_url,
            "asset_size": self.asset_size,
            "error": self.error,
        }


def normalize_version(value: str) -> str:
    value = str(value or "").strip()
    if value.lower().startswith("v"):
        value = value[1:]
    return value.strip()


def version_tuple(value: str) -> tuple[int, ...]:
    value = normalize_version(value)
    parts = re.findall(r"\d+", value)
    if not parts:
        return (0,)
    return tuple(int(part) for part in parts[:4])


def is_newer_version(latest: str, current: str) -> bool:
    left = list(version_tuple(latest))
    right = list(version_tuple(current))
    size = max(len(left), len(right))
    left.extend([0] * (size - len(left)))
    right.extend([0] * (size - len(right)))
    return tuple(left) > tuple(right)


def _request_json(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodexPetCompanion",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("GitHub returned an unexpected response")
    return data


def _select_asset(release: dict[str, Any]) -> tuple[str, str, int]:
    assets = release.get("assets")
    if not isinstance(assets, list):
        return "", "", 0

    clean_assets = [asset for asset in assets if isinstance(asset, dict)]
    by_name = {
        str(asset.get("name") or ""): asset
        for asset in clean_assets
        if str(asset.get("name") or "")
    }

    selected = None
    for wanted in PREFERRED_ASSETS:
        if wanted in by_name:
            selected = by_name[wanted]
            break

    if selected is None:
        for asset in clean_assets:
            name = str(asset.get("name") or "")
            if name.lower().endswith(".zip") and "codexpetcompanion" in name.lower().replace("-", "").replace("_", ""):
                selected = asset
                break

    if selected is None:
        return "", "", 0

    name = str(selected.get("name") or "")
    url = str(selected.get("browser_download_url") or "")
    try:
        size = int(selected.get("size") or 0)
    except (TypeError, ValueError):
        size = 0
    return name, url, size


def check_for_update(current_version: str, timeout: float = 5.0) -> UpdateInfo:
    try:
        release = _request_json(LATEST_RELEASE_URL, timeout)
        if bool(release.get("draft", False)) or bool(release.get("prerelease", False)):
            return UpdateInfo(
                ok=True,
                update_available=False,
                install_available=False,
                current_version=current_version,
            )

        latest = normalize_version(str(release.get("tag_name") or ""))
        if not latest:
            return UpdateInfo(
                ok=False,
                update_available=False,
                install_available=False,
                current_version=current_version,
                error="Latest release does not contain a version tag.",
            )

        asset_name, asset_url, asset_size = _select_asset(release)
        available = is_newer_version(latest, current_version)
        return UpdateInfo(
            ok=True,
            update_available=available,
            install_available=available and bool(asset_url),
            current_version=current_version,
            latest_version=latest,
            release_url=str(release.get("html_url") or ""),
            release_notes=str(release.get("body") or ""),
            published_at=str(release.get("published_at") or ""),
            asset_name=asset_name,
            asset_download_url=asset_url,
            asset_size=asset_size,
        )
    except Exception as exc:  # noqa: BLE001 - update checks must not crash the app
        return UpdateInfo(
            ok=False,
            update_available=False,
            install_available=False,
            current_version=current_version,
            error=str(exc),
        )


def download_update(info: UpdateInfo, target_dir: Path | None = None, timeout: float = 30.0) -> Path:
    if not info.asset_download_url:
        raise RuntimeError("No downloadable update asset was found.")

    if target_dir is None:
        target_dir = Path(tempfile.mkdtemp(prefix="codex-pet-update-"))
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = info.asset_name or "CodexPetCompanion-update"
    target = target_dir / filename
    partial = target.with_suffix(target.suffix + ".part")

    request = urllib.request.Request(
        info.asset_download_url,
        headers={"User-Agent": "CodexPetCompanion"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("wb") as out:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                out.write(chunk)
        if partial.stat().st_size <= 0:
            raise RuntimeError("Downloaded update file is empty.")
        if info.asset_size and partial.stat().st_size != info.asset_size:
            raise RuntimeError(
                f"Downloaded update size mismatch: got {partial.stat().st_size}, expected {info.asset_size}."
            )
        if target.exists():
            target.unlink()
        partial.replace(target)
        return target
    except Exception:
        try:
            partial.unlink()
        except OSError:
            pass
        raise
