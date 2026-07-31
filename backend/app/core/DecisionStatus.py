from __future__ import annotations

from enum import Enum


class DecisionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WAIT = "WAIT"
    WARNING = "WARNING"
    READY = "READY"


_ALLOWED_TRANSITIONS: dict[DecisionStatus, set[DecisionStatus]] = {
    DecisionStatus.WAIT: {DecisionStatus.READY, DecisionStatus.PASS, DecisionStatus.FAIL, DecisionStatus.WARNING},
    DecisionStatus.READY: {DecisionStatus.PASS, DecisionStatus.FAIL, DecisionStatus.WARNING, DecisionStatus.WAIT},
    DecisionStatus.WARNING: {DecisionStatus.READY, DecisionStatus.PASS, DecisionStatus.FAIL, DecisionStatus.WAIT},
    DecisionStatus.FAIL: {DecisionStatus.WAIT, DecisionStatus.READY},
    DecisionStatus.PASS: {DecisionStatus.WAIT, DecisionStatus.READY},
}


def can_transition(current: DecisionStatus, target: DecisionStatus) -> bool:
    if current == target:
        return True

    return target in _ALLOWED_TRANSITIONS[current]
