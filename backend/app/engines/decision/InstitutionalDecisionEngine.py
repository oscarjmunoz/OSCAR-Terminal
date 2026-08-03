from __future__ import annotations

import time
from typing import Literal
from typing import TypedDict

from app.core.DecisionNode import DecisionNode
from app.core.DecisionStatus import DecisionStatus
from app.core.DecisionTree import DecisionTree
from app.core.Rule import Rule
from app.core.RuleResult import RuleResult
from app.core.Score import Score
from app.engines.context.ContextResult import ContextResult
from app.engines.decision.InstitutionalDecisionResult import DecisionDirection
from app.engines.decision.InstitutionalDecisionResult import InstitutionalDecisionState
from app.engines.decision.InstitutionalDecisionResult import InstitutionalDecisionResult
from app.engines.liquidity.LiquidityMap import LiquidityMap
from app.engines.mss.MSSResult import MSSResult
from app.engines.premium_discount.PremiumDiscountResult import PremiumDiscountResult


class ConfluenceResult(TypedDict):
    valid: bool
    direction: Literal["BULLISH", "BEARISH", "NONE"]
    inInstitutionalZone: bool
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]


class ScoreResult(TypedDict):
    valid: bool
    institutionalScore: int
    confidence: int
    passedRules: list[str]
    failedRules: list[str]
    reasons: list[str]
    warnings: list[str]


class InstitutionalDecisionInput(TypedDict):
    context: ContextResult
    liquidity: LiquidityMap
    premiumDiscount: PremiumDiscountResult
    mss: MSSResult
    confluence: ConfluenceResult
    score: ScoreResult


RULES: list[Rule] = [
    Rule("IDE-001", "IDE-001", "Context Valid", "Context engine must be valid.", "DECISION", 15, True),
    Rule("IDE-002", "IDE-002", "Liquidity Available", "Liquidity map must be available.", "DECISION", 15, True),
    Rule("IDE-003", "IDE-003", "PD Valid", "Premium/Discount engine must be valid.", "DECISION", 12, True),
    Rule("IDE-004", "IDE-004", "MSS Valid", "MSS engine must be valid.", "DECISION", 12, True),
    Rule("IDE-005", "IDE-005", "Confluence Valid", "Confluence engine must be valid and in-zone.", "DECISION", 14, True),
    Rule("IDE-006", "IDE-006", "Directional Coherence", "MSS and Confluence directions must align.", "DECISION", 12, True),
    Rule("IDE-007", "IDE-007", "Location Coherence", "Direction must align with premium/discount zone.", "DECISION", 10, False),
    Rule("IDE-008", "IDE-008", "Score Valid", "Score engine output must be valid.", "DECISION", 10, False),
]

RULES_BY_ID: dict[str, Rule] = {rule.id: rule for rule in RULES}


