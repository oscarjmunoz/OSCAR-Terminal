from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rule:
    id: str
    code: str
    title: str
    description: str
    category: str
    weight: int
    critical: bool

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError("Rule weight must be >= 0")
