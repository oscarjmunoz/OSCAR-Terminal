# OSCAR Python Launcher

This folder contains the Python-based launcher for OSCAR Terminal.

## Files

- `launcher.py`: Start/stop/restart/check entrypoint.
- `config.py`: Host, ports, browser, and timeout configuration.
- `check_system.py`: Tool and project structure validation.

## Behavior

`launcher.py start` does the following:

1. Detects project root automatically.
2. Verifies `backend` and `frontend` folders.
3. Starts backend (`backend/run.py`).
4. Waits for `http://127.0.0.1:8000/health` to return HTTP 200.
5. Starts frontend (`npm run dev -- --host 127.0.0.1 --port 5173`).
6. Waits for `http://localhost:5173` to respond.
7. Opens browser.
8. Prints:
   - `Backend Ready`
   - `Frontend Ready`
   - `OSCAR Ready`

## Configuration

Defaults are in `config.py`, and can be overridden via environment variables:

- `OSCAR_HOST` (default `127.0.0.1`)
- `OSCAR_BACKEND_PORT` (default `8000`)
- `OSCAR_FRONTEND_PORT` (default `5173`)
- `OSCAR_BROWSER` (optional browser controller name)
- `OSCAR_BACKEND_TIMEOUT` (seconds, default `120`)
- `OSCAR_FRONTEND_TIMEOUT` (seconds, default `120`)
- `OSCAR_POLL_INTERVAL` (seconds, default `1.0`)

## Usage

From this `launcher` folder:

```bash
python launcher.py start
python launcher.py stop
python launcher.py restart
python launcher.py check
```

## Windows BAT wrappers

- `start_oscar.bat` calls `python launcher.py start`
- `stop_oscar.bat` calls `python launcher.py stop`

This keeps launcher logic in Python and BAT files minimal.

## Linux readiness

The implementation is prepared for Linux:

- Uses `pathlib` and cross-platform process spawning.
- Uses `taskkill` only on Windows and signals on non-Windows.
- Keeps host/ports/timeouts configurable.
