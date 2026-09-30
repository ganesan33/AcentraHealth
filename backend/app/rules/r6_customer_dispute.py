from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class CustomerDisputeClaimRule(BaseFraudRule):
    """
    R6: Customer Dispute / Unauthorized Claim Rule.
    Flags transactions actively contested by the cardholder via dispute claims,
    unauthorized charge reports, or stolen card notifications.
    """
    rule_id: str = "R6"
    rule_name: str = "Customer Dispute / Unauthorized Claim"
    description: str = "Identifies active customer dispute filings, stolen card reports, or unauthorized claims"
    weight: float = 45.0
    enabled: bool = True

    def __init__(self, weight: float = 45.0) -> None:
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        stolen_card = (
            transaction_data.get("stolen_card") is True
            or transaction_data.get("stolen_flag") is True
            or transaction_data.get("stolen_cards_count", 0) > 0
        )
        customer_dispute = (
            transaction_data.get("customer_dispute") is True
            or transaction_data.get("disputed") is True
            or transaction_data.get("unauthorized_claim") is True
            or str(transaction_data.get("trigger_type", "")).lower() == "customer_report"
        )

        triggered = stolen_card or customer_dispute
        reasons = []
        if stolen_card:
            reasons.append("Card associated with transaction is flagged as STOLEN")
        if customer_dispute:
            reasons.append("Cardholder filed formal unauthorized dispute / claim")

        severity = "CRITICAL" if stolen_card else ("HIGH" if customer_dispute else "INFO")

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity=severity,
            score_impact=self.weight if triggered else 0.0,
            reason="; ".join(reasons) if triggered else "No active customer dispute or stolen card flags present",
            metadata={
                "stolen_card": stolen_card,
                "customer_dispute": customer_dispute,
            },
        )
