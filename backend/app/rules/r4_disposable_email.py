from typing import Any, Dict, Set, Optional
from app.rules.base import BaseFraudRule, RuleResult

# Comprehensive catalog of popular disposable, burner, and throwaway email domains
DEFAULT_DISPOSABLE_DOMAINS: Set[str] = {
    "mailinator.com",
    "guerrillamail.com",
    "tempmail.com",
    "throwawaymail.com",
    "10minutemail.com",
    "yopmail.com",
    "sharklasers.com",
    "trashmail.com",
    "dispostable.com",
    "getairmail.com",
    "fakeinbox.com",
    "maildrop.cc",
    "inboxkitten.com",
    "mohmal.com",
    "temp-mail.org",
    "crazymailing.com",
    "burnermail.io",
}


class DisposableEmailDomainRule(BaseFraudRule):
    """
    R4: Disposable / High-Risk Email Domain Rule.
    Flags transactions where the customer email address belongs to a known
    burner or temporary inbox service.
    """
    rule_id: str = "R4"
    rule_name: str = "Disposable / High-Risk Email Domain"
    description: str = "Flags disposable, burner, or temporary inboxes used to conceal user identity"
    weight: float = 25.0
    enabled: bool = True

    def __init__(self, custom_domains: Optional[Set[str]] = None, weight: float = 25.0) -> None:
        self.disposable_domains = custom_domains or DEFAULT_DISPOSABLE_DOMAINS
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        explicit_disposable = (
            transaction_data.get("is_disposable_email") is True
            or transaction_data.get("disposable_email_domains_count", 0) > 0
        )

        email = str(
            transaction_data.get("email")
            or transaction_data.get("customer_email")
            or transaction_data.get("user_email")
            or ""
        ).strip().lower()

        domain = email.split("@")[-1] if "@" in email else ""
        is_known_disposable = domain in self.disposable_domains

        triggered = explicit_disposable or is_known_disposable
        reason = (
            f"Disposable / high-risk email domain detected: '{domain or email}'"
            if triggered
            else (f"Email domain '{domain}' verified as standard" if domain else "No email provided")
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity="MEDIUM" if triggered else "INFO",
            score_impact=self.weight if triggered else 0.0,
            reason=reason,
            metadata={"email": email, "domain": domain, "disposable": triggered},
        )
