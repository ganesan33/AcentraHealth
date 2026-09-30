import pytest
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
from app.rules import (
    rule_registry,
    HighFrequencyTransactionRule,
    UnusualAmountRule,
)
from app.engine.fraud_engine import FraudEngine
from app.engine.result import FraudDecision


@pytest.mark.asyncio
async def test_r1_velocity_spike() -> None:
    """R1: Test velocity spike triggers on threshold >= 5."""
    rule = HighVelocitySpikeRule(max_allowed=5)
    
    # Below threshold
    res_normal = await rule.evaluate({"velocity_count": 3})
    assert res_normal.triggered is False

    # At or above threshold
    res_spike = await rule.evaluate({"velocity_count": 6})
    assert res_spike.triggered is True
    assert res_spike.score_impact == 35.0
    assert res_spike.severity in ["HIGH", "CRITICAL"]


@pytest.mark.asyncio
async def test_r2_device_anomaly() -> None:
    """R2: Test device fingerprint anomaly triggers on VPN, proxy, TOR."""
    rule = DeviceFingerprintAnomalyRule()

    # Normal device
    res_clean = await rule.evaluate({"vpn_detected": False, "proxy_detected": False})
    assert res_clean.triggered is False

    # VPN detected
    res_vpn = await rule.evaluate({"vpn_detected": True})
    assert res_vpn.triggered is True
    assert res_vpn.score_impact == 30.0

    # TOR node detected
    res_tor = await rule.evaluate({"tor_detected": True})
    assert res_tor.triggered is True
    assert res_tor.severity == "CRITICAL"


@pytest.mark.asyncio
async def test_r3_billing_region_mismatch() -> None:
    """R3: Test billing region mismatch between billing country and location country."""
    rule = BillingRegionMismatchRule()

    # Matching countries
    res_match = await rule.evaluate({"billing_country": "US", "location_country": "US"})
    assert res_match.triggered is False

    # Mismatched countries
    res_mismatch = await rule.evaluate({"billing_country": "US", "location_country": "NG"})
    assert res_mismatch.triggered is True
    assert res_mismatch.score_impact == 25.0


@pytest.mark.asyncio
async def test_r4_disposable_email() -> None:
    """R4: Test disposable / temporary email domain detection."""
    rule = DisposableEmailDomainRule()

    # Corporate email
    res_corp = await rule.evaluate({"email": "john.doe@company.com"})
    assert res_corp.triggered is False

    # Burner email
    res_burner = await rule.evaluate({"email": "scammer99@mailinator.com"})
    assert res_burner.triggered is True
    assert res_burner.score_impact == 25.0


@pytest.mark.asyncio
async def test_r5_prior_chargeback_link() -> None:
    """R5: Test prior chargeback or historical fraud case link."""
    rule = PriorChargebackLinkRule()

    # Clean history
    res_clean = await rule.evaluate({"prior_chargeback": False, "has_historical_fraud": False})
    assert res_clean.triggered is False

    # Prior chargeback record
    res_cb = await rule.evaluate({"prior_chargeback": True})
    assert res_cb.triggered is True
    assert res_cb.score_impact == 40.0


@pytest.mark.asyncio
async def test_r6_customer_dispute() -> None:
    """R6: Test customer dispute and stolen card claims."""
    rule = CustomerDisputeClaimRule()

    # Normal transaction
    res_clean = await rule.evaluate({"customer_dispute": False, "stolen_card": False})
    assert res_clean.triggered is False

    # Dispute filed
    res_disp = await rule.evaluate({"customer_dispute": True})
    assert res_disp.triggered is True
    assert res_disp.score_impact == 45.0

    # Stolen card
    res_stolen = await rule.evaluate({"stolen_card": True})
    assert res_stolen.triggered is True
    assert res_stolen.severity == "CRITICAL"


