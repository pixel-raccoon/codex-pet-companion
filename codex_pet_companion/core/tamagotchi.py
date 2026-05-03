from __future__ import annotations

import time
from typing import Any

from .constants import ACHIEVEMENTS, EVENT_TO_ANIMATION, TRAITS
from .phrases import (
    care_line,
    chat_response,
    get_friendship_titles,
    get_milestones,
    get_special_day_line,
    hint_line,
    phrase,
)
from .text_profiles import text_profile_id
from .state import add_codex_log, add_log, clamp, now, unlock

def level_value(state: dict[str, Any]) -> int:
    return max(1, int(state.get("level", 1) or 1))

FRIENDSHIP_THRESHOLDS = [0, 20, 50, 90, 140, 200, 270, 350, 440, 540, 650]
# Friendship titles are now stored in phrases/; use get_friendship_titles(pet_id)

# Milestones and special day lines are now stored in phrases/; use get_milestones() / get_special_day_line()

MILESTONE_ACHIEVEMENTS = {
    7: "milestone_7_days",
    30: "milestone_30_days",
    100: "milestone_100_days",
    365: "milestone_365_days",
}


def today_key() -> str:
    return time.strftime("%Y-%m-%d")

def special_seen(state: dict[str, Any]) -> list[str]:
    seen = state.get("special_day_seen")
    if not isinstance(seen, list):
        seen = []
        state["special_day_seen"] = seen
    return seen

def mark_special_once(state: dict[str, Any], key: str, message: str, achievement_id: str = "") -> None:
    seen = special_seen(state)
    today = today_key()
    token = f"{today}:{key}"
    if token in seen:
        return
    seen.append(token)
    del seen[:-80]
    add_log(state, message)
    if achievement_id:
        unlock(state, achievement_id)

def special_day_message(event_id: str, pet_id: str) -> str:
    return get_special_day_line(event_id, pet_id)

def check_special_days(state: dict[str, Any], pet_id: str) -> None:
    today = today_key()
    month_day = time.strftime("%m-%d")

    if month_day == "01-01":
        mark_special_once(state, "holiday_new_year", special_day_message("holiday_new_year", pet_id), "holiday_new_year")
    if month_day == "10-31":
        mark_special_once(state, "holiday_halloween", special_day_message("holiday_halloween", pet_id), "holiday_halloween")

    first_seen = str(state.get("first_seen_date") or "")
    if first_seen and first_seen != today and len(first_seen) >= 10 and first_seen[5:10] == month_day:
        mark_special_once(
            state,
            f"holiday_first_launch_anniversary:{first_seen}",
            special_day_message("holiday_first_launch_anniversary", pet_id),
            "holiday_first_launch_anniversary",
        )


def ensure_bond_state(state: dict[str, Any], pet_id: str = "") -> None:
    today = today_key()
    if not state.get("first_seen_date"):
        state["first_seen_date"] = today
    if not isinstance(state.get("seen_days"), list):
        state["seen_days"] = []
    if today not in state["seen_days"]:
        state["seen_days"].append(today)
        state["seen_days"] = sorted(set(str(day) for day in state["seen_days"] if day))
        days = len(state["seen_days"])
        if days > 1:
            add_log(state, milestone_message(days, pet_id))
            achievement_id = MILESTONE_ACHIEVEMENTS.get(days)
            if achievement_id:
                unlock(state, achievement_id)
        state["last_seen_date"] = today
    if not state.get("last_seen_date"):
        state["last_seen_date"] = today
    if not isinstance(state.get("daily_bond"), dict):
        state["daily_bond"] = {}
    state["daily_bond"].setdefault(today, {})
    if not isinstance(state.get("bond_milestones"), list):
        state["bond_milestones"] = []
    try:
        state["friendship_points"] = float(state.get("friendship_points", 0.0) or 0.0)
    except Exception:
        state["friendship_points"] = 0.0
    state["friendship_rank"] = friendship_rank(state)
    check_special_days(state, pet_id)

def days_together(state: dict[str, Any]) -> int:
    seen = state.get("seen_days")
    if isinstance(seen, list) and seen:
        return len(set(str(day) for day in seen if day))
    return 1

def milestone_message(days: int, pet_id: str) -> str:
    milestones = get_milestones(pet_id)
    return milestones.get(days, f"Day together: {days}.")

