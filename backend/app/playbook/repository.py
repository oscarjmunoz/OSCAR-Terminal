from __future__ import annotations

from app.playbook.models import PlaybookSetup


class PlaybookRepository:
    def add(self, setup: PlaybookSetup) -> PlaybookSetup:
        raise NotImplementedError

    def get(self, setup_id: str) -> PlaybookSetup | None:
        raise NotImplementedError

    def list(self) -> list[PlaybookSetup]:
        raise NotImplementedError

    def update(self, setup: PlaybookSetup) -> PlaybookSetup:
        raise NotImplementedError

    def delete(self, setup_id: str) -> PlaybookSetup | None:
        raise NotImplementedError


class InMemoryPlaybookRepository(PlaybookRepository):
    def __init__(self):
        self._setups: dict[str, PlaybookSetup] = {}

    def add(self, setup: PlaybookSetup) -> PlaybookSetup:
        self._setups[setup.id] = setup
        return setup

    def get(self, setup_id: str) -> PlaybookSetup | None:
        return self._setups.get(setup_id)

    def list(self) -> list[PlaybookSetup]:
        return sorted(self._setups.values(), key=lambda setup: (setup.createdAt, setup.name.lower(), setup.id))

    def update(self, setup: PlaybookSetup) -> PlaybookSetup:
        self._setups[setup.id] = setup
        return setup

    def delete(self, setup_id: str) -> PlaybookSetup | None:
        return self._setups.pop(setup_id, None)
