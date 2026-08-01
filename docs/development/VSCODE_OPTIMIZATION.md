# VS Code Optimization for OSCAR Terminal

## Workspace Strategy

Use focused workspace files and avoid opening the full repository folder when developing.

- OSCAR-Backend.code-workspace includes only `backend/` and `backend/tests/`
- OSCAR-Frontend.code-workspace includes only `frontend/`
- OSCAR-Docs.code-workspace includes only `docs/`

Why this works:

- Lower file index scope for Python, TypeScript, and search services
- Fewer file system watchers, especially on large generated directories
- Less extension-host memory pressure on 8 GB machines

## Memory Optimization

The shared `.vscode/settings.json` uses a low-memory profile designed for Windows 10 + 8 GB RAM.

Key optimizations:

- Exclude heavy folders from explorer, search, and watchers:
  - `node_modules`, `dist`, `build`, `.vite`, `.git`, `coverage`, `.pytest_cache`, `__pycache__`, `.venv`, `logs`
- TypeScript memory cap:
  - `typescript.tsserver.maxTsServerMemory = 768`
- Python analysis optimization:
  - Disable full indexing
  - Limit user file indexing
  - Analyze open files only
- Git background activity reduction:
  - Disable auto-fetch and auto-refresh
  - Disable decorations and hide untracked noise
- Extension host load reduction:
  - Disable extension auto-update checks
  - Disable npm script auto-detection
- Editor feature trimming:
  - Disable minimap, sticky scroll, CodeLens, inlay hints, and breadcrumbs

## Extension Recommendations

Only these extensions are recommended:

- OpenAI ChatGPT (`openai.chatgpt`)
- Python (`ms-python.python`)
- Pylance (`ms-python.vscode-pylance`)
- Debugpy (`ms-python.debugpy`)
- Prettier (`esbenp.prettier-vscode`)
- ESLint (`dbaeumer.vscode-eslint`)
- Material Icon Theme (`pkief.material-icon-theme`)

## Best Practices

- Open only one focused workspace at a time.
- Keep one backend terminal and one frontend terminal active; close extras.
- Run tests/builds from tasks, not multiple ad-hoc shells.
- Restart VS Code after dependency updates or branch switches.
- Avoid installing large extension packs on this hardware profile.

## Tasks and Debug Profiles

Configured tasks:

- Run Backend
- Run Frontend
- Run pytest
- npm install
- npm run build

Configured debug profiles:

- FastAPI: Debug Backend
- React/Vite: Debug Frontend
