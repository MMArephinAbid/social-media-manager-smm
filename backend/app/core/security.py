"""
Security utilities - JWT, password hashing, encryption.
Created by: Sadia (Backend Lead)
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Union
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
import hashlib

from ..config import settings


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.PASSWORD_HASH_ROUNDS
)


# ============== Password Hashing ==============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============== JWT Tokens ==============

def create_access_token(
    subject: Union[str, UUID],
    organization_id: Optional[UUID] = None,
    role: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: User ID
        organization_id: User's organization ID
        role: User's role
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    if organization_id:
        to_encode["org_id"] = str(organization_id)

    if role:
        to_encode["role"] = role

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: User ID
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify an access token and return payload.

    Args:
        token: JWT access token

    Returns:
        Token payload or None if invalid
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verify a refresh token and return payload.

    Args:
        token: JWT refresh token

    Returns:
        Token payload or None if invalid
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


# ============== Encryption ==============

def get_fernet() -> Fernet:
    """Get Fernet instance for encryption."""
    # Create a valid Fernet key from our config key
    key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(key)
    return Fernet(key)


def encrypt_string(plain_text: str) -> str:
    """
    Encrypt a string (e.g., Facebook access tokens).

    Args:
        plain_text: String to encrypt

    Returns:
        Encrypted string (base64 encoded)
    """
    f = get_fernet()
    encrypted = f.encrypt(plain_text.encode())
    return encrypted.decode()


def decrypt_string(encrypted_text: str) -> str:
    """
    Decrypt an encrypted string.

    Args:
        encrypted_text: Encrypted string (base64 encoded)

    Returns:
        Decrypted plain text
    """
    f = get_fernet()
    decrypted = f.decrypt(encrypted_text.encode())
    return decrypted.decode()


# ============== Token Generation ==============

def generate_random_token(length: int = 32) -> str:
    """Generate a random token for password reset, etc."""
    import secrets
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    import secrets
    return ''.join(secrets.choice('0123456789') for _ in range(length))


# ============== Webhook Verification ==============

def verify_facebook_signature(
    payload: bytes,
    signature: str,
    app_secret: str = None
) -> bool:
    """
    Verify Facebook webhook signature.

    Args:
        payload: Request body bytes
        signature: X-Hub-Signature-256 header value
        app_secret: Facebook app secret

    Returns:
        True if signature is valid
    """
    import hmac

    if not signature or not signature.startswith("sha256="):
        return False

    app_secret = app_secret or settings.FACEBOOK_APP_SECRET
    expected_signature = hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    received_signature = signature[7:]  # Remove "sha256=" prefix

    return hmac.compare_digest(expected_signature, received_signature)


def verify_razorpay_signature(
    order_id: str,
    payment_id: str,
    signature: str
) -> bool:
    """
    Verify Razorpay payment signature.

    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Razorpay signature

    Returns:
        True if signature is valid
    """
    import hmac

    message = f"{order_id}|{payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)
