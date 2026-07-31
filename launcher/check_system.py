"""System checks for OSCAR launcher prerequisites."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import sys


@dataclass
class CheckResult:
    label: str
    status: str
    detail: str = ""


def detect_project_root(start: Path) -> Path:
    """Find project root by searching for backend and frontend folders."""
    for candidate in [start, *start.parents]:
        if (candidate / "backend").is_dir() and (candidate / "frontend").is_dir():
            return candidate
    raise RuntimeError("Could not detect project root (backend/frontend missing).")


def _tool_result(binary: str, label: str) -> CheckResult:
    resolved = shutil.which(binary)
    if resolved:
        return CheckResult(label=label, status="OK", detail=resolved)
    return CheckResult(label=label, status="MISSING")


def _mt5_result() -> CheckResult:
    if os.name != "nt":
        return CheckResult(label="MT5", status="WARN", detail="Auto-detection currently focused on Windows.")

    common_paths = [
        Path(os.environ.get("ProgramFiles", "")) / "MetaTrader 5" / "terminal64.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "MetaTrader 5" / "terminal64.exe",
    ]
    for mt5_path in common_paths:
        if mt5_path.exists():
            return CheckResult(label="MT5", status="OK", detail=str(mt5_path))

    appdata = Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal"
    if appdata.exists():
        for candidate in appdata.glob("**/terminal64.exe"):
            return CheckResult(label="MT5", status="OK", detail=str(candidate))

    return CheckResult(label="MT5", status="WARN", detail="Not detected in common paths.")


def run_system_check(start_dir: Path | None = None) -> tuple[list[CheckResult], int]:
    """Run full system checks and return results with an exit code."""
    here = start_dir or Path(__file__).resolve().parent
    root = detect_project_root(here)

    results: list[CheckResult] = [
        _tool_result("python", "Python"),
        _tool_result("node", "Node"),
        _tool_result("npm", "npm"),
        _tool_result("git", "Git"),
    ]

    backend_dir = root / "backend"
    frontend_dir = root / "frontend"

    results.extend(
        [
            CheckResult("Backend", "OK" if backend_dir.is_dir() else "MISSING", str(backend_dir)),
            CheckResult(
                "Backend run.py",
                "OK" if (backend_dir / "run.py").is_file() else "MISSING",
                str(backend_dir / "run.py"),
            ),
            CheckResult("Frontend", "OK" if frontend_dir.is_dir() else "MISSING", str(frontend_dir)),
            CheckResult(
                "Frontend package.json",
                "OK" if (frontend_dir / "package.json").is_file() else "MISSING",
                str(frontend_dir / "package.json"),
            ),
            _mt5_result(),
        ]
    )

    has_missing = any(item.status == "MISSING" for item in results)
    return results, 1 if has_missing else 0


def print_report(results: list[CheckResult]) -> None:
    """Print launcher-style report."""
    print("=" * 38)
    print("OSCAR Launcher - SYSTEM CHECK")
    print("=" * 38)
    for row in results:
        detail = f" ({row.detail})" if row.detail else ""
        print(f"[{row.status}] {row.label}{detail}")


def main() -> int:
    try:
        results, code = run_system_check()
    except Exception as exc:  # pragma: no cover - defensive error path
        print(f"[ERROR] {exc}")
        return 1

    print_report(results)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
