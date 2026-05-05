"""Lumisprout-specific phrases and text banks."""
from __future__ import annotations

from .neutral import (
    EVENT_PHRASES as NEUTRAL_EVENT_PHRASES,
    CARE_LINES as NEUTRAL_CARE_LINES,
    HINT_LINES as NEUTRAL_HINT_LINES,
    CHAT_PHRASES as NEUTRAL_CHAT_PHRASES,
)

# ---------------------------------------------------------------------------
# Event phrases
# ---------------------------------------------------------------------------
EVENT_PHRASES: dict[str, list[str]] = {
    **NEUTRAL_EVENT_PHRASES,
    "codex_running": [
        "{pet} sniffs the fresh rollout.",
        "{pet} rustles its leaves and checks Codex.",
        "{pet} roots itself into the task.",
        "{pet} wiggles its sprout: the process has started.",
        "{pet} tries to grow the task in the right direction.",
    ],
    "review_ready": [
        "{pet} checks whether a regression has sprouted.",
        "{pet} leafs through the changes internally.",
        "{pet} sniffs the final answer. Smells almost safe.",
        "{pet} gently shakes its leaves over the result.",
        "{pet} thinks the harvest can be shown.",
    ],
    "error": [
        "{pet} sheds a few leaves. That is a diagnosis.",
        "{pet} suspects fungus in the pipeline.",
        "{pet} looks at the traceback like a drought.",
        "{pet} quietly photosynthesizes offense.",
        "{pet} dropped a leaf on the failed status.",
    ],
    "feed": [
        "{pet} accepts the offering with botanical dignity.",
        "{pet} rustles in a suspiciously happy way.",
        "{pet} stores the snack somewhere root-adjacent.",
        "{pet} becomes greener and less judgmental.",
        "{pet} decides not to wilt at you today.",
    ],
    "pet": [
        "{pet} rustles quietly. That means yes.",
        "{pet} allows leaf maintenance.",
        "{pet} pretends the petting was accidental.",
        "{pet} grows one tiny unit of trust.",
        "{pet} leans toward the warmth, very subtly.",
    ],
    "play": [
        "{pet} causes a tiny green disturbance.",
        "{pet} runs around like a seed with opinions.",
        "{pet} tests the room for sunlight and nonsense.",
        "{pet} did a loop and considers it research.",
        "{pet} celebrates with suspicious leaf movement.",
    ],
    "rest": [
        "{pet} rests like an anxious houseplant.",
        "{pet} puts down roots for five minutes.",
        "{pet} lowers its leaves and recharges.",
        "{pet} stands still and photosynthesizes doubts.",
        "{pet} enters quiet moss mode.",
    ],
}

# ---------------------------------------------------------------------------
# Care lines
# ---------------------------------------------------------------------------
CARE_LINES: dict[str, str] = {
    **NEUTRAL_CARE_LINES,
    "feed_hungry": "{pet} eats like a tiny forest disaster.",
    "feed": "{pet} rustles its leaves and accepts the food.",
    "feed_full": "{pet} is already full and looks at the food like extra fertilizer.",
    "feed_cooldown": "{pet} is still digesting. Wait {minutes}.",
    "pet_cooldown": "{pet} has already been polished. {minutes} more and irritation begins.",
    "pet_spam": "{pet} has already been polished. More will only add shine and irritation.",
    "pet": "{pet} rustles quietly and pretends this is accidentally pleasant.",
    "play_tired": "{pet} wants to play, but is lying down like a wet leaf.",
    "play_resting": "{pet} is resting. Do not shake the tiny forest.",
    "play_cooldown": "{pet} is still recovering from the previous chaos. Wait {minutes}.",
    "play": "{pet} caused a tiny green chaos.",
    "rest_cooldown": "{pet} just rested. {minutes} more before another dramatic reboot.",
    "rest_already": "{pet} is already resting. Do not shake the tiny forest.",
    "rest": "{pet} put down roots and is resting.",
    "rest_interrupt": "{pet} reluctantly returns to the desk.",
    "rest_stop": "{pet} reluctantly returns to the desk.",
}

