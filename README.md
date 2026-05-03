# Codex Pet Companion

A small desktop pet companion for working alongside Codex.

## What it does

- Shows a pet in full mode and mini mode.
- Switches to a running animation while you drag the mini pet.
- Reacts to Codex activity: task starts, tool calls, ready-to-review answers, and errors.
- Shows short notifications near the mini pet.
- Includes tamagotchi-style stats: fullness, mood, energy, focus, rest, friendship, and days together.
- Includes built-in pets:
  - Lumisprout — a tiny glowing sprout-cat forest spirit.
  - Vikamon — a mischievous chibi mascot in a green monster hoodie.
- Supports custom pet packs through the "Adopt pet" button.
- Achievements use neutral names and work with any pet.
- Includes minimal special dates: 7/30/100/365 days together, New Year, Halloween, and first launch anniversary.

## Where data is stored

Normal mode:

```text
%CODEX_HOME%/pet-companion/
```

If `CODEX_HOME` is not set:

```text
%USERPROFILE%/.codex/pet-companion/
```

This folder contains:

```text
config.json
state.json
```

If you create this empty file next to the app:

```text
portable.flag
```

the app switches to portable mode and stores `config.json` and `state.json` next to itself.

## How to use

1. Run `start_companion_qt.bat` or the exe build.
2. Check the Codex folder in Settings.
3. Choose a pet.
4. Open mini mode from the button in the main window.
5. Double-click the mini pet to return to the full window.

## Custom pets

A pet pack must contain:

```text
pet.json
spritesheet.webp
```

Spritesheet grid:

```text
1536x1872
8 columns x 9 rows
192x208 per frame
transparent background
```

Custom pets use neutral text, so they will not receive Lumisprout or Vikamon-specific lines.

## App icon

The release includes an icon:

```text
app_icon.ico
```

The build scripts use it automatically, so the generated `.exe` receives the icon.

## Build exe

On Windows, install dependencies and run:

```text
build_windows_exe.bat
```

The finished file will appear here:

```text
dist/CodexPetCompanion.exe
```

For a console/debug build, run:

```text
build_windows_exe_debug.bat
```
