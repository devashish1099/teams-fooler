"""Keep Active - keeps Windows (and Microsoft Teams) from marking you idle.

Sends a harmless F15 keypress or a 1px mouse nudge at random intervals,
which resets the Windows idle timer that Teams uses for "Away" status.
Standard library only (tkinter + ctypes). Windows only.
"""

import ctypes
import random
import sys
import time
import tkinter as tk
from tkinter import ttk

if sys.platform != "win32":
    sys.exit("Keep Active only runs on Windows.")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_F15 = 0x7E
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_MOVE = 0x0001

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

METHOD_F15 = "F15 keypress (invisible)"
METHOD_MOUSE = "Mouse nudge (1px)"

MIN_SECONDS = 5
MAX_SECONDS = 290  # stay under Teams' 5-minute idle threshold


def press_f15():
    user32.keybd_event(VK_F15, 0, 0, 0)
    user32.keybd_event(VK_F15, 0, KEYEVENTF_KEYUP, 0)


def nudge_mouse():
    user32.mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_MOVE, -1, 0, 0, 0)


def keep_awake(on):
    flags = ES_CONTINUOUS
    if on:
        flags |= ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    kernel32.SetThreadExecutionState(flags)


class App:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.ping_job = None
        self.next_ping_at = 0.0
        self.last_ping = "never"

        root.title("Keep Active")
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=14)
        frame.grid()

        ttk.Label(frame, text="Method").grid(row=0, column=0, sticky="w")
        self.method = tk.StringVar(value=METHOD_F15)
        ttk.Combobox(
            frame, textvariable=self.method, state="readonly", width=26,
            values=[METHOD_F15, METHOD_MOUSE],
        ).grid(row=0, column=1, columnspan=3, sticky="we", pady=4)

        ttk.Label(frame, text="Interval (sec)").grid(row=1, column=0, sticky="w")
        self.min_s = tk.IntVar(value=60)
        self.max_s = tk.IntVar(value=180)
        ttk.Spinbox(frame, from_=MIN_SECONDS, to=MAX_SECONDS, width=6,
                    textvariable=self.min_s).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Label(frame, text="to").grid(row=1, column=2, padx=4)
        ttk.Spinbox(frame, from_=MIN_SECONDS, to=MAX_SECONDS, width=6,
                    textvariable=self.max_s).grid(row=1, column=3, sticky="w", pady=4)

        self.button = ttk.Button(frame, text="Start", command=self.toggle)
        self.button.grid(row=2, column=0, columnspan=4, sticky="we", pady=(10, 6))

        self.status = tk.StringVar(value="Paused")
        ttk.Label(frame, textvariable=self.status, foreground="#555").grid(
            row=3, column=0, columnspan=4, sticky="w")

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tick()

    def interval(self):
        try:
            lo, hi = int(self.min_s.get()), int(self.max_s.get())
        except (tk.TclError, ValueError):
            lo, hi = 60, 180
        lo = max(MIN_SECONDS, min(lo, MAX_SECONDS))
        hi = max(MIN_SECONDS, min(hi, MAX_SECONDS))
        if lo > hi:
            lo, hi = hi, lo
        return random.randint(lo, hi)

    def toggle(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def start(self):
        self.running = True
        self.button.config(text="Pause")
        keep_awake(True)
        self.ping()

    def pause(self):
        self.running = False
        self.button.config(text="Start")
        if self.ping_job:
            self.root.after_cancel(self.ping_job)
            self.ping_job = None
        keep_awake(False)

    def ping(self):
        if not self.running:
            return
        if self.method.get() == METHOD_MOUSE:
            nudge_mouse()
        else:
            press_f15()
        self.last_ping = time.strftime("%H:%M:%S")
        delay = self.interval()
        self.next_ping_at = time.monotonic() + delay
        self.ping_job = self.root.after(delay * 1000, self.ping)

    def tick(self):
        if self.running:
            left = max(0, int(self.next_ping_at - time.monotonic()))
            self.status.set(f"Running · next in {left}s · last ping {self.last_ping}")
        else:
            self.status.set(f"Paused · last ping {self.last_ping}")
        self.root.after(1000, self.tick)

    def on_close(self):
        self.pause()
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
