# OSCAR Architecture

## Overview

OSCAR Terminal is a trading decision platform with separated backend and frontend applications.

- Backend: FastAPI services, market data access, and domain endpoints.
- Frontend: React + Vite decision workspace and visualization.
- Launcher: Python-based operational entrypoint for local startup.

## High-Level Components

1. Backend API layer
2. Domain services and engines
3. Frontend orchestration layer
4. UI components and layouts
5. Launcher and local developer tooling

## Design Principles

- Deterministic processing for analysis pipelines.
- Clear module boundaries between API, domain, and presentation.
- Single canonical output per analysis stage.
- Operational readiness checks before UI startup.

## Runtime Flow

1. Launcher starts backend.
2. Launcher waits for backend health readiness.
3. Launcher starts frontend.
4. Frontend consumes backend endpoints and renders decision views.

## Documentation Map

- Engine details: OSCAR_ENGINE.md
- Product scope: OSCAR_PRODUCT.md
- UI conventions: OSCAR_UI_GUIDE.md
- Decisions record: ADR/
