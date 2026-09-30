from typing import List, Optional, Tuple
from app.rules.base import RuleResult
from app.engine.result import FraudDecision


class RiskScorer:
    """
    Calculates overall transaction risk score and binds final decisions based on rule outcomes.
    Enforces deterministic policy rules (R1-R10):
    - Critical fraud (Stolen card / high velocity spike) -> REJECT / CONFIRMED_FRAUD / DECLINED
    - R7 Pending Evidence Guard -> Forces REVIEW / VERIFICATION_PENDING / NEEDS_REVIEW
    - R8 Customer Confirmed Legitimacy -> Forces APPROVE / CLEARED / APPROVED (unless stolen card)
    - R10 Cumulative Thresholds: >= 75 REJECT, >= 40 REVIEW, < 40 APPROVE
    """

    def __init__(self, review_threshold: float = 40.0, reject_threshold: float = 75.0) -> None:
        self.review_threshold = review_threshold
        self.reject_threshold = reject_threshold

    def calculate_score(self, rule_results: List[RuleResult]) -> float:
        """
        Calculate total risk score (0-100) from rule results, aggregating positive and negative impacts.
        """
        total_score = sum(res.score_impact for res in rule_results if res.triggered)
        return min(100.0, max(0.0, total_score))

    def determine_decision(
        self,
        risk_score: float,
        rule_results: Optional[List[RuleResult]] = None,
    ) -> FraudDecision:
        """Map risk score and rule results to a FraudDecision enum."""
        decision, _, _ = self.determine_decision_and_state(risk_score, rule_results)
        return decision

    def determine_decision_and_state(
        self,
        risk_score: float,
        rule_results: Optional[List[RuleResult]] = None,
    ) -> Tuple[FraudDecision, str, str]:
        """
        Determine (FraudDecision, decision_state, verdict) enforcing policy guards.
        Returns:
            Tuple of (decision, decision_state, verdict)
            decision: APPROVE, REVIEW, REJECT
            decision_state: CONFIRMED_FRAUD, VERIFICATION_PENDING, UNDER_INVESTIGATION, CLEARED
            verdict: APPROVED, NEEDS_REVIEW, DECLINED
        """
        results = rule_results or []
        triggered_rules = {r.rule_id: r for r in results if r.triggered}

        # Check for critical hard fraud signals (e.g. stolen card or critical dispute or severe velocity)
        r6_result = triggered_rules.get("R6")
        stolen_card = bool(r6_result and r6_result.metadata.get("stolen_card"))
        critical_fraud = (
            stolen_card
            or risk_score >= self.reject_threshold
            or any(r.severity == "CRITICAL" for r in triggered_rules.values())
        )

        # 1. Critical fraud takes highest precedence
        if critical_fraud:
            return FraudDecision.REJECT, "CONFIRMED_FRAUD", "DECLINED"

        # 2. R7: Pending Evidence Verification Guard (forces REVIEW / VERIFICATION_PENDING / NEEDS_REVIEW)
        r7_result = triggered_rules.get("R7")
        if r7_result:
            return FraudDecision.REVIEW, "VERIFICATION_PENDING", "NEEDS_REVIEW"

        # 3. R8: Customer Confirmed Legitimacy (forces APPROVE / CLEARED / APPROVED)
        r8_result = triggered_rules.get("R8")
        if r8_result and not stolen_card:
            return FraudDecision.APPROVE, "CLEARED", "APPROVED"

        # 4. R10 / Cumulative Threshold Boundary Evaluation
        if risk_score >= self.reject_threshold:
            return FraudDecision.REJECT, "CONFIRMED_FRAUD", "DECLINED"
        elif risk_score >= self.review_threshold or len(triggered_rules) > 0:
            return FraudDecision.REVIEW, "UNDER_INVESTIGATION", "NEEDS_REVIEW"

        return FraudDecision.APPROVE, "CLEARED", "APPROVED"
