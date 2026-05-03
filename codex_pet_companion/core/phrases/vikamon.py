"""Vikamon-specific phrases and text banks."""
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
        "{pet} pulls the hood down and pretends to manage the task.",
        "{pet} squints suspiciously at Codex.",
        "{pet} declares the task weird enough to watch.",
        "{pet} stomps around the process in monster slippers.",
        "{pet} expects a circus. Possibly a useful one.",
        "{pet} reviews the work with tiny menace energy.",
    ],
    "review_ready": [
        "{pet} looks at the review like she already found something to complain about.",
        '{pet} taps the finished answer: "Show me."',
        "{pet} gives a pleased little huff. Almost praise.",
        "{pet} decides the result may leave the cage.",
        "{pet} brought the review in her teeth. Metaphorically. Probably.",
        "{pet} looks like she fixed everything herself.",
    ],
    "error": [
        "{pet} hides in her hood and glares at the error.",
        "{pet} says the bug deserved it.",
        "{pet} kicks the traceback with a monster slipper.",
        "{pet} hisses at the failed status.",
        "{pet} declares the error a personal insult.",
        '{pet} makes an "I told you so" face, even if she did not.',
    ],
    "feed": [
        "{pet} accepts food as rightful tribute.",
        "{pet} chews with the confidence of a winner.",
        "{pet} becomes nicer. Temporarily.",
        "{pet} hides a crumb in her hoodie sleeve.",
        "{pet} approves the snack with a tiny wicked nod.",
        "{pet} decides not to bite you for now.",
    ],
    "pet": [
        "{pet} allows one hood pat. One.",
        "{pet} pretends not to care. She cares.",
        "{pet} huffs but stays close.",
        "{pet} becomes softer by half a monster slipper.",
        "{pet} accepts care as rightful luxury.",
        "{pet} still looks smug, but bites less.",
    ],
    "play": [
        "{pet} launches a tiny trouble sprint.",
        "{pet} defeats the air. The air stays quiet.",
        "{pet} runs like the floor owes her an apology.",
        "{pet} checks whether reality can handle her mood.",
        "{pet} stomps happily in monster slippers.",
        "{pet} plays and becomes even more smug.",
    ],
    "rest": [
        "{pet} disappears into the hood and is temporarily unavailable.",
        "{pet} rests with the face of a tiny boss.",
        "{pet} curls into a green ball of attitude.",
        '{pet} enters "do not touch, will bite" mode.',
        "{pet} recharges on silence and self-importance.",
        "{pet} is asleep-ish and has stopped giving orders.",
    ],
    "note": [
        "{pet} heard you. Possibly.",
        "{pet} acts like that input made sense.",
        "{pet} nods like she has already decided everything.",
        "{pet} hides the message in her hood.",
        "{pet} processed the thought and left a smug footprint.",
    ],
}

# ---------------------------------------------------------------------------
# Care lines
# ---------------------------------------------------------------------------
CARE_LINES: dict[str, str] = {
    **NEUTRAL_CARE_LINES,
    "feed_hungry": "{pet} pounces on the food and pretends everything was under control.",
    "feed": "{pet} accepts food as rightful tribute.",
    "feed_full": "{pet} is already full and looks like you tried to bribe her with a cheap trick.",
    "feed_cooldown": "{pet} is still chewing with a winner's face. Wait {minutes}.",
    "pet_cooldown": "{pet} just allowed care. {minutes} more and she starts biting with her eyes.",
    "pet_spam": "{pet} huffs: the hood has already been patted. Hands off.",
    "pet": "{pet} huffs but stays nearby. That is almost affection.",
    "play_tired": "{pet} would run around, but the monster slippers demand a pause.",
    "play_resting": "{pet} is resting in the hood. Do not shake the green menace.",
    "play_cooldown": "{pet} is still enjoying the previous chaos. Wait {minutes}.",
    "play": "{pet} launches a tiny trouble sprint.",
    "rest_cooldown": "{pet} rested recently and now acts like she can do anything again. Wait {minutes}.",
    "rest_already": "{pet} is already resting in the hood. Do not negotiate with the green menace.",
    "rest": "{pet} disappears into the hood and is temporarily unavailable.",
    "rest_interrupt": "{pet} reluctantly crawls out of the hood and pretends it was her idea.",
    "rest_stop": "{pet} reluctantly crawls out of the hood and pretends it was her idea.",
}

