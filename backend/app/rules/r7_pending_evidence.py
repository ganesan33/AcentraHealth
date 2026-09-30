from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class PendingEvidenceGuardRule(BaseFraudRule):
    """
    R7: Pending Evidence Verification Guard Rule.
    Enforces the policy that transactions or cases with open, unresolved evidence requests
    are strictly prohibited from being auto-cleared or approved.
    Forces decision state to VERIFICATION_PENDING / NEEDS_REVIEW.
    """
    rule_id: str = "R7"
    rule_name: str = "Pending Evidence Verification Guard"
    description: str = "Enforces that unresolved evidence requests block auto-clearing and mandate manual review"
    weight: float = 20.0
    enabled: bool = True

    def __init__(self, weight: float = 20.0) -> None:
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        evidence_status = str(transaction_data.get("evidence_status", "")).upper()
        has_pending_flag = transaction_data.get("has_pending_evidence") is True
        
        pending_requests = transaction_data.get("pending_evidence_requests")
        has_pending_list = bool(pending_requests and len(pending_requests) > 0)

        triggered = (
            has_pending_flag
            or has_pending_list
            or evidence_status in ["PENDING", "SUBMITTED", "AWAITING_RESPONSE"]
        )

        pending_id = transaction_data.get("evidence_request_id") or "EV-PENDING"

        reason = (
            f"Pending evidence verification guard triggered: EvidenceRequest {pending_id} is pending customer response. "
            "Auto-clearing prohibited; holding state at VERIFICATION_PENDING / NEEDS_REVIEW."
            if triggered
            else "No pending evidence requests outstanding"
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity="HIGH" if triggered else "INFO",
            score_impact=self.weight if triggered else 0.0,
            reason=reason,
            metadata={
                "forces_review": triggered,
                "forced_decision_state": "VERIFICATION_PENDING",
                "forced_verdict": "NEEDS_REVIEW",
                "evidence_status": evidence_status or "NONE",
            },
        )


__all__ = ["PendingEvidenceGuardRule"]
