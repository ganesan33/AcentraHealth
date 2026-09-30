from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class CustomerConfirmedLegitimacyRule(BaseFraudRule):
    """
    R8: Customer Confirmed Legitimacy Rule.
    Recognizes formal customer authorization responses. Overrides standard anomaly flags,
    credits risk score, and enables clearing to APPROVED / CLEARED (unless confirmed stolen card).
    """
    rule_id: str = "R8"
    rule_name: str = "Customer Confirmed Legitimacy"
    description: str = "Cardholder verified transaction as legitimate; overrides suspicion and clears case"
    weight: float = -50.0  # Risk score reduction / mitigation
    enabled: bool = True

    def __init__(self, credit_weight: float = -50.0) -> None:
        self.weight = credit_weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        customer_confirmed = (
            transaction_data.get("customer_confirmed_legitimacy") is True
            or transaction_data.get("customer_confirmed") is True
            or str(transaction_data.get("customer_response", "")).upper() in ["CONFIRMED_LEGITIMATE", "LEGITIMATE", "AUTHORIZED"]
            or str(transaction_data.get("evidence_status", "")).upper() in ["RESOLVED_LEGITIMATE", "CONFIRMED_BY_CUSTOMER"]
        )

        stolen_card = (
            transaction_data.get("stolen_card") is True
            or transaction_data.get("stolen_flag") is True
        )

        # Stolen card takes precedence over any confirmation
        effective_trigger = customer_confirmed and not stolen_card

        reason = (
            "Customer confirmed legitimacy: Cardholder validated authorized activity. Case cleared."
            if effective_trigger
            else (
                "Customer confirmation overridden by confirmed stolen card report"
                if customer_confirmed and stolen_card
                else "No customer confirmation of legitimacy received"
            )
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=effective_trigger,
            status="TRIGGERED" if effective_trigger else "NOT_TRIGGERED",
            severity="INFO",
            score_impact=self.weight if effective_trigger else 0.0,
            reason=reason,
            metadata={
                "forces_cleared": effective_trigger,
                "forced_decision_state": "CLEARED" if effective_trigger else None,
                "forced_verdict": "APPROVED" if effective_trigger else None,
                "customer_confirmed": customer_confirmed,
                "stolen_card_override": stolen_card,
            },
        )