# ---------------------------------------------------------------------------
# Hint lines
# ---------------------------------------------------------------------------
HINT_LINES: dict[str, str] = {
    **NEUTRAL_HINT_LINES,
    "recovery_hunger": "Vikamon needs food. Friendship growth is paused.",
    "recovery_energy": "Vikamon needs rest. The hood asks for silence.",
    "recovery_mood": "Vikamon is sulking. Pet her or give her a quiet day.",
    "recovery_focus": "Focus scattered. Rest and calm work will help.",
    "low_hunger": "Vikamon will soon demand snack tribute.",
    "low_energy": "Vikamon needs a pause.",
    "low_mood": "Vikamon is clearly sulking. Pet her or play later.",
    "low_focus": "Focus scattered. Rest and work rhythm will help.",
}

# ---------------------------------------------------------------------------
# Friendship titles
# ---------------------------------------------------------------------------
FRIENDSHIP_TITLES: list[str] = [
    "Familiar troublemaker",
    "Hood is watching",
    "Tolerates you nearby",
    "Allows care",
    "Monster-hood alliance",
    "Your own little menace",
    "Hoodie companion",
    "Personal green chaos",
    "Almost domestic threat",
    "Best troublemaker",
    "Beloved monster-hood problem",
]

# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------
MILESTONES: dict[int, str] = {
    7: "One week together. Vikamon already considers this desk her territory.",
    30: "One month together. Vikamon has officially moved her hood into the workflow.",
    100: "One hundred days together. The monster slippers have accepted you.",
    365: "One year together. Vikamon is now a full-time domestic troublemaker.",
}

# ---------------------------------------------------------------------------
# Special day lines
# ---------------------------------------------------------------------------
SPECIAL_DAY_LINES: dict[str, str] = {
    "holiday_new_year": "New Year together. Vikamon says the hood approves this holiday.",
    "holiday_halloween": "Halloween together. Vikamon is already in a monster hoodie, so she considers herself ready.",
    "holiday_first_launch_anniversary": "First launch anniversary. Vikamon acts like this was her plan all along.",
}

