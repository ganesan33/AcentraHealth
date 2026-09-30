from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class UnusualAmountRule(BaseFraudRule):
    """
    Amount Anomaly Fraud Rule: Flags transactions with unusually high monetary amounts.
    Configurable absolute threshold and multiplier triggers.
    """
    rule_id: str = "AMOUNT_SPIKE_HIGH"
    rule_name: str = "Unusual Amount Anomaly Rule"
    description: str = "Flags transactions exceeding standard authorization limits or high-value thresholds"
    weight: float = 40.0
    enabled: bool = True

    def __init__(
        self,
        threshold_amount: float = 5000.0,
        critical_threshold: float = 15000.0,
        weight: float = 40.0,
    ) -> None:
        self.threshold_amount = threshold_amount
        self.critical_threshold = critical_threshold
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        try:
            amount = float(transaction_data.get("amount", 0.0))
        except (ValueError, TypeError):
            amount = 0.0

        currency = transaction_data.get("currency", "USD")

        if amount >= self.critical_threshold:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=True,
                score_impact=min(100.0, self.weight * 1.5),
                reason=f"Critical high-risk amount: {amount:.2f} {currency} exceeds critical ceiling {self.critical_threshold:.2f}",
                metadata={"amount": amount, "threshold": self.critical_threshold, "severity": "CRITICAL"},
            )

        if amount >= self.threshold_amount:
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=True,
                score_impact=self.weight,
                reason=f"High transaction amount: {amount:.2f} {currency} exceeds threshold {self.threshold_amount:.2f}",
                metadata={"amount": amount, "threshold": self.threshold_amount, "severity": "HIGH"},
            )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=False,
            score_impact=0.0,
            reason=f"Amount {amount:.2f} {currency} is within nominal parameters (< {self.threshold_amount:.2f})",
            metadata={"amount": amount, "threshold": self.threshold_amount},
        )
