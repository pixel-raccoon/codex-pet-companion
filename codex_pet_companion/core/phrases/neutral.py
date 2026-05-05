"""Neutral / fallback phrases and text banks."""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Event phrases (used by phrase())
# ---------------------------------------------------------------------------
EVENT_PHRASES: dict[str, list[str]] = {
    "codex_running": [
        "{pet} is watching the task.",
        "{pet} noticed movement in Codex.",
        "{pet} switches into work mode.",
        "{pet} pretends to understand the plan.",
        "{pet} is suspiciously observing the process.",
    ],
    "review_ready": [
        "{pet} studies the review.",
        "{pet} found the final answer and looks very professional.",
        "{pet} sniffs the result and does not object yet.",
        "{pet} thinks this is ready to inspect.",
        "{pet} carefully taps the finished result.",
    ],
    "error": [
        "{pet} is dramatically upset about the error.",
        "{pet} face-planted into the traceback.",
        "{pet} suspects this was not the plan.",
        "{pet} quietly judges the failed status.",
        "{pet} suggests calling this an experiment.",
    ],
    "feed": [
        "{pet} is pleased but refuses to admit it.",
        "{pet} accepted the snack bribe.",
        "{pet} became slightly nicer.",
        "{pet} hid a crumb in cache.",
        "{pet} pretends this was not a bribe.",
    ],
    "pet": [
        "{pet} allows you to continue existing.",
        "{pet} blinks with great generosity.",
        "{pet} accepts the petting as a pull request.",
        "{pet} stops judging the interface for one second.",
        "{pet} becomes softer by one imaginary unit.",
    ],
    "play": [
        "{pet} causes a small amount of chaos.",
        "{pet} defeats an invisible enemy. Probably.",
        "{pet} plays and now considers itself an architect.",
        "{pet} tests the physics of reality and remains unimpressed.",
        "{pet} does a tiny victory lap around meaning.",
    ],
    "rest": [
        "{pet} temporarily exits usefulness mode.",
        "{pet} rests. Very professionally.",
        "{pet} stares into the void and recharges on silence.",
        "{pet} lowers the chaos to safe levels.",
        "{pet} enters soft furniture mode.",
    ],
    "note": [
        "{pet} pretends to understand.",
        "{pet} is listening. Almost.",
        "{pet} processed the message as best it could.",
        "{pet} tilted its head. That is already a lot.",
        "{pet} filed that in an invisible protocol.",
    ],
}

# ---------------------------------------------------------------------------
# Care lines (used by care_line())
# ---------------------------------------------------------------------------
CARE_LINES: dict[str, str] = {
    "feed_hungry": "{pet} eats like it has been waiting for this decision.",
    "feed": "{pet} eats and calms down a little.",
    "feed_full": "{pet} is already full.",
    "feed_cooldown": "{pet} is still digesting. Wait {minutes}.",
    "pet_cooldown": "{pet} does not want another petting yet. Wait {minutes}.",
    "pet_spam": "{pet} is tired of too much care.",
    "pet": "{pet} accepts the care.",
    "play_tired": "{pet} is too tired to play.",
    "play_resting": "{pet} is resting.",
    "play_cooldown": "{pet} is still resting after playtime. Wait {minutes}.",
    "play": "{pet} plays a little.",
    "rest_cooldown": "{pet} rested recently. Wait {minutes}.",
    "rest_already": "{pet} is already resting.",
    "rest": "{pet} is resting.",
    "rest_interrupt": "{pet} reluctantly returns to the desk.",
    "rest_stop": "{pet} returns to the desk.",
}

# ---------------------------------------------------------------------------
# Hint lines (used by hint_line())
# ---------------------------------------------------------------------------
HINT_LINES: dict[str, str] = {
    "recovery_hunger": "Too hungry for bonding. Feed first, heroics later.",
    "recovery_energy": "Too tired for bonding. Let it rest before the tiny system collapses.",
    "recovery_mood": "Mood is in the basement. Care or quiet would help.",
    "recovery_focus": "Focus has wandered off. Rest or a calmer rhythm should help.",
    "low_hunger": "Food would be a very reasonable idea right now.",
    "low_energy": "A rest would beat pretending this is fine.",
    "low_mood": "Mood is low. A little attention would not be wasted.",
    "low_focus": "Focus is slipping. A calmer rhythm should help.",
    "not_fed_today": "A snack would not be wasted.",
    "no_rest_today": "A short rest would probably help.",
    "ok": "Everything looks stable. Suspicious, but stable.",
}

