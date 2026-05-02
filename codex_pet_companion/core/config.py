from __future__ import annotations

import json
import os
import sys
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

def data_dir() -> Path:
    base = app_base_dir()
    if (base / PORTABLE_FLAG).exists():
        return base
    codex_home = default_codex_home()
    if codex_home is not None:
        return codex_home / APP_NAME
    return appdata_fallback_dir()

CONFIG_PATH = data_dir() / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "codexHome": "auto",
    "stateDir": "auto",
    "miniAlwaysOnTop": True,
    "startMode": "full",
    "fullScale": 2,
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
    "sessionGlob": "sessions/*/*/*/rollout-*.jsonl",
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
    "bridgeFreshFileSlackSeconds": 3,
    "bridgeInactiveSeconds": 45,
    "bridgeLiveEventAgeSeconds": 60,
    "bridgeMaxEventAgeSeconds": 900,
    "debugBridge": False,
    "debugBridgeMaxLines": 160,
    "selectedPetId": "lumisprout",
    "customDisplayName": "",
    "windowOpacity": 0.96,
    "closeToCompact": False,
    "enableTray": False,
    "singleInstance": True,
    "accentColor": "#a7f2c3",
}

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
    # v11.3.1 removed tray startup. Old configs must not silently hide the app.
    if str(config.get("startMode") or "").lower() == "tray":
        config["startMode"] = "full"
        save_config(config)
    config["enableTray"] = bool(config.get("enableTray", False))
    return config

def save_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def default_codex_home() -> Path:
    raw = os.environ.get("CODEX_HOME")
    return Path(raw).expanduser() if raw else Path.home() / ".codex"

def resolve_codex_home(config: dict[str, Any]) -> Path | None:
    raw = str(config.get("codexHome") or "auto").strip()
    path = default_codex_home() if raw.lower() == "auto" else Path(raw).expanduser()
    return path.resolve() if path.exists() and path.is_dir() else None

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
