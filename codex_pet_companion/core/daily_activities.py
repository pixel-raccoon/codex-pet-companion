"""
Daily activity state management.

Handles:
- daily activity selection (once per day, per pet, stable)
- idle discovery cooldown / limit (max 2 per day)
- special/milestone activity priority
- activity text assembly for UI consumption

UI should call:
    ensure_activity_state(state, pet_id, codex_status, now_ts)
    activity_text(state, pet_id, pet_name, now_ts)
"""
from __future__ import annotations

import hashlib
import time
from typing import Any

from .phrases import (
    get_daily_activities,
    get_high_bond_activities,
    get_idle_discoveries,
    get_micro_reactions,
    get_special_activities,
)
from .state import now


def _today_key() -> str:
    return time.strftime("%Y-%m-%d")


def _month_day() -> str:
    return time.strftime("%m-%d")


def _activity_pick(items: list[str], seed: str) -> str:
    """Deterministic pick from a list using a hash seed."""
    if not items:
        return ""
    key = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return items[int(key[:8], 16) % len(items)]


def _stat_value(state: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(state.get(key, default) or default)
    except (TypeError, ValueError):
        return default


def _micro_reaction_text(state: dict[str, Any], pet_id: str, current_time: float) -> str:
    """Return a short stat-based reaction when the pet needs attention."""
    bank = get_micro_reactions(pet_id)
    checks = [
        ("low_energy", _stat_value(state, "energy", 100.0) < 22),
        ("low_hunger", _stat_value(state, "hunger", 100.0) < 24),
        ("low_mood", _stat_value(state, "mood", 100.0) < 28),
        ("low_focus", _stat_value(state, "focus", 100.0) < 18),
        ("high_focus", _stat_value(state, "focus", 0.0) > 84 and _stat_value(state, "energy", 100.0) > 35),
    ]
    today = _today_key()
    for key, active in checks:
        if not active:
            continue
        options = bank.get(key, [])
        if options:
            return _activity_pick(options, f"{pet_id}|micro|{today}|{key}|{int(current_time // 900)}")
    return ""


def _high_bond_text(state: dict[str, Any], pet_id: str, current_time: float) -> str:
    """Return an occasional warm high-bond fallback line."""
    from .tamagotchi import days_together, friendship_rank  # local import to avoid circular at module level
    if days_together(state) < 7 and friendship_rank(state) < 4:
        return ""
    options = get_high_bond_activities(pet_id)
    if not options:
        return ""
    today = _today_key()
    return _activity_pick(options, f"{pet_id}|high-bond|{today}|{int(current_time // 3600)}")


def _special_text(state: dict[str, Any], pet_id: str) -> str:
    """Return special-activity text if a milestone or holiday applies today, else ''."""
    from .tamagotchi import days_together  # local import to avoid circular at module level
    bank = get_special_activities(pet_id)
    days = days_together(state)
    milestone_key = f"days_{days}"
    if milestone_key in bank:
        return str(bank[milestone_key])
    md = _month_day()
    if md == "01-01":
        return str(bank.get("holiday_new_year", ""))
    if md == "10-31":
        return str(bank.get("holiday_halloween", ""))
    first_seen = str(state.get("first_seen_date") or "").strip()
    if first_seen and len(first_seen) >= 10 and first_seen[5:10] == md and days > 1:
        return str(bank.get("launch_anniversary", ""))
    return ""


def ensure_activity_state(
    state: dict[str, Any],
    pet_id: str,
    codex_status: str = "idle",
    current_time: float | None = None,
) -> None:
    """
    Ensure daily_activity and idle_activity are properly initialised for today.

    Call once per tick (or after pet change). Safe to call repeatedly.
    """
    if current_time is None:
        current_time = now()
    today = _today_key()

    # --- daily_activity: one text per day, per pet ---
    daily = state.get("daily_activity")
    if not isinstance(daily, dict):
        daily = {}
    if str(daily.get("date") or "") != today or str(daily.get("pet_id") or "") != pet_id:
        special = _special_text(state, pet_id)
        if special:
            text = special
            kind = "special"
        else:
            bank = get_daily_activities(pet_id)
            text = _activity_pick(bank, f"{pet_id}|daily|{today}")
            kind = "daily"
        state["daily_activity"] = {
            "date": today,
            "pet_id": pet_id,
            "kind": kind,
            "text": text,
        }
        state["idle_activity"] = {"date": today, "count": 0, "text": "", "until": 0.0}
        state["idle_activity_next_at"] = current_time + 1800.0

    # --- idle_activity: date rollover ---
    idle = state.get("idle_activity")
    if not isinstance(idle, dict):
        idle = {}
    if str(idle.get("date") or "") != today:
        state["idle_activity"] = {"date": today, "count": 0, "text": "", "until": 0.0}
        if float(state.get("idle_activity_next_at", 0.0) or 0.0) <= 0.0:
            state["idle_activity_next_at"] = current_time + 1800.0

    # --- idle_activity: suppress while Codex is active or notification live ---
    if codex_status != "idle":
        wait_target = current_time + 1800.0
        state["idle_activity_next_at"] = max(
            float(state.get("idle_activity_next_at", 0.0) or 0.0), wait_target
        )
        return

    if float(state.get("codex_notification_until", 0.0) or 0.0) > current_time:
        return

    idle = state.get("idle_activity")
    if not isinstance(idle, dict):
        idle = {"date": today, "count": 0, "text": "", "until": 0.0}
    count = int(idle.get("count", 0) or 0)
    next_at = float(state.get("idle_activity_next_at", 0.0) or 0.0)
    if count >= 2 or current_time < next_at:
        return

    bank = get_idle_discoveries(pet_id)
    text = _activity_pick(bank, f"{pet_id}|idle|{today}|{count}")
    state["idle_activity"] = {
        "date": today,
        "count": count + 1,
        "text": text,
        "until": current_time + 5400.0,
    }
    state["idle_activity_next_at"] = current_time + (7200.0 if count == 0 else 21600.0)


def activity_text(
    state: dict[str, Any],
    pet_id: str,
    pet_name: str,
    current_time: float | None = None,
) -> str:
    """
    Return the activity text to display in the UI activity card.

    Priority:
    1. Active Codex notification
    2. Codex status running / review / error
    3. Resting
    4. Active idle discovery (if within its 'until' window)
    5. Stat-based micro reaction
    6. High-bond warm variant
    7. Daily activity text
    8. Fallback
    """
    if current_time is None:
        current_time = now()

    notification = str(state.get("codex_notification") or "").strip()
    if notification:
        subtitle = str(state.get("codex_notification_subtitle") or "").strip()
        return f"{notification}\n{subtitle}" if subtitle else notification

    status = str(state.get("codex_status") or "idle")
    task_title = str(state.get("codex_current_task_title") or "").strip()
    last_note = str(state.get("codex_last_note") or "").strip()

    if status == "running":
        if task_title:
            return f"Codex is working on: {task_title}\n{pet_name} is keeping a very serious eye on it."
        if last_note:
            return f"Codex is busy: {last_note}\n{pet_name} is following along."
        return f"{pet_name} is watching Codex work and trying not to look impressed."
    if status == "review":
        if task_title:
            return f"Review ready: {task_title}\n{pet_name} clearly wants a look."
        return f"{pet_name} found something worth reviewing."
    if status == "error":
        if last_note:
            return f"Codex hit an error: {last_note}\n{pet_name} is pretending this was expected."
        return f"{pet_name} noticed the error and is pretending this was expected."

    if float(state.get("rest_until", 0.0) or 0.0) > current_time:
        return f"{pet_name} is resting for a bit. Let the tiny creature recover."

    idle = state.get("idle_activity")
    if isinstance(idle, dict) and float(idle.get("until", 0.0) or 0.0) > current_time:
        text = str(idle.get("text") or "").strip()
        if text:
            return text

    micro = _micro_reaction_text(state, pet_id, current_time)
    if micro:
        return micro

    high_bond = _high_bond_text(state, pet_id, current_time)
    if high_bond:
        return high_bond

    daily = state.get("daily_activity")
    if isinstance(daily, dict):
        text = str(daily.get("text") or "").strip()
        if text:
            return text

    return f"Nothing dramatic yet. {pet_name} is quietly looking for trouble."
