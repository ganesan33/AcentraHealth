from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class PriorChargebackLinkRule(BaseFraudRule):
    """
    R5: Prior Chargeback / Closed Case Link Rule.
    Identifies entities associated with prior confirmed fraud cases, previous chargeback losses,
    or closed investigations resulting in adverse findings.
    """
    rule_id: str = "R5"
    rule_name: str = "Prior Chargeback / Closed Case Link"
    description: str = "Flags entities linked to historical chargebacks or past confirmed fraud investigations"
    weight: float = 40.0
    enabled: bool = True

    def __init__(self, weight: float = 40.0) -> None:
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        prior_chargebacks = (
            transaction_data.get("prior_chargeback") is True
            or transaction_data.get("prior_chargeback_count", 0) > 0
            or transaction_data.get("chargeback_history") is True
        )
        historical_fraud = (
            transaction_data.get("has_historical_fraud") is True
            or transaction_data.get("historical_fraud_cases_count", 0) > 0
        )
        closed_case_link = (
            transaction_data.get("connected_closed_cases_count", 0) > 0
            and transaction_data.get("closed_case_outcome") in ["FRAUD_CONFIRMED", "CHARGEBACK_LOST", "CONFIRMED_FRAUD"]
        )

        triggered = prior_chargebacks or historical_fraud or closed_case_link
        reasons = []
        if prior_chargebacks:
            reasons.append("Prior chargeback history detected on account")
        if historical_fraud:
            reasons.append("Linked to past confirmed fraud case")
        if closed_case_link:
            reasons.append("Connected closed case marked with confirmed fraud outcome")

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity="HIGH" if triggered else "INFO",
            score_impact=self.weight if triggered else 0.0,
            reason="; ".join(reasons) if triggered else "No adverse chargeback or historical fraud associations found",
            metadata={
                "prior_chargebacks": prior_chargebacks,
                "historical_fraud": historical_fraud,
                "closed_case_link": closed_case_link,
            },
        )


__all__ = ["PriorChargebackLinkRule"]
