from app.rules.base import BaseFraudRule, RuleResult
from app.rules.registry import rule_registry, RuleRegistry
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

# Legacy / additional rules
from app.rules.velocity import HighFrequencyTransactionRule
from app.rules.unusual_amount import UnusualAmountRule
from app.rules.impossible_location import ImpossibleLocationRule

# Auto-register R1 through R10 in the default registry
def register_default_rules() -> None:
    rules_to_register = [
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
        ImpossibleLocationRule(),
    ]
    for r in rules_to_register:
        if not rule_registry.get_rule(r.rule_id):
            rule_registry.register(r)

register_default_rules()

__all__ = [
    "BaseFraudRule",
    "RuleResult",
    "rule_registry",
    "RuleRegistry",
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
    "HighFrequencyTransactionRule",
    "UnusualAmountRule",
    "ImpossibleLocationRule",
]
