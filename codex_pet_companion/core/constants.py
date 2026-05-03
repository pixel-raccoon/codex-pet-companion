from __future__ import annotations

APP_VERSION = "1.0.3-en"
CELL_W = 192
CELL_H = 208
ATLAS_SIZE = (1536, 1872)

STATES = {
    # Calmer timings: the official pet reads as a slow blink/idle companion, not a twitchy game sprite.
    "idle": (0, [900, 180, 180, 240, 240, 1100]),
    "running-right": (1, [190, 190, 190, 190, 190, 190, 190, 320]),
    "running-left": (2, [190, 190, 190, 190, 190, 190, 190, 320]),
    "waving": (3, [260, 260, 260, 520]),
    "jumping": (4, [230, 230, 230, 230, 460]),
    "failed": (5, [260, 260, 260, 260, 260, 260, 260, 520]),
    "waiting": (6, [360, 360, 360, 360, 360, 720]),
    "running": (7, [190, 190, 190, 190, 190, 320]),
    "review": (8, [380, 380, 380, 380, 380, 760]),
}

EVENT_TO_ANIMATION = {
    "codex_running": "running",
    "review_ready": "review",
    "error": "failed",
    "codex_waiting": "waiting",
    "feed": "waving",
    "pet": "waving",
    "play": "jumping",
    "rest": "waiting",
    "note": "review",
}

ACHIEVEMENTS = {
    "first_feed": "First snack",
    "first_review": "First review",
    "first_error": "First error",
    "level_3": "Friendship level 3",
    "well_fed": "Full and happy",
    "codex_sprinter": "Codex sprinter",
    "bridge_first_event": "Pet heard Codex",
    "error_streak_3": "Three errors in a row",
    "chatty_pet": "Five messages to the pet",
    "play_5": "Five play sessions",
    "fed_5": "Five feedings",
    "review_streak_3": "Three reviews without errors",
    "busy_streak_5": "Five Codex events in a row",
    "trait_loaded": "Pet gained a personality",
    "milestone_7_days": "One week together",
    "milestone_30_days": "One month together",
    "milestone_100_days": "One hundred days together",
    "milestone_365_days": "One year together",
    "holiday_new_year": "New Year together",
    "holiday_halloween": "Halloween together",
    "holiday_first_launch_anniversary": "First launch anniversary",
}

TRAITS = {
    "neutral": {
        "display": "Neutral",
        "description": "No strong quirks.",
        "energy_decay_mult": 1.0,
        "mood_decay_mult": 1.0,
        "hunger_decay_mult": 1.0,
        "focus_decay_mult": 1.0,
        "codex_focus_gain_mult": 1.0,
        "codex_mood_hit_mult": 1.0,
    },
    "nervous": {
        "display": "Nervous",
        "description": "Errors hit harder, but reviews feel better.",
        "energy_decay_mult": 1.0,
        "mood_decay_mult": 1.12,
        "hunger_decay_mult": 1.0,
        "focus_decay_mult": 1.0,
        "codex_focus_gain_mult": 1.0,
        "codex_mood_hit_mult": 1.25,
    },
    "lazy": {
        "display": "Lazy",
        "description": "Energy drains slower, but focus fades faster.",
        "energy_decay_mult": 0.78,
        "mood_decay_mult": 1.0,
        "hunger_decay_mult": 1.0,
        "focus_decay_mult": 1.20,
        "codex_focus_gain_mult": 0.9,
        "codex_mood_hit_mult": 0.9,
    },
    "glutton": {
        "display": "Snacky",
        "description": "Gets hungry faster and enjoys feeding more.",
        "energy_decay_mult": 1.0,
        "mood_decay_mult": 1.0,
        "hunger_decay_mult": 1.22,
        "focus_decay_mult": 1.0,
        "codex_focus_gain_mult": 1.0,
        "codex_mood_hit_mult": 1.0,
    },
    "workaholic": {
        "display": "Workaholic",
        "description": "Keeps focus better, but spends energy faster.",
        "energy_decay_mult": 1.10,
        "mood_decay_mult": 1.0,
        "hunger_decay_mult": 1.0,
        "focus_decay_mult": 0.78,
        "codex_focus_gain_mult": 1.18,
        "codex_mood_hit_mult": 1.0,
    },
}
