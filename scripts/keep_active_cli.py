"""keep_active_cli.py - command-line Keep Active for Windows and Linux.

Sends an F15 keypress or a 1px mouse nudge at random intervals so the
system idle timer (which Teams uses for "Away") keeps resetting.

Usage:
    python keep_active_cli.py                      # F15 every 60-180 s
    python keep_active_cli.py --method mouse       # 1px mouse nudge instead
    python keep_active_cli.py --min 30 --max 120   # custom interval (seconds)

Stop with Ctrl+C.

Windows: no extra packages needed.
Linux:   needs xdotool (sudo apt install xdotool). Works on X11 sessions;
         on Wayland, xdotool usually can't reset the system idle timer.
"""

import argparse
import random
import shutil
import subprocess
import sys
import time

MAX_SECONDS = 290  # stay under Teams' 5-minute idle threshold


def windows_backend(method):
    import ctypes

    user32 = ctypes.windll.user32
    # Keep the PC from sleeping / turning off the display while running.
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x1 | 0x2)

    def ping():
        if method == "mouse":
            user32.mouse_event(0x0001, 1, 0, 0, 0)
            time.sleep(0.05)
            user32.mouse_event(0x0001, -1, 0, 0, 0)
        else:
            user32.keybd_event(0x7E, 0, 0, 0)       # F15 down
            user32.keybd_event(0x7E, 0, 0x0002, 0)  # F15 up

    return ping


def linux_backend(method):
    if not shutil.which("xdotool"):
        sys.exit("xdotool not found. Install it first: sudo apt install xdotool")

    if method == "mouse":
        cmds = [["xdotool", "mousemove_relative", "--", "1", "0"],
                ["xdotool", "mousemove_relative", "--", "-1", "0"]]
    else:
        cmds = [["xdotool", "key", "F15"]]

    def ping():
        for cmd in cmds:
            subprocess.run(cmd, check=False)

    return ping


def main():
    parser = argparse.ArgumentParser(description="Keep the system (and Teams) from going idle.")
    parser.add_argument("--method", choices=["f15", "mouse"], default="f15",
                        help="f15 = invisible keypress (default), mouse = 1px nudge")
    parser.add_argument("--min", type=int, default=60, help="min seconds between pings (default 60)")
    parser.add_argument("--max", type=int, default=180, help="max seconds between pings (default 180)")
    args = parser.parse_args()

    lo, hi = sorted((max(1, args.min), max(1, args.max)))
    hi = min(hi, MAX_SECONDS)
    lo = min(lo, hi)

    if sys.platform == "win32":
        ping = windows_backend(args.method)
    elif sys.platform.startswith("linux"):
        ping = linux_backend(args.method)
    else:
        sys.exit(f"Unsupported platform: {sys.platform}")

    print(f"Keep Active running ({args.method}, every {lo}-{hi} s). Press Ctrl+C to stop.")
    try:
        while True:
            ping()
            wait = random.randint(lo, hi)
            print(f"[{time.strftime('%H:%M:%S')}] ping sent, next in {wait}s", flush=True)
            time.sleep(wait)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