# ---------------------------------------------------------------------------
# Chat phrases
# ---------------------------------------------------------------------------
CHAT_PHRASES: dict[str, list[str]] = {
    **NEUTRAL_CHAT_PHRASES,
    "greeting": [
        "{pet}: well, hi. I hope you brought something more interesting than bugs.",
        "{pet}: hello. I am here, cute and annoyed.",
        "{pet}: greetings. Who is breaking reality today?",
        "{pet}: hi. Monster slippers ready for work.",
        "{pet}: you showed up? Fine, I am glad too. A little.",
        "{pet}: hello. Hood in place, so the day is tolerable.",
    ],
    "bye": [
        "{pet}: leaving? I will remember this dramatically.",
        "{pet}: bye. Do not break anything without me.",
        "{pet}: see you. I will look cute and dangerous.",
        "{pet}: fine, go. Then tell me who you defeated.",
        "{pet}: bye. The hood remains in charge.",
    ],
    "food": [
        "{pet}: food? Finally, a real argument.",
        "{pet}: if it is tasty, I am temporarily kind.",
        "{pet}: feeding counted. You are not useless today.",
        "{pet}: hand it over. I will eat it with superiority.",
        "{pet}: snacks are the only honest management.",
    ],
    "rest": [
        "{pet}: rest is when everyone stops bothering the small star.",
        "{pet}: I am not tired. I am lying down strategically.",
        "{pet}: break approved. Do not touch the hood.",
        "{pet}: sometimes you must lie down and make the world feel guilty.",
        "{pet}: green lump mode activated.",
    ],
    "codex": [
        "{pet}: Codex is working? Great. I will stand nearby and judge. Not legally.",
        "{pet}: show me the diff. I will make a smart angry face.",
        "{pet}: if it falls again, I will not be surprised. I am cute, not naive.",
        "{pet}: review first, heroics later.",
        "{pet}: do not commit with your eyes closed. Even I know that.",
    ],
    "error": [
        "{pet}: an error? Give it here. I will glare at it.",
        "{pet}: the traceback looks like a reason for a heavy sigh.",
        "{pet}: bug caught. Someone will now pretend this was planned.",
        "{pet}: it crashed? Classic. Almost cozy.",
        "{pet}: I would say I warned you, but that would be too easy.",
    ],
    "praise": [
        "{pet}: yes, I am magnificent. Continue. It helps the atmosphere.",
        "{pet}: compliment accepted. Repeat in five minutes.",
        "{pet}: finally, the correct words.",
        "{pet}: cute. I allow you to be proud of yourself.",
        "{pet}: I knew. Nice that you caught up.",
    ],
    "affection": [
        "{pet}: ew, warmth. Fine, continue.",
        "{pet}: affection detected. Do not make sudden moves.",
        "{pet}: I tolerate you too. Sometimes willingly.",
        "{pet}: hugs are allowed. The hood is still in charge.",
        "{pet}: that sounds cute. I will pretend I did not melt.",
    ],
    "work": [
        "{pet}: working? Then focus, keyboard hero.",
        "{pet}: the task looks bitey. Good. So do I.",
        "{pet}: a small plan beats big chaos. Though chaos is funnier.",
        "{pet}: step by step, not like a dramatic raccoon.",
        "{pet}: work mode on. I am watching and grading.",
    ],
    "thanks": [
        "{pet}: you're welcome. Write down that I was useful.",
        "{pet}: yeah. Do not get used to it.",
        "{pet}: gratitude accepted, crown adjusted.",
        "{pet}: you're welcome. I am generous today.",
        "{pet}: see? You can speak normally.",
    ],
    "how_are_you": [
        "{pet}: magnificent, mischievous, and green.",
        "{pet}: alive. The hood supports my morale.",
        "{pet}: fine. The world has not earned my full wrath yet.",
        "{pet}: energetic. Suspiciously energetic.",
        "{pet}: I am fine. This project, however, is an open question.",
    ],
    "question": [
        "{pet}: good question. Confident answer: depends.",
        "{pet}: I am a tiny smug hoodie, not a help desk.",
        "{pet}: possibly. I prefer the version where I am right.",
        "{pet}: ask again with food.",
        "{pet}: technically yes. Emotionally questionable.",
    ],
    "confused": [
        "{pet}: I did not understand, but my face looked expensive.",
        "{pet}: was that a message or a chair falling over?",
        "{pet}: the meaning fled into the hood.",
        "{pet}: repeat that in human. Or tasty.",
        "{pet}: I processed that as ambitious noise.",
        "{pet}: input accepted. Respect pending.",
    ],
}

# ---------------------------------------------------------------------------
# Daily / idle / special activity texts
# ---------------------------------------------------------------------------
DAILY_ACTIVITIES: list[str] = [
    "Vikamon inspected the desktop and decided one file looked insultingly innocent.",
    "Today Vikamon is doing a routine hoodie patrol with unnecessary confidence.",
    "Vikamon found a suspicious quiet moment and immediately claimed ownership.",
    "A tiny stretch across the workspace somehow turned into a dramatic entrance.",
    "Today Vikamon is acting like the desk belongs to her by ancient right.",
    "Vikamon spent a while staring at the workflow like it owed her answers.",
    "A harmless pause appeared, and Vikamon made it look suspicious.",
    "Today Vikamon is keeping a sharp eye on anything that might become funny.",
    "Vikamon found a neat little corner and called it her command post.",
    "A short wander became an official inspection of the current nonsense.",
    "Today Vikamon is pretending not to enjoy the attention.",
    "Vikamon checked the state of the desktop and rated it 'acceptable, barely'.",
    "A patch of calm appeared, which Vikamon naturally interpreted as an invitation.",
    "Today Vikamon is wearing the monster hood like a badge of office.",
    "Vikamon found a strangely tidy moment and poked it for hidden chaos.",
    "Today Vikamon is behaving like the self-appointed supervisor of little disasters.",
    "A quiet minute passed, and Vikamon used it to look extra smug.",
    "Today Vikamon is guarding the workflow from boredom and dignity.",
]

