import pytest
from app.rules.velocity import HighFrequencyTransactionRule
from app.rules.unusual_amount import UnusualAmountRule
from app.rules.impossible_location import ImpossibleLocationRule


@pytest.mark.asyncio
async def test_velocity_rule_triggers_on_burst() -> None:
    """Test that velocity rule triggers when transaction limit is exceeded."""
    rule = HighFrequencyTransactionRule(max_allowed=2, window_seconds=60)
    tx = {"user_id": "usr_burst_test", "amount": 50.0}

    # First and second transaction should pass
    res1 = await rule.evaluate(tx)
    assert res1.triggered is False

    res2 = await rule.evaluate(tx)
    assert res2.triggered is False

    # Third transaction exceeds limit (2)
    res3 = await rule.evaluate(tx)
    assert res3.triggered is True
    assert res3.score_impact == 35.0
    assert "exceeded velocity threshold" in res3.reason


@pytest.mark.asyncio
async def test_unusual_amount_rule() -> None:
    """Test amount anomalies for normal, high, and critical levels."""
    rule = UnusualAmountRule(threshold_amount=1000.0, critical_threshold=5000.0, weight=40.0)

    # Normal amount
    res_normal = await rule.evaluate({"amount": 250.0, "currency": "USD"})
    assert res_normal.triggered is False
    assert res_normal.score_impact == 0.0

    # High amount (> 1000)
    res_high = await rule.evaluate({"amount": 1500.0, "currency": "USD"})
    assert res_high.triggered is True
    assert res_high.score_impact == 40.0

    # Critical amount (> 5000)
    res_crit = await rule.evaluate({"amount": 6000.0, "currency": "USD"})
    assert res_crit.triggered is True
    assert res_crit.score_impact >= 60.0


@pytest.mark.asyncio
async def test_impossible_location_rule_speed() -> None:
    """Test geo-velocity detects physically impossible transit speed."""
    rule = ImpossibleLocationRule(max_speed_kmh=800.0, weight=50.0)
    user_id = "usr_geo_traveler"

    # Transaction 1: London (approx 51.5, -0.12)
    tx1 = {
        "user_id": user_id,
        "latitude": 51.5074,
        "longitude": -0.1278,
        "location_country": "GB",
    }
    res1 = await rule.evaluate(tx1)
    assert res1.triggered is False

    # Transaction 2: New York (approx 40.7, -74.0) instantly afterwards
    tx2 = {
        "user_id": user_id,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_country": "US",
    }
    res2 = await rule.evaluate(tx2)
    assert res2.triggered is True
    assert res2.score_impact == 50.0
    assert "Impossible" in res2.reason