class InstitutionalDecisionEngine:

    ENGINE_SEQUENCE: list[str] = [
        "Liquidity",
        "Context",
        "PremiumDiscount",
        "MSS",
        "Confluence",
        "Score",
        "Decision",
    ]

    @staticmethod
    def evaluate(data: InstitutionalDecisionInput) -> InstitutionalDecisionResult:
        start = time.perf_counter()

        confluence_direction = data["confluence"]["direction"]
        mss_direction = data["mss"]["direction"]
        direction = InstitutionalDecisionEngine._resolve_direction(
            confluence_direction=confluence_direction,
            mss_direction=mss_direction,
        )

        result = InstitutionalDecisionResult.bootstrap(direction=direction)
        result.engineSequence = [*InstitutionalDecisionEngine.ENGINE_SEQUENCE]

        failed_critical = False
        stop_processing = False

        if not stop_processing:
            ide_001 = data["context"]["valid"]
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-001",
                condition=ide_001,
                pass_message="Context validation is complete.",
                fail_message="Context validation failed.",
                failed_critical=failed_critical,
                engine_name="Context",
                critical_failure="CONTEXT_NOT_VALID",
            )

        if not stop_processing:
            ide_002 = InstitutionalDecisionEngine._is_liquidity_map_available(data["liquidity"])
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-002",
                condition=ide_002,
                pass_message="Liquidity map availability is confirmed.",
                fail_message="Liquidity map is missing required levels.",
                failed_critical=failed_critical,
                engine_name="Liquidity",
                critical_failure="NO_LIQUIDITY_MAP",
            )

        if not stop_processing:
            ide_003 = data["premiumDiscount"]["valid"]
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-003",
                condition=ide_003,
                pass_message="Premium/Discount validation is complete.",
                fail_message="Premium/Discount validation failed.",
                failed_critical=failed_critical,
                engine_name="PremiumDiscount",
                critical_failure="PREMIUM_NOT_VALID",
            )

        if not stop_processing:
            ide_004 = data["mss"]["valid"]
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-004",
                condition=ide_004,
                pass_message="MSS validation is complete.",
                fail_message="MSS validation failed.",
                failed_critical=failed_critical,
                engine_name="MSS",
                critical_failure="MSS_NOT_CONFIRMED",
            )

        if not stop_processing:
            ide_005 = data["confluence"]["valid"] and data["confluence"]["inInstitutionalZone"]
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-005",
                condition=ide_005,
                pass_message="Confluence validation is complete and in-zone.",
                fail_message="Confluence is invalid or outside institutional zone.",
                failed_critical=failed_critical,
                engine_name="Confluence",
                critical_failure="CONFLUENCE_NOT_VALID",
            )

        if not stop_processing:
            ide_006 = InstitutionalDecisionEngine._is_directionally_coherent(
                confluence_direction=confluence_direction,
                mss_direction=mss_direction,
            )
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-006",
                condition=ide_006,
                pass_message="Directional coherence is confirmed across MSS and Confluence.",
                fail_message="Directional coherence failed across MSS and Confluence.",
                failed_critical=failed_critical,
                engine_name="Decision",
                critical_failure="DIRECTION_MISMATCH",
            )

        if not stop_processing:
            ide_007 = InstitutionalDecisionEngine._is_location_coherent(
                direction=direction,
                zone=data["premiumDiscount"]["zone"],
            )
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-007",
                condition=ide_007,
                pass_message="Directional location is coherent with premium/discount zone.",
                fail_message="Directional location is not coherent with premium/discount zone.",
                failed_critical=failed_critical,
                engine_name="PremiumDiscount",
                critical_failure="LOCATION_NOT_COHERENT",
            )

        if not stop_processing:
            ide_008 = data["score"]["valid"]
            failed_critical, stop_processing = InstitutionalDecisionEngine._register_rule(
                result=result,
                rule_id="IDE-008",
                condition=ide_008,
                pass_message="Score engine validation is complete.",
                fail_message="Score engine validation failed.",
                failed_critical=failed_critical,
                engine_name="Score",
                critical_failure="SCORE_NOT_VALID",
            )

        confidence = InstitutionalDecisionEngine._resolve_confidence(score_result=data["score"])
        is_valid = len(result.failedRules) == 0
        decision_state = InstitutionalDecisionEngine._resolve_decision_state(valid=is_valid, direction=direction)

        result.valid = is_valid
        result.decisionState = decision_state
        result.direction = direction
        result.institutionalScore = data["score"]["institutionalScore"]
        result.confidence = confidence
        result.blockedBy = [rule_result.rule.id for rule_result in result.failedRules]
        result.failedAt = result.failedAt if result.failedAt != "NONE" else ("Decision" if is_valid else "NONE")
        result.summary = InstitutionalDecisionEngine._build_summary(result=result)
        result.score = Score(result.institutionalScore)
        result.status = InstitutionalDecisionEngine._resolve_status(is_valid=is_valid, failed_critical=failed_critical)
        result.executionTime = round((time.perf_counter() - start) * 1000, 4)

        return result

    @staticmethod
    def run(data: InstitutionalDecisionInput, tree: DecisionTree | None = None) -> DecisionNode:
        result = InstitutionalDecisionEngine.evaluate(data)
        node = DecisionNode.from_engine_result(result)

        if tree is not None:
            tree.add_node(node)
            tree.set_next_step("ExecutionEngine" if result.valid else "WAIT")

        return node

    @staticmethod
    def _register_rule(
        result: InstitutionalDecisionResult,
        rule_id: str,
        condition: bool,
        pass_message: str,
        fail_message: str,
        failed_critical: bool,
        engine_name: Literal["Context", "Liquidity", "PremiumDiscount", "MSS", "Confluence", "Score", "Decision"],
        critical_failure: str,
    ) -> tuple[bool, bool]:
        rule = RULES_BY_ID[rule_id]

        if condition:
            result.add_rule_result(
                RuleResult(
                    rule=rule,
                    status=DecisionStatus.PASS,
                    score=rule.weight,
                    reason=f"{rule_id}: {pass_message}",
                )
            )
            return failed_critical, False

        result.add_rule_result(
            RuleResult(
                rule=rule,
                status=DecisionStatus.FAIL if rule.critical else DecisionStatus.WARNING,
                score=0,
                warning=f"{rule_id}: {fail_message}",
            )
        )
        if rule.critical:
            result.failedAt = engine_name
            result.criticalFailure = critical_failure
            return True, True

        return failed_critical, False

    @staticmethod
    def _resolve_direction(
        confluence_direction: Literal["BULLISH", "BEARISH", "NONE"],
        mss_direction: Literal["BULLISH", "BEARISH", "NONE"],
    ) -> DecisionDirection:
        for direction in (confluence_direction, mss_direction):
            if direction in {"BULLISH", "BEARISH"}:
                return direction

        return "NONE"

    @staticmethod
    def _is_directionally_coherent(
        confluence_direction: Literal["BULLISH", "BEARISH", "NONE"],
        mss_direction: Literal["BULLISH", "BEARISH", "NONE"],
    ) -> bool:
        directions = [direction for direction in (confluence_direction, mss_direction) if direction != "NONE"]

        if len(directions) != 2:
            return False

        return len(set(directions)) == 1

    @staticmethod
    def _is_liquidity_map_available(liquidity: LiquidityMap) -> bool:
        required_keys = {
            "pdh",
            "pdl",
            "pwh",
            "pwl",
            "h4SwingHigh",
            "h4SwingLow",
            "nearestBuySideLiquidity",
            "nearestSellSideLiquidity",
        }
        return required_keys.issubset(set(liquidity.keys()))

    @staticmethod
    def _is_location_coherent(
        direction: DecisionDirection,
        zone: Literal["PREMIUM", "DISCOUNT", "EQUILIBRIUM", "UNKNOWN"],
    ) -> bool:
        if direction == "BULLISH":
            return zone in {"DISCOUNT", "EQUILIBRIUM"}

        if direction == "BEARISH":
            return zone in {"PREMIUM", "EQUILIBRIUM"}

        return False

    @staticmethod
    def _resolve_confidence(score_result: ScoreResult) -> int:
        return score_result["confidence"]

    @staticmethod
    def _resolve_decision_state(valid: bool, direction: DecisionDirection) -> InstitutionalDecisionState:
        if not valid:
            return "INVALID"

        if direction == "BULLISH":
            return "VALID_LONG"

        if direction == "BEARISH":
            return "VALID_SHORT"

        return "INVALID"

    @staticmethod
    def _resolve_status(is_valid: bool, failed_critical: bool) -> DecisionStatus:
        if is_valid:
            return DecisionStatus.PASS

        if failed_critical:
            return DecisionStatus.FAIL

        return DecisionStatus.WARNING

    @staticmethod
    def _build_summary(result: InstitutionalDecisionResult) -> str:
        if result.valid:
            return (
                f"Institutional setup validated with state {result.decisionState}, "
                f"score {result.institutionalScore}, confidence {result.confidence}."
            )

        blocked = ", ".join(result.blockedBy or [])
        if result.criticalFailure:
            return (
                f"Institutional setup blocked at {result.failedAt} "
                f"by {result.criticalFailure}. Failed rules: {blocked}."
            )

        return f"Institutional setup invalid with non-critical warnings. Failed rules: {blocked}."
