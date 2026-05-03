# Codex Pet Companion 1.0.3-en

English release package.

## Included

- Full and mini pet modes.
- Codex activity reactions.
- Tamagotchi-style stats: fullness, mood, energy, focus, rest, friendship, and days together.
- Built-in pets: Lumisprout and Vikamon.
- Custom pet packs.
- Neutral text for custom pets.
- Special dates and milestone achievements.
- Portable mode through `portable.flag`.
- App icon included in the PyInstaller build scripts.

## Data

Normal mode:

```text
%CODEX_HOME%/pet-companion/
```

If `CODEX_HOME` is not set:

```text
%USERPROFILE%/.codex/pet-companion/
```

Portable mode:

```text
portable.flag next to the exe
```


## 1.0.3-en

- Rebalanced rest and energy.
- Offline time now behaves like sleep: energy no longer drains while the app is closed.
- Rest gives an immediate low-energy boost and restores energy much faster.
- Pressing Rest again no longer cancels rest; it says the pet is already resting.
- Feed, pet, play, chat, or Codex work can interrupt rest with a separate log message.
