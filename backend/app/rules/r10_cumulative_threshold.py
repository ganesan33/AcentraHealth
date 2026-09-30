from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class CumulativeFraudScoreThresholdRule(BaseFraudRule):
    """
    R10: Cumulative Fraud Score Threshold Rule.
    Evaluates aggregate cumulative risk score against systemic policy boundaries:
    - Score >= 75.0: CONFIRMED_FRAUD / DECLINED
    - Score >= 40.0: UNDER_INVESTIGATION / NEEDS_REVIEW
    - Score < 40.0:  CLEARED / APPROVED
    """
    rule_id: str = "R10"
    rule_name: str = "Cumulative Fraud Score Threshold"
    description: str = "Evaluates composite risk score against systemic policy decision boundaries"
    weight: float = 0.0  # Acts as policy outcome evaluator
    enabled: bool = True

    def __init__(self, review_threshold: float = 40.0, reject_threshold: float = 75.0) -> None:
        self.review_threshold = review_threshold
        self.reject_threshold = reject_threshold

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        # Check if an explicit risk score was passed or pre-calculated
        risk_score = float(transaction_data.get("risk_score") or transaction_data.get("cumulative_score") or 0.0)

        triggered = risk_score >= self.review_threshold
        if risk_score >= self.reject_threshold:
            severity = "CRITICAL"
            policy_action = "REJECT / DECLINED"
            verdict = "DECLINED"
            state = "CONFIRMED_FRAUD"
        elif risk_score >= self.review_threshold:
            severity = "HIGH"
            policy_action = "REVIEW / NEEDS_REVIEW"
            verdict = "NEEDS_REVIEW"
            state = "UNDER_INVESTIGATION"
        else:
            severity = "INFO"
            policy_action = "APPROVE / CLEARED"
            verdict = "APPROVED"
            state = "CLEARED"

        reason = (
            f"Cumulative score policy evaluation: Risk score {risk_score:.1f}/100 "
            f"maps to {policy_action} (Review: {self.review_threshold:.1f}, Reject: {self.reject_threshold:.1f})"
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity=severity,
            score_impact=0.0,
            reason=reason,
            metadata={
                "risk_score": risk_score,
                "review_threshold": self.review_threshold,
                "reject_threshold": self.reject_threshold,
                "policy_action": policy_action,
                "policy_verdict": verdict,
                "policy_state": state,
            },
        )
