"""
Fraud Detection Rules Package.
Implements policy rules R1 through R10 for transaction risk evaluation.
"""

from app.rules.base import BaseFraudRule, RuleResult
from app.rules.registry import RuleRegistry, rule_registry
from app.rules.r1_velocity_spike import HighVelocitySpikeRule
from app.rules.r2_device_anomaly import DeviceFingerprintAnomalyRule
from app.rules.r3_billing_region import BillingRegionMismatchRule
from app.rules.r4_disposable_email import DisposableEmailDomainRule
from app.rules.r5_chargeback_link import PriorChargebackLinkRule
from app.rules.r6_customer_dispute import CustomerDisputeClaimRule
from app.rules.r7_pending_evidence import PendingEvidenceGuardRule
from app.rules.r8_customer_legitimacy import CustomerConfirmedLegitimacyRule
from app.rules.r9_high_exposure import HighTransactionExposureRule
from app.rules.r10_cumulative_threshold import CumulativeFraudScoreThresholdRule

# Backward-compatibility aliases
HighFrequencyTransactionRule = HighVelocitySpikeRule
UnusualAmountRule = HighTransactionExposureRule


def register_default_rules() -> None:
    """Register the canonical R1-R10 rules into the global rule registry."""
    canonical_rules = [
        HighVelocitySpikeRule(),
        DeviceFingerprintAnomalyRule(),
        BillingRegionMismatchRule(),
        DisposableEmailDomainRule(),
        PriorChargebackLinkRule(),
        CustomerDisputeClaimRule(),
        PendingEvidenceGuardRule(),
        CustomerConfirmedLegitimacyRule(),
        HighTransactionExposureRule(),
        CumulativeFraudScoreThresholdRule(),
    ]
    for r in canonical_rules:
        if not rule_registry.get_rule(r.rule_id):
            rule_registry.register(r)


# Initialize default rules
register_default_rules()

__all__ = [
    # Core interfaces
    "BaseFraudRule",
    "RuleResult",
    "RuleRegistry",
    "rule_registry",
    "register_default_rules",
    # Canonical R1 - R10 rules
    "HighVelocitySpikeRule",
    "DeviceFingerprintAnomalyRule",
    "BillingRegionMismatchRule",
    "DisposableEmailDomainRule",
    "PriorChargebackLinkRule",
    "CustomerDisputeClaimRule",
    "PendingEvidenceGuardRule",
    "CustomerConfirmedLegitimacyRule",
    "HighTransactionExposureRule",
    "CumulativeFraudScoreThresholdRule",
    # Compatibility aliases
    "HighFrequencyTransactionRule",
    "UnusualAmountRule",
]
