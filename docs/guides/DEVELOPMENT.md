# Development Guide

## Workflow

1. Create a feature branch from the integration branch.
2. Keep commits small and purpose-specific.
3. Validate local behavior before push.

## Local Operations

- Start stack: python launcher.py start
- Stop stack: python launcher.py stop
- Restart stack: python launcher.py restart
- Environment check: python launcher.py check

## Standards

- Preserve deterministic behavior in core analysis paths.
- Avoid duplicated logic across layers.
- Keep documentation updated with feature evolution.
