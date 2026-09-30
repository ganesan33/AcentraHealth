from typing import List
from app.rules.base import RuleResult
from app.engine.result import FraudDecision


class RiskScorer:
    """
    Calculates overall transaction risk score and decision based on rule evaluation results.
    Skeleton implementation for future scoring algorithms.
    """

    def __init__(self, review_threshold: float = 40.0, reject_threshold: float = 75.0) -> None:
        self.review_threshold = review_threshold
        self.reject_threshold = reject_threshold

    def calculate_score(self, rule_results: List[RuleResult]) -> float:
        """
        Calculate total risk score (0-100) from rule results.
        Placeholder logic to be expanded.
        """
        total_score = sum(res.score_impact for res in rule_results if res.triggered)
        return min(100.0, max(0.0, total_score))

    def determine_decision(self, risk_score: float) -> FraudDecision:
        """
        Map risk score to a final decision (APPROVE, REVIEW, REJECT).
        """
        if risk_score >= self.reject_threshold:
            return FraudDecision.REJECT
        elif risk_score >= self.review_threshold:
            return FraudDecision.REVIEW
        return FraudDecision.APPROVE