# ---------------------------------------------------------------------------
# Hint lines
# ---------------------------------------------------------------------------
HINT_LINES: dict[str, str] = {
    **NEUTRAL_HINT_LINES,
    "recovery_hunger": "Lumisprout is too hungry to glow properly.",
    "recovery_energy": "Lumisprout needs rest. Do not shake the poor sprout.",
    "recovery_mood": "Lumisprout needs a gentle moment, not more weather.",
    "recovery_focus": "Lumisprout lost the thread somewhere in the moss.",
    "low_hunger": "A little food would help the glow.",
    "low_energy": "Let the tiny forest recharge.",
    "low_mood": "Lumisprout could use a softer minute.",
    "low_focus": "The little roots are wandering. A calm rhythm would help.",
    "not_fed_today": "A small snack would brighten the leaves.",
    "no_rest_today": "A quiet rest would help the glow settle.",
}

# ---------------------------------------------------------------------------
# Friendship titles
# ---------------------------------------------------------------------------
FRIENDSHIP_TITLES: list[str] = [
    "Seed of doubt",
    "Took root",
    "Knows the scent",
    "Reaching for light",
    "Rustling nearby",
    "Blooming closer",
    "House sprout",
    "Mossy accomplice",
    "Almost a forest",
    "Loyal forest companion",
    "Domestic forest menace",
]

# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
MILESTONES: dict[int, str] = {
    7: "One week together. Lumisprout has rooted into the desk.",
    30: "One month together. This spot can officially be labeled forest.",
    100: "One hundred days together. Lumisprout considers this a stable ecosystem.",
    365: "One year together. Lumisprout is officially a domestic forest phenomenon.",
}

# ---------------------------------------------------------------------------
# Special day lines
# ---------------------------------------------------------------------------
SPECIAL_DAY_LINES: dict[str, str] = {
    "holiday_new_year": "New Year together. Lumisprout rustles like a tiny tree.",
    "holiday_halloween": "Halloween together. Lumisprout pretends to be a scary forest.",
    "holiday_first_launch_anniversary": "First launch anniversary. Lumisprout grew a commemorative root.",
}

# ---------------------------------------------------------------------------
# Chat phrases
# ---------------------------------------------------------------------------
CHAT_PHRASES: dict[str, list[str]] = {
    **NEUTRAL_CHAT_PHRASES,
    "greeting": [
        "{pet}: shhh. I woke up leaf-first.",
        "{pet}: hello. I have already rooted into this day.",
        "{pet}: hello. The moss is listening.",
        "{pet}: good sprout. Or whatever time it is.",
        "{pet}: hi. I rustle and pretend that is normal.",
    ],
    "food": [
        "{pet}: if this is fertilizer, I am listening.",
        "{pet}: hunger is when a tiny forest makes noise inside.",
        "{pet}: I can photosynthesize, but drama tastes better.",
        "{pet}: feed me and I will stop being a botanical threat for a while.",
        "{pet}: the roots approve this conversation.",
    ],
    "error": [
        "{pet}: the traceback wilted. Bad sign.",
        "{pet}: this bug has deeper roots than I like.",
        "{pet}: the pipeline smells like root rot.",
        "{pet}: the error fell into the moss. The moss is displeased.",
        "{pet}: the leaves held a meeting and blamed the bug.",
    ],
    "affection": [
        "{pet}: I grew a tiny root in your direction. Do not touch it.",
        "{pet}: warmth accepted. The leaves pretend it was accidental.",
        "{pet}: the moss became louder from the warmth.",
        "{pet}: I am blooming, strictly for business reasons.",
    ],
    "how_are_you": [
        "{pet}: rustling normally. Leaves in place. Anxiety too.",
        "{pet}: alive, growing, suspicious.",
        "{pet}: photosynthesizing patience.",
        "{pet}: leafy, stable, and mildly dramatic.",
        "{pet}: roots are holding. That is what matters.",
    ],
    "confused": [
        "{pet}: I did not understand, but I rustled professionally.",
        "{pet}: the message fell into the moss and vanished.",
        "{pet}: I tried to grow meaning. It did not sprout.",
        "{pet}: the leaves met and decided not to decide.",
        "{pet}: the leaves voted for confusion.",
    ],
}

