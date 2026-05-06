"""
Public API for the phrases package.

Usage:
    from codex_pet_companion.core.phrases import phrase, hint_line, care_line, chat_response
"""
from __future__ import annotations

import random
from typing import Any

from ..text_profiles import text_profile_id
from . import neutral, lumisprout, vikamon

# ---------------------------------------------------------------------------
# Internal registry
# ---------------------------------------------------------------------------
_EVENT_BANKS = {
    "neutral": neutral.EVENT_PHRASES,
    "lumisprout": lumisprout.EVENT_PHRASES,
    "vikamon": vikamon.EVENT_PHRASES,
}

_CARE_BANKS = {
    "neutral": neutral.CARE_LINES,
    "lumisprout": lumisprout.CARE_LINES,
    "vikamon": vikamon.CARE_LINES,
}

_HINT_BANKS = {
    "neutral": neutral.HINT_LINES,
    "lumisprout": lumisprout.HINT_LINES,
    "vikamon": vikamon.HINT_LINES,
}

_CHAT_BANKS = {
    "neutral": neutral.CHAT_PHRASES,
    "lumisprout": lumisprout.CHAT_PHRASES,
    "vikamon": vikamon.CHAT_PHRASES,
}

_FRIENDSHIP_TITLES = {
    "neutral": neutral.FRIENDSHIP_TITLES,
    "lumisprout": lumisprout.FRIENDSHIP_TITLES,
    "vikamon": vikamon.FRIENDSHIP_TITLES,
}

_MILESTONES = {
    "neutral": neutral.MILESTONES,
    "lumisprout": lumisprout.MILESTONES,
    "vikamon": vikamon.MILESTONES,
}

_SPECIAL_DAY_LINES = {
    "neutral": neutral.SPECIAL_DAY_LINES,
    "lumisprout": lumisprout.SPECIAL_DAY_LINES,
    "vikamon": vikamon.SPECIAL_DAY_LINES,
}

_DAILY_ACTIVITIES = {
    "neutral": neutral.DAILY_ACTIVITIES,
    "lumisprout": lumisprout.DAILY_ACTIVITIES,
    "vikamon": vikamon.DAILY_ACTIVITIES,
}

_IDLE_DISCOVERIES = {
    "neutral": neutral.IDLE_DISCOVERIES,
    "lumisprout": lumisprout.IDLE_DISCOVERIES,
    "vikamon": vikamon.IDLE_DISCOVERIES,
}

_MICRO_REACTIONS = {
    "neutral": neutral.MICRO_REACTIONS,
    "lumisprout": lumisprout.MICRO_REACTIONS,
    "vikamon": vikamon.MICRO_REACTIONS,
}

_HIGH_BOND_ACTIVITIES = {
    "neutral": neutral.HIGH_BOND_ACTIVITIES,
    "lumisprout": lumisprout.HIGH_BOND_ACTIVITIES,
    "vikamon": vikamon.HIGH_BOND_ACTIVITIES,
}

_SPECIAL_ACTIVITIES = {
    "neutral": neutral.SPECIAL_ACTIVITIES,
    "lumisprout": lumisprout.SPECIAL_ACTIVITIES,
    "vikamon": vikamon.SPECIAL_ACTIVITIES,
}


def _profile(pet_id: str) -> str:
    return text_profile_id(pet_id)