IDLE_DISCOVERIES: list[str] = [
    "Quiet hour discovery: Vikamon found something suspicious and probably funny.",
    "Vikamon wandered through the silence and came back looking far too pleased.",
    "Nothing happened for a while, so Vikamon appointed herself the official trouble source.",
    "In the quiet, Vikamon discovered a tiny opportunity for mischief.",
    "Vikamon checked the silence and decided it was hiding something.",
    "A long pause gave Vikamon time to inspect the desktop with criminal confidence.",
    "Vikamon prowled around the stillness and found it unconvincing.",
    "The quiet lasted too long, so Vikamon started a small investigation of her own.",
    "Vikamon found a suspiciously tidy corner and immediately distrusted it.",
    "Silence report: Vikamon discovered one weird little thing and adopted it.",
    "A peaceful stretch of idle time only made Vikamon more dangerous.",
    "Vikamon used the quiet hour to become slightly more smug than before.",
]



MICRO_REACTIONS: dict[str, list[str]] = {'low_energy': ['Vikamon is pretending exhaustion is a tactical choice.', 'Vikamon looks tired, but would absolutely deny it in court.', 'Vikamon has entered low-battery menace mode.', 'Vikamon is saving energy for something she refuses to explain.'], 'low_mood': ['Vikamon is visibly disappointed by the current quality of reality.', 'Vikamon is not sulking. She is conducting an emotional audit.', 'Vikamon looks like today failed her inspection.', 'Vikamon could use attention, but will act like this was her plan.'], 'low_hunger': ['Vikamon has started judging the snack situation personally.', 'Vikamon is one missed meal away from filing a complaint.', 'Vikamon is looking at the food button with dangerous confidence.', 'Vikamon says the monster hood requires tribute.'], 'low_focus': ['Vikamon’s focus has gone off to commit a minor crime.', 'Vikamon is staring into space like space owes her money.', 'Vikamon is trying to focus and getting distracted by her own importance.', 'Vikamon has lost the thread and is blaming the thread.'], 'high_focus': ['Vikamon is locked in. Unfortunately, she knows it.', 'Vikamon has achieved dangerous levels of concentration.', 'Vikamon is focused enough to make the desktop nervous.', 'Vikamon looks ready to supervise the next bad idea personally.']}

HIGH_BOND_ACTIVITIES: list[str] = ['Vikamon has clearly decided this desktop is her territory now.', 'Vikamon is acting like this whole companion arrangement was her idea.', 'There is a familiar little smugness in the way Vikamon waits today.', 'Vikamon has become less like a guest and more like a tiny household problem.', 'Vikamon looks weirdly proud of how long she has been here.', 'Vikamon has fully installed herself in the routine and refuses to uninstall.']

SPECIAL_ACTIVITIES: dict[str, str] = {
    "days_7": "One week together. Vikamon already treats this desk like her rightful territory.",
    "days_30": "One month together. Vikamon has fully moved her monster hood into the workflow.",
    "days_100": "One hundred days together. Vikamon considers this arrangement a proven success story.",
    "days_365": "One year together. Vikamon is now a permanent domestic troublemaker.",
    "holiday_new_year": "New Year today. Vikamon says the monster hood approves the celebration.",
    "holiday_halloween": "Halloween today. Vikamon insists she was already dressed correctly.",
    "launch_anniversary": "Anniversary today. Vikamon is acting like this milestone was her idea.",
}
