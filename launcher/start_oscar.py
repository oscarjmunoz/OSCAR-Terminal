from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
LAUNCHER_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
STATE_FILE = LAUNCHER_DIR / "oscar_launcher_state.json"

BACKEND_URL = "http://127.0.0.1:8000/health"
READINESS_URL = "http://127.0.0.1:8000/api/v1/health/readiness"
FRONTEND_URL = "http://127.0.0.1:5173"


def _banner() -> None:
    print("===================================")
    print("OSCAR Trade IA")
    print("Institutional Trading Copilot")
    print("===================================")


def _ok(label: str) -> None:
    print(f"[OK] {label}")


def _warn(label: str) -> None:
    print(f"[WARN] {label}")


def _err(label: str) -> None:
    print(f"[ERROR] {label}")


def _find_venv_python() -> Path | None:
    candidates = [
        ROOT_DIR / ".venv" / "Scripts" / "python.exe",
        BACKEND_DIR / ".venv" / "Scripts" / "python.exe",
        ROOT_DIR.parent / ".venvs" / "oscar-terminal" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _select_python() -> str:
    venv_python = _find_venv_python()
    if venv_python is not None:
        _ok("Virtual Environment")
        return str(venv_python)

    _warn("Virtual Environment not found. Using current Python runtime.")
    return sys.executable


def _check_python_runtime(python_exec: str) -> bool:
    try:
        completed = subprocess.run(
            [python_exec, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False

    if completed.returncode != 0:
        return False

    version = (completed.stdout or completed.stderr).strip()
    _ok(f"Python ({version})")
    return True


def _find_npm() -> str | None:
    for name in ("npm.cmd", "npm"):
        path = shutil_which(name)
        if path:
            return path
    return None


def shutil_which(command: str) -> str | None:
    path_env = os.environ.get("PATH", "")
    if not path_env:
        return None

    for base in path_env.split(os.pathsep):
        candidate = Path(base) / command
        if candidate.exists():
            return str(candidate)
    return None


def _check_node() -> tuple[bool, str | None]:
    node_path = shutil_which("node.exe") or shutil_which("node")
    npm_path = _find_npm()
    if not node_path or not npm_path:
        _err("Node.js / npm not found. Install Node.js 20+ and retry.")
        return False, None

    completed = subprocess.run(
        [node_path, "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    version = (completed.stdout or completed.stderr).strip()
    _ok(f"Node ({version})")
    return True, npm_path


def _check_backend_dependencies(python_exec: str) -> bool:
    import_script = (
        "try:\n"
        "    import fastapi\n"
        "    import uvicorn\n"
        "    import pydantic\n"
        "    import pydantic_settings\n"
        "    import dotenv\n"
        "    import sqlalchemy\n"
        "    import httpx\n"
        "except ImportError as e:\n"
        "    print(e.name)\n"
        "    raise SystemExit(1)\n"
        "raise SystemExit(0)"
    )
    completed = subprocess.run(
        [python_exec, "-c", import_script],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(BACKEND_DIR),
    )

    missing = (completed.stdout or "").strip()
    if completed.returncode != 0:
        _err("Backend dependencies missing.")
        if missing:
            print(f"        Missing Python modules: {missing}")
        print("        Install with: pip install -r backend/requirements.txt")
        return False

    _ok("Backend dependencies")
    return True


def _check_frontend_dependencies() -> bool:
    pkg = FRONTEND_DIR / "package.json"
    node_modules = FRONTEND_DIR / "node_modules"
    if not pkg.exists():
        _err("frontend/package.json not found.")
        return False
    if not node_modules.exists():
        _err("Frontend dependencies not installed.")
        print("        Run: cd frontend && npm install")
        return False
    _ok("Frontend dependencies")
    return True


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _wait_for_http(url: str, timeout_seconds: int = 60) -> tuple[bool, dict[str, Any] | None]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                body = response.read().decode("utf-8", errors="ignore")
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = None
                if 200 <= response.status < 400:
                    return True, payload
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            pass
        time.sleep(1)
    return False, None


def _start_process(command: list[str], cwd: Path) -> subprocess.Popen[Any]:
    flags = 0
    flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    flags |= getattr(subprocess, "DETACHED_PROCESS", 0)

    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )


def _write_state(data: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _kill_pid_tree(pid: int) -> None:
    subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        check=False,
        capture_output=True,
        text=True,
    )


def _load_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _print_summary(mt5_status: str) -> None:
    _ok("Backend")
    _ok("Frontend")
    _ok(f"MT5 ({mt5_status})")
    _ok("Health")
    print("Opening Dashboard...")


def main() -> int:
    parser = argparse.ArgumentParser(description="Start OSCAR Trade IA launcher")
    parser.add_argument("--dry-run", action="store_true", help="Only validate prerequisites")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser")
    args = parser.parse_args()

    _banner()

    python_exec = _select_python()
    if not _check_python_runtime(python_exec):
        _err("Python runtime is not available.")
        return 1

    node_ok, npm_exec = _check_node()
    if not node_ok or not npm_exec:
        return 1

    if not _check_backend_dependencies(python_exec):
        return 1
    if not _check_frontend_dependencies():
        return 1

    existing = _load_state()
    if existing:
        backend_pid = int(existing.get("backend", {}).get("pid", 0))
        frontend_pid = int(existing.get("frontend", {}).get("pid", 0))
        if backend_pid and frontend_pid and _is_pid_running(backend_pid) and _is_pid_running(frontend_pid):
            _warn("OSCAR appears to be already running.")
            if not args.no_open:
                webbrowser.open(FRONTEND_URL)
            return 0

    if _port_in_use(8000):
        _err("Port 8000 is already in use. Stop conflicting process and retry.")
        return 1
    if _port_in_use(5173):
        _err("Port 5173 is already in use. Stop conflicting process and retry.")
        return 1

    if args.dry_run:
        _ok("Dry run completed")
        return 0

    backend_cmd = [python_exec, "run.py"]
    backend_proc = _start_process(backend_cmd, BACKEND_DIR)

    backend_ready, _ = _wait_for_http(BACKEND_URL, timeout_seconds=90)
    if not backend_ready:
        _err("Backend did not become healthy in time.")
        _kill_pid_tree(backend_proc.pid)
        return 1

    frontend_cmd = [npm_exec, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"]
    frontend_proc = _start_process(frontend_cmd, FRONTEND_DIR)

    frontend_ready, _ = _wait_for_http(FRONTEND_URL, timeout_seconds=120)
    if not frontend_ready:
        _err("Frontend did not become available in time.")
        _kill_pid_tree(frontend_proc.pid)
        _kill_pid_tree(backend_proc.pid)
        return 1

    mt5_status = "unknown"
    readiness_ok, readiness_payload = _wait_for_http(READINESS_URL, timeout_seconds=5)
    if readiness_ok and readiness_payload and isinstance(readiness_payload, dict):
        items = readiness_payload.get("items", [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("key") == "mt5":
                    mt5_status = str(item.get("status", "unknown")).lower()
                    break

    state = {
        "startedAt": int(time.time()),
        "backend": {"pid": backend_proc.pid, "cwd": str(BACKEND_DIR), "command": backend_cmd},
        "frontend": {"pid": frontend_proc.pid, "cwd": str(FRONTEND_DIR), "command": frontend_cmd},
    }
    _write_state(state)

    _print_summary(mt5_status)

    if not args.no_open:
        webbrowser.open(FRONTEND_URL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