def friendship_rank(state: dict[str, Any]) -> int:
    points = float(state.get("friendship_points", 0.0) or 0.0)
    rank = 0
    for index, threshold in enumerate(FRIENDSHIP_THRESHOLDS):
        if points >= threshold:
            rank = index
    return min(rank, len(FRIENDSHIP_THRESHOLDS) - 1)

def friendship_title(state: dict[str, Any], pet_id: str) -> str:
    rank = friendship_rank(state)
    titles = get_friendship_titles(pet_id)
    return titles[min(rank, len(titles) - 1)]

def friendship_hearts(state: dict[str, Any]) -> str:
    rank = friendship_rank(state)
    filled = min(5, max(0, round(rank / 2)))
    return "♥" * filled + "♡" * (5 - filled)

def friendship_progress_line(state: dict[str, Any], pet_id: str) -> str:
    title = friendship_title(state, pet_id)
    return f"{title}\n{friendship_hearts(state)}"

def friendship_progress_ratio(state: dict[str, Any]) -> float:
    rank = friendship_rank(state)
    if rank >= len(FRIENDSHIP_THRESHOLDS) - 1:
        return 1.0
    points = float(state.get("friendship_points", 0.0) or 0.0)
    low = FRIENDSHIP_THRESHOLDS[rank]
    high = FRIENDSHIP_THRESHOLDS[rank + 1]
    if high <= low:
        return 1.0
    return max(0.0, min(1.0, (points - low) / (high - low)))

def add_bond(state: dict[str, Any], reason: str, amount: float, pet_name: str, pet_id: str, daily_limit: int = 1) -> None:
    ensure_bond_state(state, pet_id)
    if not friendship_growth_allowed(state):
        return
    today = today_key()
    daily = state["daily_bond"].setdefault(today, {})
    count = int(daily.get(reason, 0) or 0)
    if count >= daily_limit:
        return
    daily[reason] = count + 1
    before = friendship_rank(state)
    state["friendship_points"] = max(0.0, float(state.get("friendship_points", 0.0) or 0.0) + amount)
    after = friendship_rank(state)
    state["friendship_rank"] = after
    if after > before:
        add_log(state, f"Friendship grew: {friendship_title(state, pet_id)}.")

def add_xp(state: dict[str, Any], amount: int) -> None:
    # Legacy field kept for old saves. Friendship is the visible progression now.
    state["xp"] = int(state.get("xp", 0)) + amount

def current_emotion(state: dict[str, Any]) -> str:
    if float(state.get("emotion_until", 0) or 0) > now():
        return str(state.get("emotion") or "neutral")
    return "neutral"

def set_emotion(state: dict[str, Any], emotion: str, seconds: float = 45.0) -> None:
    state["emotion"] = emotion
    state["emotion_until"] = now() + seconds

def increment_counter(state: dict[str, Any], key: str) -> int:
    counters = state.get("counters")
    if not isinstance(counters, dict):
        counters = {}
        state["counters"] = counters
    value = int(counters.get(key, 0) or 0) + 1
    counters[key] = value
    return value

def trait_mult(trait_key: str, name: str) -> float:
    return float(TRAITS.get(trait_key, TRAITS["neutral"]).get(name, 1.0))

def clamp_float(value: float) -> float:
    return max(0.0, min(100.0, float(value)))

def daily_record(state: dict[str, Any]) -> dict[str, Any]:
    day = today_key()
    if not isinstance(state.get("daily_care"), dict):
        state["daily_care"] = {}
    if state.get("current_day") and state.get("current_day") != day:
        close_previous_day(state, str(state.get("current_day") or ""))
    state["current_day"] = day
    record = state["daily_care"].setdefault(day, {})
    if not isinstance(record, dict):
        record = {}
        state["daily_care"][day] = record
    for key in ["feed", "pet", "play", "rest", "codex_tasks", "codex_tools", "codex_reviews", "codex_errors", "focused_seconds"]:
        record.setdefault(key, 0)
    return record

def close_previous_day(state: dict[str, Any], day: str) -> None:
    if not day:
        return
    care = state.get("daily_care") if isinstance(state.get("daily_care"), dict) else {}
    record = care.get(day) if isinstance(care.get(day), dict) else {}
    if not record or record.get("closed"):
        return
    good = int(record.get("feed", 0) or 0) >= 1 and int(record.get("pet", 0) or 0) >= 1 and int(record.get("rest", 0) or 0) >= 1
    work = int(record.get("codex_tasks", 0) or 0) + int(record.get("codex_reviews", 0) or 0)
    if good:
        state["friendship_points"] = max(0.0, float(state.get("friendship_points", 0.0) or 0.0) + (2.0 if work else 1.2))
        state["friendship_rank"] = friendship_rank(state)
        record["good_care"] = True
    record["closed"] = True

