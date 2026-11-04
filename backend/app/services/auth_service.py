from pymongo.errors import DuplicateKeyError

from app.models.user_model import (
    create_user,
    get_user_by_email,
    email_exists
)
from datetime import datetime, timezone

from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError

from app.models.user_model import (
    get_user_by_email,
    get_user_by_id
)

from app.models.token_model import (
    store_refresh_token,
    consume_refresh_token
)

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token
)

from app.core.config import settings

from app.schemas.auth_schema import TokenResponse

from app.core.security import hash_password

from app.schemas.auth_schema import UserResponse


def register_user(user_data: dict):

    # 1. Check duplicate email
    if email_exists(user_data["email"]):

        raise ValueError(
            "Email is already registered"
        )

    # 2. Hash password
    hashed_password = hash_password(
        user_data["password"]
    )

    # 3. Prepare MongoDB document
    new_user = {
        "full_name": user_data["full_name"],
        "email": user_data["email"].lower(),

        "password_hash": hashed_password,

        # Public registration gets a basic role
        "role": "investigator",

        "organization_id": None,

        "is_active": True,
        "is_verified": False
    }

    # 4. Store user
    try:
        user_id = create_user(new_user)

    except DuplicateKeyError:
        raise ValueError(
            "Email is already registered"
        )

    # 5. Return safe response
    return UserResponse(
        id=user_id,
        full_name=new_user["full_name"],
        email=new_user["email"],
        role=new_user["role"],
        is_active=new_user["is_active"],
        is_verified=new_user["is_verified"]
    )

def login_user(email: str, password: str):

    user = get_user_by_email(email.lower())

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not user.get("is_active", False):

        raise HTTPException(
            status_code=403,
            detail="Account is inactive"
        )

    if not verify_password(
        password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    user_id = str(user["_id"])

    access_token = create_access_token(
        user_id,
        user["role"]
    )

    refresh_token = create_refresh_token(
        user_id
    )

    payload = decode_token(refresh_token)

    store_refresh_token(
        user_id,
        hash_refresh_token(refresh_token),
        datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc
        )
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

def refresh_user_token(refresh_token: str):

    try:

        payload = decode_token(refresh_token)

        if payload["type"] != "refresh":
            raise ValueError("Wrong token type")

    except (InvalidTokenError, ValueError, KeyError):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )

    token_hash = hash_refresh_token(refresh_token)

    # Atomically consume the old token
    stored_token = consume_refresh_token(token_hash)

    if not stored_token:

        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked or already used"
        )

    user = get_user_by_id(payload["sub"])

    if not user or not user.get("is_active", False):

        raise HTTPException(
            status_code=401,
            detail="User is unavailable"
        )

    user_id = str(user["_id"])

    # Generate a new token pair
    new_access_token = create_access_token(
        user_id,
        user["role"]
    )

    new_refresh_token = create_refresh_token(
        user_id
    )

    new_payload = decode_token(new_refresh_token)

    store_refresh_token(
        user_id,
        hash_refresh_token(new_refresh_token),
        datetime.fromtimestamp(
            new_payload["exp"],
            tz=timezone.utc
        )
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

def logout_user(refresh_token: str):

    try:
        payload = decode_token(refresh_token)

        if payload["type"] != "refresh":
            raise ValueError("Wrong token type")

    except (InvalidTokenError, ValueError, KeyError):

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    revoked = consume_refresh_token(
        hash_refresh_token(refresh_token)
    )

    if not revoked:

        raise HTTPException(
            status_code=401,
            detail="Refresh token already revoked or expired"
        )

    return {"message": "Logged out successfully"}