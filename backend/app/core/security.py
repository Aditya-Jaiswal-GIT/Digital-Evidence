import jwt
import hashlib
import secrets

from datetime import datetime, timedelta, timezone

from app.core.config import settings
from pwdlib import PasswordHash


# -------------------------
# PASSWORD SECURITY
# -------------------------

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:

    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hasher.verify(
        plain_password,
        hashed_password
    )


# -------------------------
# JWT TOKEN GENERATION
# -------------------------

def create_access_token(user_id: str, role: str):

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "jti": secrets.token_urlsafe(16),
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def create_refresh_token(user_id: str):

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),
        "iat": now,
        "exp": now + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


# -------------------------
# JWT VERIFICATION
# -------------------------

def decode_token(token: str):

    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={
            "require": ["exp", "iat", "sub", "jti", "type"]
        }
    )


# -------------------------
# REFRESH TOKEN HASHING
# -------------------------

def hash_refresh_token(token: str) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()