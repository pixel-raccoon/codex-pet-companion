from __future__ import annotations

import random

from .text_profiles import text_profile_id


NEUTRAL_PHRASES = {
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

LUMISPROUT_PHRASES = {
    **NEUTRAL_PHRASES,
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

VIKAMON_PHRASES = {
    **NEUTRAL_PHRASES,
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
        "{pet} taps the finished answer: “Show me.”",
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
        "{pet} makes an “I told you so” face, even if she did not.",
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
        "{pet} enters “do not touch, will bite” mode.",
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

PHRASE_BANKS = {
    "neutral": NEUTRAL_PHRASES,
    "lumisprout": LUMISPROUT_PHRASES,
    "vikamon": VIKAMON_PHRASES,
}


def phrase(event: str, pet_name: str, pet_id: str) -> str:
    bank = PHRASE_BANKS.get(text_profile_id(pet_id), NEUTRAL_PHRASES)
    options = bank.get(event) or NEUTRAL_PHRASES.get(event) or ["{pet} reacts."]
    return random.choice(options).format(pet=pet_name)


CHAT_NEUTRAL = {
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

CHAT_LUMISPROUT = {
    **CHAT_NEUTRAL,
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

CHAT_VIKAMON = {
    **CHAT_NEUTRAL,
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

CHAT_BANKS = {
    "neutral": CHAT_NEUTRAL,
    "lumisprout": CHAT_LUMISPROUT,
    "vikamon": CHAT_VIKAMON,
}


def has_any(low: str, words: list[str]) -> bool:
    return any(word in low for word in words)


def classify_chat(text: str) -> str:
    low = " ".join(text.lower().strip().replace(",", " ").replace("!", " ").split())
    if not low:
        return "confused"

    greeting_words = ["hi", "hello", "hey", "yo", "good morning", "good afternoon", "good evening"]
    if low in greeting_words or has_any(low, ["hello", "hey there", "good morning", "good afternoon", "good evening"]):
        return "greeting"

    how_words = [
        "how are you", "how r u", "how do you do", "how is it going",
        "how's it going", "how are u", "you ok", "are you ok"
    ]
    if has_any(low, how_words):
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


def chat_response(text: str, pet_name: str, pet_id: str) -> str:
    bank = CHAT_BANKS.get(text_profile_id(pet_id), CHAT_NEUTRAL)
    category = classify_chat(text)
    options = bank.get(category) or CHAT_NEUTRAL["confused"]
    return random.choice(options).format(pet=pet_name)
