from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .constants import ACHIEVEMENTS

def now() -> float:
    return time.time()

def stamp() -> str:
    return time.strftime("%H:%M")

DEFAULT_STATE: dict[str, Any] = {
    "version": "11",
    "hunger": 78,
    "mood": 76,
    "energy": 72,
    "focus": 38,
    "xp": 0,
    "level": 1,
    "friendship_points": 0.0,
    "friendship_rank": 0,
    "first_seen_date": "",
    "last_seen_date": "",
    "seen_days": [],
    "daily_bond": {},
    "bond_milestones": [],
    "daily_care": {},
    "current_day": "",
    "rest_until": 0.0,
    "cooldowns": {},
    "last_care_denial": "",
    "last_care_denial_until": 0.0,
    "last_update": 0,
    "current_event": "idle",
    "event_until": 0,
    "event_status": "",
    "emotion": "neutral",
    "emotion_until": 0,
    "log": ["Pet started."],
    "codex_log": [],
    "history": [],
    "achievements": [],
    "counters": {},
    "error_streak": 0,
    "review_streak": 0,
    "busy_streak": 0,
    "codex_status": "idle",
    "codex_last_event": "",
    "codex_last_note": "",
    "codex_last_time": 0,
    "codex_session_file": "",
    "codex_counters": {"task_started": 0, "function_call": 0, "error": 0, "final_answer": 0, "events": 0},
    "codex_silence_notified": False,
}

def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        state = dict(DEFAULT_STATE)
        state["last_update"] = now()
        save_state(path, state)
        return state
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    state = dict(DEFAULT_STATE)
    state.update(loaded)
    for key in ("log", "codex_log", "history", "achievements"):
        if not isinstance(state.get(key), list):
            state[key] = []
    if not isinstance(state.get("codex_counters"), dict):
        state["codex_counters"] = dict(DEFAULT_STATE["codex_counters"])
    if not isinstance(state.get("seen_days"), list):
        state["seen_days"] = []
    if not isinstance(state.get("daily_bond"), dict):
        state["daily_bond"] = {}
    if not isinstance(state.get("daily_care"), dict):
        state["daily_care"] = {}
    if not isinstance(state.get("cooldowns"), dict):
        state["cooldowns"] = {}
    if not isinstance(state.get("bond_milestones"), list):
        state["bond_milestones"] = []
    try:
        state["friendship_points"] = float(state.get("friendship_points", 0.0) or 0.0)
    except Exception:
        state["friendship_points"] = 0.0
    return state

def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)

def clamp(value: float) -> int:
    return int(max(0, min(100, round(value))))

def add_history(state: dict[str, Any], category: str, msg: str) -> None:
    entry = {"day": time.strftime("%Y-%m-%d"), "time": stamp(), "category": category, "text": msg}
    history = state.get("history") if isinstance(state.get("history"), list) else []
    state["history"] = [entry, *history][:160]

def add_log(state: dict[str, Any], msg: str) -> None:
    state["log"] = [f"{stamp()} — {msg}", *state.get("log", [])][:80]
    add_history(state, "pet", msg)

def add_codex_log(state: dict[str, Any], msg: str) -> None:
    state["codex_log"] = [f"{stamp()} — {msg}", *state.get("codex_log", [])][:80]
    state["log"] = [f"{stamp()} — {msg}", *state.get("log", [])][:80]
    add_history(state, "codex", msg)

def unlock(state: dict[str, Any], key: str) -> None:
    if key in ACHIEVEMENTS and key not in state["achievements"]:
        state["achievements"].append(key)
        add_log(state, f"Achievement: {ACHIEVEMENTS[key]}.")

def clear_runtime_logs(state: dict[str, Any]) -> None:
    state["log"] = ["Pet started."]
    state["codex_log"] = []
    state["history"] = []
    state["codex_status"] = "idle"
    state["codex_last_event"] = ""
    state["codex_last_note"] = ""
    state["codex_last_time"] = 0
    state["codex_silence_notified"] = False
    state["codex_counters"] = {"task_started": 0, "function_call": 0, "error": 0, "final_answer": 0, "events": 0}
    state["last_update"] = now()

def history_lines(state: dict[str, Any]) -> list[str]:
    history = state.get("history")
    if not isinstance(history, list) or not history:
        return ["Nothing here yet."]
    lines: list[str] = []
    last_day = ""
    for entry in history[:80]:
        if not isinstance(entry, dict):
            continue
        day = str(entry.get("day") or "")
        if day != last_day:
            lines.append(day or "No date")
            last_day = day
        lines.append(f"  {entry.get('time', '--:--')} [{entry.get('category', '?')}] {entry.get('text', '')}")
    return lines
