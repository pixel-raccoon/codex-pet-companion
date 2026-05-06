from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APP_NAME = "pet-companion"
PORTABLE_FLAG = "portable.flag"
DEFAULT_SPRITESHEET_PATH = ROOT / "spritesheet.webp"
DEFAULT_PET_JSON_PATH = ROOT / "pet.json"

def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return ROOT

def default_codex_home() -> Path | None:
    raw = os.environ.get("CODEX_HOME")
    if raw:
        return Path(raw).expanduser()
    home = Path.home()
    if str(home):
        return home / ".codex"
    return None

def appdata_fallback_dir() -> Path:
    raw = os.environ.get("APPDATA")
    if raw:
        return Path(raw) / "CodexPetCompanion"
    return Path.home() / ".codex-pet-companion"

def legacy_data_dir() -> Path | None:
    codex_home = default_codex_home()
    if codex_home is None:
        return None
    return codex_home / APP_NAME


def _copy_legacy_data_once(target: Path) -> None:
    legacy = legacy_data_dir()
    target.mkdir(parents=True, exist_ok=True)
    if legacy is None or not legacy.is_dir() or legacy.resolve() == target.resolve():
        return
    marker = target / ".legacy_migration_done"
    if marker.exists() or any(target.iterdir()):
        return
    for item in legacy.iterdir():
        destination = target / item.name
        try:
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            elif item.is_file():
                shutil.copy2(item, destination)
        except OSError:
            continue
    marker.write_text(str(legacy), encoding="utf-8")


def data_dir() -> Path:
    # Release builds keep all user data next to the application folder:
    # Codex Pet Companion/
    #   CodexPetCompanion.exe
    #   updater.exe
    #   data/
    #     config.json
    #     state.json
    #     pets/
    target = (app_base_dir() / "data").resolve()
    _copy_legacy_data_once(target)
    return target

CONFIG_PATH = data_dir() / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "codexHome": "auto",
    "codexAutoPathsEnabled": True,
    "stateDir": "auto",
    "miniAlwaysOnTop": True,
    "startMode": "full",
    "fullScale": 1.00,
    "compactScale": 0.50,
    "compactCardMode": "always",
    "apiPort": 8787,
    "decayEnabled": True,
    "decayRate": 1.0,
    "careMode": "normal",
    "offlineDecayMaxSeconds": 300,
    "clearLogsOnStart": True,
    "workPopups": False,
    "achievementPopups": False,
    "sessionGlob": "sessions/**/rollout-*.jsonl",
    "pollSeconds": 1,
    "longSilenceSeconds": 180,
    "codexRunningTtlSeconds": 90,
    "codexReviewTtlSeconds": 600,
    "codexErrorTtlSeconds": 600,
    "codexNotificationSeconds": 5.0,
    "criticalEventCooldownSeconds": 21600,
    "criticalRecoveryFloor": 12,
    "offlineDecayCapSeconds": 28800,
    "bridgeStartFresh": True,
    "bridgeInitialTailBytes": 65536,
    "bridgeIgnoreExistingSessionTail": True,
    "bridgeSuppressUntitledCommandErrors": True,
    "bridgeFreshFileSlackSeconds": 3,
    "bridgeInactiveSeconds": 45,
    "bridgeLiveEventAgeSeconds": 60,
    "bridgeMaxEventAgeSeconds": 900,
    "bridgeNearbySessionSeconds": 180,
    "debugBridge": False,
    "debugBridgeMaxLines": 160,
    "selectedPetId": "lumisprout",
    "customDisplayName": "",
    "windowOpacity": 0.96,
    "closeToCompact": False,
    "enableTray": False,
    "singleInstance": True,
    "accentColor": "#a7f2c3",
    "checkUpdatesOnStartup": True,
    "lastUpdateCheck": 0,
    "ignoredUpdateVersion": "",
}

LEGACY_SESSION_GLOB = "sessions/*/*/*/rollout-*.jsonl"
DEFAULT_SESSION_GLOB = "sessions/**/rollout-*.jsonl"
_WSL_DISTRO_CACHE: tuple[float, list[str]] = (0.0, [])

def deep_merge(default: dict, loaded: dict) -> dict:
    result = dict(default)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    config = deep_merge(DEFAULT_CONFIG, loaded)
    changed = False
    if str(config.get("sessionGlob") or "") == LEGACY_SESSION_GLOB:
        config["sessionGlob"] = DEFAULT_SESSION_GLOB
        changed = True
    # v11.3.1 removed tray startup. Old configs must not silently hide the app.
    if str(config.get("startMode") or "").lower() == "tray":
        config["startMode"] = "full"
        changed = True
    config["enableTray"] = bool(config.get("enableTray", False))
    # 1.0.6: full mode uses a smaller centered sprite presentation with stable padding.
    try:
        if float(config.get("fullScale", 1.00) or 1.00) >= 1.15:
            config["fullScale"] = 1.00
            changed = True
    except (TypeError, ValueError):
        config["fullScale"] = 1.00
        changed = True
    if changed:
        save_config(config)
    return config

def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def default_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    return Path(raw).expanduser() if raw else Path.home() / ".codex"

def _append_unique(paths: list[Path], path: Path | None) -> None:
    if path is None:
        return
    expanded = path.expanduser()
    key = str(expanded if expanded.is_absolute() else expanded.absolute())
    if not any(str(existing) == key for existing in paths):
        paths.append(Path(key))