# ---------------------------------------------------------------------------
# Daily / idle / special activity texts
# ---------------------------------------------------------------------------
DAILY_ACTIVITIES: list[str] = [
    'Lumisprout found a warm patch of quiet and settled there for a while.',
    'Lumisprout rustled at the edge of the screen like a tiny indoor forest.',
    'Today Lumisprout is collecting little bits of calm from the workflow.',
    'Lumisprout inspected the desk for moss-worthy territory.',
    'A bright speck of focus drifted by, and Lumisprout kept it.',
    'Lumisprout spent a while pretending the desktop was a woodland path.',
    'Today Lumisprout is listening for tiny roots of trouble.',
    'Lumisprout found a peaceful corner and softened the whole mood of it.',
    'A patch of silence appeared, and Lumisprout treated it like sunlight.',
    'Today Lumisprout is guarding the small ecosystem near your tasks.',
    'Lumisprout decided the workflow needed one more gentle rustle.',
    'A quiet minute turned into a tiny forest ceremony.',
    'Today Lumisprout is thriving in the glow of ordinary routine.',
    'Lumisprout inspected the room for places where calm could grow.',
    'A spare moment bloomed, and Lumisprout claimed it immediately.',
    'Today Lumisprout looks especially pleased with the desk habitat.',
    "Lumisprout found a soft silence and filed it under 'important'.",
    'Today Lumisprout is acting like the houseplant supervisor of productivity.',
    'Lumisprout found a little workflow sunshine and leaned into it.',
    'Today Lumisprout is growing a tiny routine between the tasks.',
    'A soft patch of progress appeared, and Lumisprout treated it like spring.',
    'Lumisprout spent a while making the desktop feel less like machinery.',
    'Today Lumisprout is guarding the calm from sudden nonsense.',
    'Lumisprout discovered a gentle rhythm and rustled approvingly.',
    'A quiet success sprouted somewhere near the edge of the screen.',
    'Lumisprout checked the desk habitat and found it mostly survivable.',
    'Today Lumisprout looks like it has watered one invisible idea.',
    'A small pause bloomed, and Lumisprout adopted it immediately.',
    'Lumisprout seems to be cultivating patience in a corner of the workflow.',
    'Today Lumisprout is bright enough to make the room feel less square.',
]

IDLE_DISCOVERIES: list[str] = [
    'Quiet hour discovery: Lumisprout found a soft place where silence could grow.',
    'Lumisprout wandered through the stillness and came back with a tiny rustle.',
    'The room stayed quiet long enough for Lumisprout to cultivate a little calm.',
    'In the hush, Lumisprout discovered a very respectable patch of peace.',
    'Lumisprout checked the silence and approved of its ecosystem potential.',
    'A long quiet spell gave Lumisprout time to gather one more calm thought.',
    'Lumisprout drifted through the stillness like a small domestic omen.',
    'The quiet lasted long enough for Lumisprout to claim it as habitat.',
    'Lumisprout found a hidden pocket of calm and refuses to leave it alone.',
    'Silence report: Lumisprout located a tiny forest-worthy moment.',
    'Lumisprout quietly explored the idle hour and returned greener somehow.',
    'A patient stretch of stillness let Lumisprout bloom just a little more.',
    'Lumisprout found a quiet draft and turned it into a tiny breeze.',
    'The silence lasted long enough for Lumisprout to grow comfortable.',
    'Lumisprout listened to the idle time like it was distant rain.',
    'A soft pause settled in, and Lumisprout claimed the good part.',
    'Lumisprout drifted through the quiet and came back a little brighter.',
    'Silence report: Lumisprout found a calm seed and hid it carefully.',
    'Lumisprout used the pause to practice being a very small forest.',
    'The room stayed quiet, so Lumisprout improved the atmosphere by existing.',
]