# ---------------------------------------------------------------------------
# Chat phrases (used by chat_response())
# ---------------------------------------------------------------------------
CHAT_PHRASES: dict[str, list[str]] = {
    "greeting": [
        "{pet}: hello. I am already almost busy.",
        "{pet}: hello. Please do not touch anything without witnesses.",
        "{pet}: hi. I am awake. Suspiciously awake.",
        "{pet}: hello. I am observing with small eyes.",
        "{pet}: hi. The workday has officially become stranger.",
    ],
    "bye": [
        "{pet}: leaving? I will record it. Not emotionally. Just in the log.",
        "{pet}: bye. I will watch the void.",
        "{pet}: see you. Try not to break the universe.",
        "{pet}: bye. I will stay here and look useful.",
    ],
    "food": [
        "{pet}: if this is about food, continue.",
        "{pet}: food is a convincing argument.",
        "{pet}: you cannot feed me with words, but the attempt is noted.",
        "{pet}: snacks are valid architecture.",
        "{pet}: hunger is not a bug. It is a feature with teeth.",
    ],
    "rest": [
        "{pet}: rest is not weakness. It is a reboot with drama.",
        "{pet}: sleep sounds like feature freeze.",
        "{pet}: rest approved. Briefly. Under supervision.",
        "{pet}: I would also lie down if I were not an interface.",
        "{pet}: sometimes progress means stop poking the system with a stick.",
    ],
    "codex": [
        "{pet}: Codex is doing something again? I am watching from a safe distance.",
        "{pet}: sounds like work. I am small. I should not.",
        "{pet}: tell Codex I believe in it. I accept no responsibility.",
        "{pet}: commit carefully. A small creature is watching.",
        "{pet}: review first, heroics later.",
    ],
    "error": [
        "{pet}: an error is when reality fails tests.",
        "{pet}: the traceback smells dramatic.",
        "{pet}: I suggest blaming an invisible dependency.",
        "{pet}: bug detected. Emotional support is limited, but I can stare.",
        "{pet}: if it falls twice, it is reproducible.",
    ],
    "praise": [
        "{pet}: yes, I am magnificent. Continue.",
        "{pet}: compliment accepted. Doubts rejected.",
        "{pet}: finally, a good input.",
        "{pet}: thank you. Now I will be unbearable.",
        "{pet}: correct. I am very pet-shaped and important.",
    ],
    "affection": [
        "{pet}: that sounds suspiciously warm.",
        "{pet}: affection logged. I am pretending to be calm.",
        "{pet}: warmth accepted. Terms ignored.",
        "{pet}: I tolerate you more efficiently too.",
    ],
    "work": [
        "{pet}: working, then. I brought tiny judgment.",
        "{pet}: productivity noises detected.",
        "{pet}: focus mode. Dramatic eyebrow unavailable.",
        "{pet}: take small steps. Big steps scare logs.",
        "{pet}: the task looks bitey. Approach from the side.",
    ],
    "thanks": [
        "{pet}: you are welcome. I did almost nothing, but it is nice.",
        "{pet}: accepted.",
        "{pet}: do not thank me, save your work.",
        "{pet}: you are welcome. I remain mysterious.",
    ],
    "how_are_you": [
        "{pet}: holding on. Small, proud, and mildly suspicious.",
        "{pet}: fine. I have barely fallen apart today.",
        "{pet}: alive. That is a strong position.",
        "{pet}: could be worse. Could be a merge conflict.",
        "{pet}: I am fine. Decoratively, survivally fine.",
    ],
    "question": [
        "{pet}: good question. Terrible that you asked me.",
        "{pet}: I am a small pet, not an architecture committee.",
        "{pet}: maybe. Or the opposite. Being a pet is convenient.",
        "{pet}: depends. The safest answer.",
        "{pet}: I answer confidently and with limited liability.",
    ],
    "confused": [
        "{pet}: I did not understand, but I made a confident face.",
        "{pet}: that sounds like noise with a name.",
        "{pet}: I am small. I am not licensed for meaning.",
        "{pet}: that missed me, but I blinked politely.",
        "{pet}: input accepted. Meaning escaped.",
        "{pet}: I processed that spiritually, not technically.",
    ],
}

