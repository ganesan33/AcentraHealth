from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class HighTransactionExposureRule(BaseFraudRule):
    """
    R9: High Transaction Exposure (> $2,500) Rule.
    Flags transactions where the individual amount or cumulative exposure exceeds
    the $2,500 USD boundary, triggering elevated risk scrutiny.
    """
    rule_id: str = "R9"
    rule_name: str = "High Transaction Exposure (> $2,500)"
    description: str = "Flags high monetary exposure exceeding $2,500 threshold requiring enhanced review"
    weight: float = 30.0
    enabled: bool = True

    def __init__(self, exposure_threshold: float = 2500.0, weight: float = 30.0) -> None:
        self.exposure_threshold = exposure_threshold
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        try:
            amount = float(transaction_data.get("amount", 0.0))
        except (ValueError, TypeError):
            amount = 0.0

        try:
            total_exposure = float(transaction_data.get("total_exposure_amount", amount))
        except (ValueError, TypeError):
            total_exposure = amount

        max_exposure = max(amount, total_exposure)
        currency = transaction_data.get("currency", "USD")

        triggered = max_exposure > self.exposure_threshold
        severity = "CRITICAL" if max_exposure >= 10000.0 else ("HIGH" if triggered else "INFO")

        reason = (
            f"High transaction exposure: {max_exposure:.2f} {currency} exceeds high exposure limit of {self.exposure_threshold:.2f} {currency}"
            if triggered
            else f"Transaction exposure {max_exposure:.2f} {currency} is within nominal limit (<= {self.exposure_threshold:.2f} {currency})"
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity=severity,
            score_impact=self.weight if triggered else 0.0,
            reason=reason,
            metadata={
                "amount": amount,
                "total_exposure": max_exposure,
                "threshold": self.exposure_threshold,
                "currency": currency,
            },
        )