def _iter_wsl_codex_homes() -> list[Path]:
    homes: list[Path] = []
    distro_names = _wsl_distro_names()
    if sys.platform == "win32" and not distro_names:
        return homes
    for root in (Path(r"\\wsl.localhost"), Path(r"\\wsl$")):
        try:
            distros = [item.name for item in root.iterdir() if item.is_dir()]
        except OSError:
            distros = []
        for distro_name in [*distros, *distro_names]:
            if not distro_name:
                continue
            home_root = root / distro_name / "home"
            try:
                if not home_root.is_dir():
                    continue
                users = [item for item in home_root.iterdir() if item.is_dir()]
            except OSError:
                continue
            for user_dir in users:
                codex_home = user_dir / ".codex"
                try:
                    if codex_home.is_dir():
                        homes.append(codex_home)
                except OSError:
                    continue
    return homes

def _windows_wsl_distro_names_from_registry() -> list[str]:
    if sys.platform != "win32":
        return []
    try:
        import winreg
    except Exception:
        return []

    names: list[str] = []
    try:
        root = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Lxss",
        )
    except OSError:
        return []

    try:
        index = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(root, index)
                index += 1
            except OSError:
                break
            try:
                with winreg.OpenKey(root, subkey_name) as subkey:
                    name, _kind = winreg.QueryValueEx(subkey, "DistributionName")
            except OSError:
                continue
            if isinstance(name, str) and name.strip():
                names.append(name.strip())
    finally:
        try:
            winreg.CloseKey(root)
        except Exception:
            pass
    return names

def _wsl_distro_names() -> list[str]:
    global _WSL_DISTRO_CACHE
    current = time.time()
    cached_at, cached_names = _WSL_DISTRO_CACHE
    if current - cached_at < 300:
        return list(cached_names)

    names: list[str] = []
    registry_names = _windows_wsl_distro_names_from_registry()
    names.extend(registry_names)

    # On Windows without registered WSL distributions, calling wsl.exe can open the
    # system "install WSL" prompt. Treat WSL as optional and skip it completely.
    if sys.platform == "win32" and not registry_names:
        _WSL_DISTRO_CACHE = (current, [])
        return []

    if sys.platform == "win32":
        try:
            startupinfo = None
            creationflags = 0
            if hasattr(subprocess, "STARTUPINFO"):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            if hasattr(subprocess, "CREATE_NO_WINDOW"):
                creationflags = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(
                ["wsl.exe", "-l", "-q"],
                capture_output=True,
                timeout=1.5,
                check=False,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            output = (result.stdout or b"").decode("utf-16le", errors="ignore")
            if not output.strip():
                output = (result.stdout or b"").decode("utf-8", errors="ignore")
            for line in output.replace("\x00", "").splitlines():
                name = line.strip()
                if name:
                    names.append(name)
        except Exception:
            pass
    elif sys.platform == "linux" and os.environ.get("WSL_DISTRO_NAME"):
        current_distro = os.environ.get("WSL_DISTRO_NAME") or "local"
        names.append(current_distro)

    unique: list[str] = []
    for name in names:
        if name not in unique:
            unique.append(name)
    _WSL_DISTRO_CACHE = (current, unique)
    return unique

def _iter_windows_codex_homes_from_wsl() -> list[Path]:
    homes: list[Path] = []
    if sys.platform != "linux" or not os.environ.get("WSL_DISTRO_NAME"):
        return homes
    users_root = Path("/mnt/c/Users")
    try:
        users = [item for item in users_root.iterdir() if item.is_dir()]
    except OSError:
        return homes
    for user_dir in users:
        codex_home = user_dir / ".codex"
        try:
            if codex_home.is_dir():
                homes.append(codex_home)
        except OSError:
            continue
    return homes

def detect_codex_home_candidates(config: dict[str, Any], include_slow: bool = True) -> list[Path]:
    paths: list[Path] = []
    raw = str(config.get("codexHome") or "auto").strip()
    if raw and raw.lower() != "auto":
        _append_unique(paths, Path(raw).expanduser())

    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        _append_unique(paths, Path(env_home).expanduser())

    try:
        _append_unique(paths, Path.home() / ".codex")
    except Exception:
        pass

    if include_slow and bool(config.get("codexAutoPathsEnabled", True)):
        for codex_home in _iter_wsl_codex_homes():
            _append_unique(paths, codex_home)
        for codex_home in _iter_windows_codex_homes_from_wsl():
            _append_unique(paths, codex_home)
    return paths

def resolve_codex_home(config: dict[str, Any], include_slow: bool = False) -> Path | None:
    for path in detect_codex_home_candidates(config, include_slow=include_slow):
        try:
            if path.exists() and path.is_dir():
                return path.resolve()
        except OSError:
            continue
    return None

def resolve_state_dir(config: dict[str, Any], codex_home: Path | None) -> Path:
    raw = str(config.get("stateDir") or "auto").strip()
    if raw.lower() == "auto":
        path = data_dir()
    else:
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = data_dir() / path
    path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

def ui_default_config() -> dict[str, Any]:
    return {
        "startMode": DEFAULT_CONFIG["startMode"],
        "compactScale": DEFAULT_CONFIG["compactScale"],
        "compactCardMode": DEFAULT_CONFIG["compactCardMode"],
        "miniAlwaysOnTop": DEFAULT_CONFIG.get("miniAlwaysOnTop", True),
        "careMode": DEFAULT_CONFIG.get("careMode", "normal"),
        "customDisplayName": DEFAULT_CONFIG["customDisplayName"],
    }
