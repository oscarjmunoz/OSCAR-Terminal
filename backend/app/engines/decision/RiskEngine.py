from __future__ import annotations

from app.config.settings import settings
from app.engines.decision.PipelineModels import RiskInput
from app.engines.decision.PipelineModels import RiskResult


class RiskEngine:
    """Deterministic institutional risk validator for pipeline orchestration."""

    @staticmethod
    def evaluate(data: RiskInput) -> RiskResult:
        passed_rules: list[str] = []
        failed_rules: list[str] = []
        reasons: list[str] = []
        warnings: list[str] = []

        risk_cap_ok = data["riskPercent"] <= settings.RISK_MAX_PERCENT
        RiskEngine._register_rule(
            rule_id="RISK-001",
            condition=risk_cap_ok,
            pass_message="Per-trade risk is within configured cap.",
            fail_message="Per-trade risk exceeds configured cap.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        rr_ok = data["rr"] >= settings.RISK_MIN_RR
        RiskEngine._register_rule(
            rule_id="RISK-002",
            condition=rr_ok,
            pass_message="Risk-reward ratio is acceptable.",
            fail_message="Risk-reward ratio is below configured minimum.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        exposure_ok = data["exposurePercent"] <= settings.RISK_MAX_EXPOSURE_PERCENT
        RiskEngine._register_rule(
            rule_id="RISK-003",
            condition=exposure_ok,
            pass_message="Exposure is within configured limits.",
            fail_message="Exposure exceeds configured limits.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        stop_ok = data["stopAligned"]
        RiskEngine._register_rule(
            rule_id="RISK-004",
            condition=stop_ok,
            pass_message="Stop placement is structurally coherent.",
            fail_message="Stop placement is not structurally coherent.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        allowed_sessions = {segment.strip() for segment in settings.INSTITUTIONAL_ALLOWED_SESSIONS.split(",") if segment.strip()}
        session_ok = data["session"] in allowed_sessions
        RiskEngine._register_rule(
            rule_id="RISK-005",
            condition=session_ok,
            pass_message="Trading session is allowed by policy.",
            fail_message="Trading session is not allowed by policy.",
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            reasons=reasons,
            warnings=warnings,
        )

        passed_ratio = len(passed_rules) / max(1, len(passed_rules) + len(failed_rules))
        risk_score = int(round(100 * passed_ratio))

        return RiskResult(
            valid=len(failed_rules) == 0,
            riskScore=risk_score,
            riskPercent=data["riskPercent"],
            rr=data["rr"],
            exposurePercent=data["exposurePercent"],
            sessionAllowed=session_ok,
            passedRules=tuple(passed_rules),
            failedRules=tuple(failed_rules),
            reasons=tuple(reasons),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _register_rule(
        rule_id: str,
        condition: bool,
        pass_message: str,
        fail_message: str,
        passed_rules: list[str],
        failed_rules: list[str],
        reasons: list[str],
        warnings: list[str],
    ) -> None:
        if condition:
            passed_rules.append(rule_id)
            reasons.append(f"{rule_id}: {pass_message}")
            return

        failed_rules.append(rule_id)
        warnings.append(f"{rule_id}: {fail_message}")
