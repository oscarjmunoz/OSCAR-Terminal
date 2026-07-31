"""Configuration for the OSCAR Python launcher.

The values here are intentionally simple and can be overridden by
environment variables when needed.
"""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class LauncherConfig:
    """Launcher runtime configuration."""

    host: str = os.getenv("OSCAR_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("OSCAR_BACKEND_PORT", "8000"))
    frontend_port: int = int(os.getenv("OSCAR_FRONTEND_PORT", "5173"))
    browser: str | None = os.getenv("OSCAR_BROWSER")
    backend_timeout_sec: int = int(os.getenv("OSCAR_BACKEND_TIMEOUT", "120"))
    frontend_timeout_sec: int = int(os.getenv("OSCAR_FRONTEND_TIMEOUT", "120"))
    poll_interval_sec: float = float(os.getenv("OSCAR_POLL_INTERVAL", "1.0"))

    @property
    def backend_health_url(self) -> str:
        """Backend health URL used for readiness checks."""
        return f"http://{self.host}:{self.backend_port}/health"

    @property
    def frontend_url(self) -> str:
        """Frontend URL opened in browser and used for readiness checks."""
        return f"http://localhost:{self.frontend_port}"


CONFIG = LauncherConfig()
