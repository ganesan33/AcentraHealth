import pytest
from datetime import datetime, timezone
from app.models.transaction import Transaction
from app.models.fraud_rule import FraudRule
from app.models.review import Review
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.schemas.review import ReviewUpdateDecision, ReviewDecisionEnum


def test_transaction_schema_validation() -> None:
    """Test valid transaction creation and validation error on invalid amount."""
    data = {
        "user_id": "usr_99",
        "account_id": "acc_99",
        "amount": 120.50,
        "currency": "USD",
        "merchant_id": "mer_walmart",
    }
    tx_create = TransactionCreate(**data)
    assert tx_create.amount == 120.50
    assert tx_create.currency == "USD"
    assert tx_create.channel == "WEB"


def test_transaction_schema_negative_amount_fails() -> None:
    """Ensure negative amounts are rejected by schema."""
    with pytest.raises(Exception):
        TransactionCreate(
            user_id="u1",
            account_id="a1",
            amount=-50.0,
            merchant_id="m1",
        )


def test_review_decision_schema() -> None:
    """Verify review decision payload validation."""
    decision_payload = ReviewUpdateDecision(
        decision=ReviewDecisionEnum.APPROVE,
        decision_reason="Customer verified by phone call",
        reviewer_notes="Confirmed cardholder authorized transaction",
        analyst_id="analyst_alice",
    )
    assert decision_payload.decision == ReviewDecisionEnum.APPROVE
    assert decision_payload.analyst_id == "analyst_alice"


def test_model_instantiation() -> None:
    """Verify ORM models can be instantiated."""
    tx = Transaction(
        id="tx_test_model",
        user_id="usr_01",
        account_id="acc_01",
        amount=199.99,
        currency="USD",
        merchant_id="mer_01",
        status="APPROVED",
    )
    assert tx.id == "tx_test_model"
    assert tx.amount == 199.99

    rule = FraudRule(
        rule_code="TEST_RULE_01",
        name="Test Rule",
        weight=25.0,
    )
    assert rule.rule_code == "TEST_RULE_01"