@pytest.mark.asyncio
async def test_r7_pending_evidence_guard() -> None:
    """R7: Test pending evidence request forces review status."""
    rule = PendingEvidenceGuardRule()

    # No pending evidence
    res_none = await rule.evaluate({"evidence_status": "NONE"})
    assert res_none.triggered is False

    # Pending evidence request open
    res_pending = await rule.evaluate({"evidence_status": "PENDING", "evidence_request_id": "ER-1001"})
    assert res_pending.triggered is True
    assert res_pending.metadata["forced_decision_state"] == "VERIFICATION_PENDING"
    assert res_pending.metadata["forced_verdict"] == "NEEDS_REVIEW"


@pytest.mark.asyncio
async def test_r8_customer_confirmed_legitimacy() -> None:
    """R8: Test customer confirmation clears case with score credit."""
    rule = CustomerConfirmedLegitimacyRule()

    # Customer confirmed
    res_legit = await rule.evaluate({"customer_confirmed_legitimacy": True})
    assert res_legit.triggered is True
    assert res_legit.score_impact == -50.0
    assert res_legit.metadata["forced_decision_state"] == "CLEARED"
    assert res_legit.metadata["forced_verdict"] == "APPROVED"

    # Stolen card overrides confirmation
    res_override = await rule.evaluate({"customer_confirmed_legitimacy": True, "stolen_card": True})
    assert res_override.triggered is False


@pytest.mark.asyncio
async def test_r9_high_transaction_exposure() -> None:
    """R9: Test exposure exceeding $2,500 threshold."""
    rule = HighTransactionExposureRule()

    # Under threshold
    res_under = await rule.evaluate({"amount": 1500.0})
    assert res_under.triggered is False

    # Over threshold (> 2500)
    res_over = await rule.evaluate({"amount": 3200.0})
    assert res_over.triggered is True
    assert res_over.score_impact == 30.0


@pytest.mark.asyncio
async def test_r10_cumulative_threshold() -> None:
    """R10: Test cumulative fraud score threshold decision mapping."""
    rule = CumulativeFraudScoreThresholdRule(review_threshold=40.0, reject_threshold=75.0)

    # Low risk score
    res_low = await rule.evaluate({"risk_score": 20.0})
    assert res_low.metadata["policy_verdict"] == "APPROVED"

    # Review threshold
    res_rev = await rule.evaluate({"risk_score": 50.0})
    assert res_rev.triggered is True
    assert res_rev.metadata["policy_verdict"] == "NEEDS_REVIEW"

    # Reject threshold
    res_rej = await rule.evaluate({"risk_score": 85.0})
    assert res_rej.triggered is True
    assert res_rej.metadata["policy_verdict"] == "DECLINED"


@pytest.mark.asyncio
async def test_rule_aliases_and_registry() -> None:
    """Test backward-compatibility aliases and rule registry population."""
    assert HighFrequencyTransactionRule is HighVelocitySpikeRule
    assert UnusualAmountRule is HighTransactionExposureRule
    all_rule_ids = [r.rule_id for r in rule_registry.get_all_rules()]
    for expected_id in ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"]:
        assert expected_id in all_rule_ids


@pytest.mark.asyncio
async def test_fraud_engine_r7_guard_and_r8_cleared() -> None:
    """Integration test verifying R7 and R8 policy state transitions in FraudEngine."""
    engine = FraudEngine()

    # Transaction with low score but pending evidence -> Held at VERIFICATION_PENDING / REVIEW
    tx_pending = {
        "id": "tx_guard_test",
        "user_id": "usr_pending",
        "amount": 100.0,
        "evidence_status": "PENDING",
    }
    result_pending = await engine.evaluate_transaction(tx_pending)
    assert result_pending.decision == FraudDecision.REVIEW
    assert result_pending.decision_state == "VERIFICATION_PENDING"
    assert result_pending.verdict == "NEEDS_REVIEW"

    # Transaction with anomalies but customer confirmed -> Cleared
    tx_confirmed = {
        "id": "tx_legit_test",
        "user_id": "usr_legit",
        "amount": 2600.0,  # triggers R9
        "customer_confirmed_legitimacy": True,  # R8 overrides
    }
    result_confirmed = await engine.evaluate_transaction(tx_confirmed)
    assert result_confirmed.decision == FraudDecision.APPROVE
    assert result_confirmed.decision_state == "CLEARED"
    assert result_confirmed.verdict == "APPROVED"