def _as_options(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def _recent_phrases(state: dict[str, Any] | None, category: str) -> list[str]:
    if state is None:
        return []
    recent_by_category = state.get("phrase_recent")
    if not isinstance(recent_by_category, dict):
        recent_by_category = {}
        state["phrase_recent"] = recent_by_category
    recent = recent_by_category.get(category)
    if not isinstance(recent, list):
        recent = []
        recent_by_category[category] = recent
    return recent


def _remember_phrase(state: dict[str, Any] | None, category: str, text: str, limit: int = 5) -> None:
    if state is None or not text:
        return
    recent = _recent_phrases(state, category)
    recent[:] = [text, *[item for item in recent if item != text]][:limit]


def _choose(options: list[str], category: str, state: dict[str, Any] | None = None) -> str:
    if not options:
        return ""
    if len(options) == 1:
        return options[0]
    recent = set(_recent_phrases(state, category))
    available = [option for option in options if option not in recent]
    if not available:
        last = _recent_phrases(state, category)[:1]
        available = [option for option in options if option not in last] or options
    selected = random.choice(available)
    _remember_phrase(state, category, selected)
    return selected


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def phrase(event: str, pet_name: str, pet_id: str, state: dict[str, Any] | None = None) -> str:
    """Pick a random event phrase for the given pet profile."""
    bank = _EVENT_BANKS.get(_profile(pet_id), neutral.EVENT_PHRASES)
    options = bank.get(event) or neutral.EVENT_PHRASES.get(event) or ["{pet} reacts."]
    template = _choose(_as_options(options), f"event:{_profile(pet_id)}:{event}", state)
    return template.format(pet=pet_name)


def care_line(
    pet_id: str,
    pet_name: str,
    key: str,
    *,
    minutes: str = "",
    state: dict[str, Any] | None = None,
) -> str:
    """Return a formatted care action line for the given pet profile."""
    bank = _CARE_BANKS.get(_profile(pet_id), neutral.CARE_LINES)
    raw = bank.get(key) or neutral.CARE_LINES.get(key) or "{pet} reacts."
    options = _as_options(raw)
    event_key_by_care_key = {
        "feed": "feed",
        "feed_hungry": "feed",
        "pet": "pet",
        "play": "play",
        "rest": "rest",
    }
    if len(options) <= 1 and key in event_key_by_care_key:
        event_bank = _EVENT_BANKS.get(_profile(pet_id), neutral.EVENT_PHRASES)
        event_key = event_key_by_care_key[key]
        event_options = _as_options(event_bank.get(event_key) or neutral.EVENT_PHRASES.get(event_key))
        options = [*options, *[option for option in event_options if option not in options]] or options
    template = _choose(options, f"care:{_profile(pet_id)}:{key}", state)
    return template.format(pet=pet_name, minutes=minutes)


def hint_line(pet_id: str, key: str, state: dict[str, Any] | None = None) -> str:
    """Return a hint line for the given pet profile."""
    bank = _HINT_BANKS.get(_profile(pet_id), neutral.HINT_LINES)
    raw = bank.get(key) or neutral.HINT_LINES.get(key) or neutral.HINT_LINES["ok"]
    return _choose(_as_options(raw), f"hint:{_profile(pet_id)}:{key}", state)


def get_friendship_titles(pet_id: str) -> list[str]:
    """Return friendship title list for the given pet profile."""
    return _FRIENDSHIP_TITLES.get(_profile(pet_id), neutral.FRIENDSHIP_TITLES)


def get_milestones(pet_id: str) -> dict[int, str]:
    """Return milestone messages for the given pet profile."""
    return _MILESTONES.get(_profile(pet_id), neutral.MILESTONES)


def get_special_day_line(event_id: str, pet_id: str) -> str:
    """Return a special day message for the given event and pet profile."""
    bank = _SPECIAL_DAY_LINES.get(_profile(pet_id), neutral.SPECIAL_DAY_LINES)
    return bank.get(event_id) or neutral.SPECIAL_DAY_LINES.get(event_id) or ""


def get_daily_activities(pet_id: str) -> list[str]:
    """Return daily activity texts for the given pet profile."""
    return _DAILY_ACTIVITIES.get(_profile(pet_id), neutral.DAILY_ACTIVITIES)


def get_idle_discoveries(pet_id: str) -> list[str]:
    """Return idle discovery texts for the given pet profile."""
    return _IDLE_DISCOVERIES.get(_profile(pet_id), neutral.IDLE_DISCOVERIES)


def get_micro_reactions(pet_id: str) -> dict[str, list[str]]:
    """Return stat-based micro reaction texts for the given pet profile."""
    return _MICRO_REACTIONS.get(_profile(pet_id), neutral.MICRO_REACTIONS)


def get_high_bond_activities(pet_id: str) -> list[str]:
    """Return high-bond activity texts for the given pet profile."""
    return _HIGH_BOND_ACTIVITIES.get(_profile(pet_id), neutral.HIGH_BOND_ACTIVITIES)


def get_special_activities(pet_id: str) -> dict[str, str]:
    """Return special activity texts for the given pet profile."""
    return _SPECIAL_ACTIVITIES.get(_profile(pet_id), neutral.SPECIAL_ACTIVITIES)


# ---------------------------------------------------------------------------
# Chat response (kept for backward compatibility — used by action "note")
# ---------------------------------------------------------------------------

def _has_any(low: str, words: list[str]) -> bool:
    return any(word in low for word in words)


def _classify_chat(text: str) -> str:
    low = " ".join(text.lower().strip().replace(",", " ").replace("!", " ").split())
    if not low:
        return "confused"

    greeting_words = ["hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"]
    if low in greeting_words or _has_any(low, ["hello", "hey there", "good morning", "good afternoon", "good evening"]):
        return "greeting"

    how_words = [
        "how are you", "how r u", "how do you do", "how is it going",
        "how's it going", "how are u", "you ok", "are you ok",
    ]
    if _has_any(low, how_words):
        return "how_are_you"

    checks = [
        ("bye", ["bye", "goodbye", "see you", "later", "good night"]),
        ("thanks", ["thanks", "thank you", "thx"]),
        ("affection", ["love", "hug", "friend", "buddy", "pal", "best"]),
        ("praise", ["nice", "cute", "good", "great", "awesome", "smart", "well done"]),
        ("food", ["snack", "food", "eat", "feed", "hungry", "treat"]),
        ("rest", ["sleep", "tired", "rest", "break", "nap"]),
        ("error", ["traceback", "failed", "exception", "error", "exit code", "crash", "bug", "broken"]),
        ("codex", ["codex", "diff", "review", "pull request", " pr ", "commit", "merge", "branch", "repo"]),
        ("work", ["work", "task", "todo", "focus", "build", "project"]),
        ("question", ["?", "where", "why", "how", "what", "when"]),
    ]
    padded = f" {low} "
    for category, words in checks:
        if any((word in padded if word.startswith(" ") or word.endswith(" ") else word in low) for word in words):
            return category
    return "confused"


def chat_response(text: str, pet_name: str, pet_id: str, state: dict[str, Any] | None = None) -> str:
    """Generate a chat response for the given input text and pet profile."""
    bank = _CHAT_BANKS.get(_profile(pet_id), neutral.CHAT_PHRASES)
    category = _classify_chat(text)
    options = bank.get(category) or neutral.CHAT_PHRASES["confused"]
    template = _choose(_as_options(options), f"chat:{_profile(pet_id)}:{category}", state)
    return template.format(pet=pet_name)