def inc_daily(state: dict[str, Any], key: str, amount: float = 1.0) -> float:
    record = daily_record(state)
    value = float(record.get(key, 0) or 0) + amount
    record[key] = value
    return value

def cooldowns(state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(state.get("cooldowns"), dict):
        state["cooldowns"] = {}
    return state["cooldowns"]

def cooldown_left(state: dict[str, Any], key: str) -> float:
    return max(0.0, float(cooldowns(state).get(key, 0.0) or 0.0) - now())

def set_cooldown(state: dict[str, Any], key: str, seconds: float) -> None:
    cooldowns(state)[key] = now() + seconds

def minutes_text(seconds: float) -> str:
    minutes = max(1, round(seconds / 60.0))
    if minutes % 10 == 1 and minutes % 100 != 11:
        return f"{minutes} minute"
    if 2 <= minutes % 10 <= 4 and not 12 <= minutes % 100 <= 14:
        return f"{minutes} minutes"
    return f"{minutes} minutes"

def deny_action(state: dict[str, Any], action: str, message: str) -> None:
    state["last_care_denial"] = action
    state["last_care_denial_until"] = now() + 30.0
    state["event_status"] = message
    state["event_until"] = now() + 4.0
    add_log(state, message)

def is_resting(state: dict[str, Any]) -> bool:
    return float(state.get("rest_until", 0.0) or 0.0) > now()

def interrupt_rest(state: dict[str, Any], pet_name: str, pet_id: str) -> bool:
    if not is_resting(state):
        return False
    state["rest_until"] = 0.0
    msg = care_line(pet_id, pet_name, "rest_interrupt")
    add_log(state, msg)
    return True

def care_mode_multiplier(config: dict[str, Any]) -> float:
    mode = str(config.get("careMode") or "normal").lower()
    if mode == "soft":
        return 0.45
    if mode == "strict":
        return 1.85
    return 1.0

def decay_multiplier(state: dict[str, Any]) -> float:
    return max(0.60, 1.0 - friendship_rank(state) * 0.025)

def xp_multiplier(state: dict[str, Any]) -> float:
    mood = int(state.get("mood", 50) or 50)
    focus = int(state.get("focus", 50) or 50)
    if mood >= 75 and focus >= 60:
        return 1.25
    if mood < 25:
        return 0.85
    return 1.0

def add_scaled_xp(state: dict[str, Any], amount: int) -> None:
    add_xp(state, max(1, round(amount * xp_multiplier(state))))


def stat_value(state: dict[str, Any], key: str, default: float = 50.0) -> float:
    raw = state.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default

def clamp_decay_elapsed(elapsed: float, config: dict[str, Any]) -> float:
    cap = float(config.get("offlineDecayCapSeconds", config.get("offlineDecayMaxSeconds", 28800)) or 28800)
    if elapsed <= 0:
        return 0.0
    return min(elapsed, cap)

def recovery_flags(state: dict[str, Any]) -> dict[str, bool]:
    flags = state.get("recovery_flags")
    if not isinstance(flags, dict):
        flags = {}
        state["recovery_flags"] = flags
    return flags

def critical_seen(state: dict[str, Any]) -> dict[str, float]:
    seen = state.get("critical_event_seen")
    if not isinstance(seen, dict):
        seen = {}
        state["critical_event_seen"] = seen
    return seen

def recovery_message(flag: str) -> str:
    return {
        "hunger": "Lumisprout is back on its paws after eating.",
        "energy": "Lumisprout recovered a little after resting.",
        "mood": "Lumisprout stopped staring into the void.",
        "focus": "Lumisprout gathered its thoughts again.",
    }.get(flag, "Lumisprout recovered a little.")

def mark_critical_once(state: dict[str, Any], key: str, message: str, config: dict[str, Any]) -> None:
    seen = critical_seen(state)
    current = now()
    cooldown = float(config.get("criticalEventCooldownSeconds", 21600) or 21600)
    last = float(seen.get(key, 0.0) or 0.0)
    if current - last >= cooldown:
        add_log(state, message)
        seen[key] = current

def update_recovery_state(state: dict[str, Any], config: dict[str, Any]) -> None:
    flags = recovery_flags(state)
    floor = int(config.get("criticalRecoveryFloor", 12) or 12)
    checks = {
        "hunger": ("hunger", "Lumisprout is completely hungry."),
        "energy": ("energy", "Lumisprout is completely worn out."),
        "mood": ("mood", "Lumisprout is completely gloomy."),
        "focus": ("focus", "Lumisprout is completely scattered."),
    }

    for flag, (stat, message) in checks.items():
        value = int(stat_value(state, stat, 50.0))
        if value <= 0 and not bool(flags.get(flag, False)):
            flags[flag] = True
            mark_critical_once(state, flag, message, config)
        elif bool(flags.get(flag, False)) and value >= floor:
            flags[flag] = False
            add_log(state, recovery_message(flag))

    state["critical_growth_blocked"] = any(bool(flags.get(key, False)) for key in checks)

def friendship_growth_allowed(state: dict[str, Any]) -> bool:
    if bool(state.get("critical_growth_blocked", False)):
        return False
    return not any(bool(value) for value in recovery_flags(state).values())

def decayed(state: dict[str, Any], config: dict[str, Any], trait_key: str) -> dict[str, Any]:
    ensure_bond_state(state)
    daily_record(state)
    refresh_codex_status(state)
    if not config.get("decayEnabled", True):
        state["last_update"] = now()
        update_recovery_state(state, config)
        return state

    t = now()
    last = float(state.get("last_update") or t)
    raw_dt = t - last
    dt = clamp_decay_elapsed(raw_dt, config)
    if dt <= 0:
        update_recovery_state(state, config)
        return state

    offline_threshold = float(config.get("offlineSleepThresholdSeconds", 300) or 300)
    offline_sleep = raw_dt >= offline_threshold

    mult = care_mode_multiplier(config)
    rate = float(config.get("decayRate", 1.0) or 1.0)
    resting = is_resting(state)
    codex_status = str(state.get("codex_status") or "idle")
    codex_fresh = float(state.get("codex_status_until", 0) or 0) > t
    active_codex = codex_fresh and codex_status == "running"

    hunger = stat_value(state, "hunger", 50.0)
    energy = stat_value(state, "energy", 50.0)
    mood = stat_value(state, "mood", 50.0)
    focus = stat_value(state, "focus", 50.0)

    hunger -= dt * (1.0 / 2100.0) * rate * mult * trait_mult(trait_key, "hunger_decay_mult")

    if offline_sleep:
        energy += dt * (1.0 / 900.0) * rate
        focus -= dt * (1.0 / 7200.0) * rate * trait_mult(trait_key, "focus_decay_mult")
        mood -= dt * (1.0 / 7200.0) * rate * mult * trait_mult(trait_key, "mood_decay_mult")
    elif resting:
        energy += dt * (1.0 / 55.0) * rate
        mood += dt * (1.0 / 1500.0) * rate
        focus += dt * (1.0 / 3000.0) * rate
    else:
        energy -= dt * (1.0 / 3600.0) * rate * mult * trait_mult(trait_key, "energy_decay_mult")
        if active_codex:
            energy -= dt * (1.0 / 2200.0) * rate * trait_mult(trait_key, "energy_decay_mult")
            focus += dt * (1.0 / 360.0) * rate
            inc_daily(state, "focused_seconds", dt)
        else:
            focus -= dt * (1.0 / 3600.0) * rate * trait_mult(trait_key, "focus_decay_mult")

    if hunger < 25:
        mood -= dt * (1.0 / 2400.0) * rate
    elif hunger > 55 and energy > 35:
        mood += dt * (1.0 / 5400.0) * rate
    if energy < 20 and not offline_sleep:
        mood -= dt * (1.0 / 3000.0) * rate
    if codex_fresh and codex_status == "error" and not resting and not offline_sleep:
        mood -= dt * (1.0 / 1800.0) * rate
        focus -= dt * (1.0 / 1800.0) * rate

    state["hunger"] = clamp_float(hunger)
    state["energy"] = clamp_float(energy)
    state["mood"] = clamp_float(mood)
    state["focus"] = clamp_float(focus)
    state["last_update"] = t
    update_recovery_state(state, config)
    return state


def care_state(state: dict[str, Any]) -> tuple[str, str]:
    hunger = int(stat_value(state, "hunger", 50.0))
    mood = int(stat_value(state, "mood", 50.0))
    energy = int(stat_value(state, "energy", 50.0))
    focus = int(stat_value(state, "focus", 50.0))
    codex_status = str(state.get("codex_status") or "idle")
    codex_fresh = float(state.get("codex_status_until", 0) or 0) > now()
    flags = recovery_flags(state)

    if is_resting(state):
        return "☾", "Resting"
    if bool(flags.get("hunger", False)):
        return "🍖", "Recovery: hunger"
    if bool(flags.get("energy", False)):
        return "☾", "Recovery: tiredness"
    if bool(flags.get("mood", False)):
        return "☁", "Recovery: mood"
    if bool(flags.get("focus", False)):
        return "◇", "Recovery: focus"

    if hunger < 25:
        return "🍖", "Hungry"
    if energy < 20:
        return "⚡", "Tired"
    if mood < 25:
        return "☁", "Upset"
    if codex_fresh and codex_status == "running" and focus > 60:
        return "◆", "Focused"
    if int(state.get("busy_streak", 0) or 0) >= 5 and energy < 45:
        return "◇", "Overloaded"
    if mood > 78 and energy > 55 and hunger > 50:
        return "✦", "Happy"
    return "☘", "Calm"


def set_event(state: dict[str, Any], event: str, pet_name: str, pet_id: str, custom_status: str = "") -> None:
    state["current_event"] = EVENT_TO_ANIMATION.get(event, "idle")
    state["event_until"] = now() + {
        "codex_running": 2.4, "review_ready": 4.5, "error": 5.5, "note": 2.2,
        "feed": 2.0, "pet": 1.8, "play": 2.0, "rest": 2.8
    }.get(event, 2.0)
    state["event_status"] = custom_status or phrase(event, pet_name, pet_id)

def action_quality(state: dict[str, Any], action: str) -> tuple[float, str]:
    hunger = int(state.get("hunger", 50) or 50)
    energy = int(state.get("energy", 50) or 50)
    mood = int(state.get("mood", 50) or 50)
    if action == "play" and energy < 18:
        return 0.35, "The pet is too tired: playing barely helps."
    if action == "play" and hunger < 18:
        return 0.55, "The pet is hungry: it can play, but without enthusiasm."
    if action == "pet" and hunger < 18:
        return 0.55, "Petting works worse on an empty stomach."
    if action == "feed" and mood < 18:
        return 0.85, "The pet eats, but still looks grumpy."
    return 1.0, ""

def update_codex_status(
    state: dict[str, Any],
    status: str,
    event: str,
    note: str = "",
    session_file: str = "",
    config: dict[str, Any] | None = None,
) -> None:
    current = now()
    state["codex_status"] = status
    state["codex_last_event"] = event
    state["codex_last_note"] = note
    state["codex_last_time"] = current
    if session_file:
        state["codex_session_file"] = session_file
        state["codex_session_active"] = True

    ttl_defaults = {"running": 90.0, "review": 600.0, "error": 600.0, "waiting": 180.0}
    ttl_keys = {
        "running": "codexRunningTtlSeconds",
        "review": "codexReviewTtlSeconds",
        "error": "codexErrorTtlSeconds",
        "waiting": "longSilenceSeconds",
    }
    ttl = ttl_defaults.get(status, 90.0)
    if config is not None:
        ttl = float(config.get(ttl_keys.get(status, "codexRunningTtlSeconds"), ttl) or ttl)
    state["codex_status_until"] = current + ttl

    notification_ttl = 8.0
    if config is not None:
        notification_ttl = float(config.get("codexNotificationSeconds", 8) or 8)
    state["codex_notification"] = note
    state["codex_notification_title"] = note
    state["codex_notification_subtitle"] = ""
    state["codex_notification_until"] = current + notification_ttl
    state["codex_silence_notified"] = False

    counters = state.get("codex_counters")
    if not isinstance(counters, dict):
        counters = {"task_started": 0, "function_call": 0, "error": 0, "final_answer": 0, "events": 0}
        state["codex_counters"] = counters
    counters["events"] = int(counters.get("events", 0) or 0) + 1
    if event in counters:
        counters[event] = int(counters.get(event, 0) or 0) + 1

def refresh_codex_status(state: dict[str, Any]) -> None:
    current = now()
    status = str(state.get("codex_status") or "idle")
    until = float(state.get("codex_status_until", 0.0) or 0.0)
    if status not in {"idle", "quiet"} and until and current > until:
        state["codex_status"] = "idle"
        state["codex_session_active"] = False
    if current > float(state.get("codex_notification_until", 0.0) or 0.0):
        state["codex_notification"] = ""
        state["codex_notification_title"] = ""
        state["codex_notification_subtitle"] = ""


# care_line() and hint_line() are imported from .phrases above.

def apply_action(
    state: dict[str, Any],
    action: str,
    note: str,
    pet_name: str,
    pet_id: str,
    trait_key: str,
    session_file: str = "",
    config: dict[str, Any] | None = None,
) -> None:
    action = action.strip()
    daily_record(state)
    config = config or {}

    if action == "feed":
        left = cooldown_left(state, "feed")
        if left > 0:
            deny_action(state, "feed", care_line(pet_id, pet_name, "feed_cooldown", minutes=minutes_text(left)))
            update_recovery_state(state, config)
            return
        if float(state.get("hunger", 50) or 50) >= 85:
            set_cooldown(state, "feed", 5 * 60)
            deny_action(state, "feed", care_line(pet_id, pet_name, "feed_full"))
            update_recovery_state(state, config)
            return
        interrupt_rest(state, pet_name, pet_id)
        before = float(state.get("hunger", 50) or 50)
        gain = 34 if before < 25 else 26 if before < 55 else 18
        state["hunger"] = clamp_float(before + gain)
        state["mood"] = clamp_float(float(state.get("mood", 50) or 50) + (8 if before < 55 else 4))
        set_cooldown(state, "feed", 20 * 60)
        inc_daily(state, "feed")
        set_event(state, "feed", pet_name, pet_id)
        msg = care_line(pet_id, pet_name, "feed_hungry" if before < 25 else "feed")
        state["event_status"] = msg
        set_emotion(state, "happy", 55)
        if increment_counter(state, "feed") >= 5:
            unlock(state, "fed_5")
        add_bond(state, "feed", 1.6 if before < 55 else 0.7, pet_name, pet_id, daily_limit=2)
        add_log(state, msg)
        unlock(state, "first_feed")
        if state["hunger"] >= 95:
            unlock(state, "well_fed")
        update_recovery_state(state, config)
        return

    if action == "pet":
        left = cooldown_left(state, "pet")
        if left > 0:
            deny_action(state, "pet", care_line(pet_id, pet_name, "pet_cooldown", minutes=minutes_text(left)))
            update_recovery_state(state, config)
            return
        count = inc_daily(state, "pet")
        effect = 14 if count <= 3 else 5 if count <= 6 else 0
        if effect <= 0:
            set_cooldown(state, "pet", 4 * 60)
            deny_action(state, "pet", care_line(pet_id, pet_name, "pet_spam"))
            update_recovery_state(state, config)
            return
        interrupt_rest(state, pet_name, pet_id)
        state["mood"] = clamp_float(float(state.get("mood", 50) or 50) + effect)
        if str(state.get("codex_status") or "") == "error":
            state["mood"] = clamp_float(float(state.get("mood", 50) or 50) + 6)
            add_bond(state, "comfort_after_error", 1.5, pet_name, pet_id, daily_limit=1)
        set_cooldown(state, "pet", 3 * 60)
        set_event(state, "pet", pet_name, pet_id)
        set_emotion(state, "happy", 45)
        add_bond(state, "pet", 0.9, pet_name, pet_id, daily_limit=3)
        msg = care_line(pet_id, pet_name, "pet")
        state["event_status"] = msg
        add_log(state, msg)
        update_recovery_state(state, config)
        return

    if action == "play":
        resting_before_play = is_resting(state)
        left = cooldown_left(state, "play")
        if left > 0:
            deny_action(state, "play", care_line(pet_id, pet_name, "play_cooldown", minutes=minutes_text(left)))
            update_recovery_state(state, config)
            return
        if float(state.get("energy", 50) or 50) < 25:
            deny_action(state, "play", care_line(pet_id, pet_name, "play_tired"))
            update_recovery_state(state, config)
            return
        if resting_before_play:
            interrupt_rest(state, pet_name, pet_id)
        state["mood"] = clamp_float(float(state.get("mood", 50) or 50) + 16)
        state["focus"] = clamp_float(float(state.get("focus", 50) or 50) + 8)
        state["energy"] = clamp_float(float(state.get("energy", 50) or 50) - 14 * trait_mult(trait_key, "play_energy_mult"))
        state["hunger"] = clamp_float(float(state.get("hunger", 50) or 50) - 4)
        set_cooldown(state, "play", 12 * 60)
        inc_daily(state, "play")
        set_event(state, "play", pet_name, pet_id)
        set_emotion(state, "curious", 45)
        if increment_counter(state, "play") >= 5:
            unlock(state, "play_5")
        add_bond(state, "play", 1.4, pet_name, pet_id, daily_limit=1)
        msg = care_line(pet_id, pet_name, "play")
        state["event_status"] = msg
        add_log(state, msg)
        update_recovery_state(state, config)
        return

    if action == "rest":
        if is_resting(state):
            deny_action(state, "rest", care_line(pet_id, pet_name, "rest_already"))
            update_recovery_state(state, config)
            return
        left = cooldown_left(state, "rest")
        if left > 0:
            deny_action(state, "rest", care_line(pet_id, pet_name, "rest_cooldown", minutes=minutes_text(left)))
            update_recovery_state(state, config)
            return
        energy_before = float(state.get("energy", 50) or 50)
        low_energy = energy_before < 45
        if energy_before < 25:
            state["energy"] = clamp_float(energy_before + 12)
        elif energy_before < 45:
            state["energy"] = clamp_float(energy_before + 7)
        state["rest_until"] = now() + 20 * 60
        set_cooldown(state, "rest", 30 * 60)
        inc_daily(state, "rest")
        set_event(state, "rest", pet_name, pet_id)
        set_emotion(state, "neutral", 10)
        add_bond(state, "rest", 1.5 if low_energy else 0.7, pet_name, pet_id, daily_limit=1)
        msg = care_line(pet_id, pet_name, "rest")
        state["event_status"] = msg
        add_log(state, msg)
        update_recovery_state(state, config)
        return

    if action in {"note", "chat"}:
        interrupt_rest(state, pet_name, pet_id)
        response = chat_response(note, pet_name, pet_id)
        set_event(state, "note", pet_name, pet_id, response)
        set_emotion(state, "curious", 35)
        state["focus"] = clamp_float(float(state.get("focus", 50) or 50) + 1)
        if increment_counter(state, "chat") >= 5:
            unlock(state, "chatty_pet")
        add_bond(state, "chat", 0.5, pet_name, pet_id, daily_limit=2)
        add_log(state, response)
        update_recovery_state(state, config)
        return

    if action in {"codex_running", "codex"}:
        was_resting = interrupt_rest(state, pet_name, pet_id)
        inc_daily(state, "codex_tools" if "tool" in note.lower() else "codex_tasks")
        state["focus"] = clamp_float(float(state.get("focus", 50) or 50) + (6 if float(state.get("energy", 50) or 50) > 30 else 2))
        state["energy"] = clamp_float(float(state.get("energy", 50) or 50) - (1.0 if was_resting else 2.0))
        update_codex_status(state, "running", "function_call" if "tool" in note.lower() else "task_started", note or "Codex is working", session_file, config)
        state["busy_streak"] = int(state.get("busy_streak", 0) or 0) + 1
        if state["busy_streak"] >= 5:
            unlock(state, "busy_streak_5")
        state["error_streak"] = 0
        set_event(state, "codex_running", pet_name, pet_id)
        set_emotion(state, "focused", 50)
        add_bond(state, "codex_running", 0.35, pet_name, pet_id, daily_limit=4)
        add_codex_log(state, note or state["event_status"])
        unlock(state, "bridge_first_event")
        if state["focus"] >= 90:
            unlock(state, "codex_sprinter")
        update_recovery_state(state, config)
        return

    if action in {"review_ready", "review"}:
        inc_daily(state, "codex_reviews")
        state["focus"] = clamp_float(float(state.get("focus", 50) or 50) + 4)
        state["mood"] = clamp_float(float(state.get("mood", 50) or 50) + 7)
        update_codex_status(state, "review", "final_answer", note or "Codex is ready to review", session_file, config)
        state["review_streak"] = int(state.get("review_streak", 0) or 0) + 1
        state["busy_streak"] = 0
        if state["review_streak"] >= 3:
            unlock(state, "review_streak_3")
        state["error_streak"] = 0
        set_event(state, "review_ready", pet_name, pet_id)
        set_emotion(state, "proud", 55)
        add_bond(state, "review", 1.6 * trait_mult(trait_key, "review_xp_mult"), pet_name, pet_id, daily_limit=3)
        add_codex_log(state, note or state["event_status"])
        unlock(state, "first_review")
        unlock(state, "bridge_first_event")
        update_recovery_state(state, config)
        return

    if action in {"error", "fail", "failed"}:
        inc_daily(state, "codex_errors")
        extra = 5 if int(state.get("mood", 50) or 50) < 25 else 0
        state["mood"] = clamp_float(float(state.get("mood", 50) or 50) - (12 + extra) * trait_mult(trait_key, "error_mood_mult"))
        state["focus"] = clamp_float(float(state.get("focus", 50) or 50) - 10)
        update_codex_status(state, "error", "error", note or "Codex reported an error", session_file, config)
        state["review_streak"] = 0
        state["busy_streak"] = 0
        state["error_streak"] = int(state.get("error_streak", 0)) + 1
        set_event(state, "error", pet_name, pet_id)
        set_emotion(state, "sad", 70)
        add_bond(state, "error_seen", 0.2, pet_name, pet_id, daily_limit=2)
        add_codex_log(state, note or state["event_status"])
        unlock(state, "first_error")
        unlock(state, "bridge_first_event")
        if state["error_streak"] >= 3:
            unlock(state, "error_streak_3")
        update_recovery_state(state, config)
        return

    if action in {"codex_inactive", "inactive", "quiet"}:
        state["codex_status"] = "idle"
        state["codex_session_active"] = False
        state["codex_status_until"] = 0
        state["codex_notification"] = ""
        state["codex_notification_title"] = ""
        state["codex_notification_subtitle"] = ""
        state["codex_notification_until"] = 0
        state["codex_last_event"] = "long_silence"
        update_recovery_state(state, config)
        return

def human_codex_event(event: str) -> str:
    names = {
        "final_answer": "ready",
        "task_started": "started task",
        "function_call": "working",
        "error": "error",
        "long_silence": "quiet",
    }
    return names.get(event, event)

def codex_short_line(state: dict[str, Any]) -> str:
    refresh_codex_status(state)
    status = str(state.get("codex_status") or "idle")
    names = {
        "idle": "quiet",
        "quiet": "quiet",
        "running": "working",
        "review": "ready",
        "error": "error",
        "waiting": "quiet",
    }
    return f"Codex: {names.get(status, status)}"

def codex_status_line(state: dict[str, Any]) -> str:
    refresh_codex_status(state)
    status = str(state.get("codex_status") or "idle")
    names = {
        "idle": "quiet",
        "quiet": "quiet",
        "running": "working",
        "review": "ready to review",
        "error": "error",
        "waiting": "quiet for a while",
    }
    return f"Codex: {names.get(status, status)}"

def codex_session_lines(state: dict[str, Any]) -> list[str]:
    counters = state.get("codex_counters") if isinstance(state.get("codex_counters"), dict) else {}
    return [
        codex_status_line(state),
        "",
        f"Events: {counters.get('events', 0)}",
        f"Tasks started: {counters.get('task_started', 0)}",
        f"Tool calls: {counters.get('function_call', 0)}",
        f"Errors: {counters.get('error', 0)}",
        f"Final answer / review: {counters.get('final_answer', 0)}",
        "",
        "Session file:",
        str(state.get("codex_session_file") or "not found"),
    ]

def maybe_mark_codex_silence(state: dict[str, Any], config: dict[str, Any]) -> bool:
    refresh_codex_status(state)
    if str(state.get("codex_status") or "") != "running" or bool(state.get("codex_silence_notified", False)):
        return False
    last = float(state.get("codex_last_time") or 0)
    threshold = float(config.get("longSilenceSeconds", 180) or 180)
    if not last or now() - last < threshold:
        return False
    state["codex_status"] = "waiting"
    state["codex_status_until"] = now() + min(180.0, threshold)
    state["codex_last_event"] = "long_silence"
    state["codex_last_note"] = f"no new events for {int(now() - last)} seconds"
    state["codex_last_time"] = now()
    state["codex_silence_notified"] = True
    state["current_event"] = "waiting"
    state["event_status"] = "Codex has been quiet for a while."
    state["event_until"] = now() + 8.0
    state["codex_notification"] = "Codex has been quiet for a while."
    state["codex_notification_title"] = "Codex has been quiet for a while."
    state["codex_notification_subtitle"] = ""
    state["codex_notification_until"] = now() + float(config.get("codexNotificationSeconds", 8) or 8)
    add_codex_log(state, "Codex has been quiet for a while.")
    return True
