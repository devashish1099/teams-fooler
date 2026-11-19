# Keep Active

A tiny Windows app that keeps Microsoft Teams (and Windows) from marking you as idle/Away.

## Run it

1. Download **[KeepActive.exe](https://github.com/devashish1099/teams-fooler/releases/latest/download/KeepActive.exe)** (or from the [Releases](https://github.com/devashish1099/teams-fooler/releases) page).
2. Double-click it. No install, no Python needed.
3. If Windows shows "Windows protected your PC" (the exe isn't code-signed), click **More info → Run anyway**.
4. Pick a method, set the interval, press **Start**. Press **Pause** to stop. Close the window to quit.

From source instead: `python keep_active.py` (Python 3.8+, no extra packages).

## How it works

Teams goes Away after ~5 minutes without keyboard/mouse input (it reads the Windows idle timer).
At a random interval you choose (default 60–180 s, capped at 290 s) the app sends one of:

- **F15 keypress** – a key that almost no app reacts to; invisible, doesn't disturb your typing.
- **Mouse nudge** – moves the cursor 1px and back.

While running it also tells Windows not to sleep or turn off the display.

## Build the exe yourself

```bat
build.bat
```

Output: `dist\KeepActive.exe`.

## Limits

- Windows only.
- If the PC is locked manually, Teams will still show Away.
- Activity-monitoring software can detect software-injected input.
