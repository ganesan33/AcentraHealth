import base64
import hashlib
import hmac
import json
import secrets
import time
from enum import Enum
from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, status
from app.core.config import settings
from app.core.logging import logger


class UserRole(str, Enum):
    """User roles for access control within the Fraud Rule Engine console."""
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    INVESTIGATOR = "INVESTIGATOR"
    SERVICE = "SERVICE"


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash a password securely using PBKDF2-HMAC-SHA256.
    Returns format: pbkdf2_sha256$<iterations>$<salt>$<hex_hash>
    """
    if not salt:
        salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a PBKDF2 formatted hash string."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = parts[2]
        expected_hash = parts[3]
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(computed.hex(), expected_hash)
    except Exception as exc:
        logger.error(f"Error verifying password: {exc}")
        return False


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data_str: str) -> bytes:
    padding = "=" * (4 - (len(data_str) % 4))
    return base64.urlsafe_b64decode((data_str + padding).encode("utf-8"))


def create_access_token(
    payload: Dict[str, Any],
    secret_key: Optional[str] = None,
    expires_in_seconds: int = 3600,
) -> str:
    """
    Create a signed JWT-compatible token using HMAC-SHA256 without external dependencies.
    """
    key = (secret_key or settings.PROJECT_NAME + "_secret").encode("utf-8")
    header = {"alg": "HS256", "typ": "JWT"}
    
    token_claims = dict(payload)
    current_time = int(time.time())
    token_claims["iat"] = current_time
    token_claims["exp"] = current_time + expires_in_seconds

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(token_claims, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str, secret_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Decode and verify a signed JWT-compatible token.
    Raises HTTPException 401 if invalid or expired.
    """
    key = (secret_key or settings.PROJECT_NAME + "_secret").encode("utf-8")
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token format.",
        )
    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_signature = hmac.new(key, signing_input, hashlib.sha256).digest()
    actual_signature = _base64url_decode(signature_b64)

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature.",
        )

    claims: Dict[str, Any] = json.loads(_base64url_decode(payload_b64).decode("utf-8"))
    if "exp" in claims and claims["exp"] < int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
        )
    return claims


async def get_current_user_claims(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Dict[str, Any]:
    """
    FastAPI dependency to extract claims from Bearer token, or fallback to dev default if debug.
    """
    if not authorization:
        if settings.DEBUG:
            return {
                "sub": "dev_analyst_01",
                "role": UserRole.ANALYST.value,
                "name": "Default Dev Analyst",
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization scheme. Use 'Bearer <token>'.",
        )

    token = parts[1]
    return decode_access_token(token)
