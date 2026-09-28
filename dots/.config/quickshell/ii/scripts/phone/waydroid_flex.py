#!/usr/bin/env python3
"""Start a Waydroid Flex window without selecting the user's physical phone."""

import os
import fcntl
import re
import subprocess
import sys
import time
from pathlib import Path


def run(command, timeout=12):
    return subprocess.run(command, text=True, capture_output=True, timeout=timeout)


def status():
    return run(["waydroid", "status"]).stdout


def fail(message):
    print("WAYDROID_FLEX_ERROR: " + message, flush=True)
    subprocess.run(["notify-send", "Waydroid Flex", message], check=False)
    raise SystemExit(1)


def main():
    if not os.environ.get("WAYLAND_DISPLAY") or not os.environ.get("XDG_RUNTIME_DIR"):
        fail("Wayland desktop session is unavailable")

    lock_path = Path(os.environ["XDG_RUNTIME_DIR"]) / "waydroid-flex.lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fail("Waydroid Flex is already open")
    os.set_inheritable(lock_fd, True)

    current = status()
    if "Session:\tRUNNING" not in current:
        log = Path.home() / ".cache/illogical-impulse/phone/waydroid-session.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a") as output:
            subprocess.Popen(["waydroid", "session", "start"], stdin=subprocess.DEVNULL,
                             stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        for _ in range(45):
            time.sleep(1)
            current = status()
            if "Session:\tRUNNING" in current:
                break
        else:
            fail("Waydroid session did not start; see " + str(log))

    # Keeping the native surface open prevents Waydroid from suspending its
    # container while scrcpy's virtual display is active.
    ui = run(["waydroid", "show-full-ui"], timeout=20)
    if ui.returncode:
        fail("Could not open Waydroid: " + (ui.stderr.strip() or ui.stdout.strip()))

    for _ in range(20):
        current = status()
        if "Container:\tRUNNING" in current:
            break
        time.sleep(1)
    else:
        fail("Waydroid container is not running")

    match = re.search(r"^IP address:\s*(\d+\.\d+\.\d+\.\d+)\s*$", current, re.M)
    if not match:
        fail("Waydroid did not report an ADB address")
    serial = match.group(1) + ":5555"

    for _ in range(15):
        run(["adb", "connect", serial], timeout=5)
        devices = run(["adb", "devices"], timeout=5).stdout
        if re.search(r"^" + re.escape(serial) + r"\s+device\s*$", devices, re.M):
            break
        if re.search(r"^" + re.escape(serial) + r"\s+unauthorized\s*$", devices, re.M):
            fail("Allow the ADB debugging prompt in Waydroid, then try again")
        time.sleep(1)
    else:
        fail("Waydroid ADB did not become available")

    print("WAYDROID_FLEX_READY", flush=True)
    os.execvp("scrcpy", ["scrcpy", "-s", serial,
                        "--new-display=540x960/180", "--flex-display", "--no-audio",
                        "--video-encoder=c2.android.avc.encoder",
                        "--max-size=960", "--video-bit-rate=4M", "--max-fps=60",
                        "--start-app=com.android.settings", "--window-title=Waydroid Flex"])


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(str(exc))
