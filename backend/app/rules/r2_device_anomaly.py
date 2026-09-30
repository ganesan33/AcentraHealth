from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult


class DeviceFingerprintAnomalyRule(BaseFraudRule):
    """
    R2: Device Fingerprint Anomaly Rule.
    Detects network anonymization (VPN, Proxy, TOR exit nodes), device spoofing,
    or abnormal device fingerprint mutations.
    """
    rule_id: str = "R2"
    rule_name: str = "Device Fingerprint Anomaly"
    description: str = "Flags anonymized connections (VPN, Proxy, TOR) or abnormal device fingerprint tampering"
    weight: float = 30.0
    enabled: bool = True

    def __init__(self, weight: float = 30.0) -> None:
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        device_meta = transaction_data.get("device_info") or {}
        if not isinstance(device_meta, dict):
            device_meta = {}

        # Check direct and nested device anomaly indicators
        vpn_detected = (
            transaction_data.get("vpn_detected") is True
            or device_meta.get("vpn_detected") is True
            or transaction_data.get("vpn_devices_count", 0) > 0
        )
        proxy_detected = (
            transaction_data.get("proxy_detected") is True
            or device_meta.get("proxy_detected") is True
        )
        tor_detected = (
            transaction_data.get("tor_detected") is True
            or device_meta.get("tor_detected") is True
        )
        fingerprint_anomaly = (
            transaction_data.get("device_fingerprint_anomaly") is True
            or device_meta.get("fingerprint_mismatch") is True
            or transaction_data.get("is_emulator") is True
        )

        anomalies = []
        if vpn_detected:
            anomalies.append("VPN connection detected")
        if proxy_detected:
            anomalies.append("Proxy server detected")
        if tor_detected:
            anomalies.append("TOR exit node connection")
        if fingerprint_anomaly:
            anomalies.append("Device fingerprint mismatch/tampering")

        triggered = len(anomalies) > 0
        severity = "CRITICAL" if tor_detected else ("HIGH" if triggered else "INFO")

        reason = (
            f"Device fingerprint anomaly detected: {', '.join(anomalies)}"
            if triggered
            else "Device fingerprint and network connection appear authentic and direct"
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
                "anomalies": anomalies,
                "device_id": transaction_data.get("device_id"),
                "ip_address": transaction_data.get("ip_address"),
            },
        )


__all__ = ["DeviceFingerprintAnomalyRule"]
