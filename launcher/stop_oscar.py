from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

LAUNCHER_DIR = Path(__file__).resolve().parent
STATE_FILE = LAUNCHER_DIR / "oscar_launcher_state.json"


def _banner() -> None:
    print("===================================")
    print("OSCAR Trade IA")
    print("Stop Launcher")
    print("===================================")


def _ok(label: str) -> None:
    print(f"[OK] {label}")


def _warn(label: str) -> None:
    print(f"[WARN] {label}")


def _load_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _kill_pid_tree(pid: int) -> bool:
    completed = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def _collect_pids(state: dict[str, Any]) -> list[int]:
    pids: list[int] = []
    for key in ("backend", "frontend"):
        block = state.get(key, {})
        if isinstance(block, dict):
            pid = int(block.get("pid", 0) or 0)
            if pid > 0:
                pids.append(pid)
    return pids


def main() -> int:
    _banner()

    state = _load_state()
    if not state:
        _warn("No launcher state found. Nothing to stop.")
        return 0

    pids = _collect_pids(state)
    if not pids:
        _warn("No managed process IDs found in launcher state.")
        return 0

    failed: list[int] = []
    for pid in pids:
        if _kill_pid_tree(pid):
            _ok(f"Stopped process tree PID {pid}")
        else:
            failed.append(pid)

    time.sleep(1)

    if STATE_FILE.exists():
        STATE_FILE.unlink()

    if failed:
        _warn(f"Some managed processes were not stopped: {', '.join(str(p) for p in failed)}")
        return 1

    _ok("Backend")
    _ok("Frontend")
    _ok("Launcher state cleared")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
