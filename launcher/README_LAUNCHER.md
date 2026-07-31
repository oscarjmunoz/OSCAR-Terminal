# OSCAR Launcher (Windows)

This launcher starts and stops OSCAR Lite from the project root using relative paths only.

## Files

- `start_oscar.bat`
- `stop_oscar.bat`
- `restart_oscar.bat`
- `check_system.bat`

## How To Start

1. Double click `launcher/start_oscar.bat`.
2. It checks that `backend` and `frontend` exist.
3. It starts backend in a new terminal window:
   - If `backend/.venv` exists, it activates that environment.
   - Runs `python run.py`.
4. It starts frontend in another terminal window with `npm run dev`.
5. It waits for Vite and opens `http://localhost:5174` automatically.

## How To Stop

1. Double click `launcher/stop_oscar.bat`.
2. It closes launcher-created windows and stops OSCAR-related Python/Node processes.

## How To Restart

1. Double click `launcher/restart_oscar.bat`.
2. It runs stop first, then start.

## How To Verify System

1. Double click `launcher/check_system.bat`.
2. It verifies:
   - Python
   - Node
   - npm
   - Git
   - MT5 installation (common paths)
   - Backend and frontend project structure

## Compatibility

- Windows 10
- Windows 11

## Notes

- All scripts use relative paths from the repository root.
- No backend, frontend, pipeline, or engine code is modified by launcher scripts.