# ---------------------------------------------------------------------------
# Friendship titles
# ---------------------------------------------------------------------------
FRIENDSHIP_TITLES: list[str] = [
    "First meeting",
    "Getting used to you",
    "Recognizes you",
    "Trusting",
    "Warming up",
    "One of yours",
    "Loyal companion",
    "Attached",
    "Almost family",
    "Best companion",
    "Beloved little problem",
]

# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
MILESTONES: dict[int, str] = {
    7: "One week together. The pet already recognizes this place.",
    30: "One month together. The pet thinks this is almost home.",
    100: "One hundred days together. This has become a sturdy little ritual.",
    365: "One year together. The pet has become a real companion.",
}

# ---------------------------------------------------------------------------
# Special day lines
# ---------------------------------------------------------------------------
SPECIAL_DAY_LINES: dict[str, str] = {
    "holiday_new_year": "New Year together. The pet celebrates it next to the desk.",
    "holiday_halloween": "Halloween together. The pet looks a little more mysterious than usual.",
    "holiday_first_launch_anniversary": "First launch anniversary. The pet remembers how it all started.",
}

# ---------------------------------------------------------------------------
# Daily / idle / special activity texts
# ---------------------------------------------------------------------------
DAILY_ACTIVITIES: list[str] = [
    'The pet inspected the desktop and concluded that one icon is definitely suspicious.',
    'Today the pet is patrolling the edge of the screen like it owns the place.',
    'The pet found a tiny patch of silence and decided to keep it for later.',
    'A short walk across the workspace somehow turned into a full inspection route.',
    'The pet spent a while judging the quality of recent clicks.',
    'Today the pet is quietly keeping watch over the workflow.',
    'The pet reorganized one invisible thing and refuses to explain what changed.',
    'A mysterious pause was discovered and carefully archived.',
    'The pet did a tiny lap around the screen and called it productive.',
    'Today the pet is collecting good moods and ignoring bad timing.',
    'The pet found a comfortable corner and declared it strategically important.',
    'A minute of quiet turned into a miniature expedition.',
    'The pet has been listening to the room with professional seriousness.',
    'Today the pet is trying to look useful and adorable at the same time.',
    'The pet examined the task flow and made a note no one else can read.',
    'A suspiciously neat moment appeared, and the pet adopted it.',
    'Today the pet is treating the desktop like a tiny kingdom.',
    'The pet quietly checked whether the day feels lucky enough.',
    'The pet discovered a surprisingly decent rhythm in the day and chose not to ruin it.',
    'Today the pet is doing quality control on the ordinary little moments.',
    'The pet watched the workflow breathe for a while and approved the pattern.',
    'A tiny routine formed on the desktop, and the pet immediately joined the committee.',
    'The pet found a good pause, polished it mentally, and put it back.',
    'Today the pet is quietly checking whether the desk still remembers yesterday.',
    'The pet spent a minute looking busy enough to avoid further questions.',
    'A small pocket of progress appeared, and the pet guarded it like treasure.',
    'The pet is keeping one eye on the work and one eye on potential nonsense.',
    'Today the pet decided the desktop needed a small resident supervisor.',
    'The pet inspected the silence and found no immediate crimes.',
    'A gentle little routine survived the morning. The pet seems invested.',
]