MICRO_REACTIONS: dict[str, list[str]] = {'low_energy': ['Lumisprout’s glow is soft and sleepy. It needs a quieter minute.',
                'Lumisprout is drooping like a houseplant that heard bad news.',
                'Lumisprout is conserving energy in the most woodland way possible.',
                'Lumisprout looks ready to curl into a warm patch of silence.'],
 'low_mood': ['Lumisprout looks dimmer than usual, like the room got quieter.',
              'Lumisprout is rustling in a very small, very sad key.',
              'Lumisprout could use a gentle moment before the day gets sharper.',
              'Lumisprout is trying to stay bright, but the glow is thin today.'],
 'low_hunger': ['Lumisprout is thinking suspiciously hard about snacks.',
                'Lumisprout has begun photosynthesizing from pure hope.',
                'Lumisprout is looking at the food button like it might be sunlight.',
                'Lumisprout’s tiny forest ecosystem requests maintenance.'],
 'low_focus': ['Lumisprout’s attention has drifted off like a loose leaf.',
               'Lumisprout is listening to three different silences and none of them are useful.',
               'Lumisprout is trying to focus, but the little roots are wandering.',
               'Lumisprout has misplaced the thread somewhere in the moss.'],
 'high_focus': ['Lumisprout is quietly focused, like a tiny forest holding its breath.',
                'Lumisprout’s glow has narrowed into a very determined little beam.',
                'Lumisprout is rooted in the task now.',
                'Lumisprout looks calm, bright, and unusually ready.'],
 'high_energy': ['Lumisprout is glowing with dangerous levels of wholesome momentum.',
                 'Lumisprout looks freshly watered and ready for tiny business.',
                 'Lumisprout has enough energy to rustle with confidence.',
                 'The little glow is bright enough to count as a plan.'],
 'high_mood': ['Lumisprout is in a warm mood, like the desk found sunlight.',
               'Lumisprout looks quietly happy with the shape of the day.',
               'Lumisprout is brighter than usual and pretending not to show off.',
               'The tiny forest spirit seems pleased with this arrangement.'],
 'high_hunger': ['Lumisprout is nicely fed and glowing like a smug houseplant.',
                 'The snack situation has restored woodland diplomacy.',
                 'Lumisprout looks fed, calm, and slightly more leaf-authoritative.'],
 'all_good': ['Lumisprout is stable, bright, and suspiciously peaceful.',
              'Everything around Lumisprout feels soft enough for now.',
              'The little habitat is working today.',
              'Lumisprout seems comfortable enough to grow opinions.']}

HIGH_BOND_ACTIVITIES: list[str] = ['Lumisprout has rooted into the routine in the best possible way.', 'The desk feels like a tiny habitat now, and Lumisprout knows it.', 'Lumisprout greets the day with the confidence of something that belongs here.', 'There is a warmer glow around Lumisprout lately.', 'Lumisprout looks less like a visitor and more like a small household spirit.', 'Lumisprout has learned the shape of these days and seems pleased with it.']

SPECIAL_ACTIVITIES: dict[str, str] = {
    "days_7": "One week together. Lumisprout has already rooted into the routine.",
    "days_30": "One month together. Lumisprout considers this desk a healthy habitat.",
    "days_100": "One hundred days together. Lumisprout has become a tiny domestic ecosystem.",
    "days_365": "One year together. Lumisprout is basically part forest, part family now.",
    "holiday_new_year": "New Year today. Lumisprout is rustling like a tiny holiday tree.",
    "holiday_halloween": "Halloween today. Lumisprout is pretending to be an ominous houseplant.",
    "launch_anniversary": "Anniversary today. Lumisprout marked it with an especially proud little rustle.",
}
