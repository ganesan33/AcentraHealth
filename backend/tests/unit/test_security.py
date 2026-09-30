import pytest
import time
from fastapi import HTTPException
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    UserRole,
)


def test_password_hashing_and_verification() -> None:
    """Test PBKDF2 hashing generates valid hash and correctly verifies matches."""
    plain = "SuperSecretPassword123!"
    hashed = hash_password(plain)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_creation_and_decoding() -> None:
    """Test JWT creation and claims retrieval."""
    payload = {"sub": "analyst_42", "role": UserRole.ANALYST.value}
    token = create_access_token(payload, expires_in_seconds=60)
    claims = decode_access_token(token)

    assert claims["sub"] == "analyst_42"
    assert claims["role"] == UserRole.ANALYST.value
    assert "exp" in claims


def test_jwt_token_expiration() -> None:
    """Test that expired tokens raise HTTPException 401."""
    payload = {"sub": "expired_user"}
    # Token that expired 5 seconds ago
    token = create_access_token(payload, expires_in_seconds=-5)

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()
