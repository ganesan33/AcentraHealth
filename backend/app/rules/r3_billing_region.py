from typing import Any, Dict, Optional
from app.rules.base import BaseFraudRule, RuleResult


class BillingRegionMismatchRule(BaseFraudRule):
    """
    R3: Billing Region Mismatch Rule.
    Flags cross-border discrepancies between card billing country, IP geolocation,
    and merchant/shipping location.
    """
    rule_id: str = "R3"
    rule_name: str = "Billing Region Mismatch"
    description: str = "Detects geographical conflict between billing address, issuing country, and transaction IP origin"
    weight: float = 25.0
    enabled: bool = True

    def __init__(self, weight: float = 25.0) -> None:
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        # Explicit indicator
        explicit_mismatch = (
            transaction_data.get("regional_mismatch") is True
            or transaction_data.get("billing_region_mismatch") is True
            or transaction_data.get("regional_mismatches_count", 0) > 0
        )

        billing_country = (
            transaction_data.get("billing_country")
            or transaction_data.get("card_country")
            or transaction_data.get("billing_region")
        )
        location_country = (
            transaction_data.get("location_country")
            or transaction_data.get("ip_country")
            or transaction_data.get("country")
        )

        mismatched = False
        details = ""

        if explicit_mismatch:
            mismatched = True
            details = "Explicit billing/regional mismatch signal present in telemetry"
        elif (
            billing_country
            and location_country
            and str(billing_country).strip().upper() != str(location_country).strip().upper()
        ):
            mismatched = True
            details = f"Billing country '{billing_country.upper()}' does not match transaction origin country '{location_country.upper()}'"

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=mismatched,
            status="TRIGGERED" if mismatched else "NOT_TRIGGERED",
            severity="MEDIUM",
            score_impact=self.weight if mismatched else 0.0,
            reason=details if mismatched else "Billing and transaction origin geographic regions match",
            metadata={
                "billing_country": billing_country,
                "location_country": location_country,
            },
        )
