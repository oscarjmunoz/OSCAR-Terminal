from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from app.core.DecisionNode import DecisionNode
from app.core.DecisionStatus import DecisionStatus
from app.core.Score import Score


@dataclass(slots=True)
class DecisionTree:
    nodes: list[DecisionNode] = field(default_factory=list)
    overallScore: Score = field(default_factory=lambda: Score(0))
    currentStep: str = ""
    nextStep: str = ""
    blockedBy: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)

    def add_node(self, node: DecisionNode) -> None:
        self.nodes.append(node)
        self.currentStep = node.engine
        self.timeline.append(f"{node.timestamp} | {node.engine} | {node.status.value}")

        if node.status in {DecisionStatus.FAIL, DecisionStatus.WARNING} and node.engine not in self.blockedBy:
            self.blockedBy.append(node.engine)

        self._recalculate_score()

    def set_next_step(self, next_step: str) -> None:
        self.nextStep = next_step

    def _recalculate_score(self) -> None:
        if not self.nodes:
            self.overallScore = Score(0)
            return

        average = sum(node.score.value for node in self.nodes) / len(self.nodes)
        self.overallScore = Score(average)
