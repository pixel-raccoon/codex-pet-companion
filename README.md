# Codex Pet Companion

A small desktop tamagotchi-style pet companion for working alongside Codex.

![Codex Pet Companion screenshot](screenshot.png)

## Download

Get the latest Windows build from the [Releases](https://github.com/pixel-raccoon/codex-pet-companion/releases) page.

Download `CodexPetCompanion.exe`, run it, then choose your Codex folder in Settings.

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

## How Codex affects the pet

Codex affects the pet through work activity.

When Codex starts a task, thinks, writes, or runs tools, the pet becomes more focused and gains a little friendship, but spends energy faster.

When Codex finishes an answer or review, the pet gains mood, focus, and friendship.

If Codex reports an error, the pet reacts as if stressed and may lose a little mood or focus.

In short: the pet lives next to your Codex workflow and reacts to activity, success, and errors.

## Where data is stored

Normal mode:

```text
%CODEX_HOME%/pet-companion/

If CODEX_HOME is not set:

%USERPROFILE%/.codex/pet-companion/

This folder contains:

config.json
state.json

If you create this empty file next to the app:

portable.flag

the app switches to portable mode and stores config.json and state.json next to itself.

How to use
Download CodexPetCompanion.exe from Releases.
Run the app.
Check the Codex folder in Settings.
Choose a pet.
Open mini mode from the button in the main window.
Double-click the mini pet to return to the full window.

If you are running from source, use:

start_companion_qt.bat
Custom pets

A pet pack must contain:

pet.json
spritesheet.webp

Spritesheet grid:

1536x1872
8 columns x 9 rows
192x208 per frame
transparent background

Custom pets use neutral text, so they will not receive Lumisprout or Vikamon-specific lines.

App icon

The release includes an icon:

app_icon.ico

The build scripts use it automatically, so the generated .exe receives the icon.

Build exe

On Windows, install dependencies and run:

build_windows_exe.bat

The finished file will appear here:

dist/CodexPetCompanion.exe

For a console/debug build, run:

build_windows_exe_debug.bat