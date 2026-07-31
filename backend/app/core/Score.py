from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Score:
    value: float
    max_value: float = 100.0

    def __post_init__(self) -> None:
        self.value = max(0.0, min(self.value, self.max_value))

    @property
    def percentage(self) -> float:
        if self.max_value <= 0:
            return 0.0

        return (self.value / self.max_value) * 100
