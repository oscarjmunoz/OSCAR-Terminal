"""Python launcher for OSCAR Terminal.

Responsibilities:
- Detect project root automatically.
- Start backend and wait for /health HTTP 200.
- Start frontend and wait until frontend URL responds.
- Open browser.
- Stop processes previously started by this launcher.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

from config import CONFIG
from check_system import run_system_check, print_report


STATE_FILE = ".oscar_launcher_state.json"


def detect_project_root(start: Path) -> Path:
    """Find project root by walking up until backend/frontend are found."""
    for candidate in [start, *start.parents]:
        if (candidate / "backend").is_dir() and (candidate / "frontend").is_dir():
            return candidate
    raise RuntimeError("Could not detect project root. Expected backend and frontend folders.")


def _wait_for_http(url: str, timeout_sec: int, strict_200: bool, poll_interval_sec: float) -> bool:
    """Poll URL until it responds, optionally requiring HTTP 200."""
    deadline = time.time() + timeout_sec
    req = urllib.request.Request(url, headers={"User-Agent": "OSCAR-Launcher"})

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(req, timeout=2) as response:
                status = response.getcode()
                if strict_200 and status == 200:
                    return True
                if not strict_200 and 100 <= status < 500:
                    return True
        except urllib.error.URLError:
            pass
        except TimeoutError:
            pass

        time.sleep(poll_interval_sec)

    return False


def _python_for_backend(backend_dir: Path) -> str:
    """Pick backend Python interpreter with virtualenv preference."""
    if os.name == "nt":
        venv_python = backend_dir / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = backend_dir / ".venv" / "bin" / "python"

    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _npm_binary() -> str:
    """Use npm.cmd on Windows and npm elsewhere."""
    return "npm.cmd" if os.name == "nt" else "npm"


def _creation_flags() -> int:
    """Process creation flags for detached consoles on Windows."""
    if os.name != "nt":
        return 0
    return subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]


def _state_path(launcher_dir: Path) -> Path:
    return launcher_dir / STATE_FILE


def _write_state(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _terminate_pid(pid: int) -> None:
    """Stop process by PID, including children on Windows."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return


def start() -> int:
    launcher_dir = Path(__file__).resolve().parent
    root = detect_project_root(launcher_dir)
    backend_dir = root / "backend"
    frontend_dir = root / "frontend"

    if not backend_dir.is_dir() or not frontend_dir.is_dir():
        print("[ERROR] Backend or frontend folder not found.")
        return 1

    env = os.environ.copy()
    env["OSCAR_LAUNCHER"] = "1"
    env["OSCAR_ROOT"] = str(root)

    backend_cmd = [_python_for_backend(backend_dir), "run.py"]
    frontend_cmd = [_npm_binary(), "run", "dev", "--", "--host", CONFIG.host, "--port", str(CONFIG.frontend_port)]

    print("Starting backend...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(backend_dir),
        env=env,
        creationflags=_creation_flags(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_http(CONFIG.backend_health_url, CONFIG.backend_timeout_sec, strict_200=True, poll_interval_sec=CONFIG.poll_interval_sec):
        _terminate_pid(backend_proc.pid)
        print("[ERROR] Backend did not return HTTP 200 on /health.")
        return 1

    print("Backend Ready")

    print("Starting frontend...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(frontend_dir),
        env=env,
        creationflags=_creation_flags(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not _wait_for_http(CONFIG.frontend_url, CONFIG.frontend_timeout_sec, strict_200=False, poll_interval_sec=CONFIG.poll_interval_sec):
        _terminate_pid(frontend_proc.pid)
        _terminate_pid(backend_proc.pid)
        print(f"[ERROR] Frontend did not respond on {CONFIG.frontend_url}.")
        return 1

    print("Frontend Ready")

    try:
        if CONFIG.browser:
            webbrowser.get(CONFIG.browser).open(CONFIG.frontend_url)
        else:
            webbrowser.open(CONFIG.frontend_url)
    except webbrowser.Error:
        print("[WARN] Browser could not be opened automatically.")

    _write_state(
        _state_path(launcher_dir),
        {
            "project_root": str(root),
            "backend_pid": backend_proc.pid,
            "frontend_pid": frontend_proc.pid,
            "backend_url": CONFIG.backend_health_url,
            "frontend_url": CONFIG.frontend_url,
            "started_at": time.time(),
        },
    )

    print("OSCAR Ready")
    return 0


def stop() -> int:
    launcher_dir = Path(__file__).resolve().parent
    state = _read_state(_state_path(launcher_dir))

    if not state:
        print("[WARN] No launcher state file found. Nothing to stop.")
        return 0

    for key in ("frontend_pid", "backend_pid"):
        pid = state.get(key)
        if isinstance(pid, int) and pid > 0:
            _terminate_pid(pid)

    try:
        _state_path(launcher_dir).unlink(missing_ok=True)
    except OSError:
        pass

    print("OSCAR processes stopped.")
    return 0


def restart() -> int:
    stop_code = stop()
    if stop_code != 0:
        return stop_code
    time.sleep(1)
    return start()


def check() -> int:
    results, code = run_system_check(Path(__file__).resolve().parent)
    print_report(results)
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OSCAR Python launcher")
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        choices=["start", "stop", "restart", "check"],
        help="Launcher command to execute.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.command == "start":
        return start()
    if args.command == "stop":
        return stop()
    if args.command == "restart":
        return restart()
    if args.command == "check":
        return check()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