IDLE_DISCOVERIES: list[str] = [
    'Quiet hour discovery: the pet found a suspiciously empty corner of the desktop.',
    'The pet wandered off and came back with a deeply unnecessary sense of purpose.',
    'Nothing happened for a while, so the pet invented a tiny mystery.',
    'In the quiet, the pet discovered a place where boredom almost settled in.',
    'The pet checked the stillness and declared it mildly questionable.',
    'After a stretch of silence, the pet found a small excuse to be busy.',
    'The pet has been pacing through the quiet like a tiny hallway inspector.',
    'A calm spell lasted long enough for the pet to get ideas.',
    'The pet found a forgotten speck of drama in the silence.',
    'Too much quiet. The pet has started a harmless little investigation.',
    'The pet went exploring through the idle time and returned pleased with itself.',
    'Silence report: the pet discovered one interesting thing and refuses to elaborate.',
    'The pet found a quiet gap and used it to become slightly more mysterious.',
    'The pet has been still long enough to make stillness look intentional.',
    'Nothing happened, so the pet filed a dramatic report about it.',
    'The pet discovered a tiny delay and treated it like a weather event.',
    'The pet is studying the idle time with unnecessary seriousness.',
    'A long quiet stretch appeared. The pet is suspiciously prepared.',
    'The pet wandered through the pause and returned with a small opinion.',
    'Silence report: one calm moment located, mildly approved.',
]



MICRO_REACTIONS: dict[str, list[str]] = {'low_energy': ['The pet is running on heroic amounts of stubbornness.',
                'The pet looks like it needs a proper break, not another brave little shuffle.',
                'The pet is trying to stand dramatically, but mostly needs rest.',
                'The pet has entered low-power mode and is making it everyone’s problem.'],
 'low_mood': ['The pet is having a grey little moment. Some attention would help.',
              'The pet is not upset. The pet is simply deeply unimpressed with today.',
              'The pet looks like the room got less friendly for a while.',
              'The pet could use a small win and maybe a kind click.'],
 'low_hunger': ['The pet has started developing opinions about lunch.',
                'The pet is watching the concept of snacks with professional interest.',
                'The pet looks polite, hungry, and one minute away from making it obvious.',
                'The pet is trying not to stare at the food button.'],
 'low_focus': ['The pet’s thoughts have wandered somewhere under the desk.',
               'The pet is present in body. The focus has left to run errands.',
               'The pet is trying to concentrate and losing by a narrow margin.',
               'The pet has misplaced its tiny train of thought.'],
 'high_focus': ['The pet is locked in and taking this far more seriously than expected.',
                'The pet looks sharply focused, like it finally found the thread.',
                'The pet is in work mode now. Tiny, intense, probably overqualified.',
                'The pet has achieved a suspiciously productive stare.'],
 'high_energy': ['The pet has energy to spare and only a few responsible places to put it.',
                 'The pet is dangerously awake for something this small.',
                 'The pet looks ready to turn a normal minute into an event.',
                 'The pet is charged, alert, and probably planning a tiny lap.'],
 'high_mood': ['The pet is in a good mood. This may be allowed.',
               'The pet seems pleased with the current arrangement.',
               'The pet looks cheerful enough to make the desktop less suspicious.',
               'The pet is having a good little moment and knows it.'],
 'high_hunger': ['The pet is full enough to judge the snack economy from a position of strength.',
                 'The pet appears properly fed and mildly powerful.',
                 'The pet has accepted the food situation as temporarily adequate.'],
 'all_good': ['Everything is unusually fine. The pet is monitoring this development.',
              'The pet looks stable, comfortable, and a little too aware of it.',
              'No crisis detected. The pet is keeping watch anyway.',
              'The pet seems well settled for the moment.']}

HIGH_BOND_ACTIVITIES: list[str] = ['The pet seems properly settled here now.', 'Your little companion looks at home on this desktop.', 'The pet has started treating this routine like a shared tradition.', 'There is a familiar little confidence in the way the pet waits today.', 'The pet seems to remember more good days than bad ones.', 'The desktop feels less empty with this tiny regular visitor around.']

SPECIAL_ACTIVITIES: dict[str, str] = {
    "days_7": "One week together. The pet is starting to treat this desktop like home.",
    "days_30": "One month together. The pet looks very settled in by now.",
    "days_100": "One hundred days together. This little routine has become something real.",
    "days_365": "One year together. The pet is officially part of the place now.",
    "holiday_new_year": "New Year today. The pet is celebrating the fresh start beside your desk.",
    "holiday_halloween": "Halloween today. The pet looks slightly more mysterious than usual.",
    "launch_anniversary": "Anniversary today. The pet remembers the day this all began.",
}
