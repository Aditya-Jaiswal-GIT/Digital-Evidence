from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jwt.exceptions import InvalidTokenError

from app.core.security import decode_token
from app.models.user_model import get_user_by_id
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.core.permissions import (
    Role,
    Permission,
    ROLE_PERMISSIONS
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = decode_token(token)

        if payload["type"] != "access":
            raise ValueError("Invalid token type")

        user_id = payload["sub"]

    except (InvalidTokenError, ValueError, KeyError):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = get_user_by_id(user_id)

    if not user or not user.get("is_active", False):

        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


def require_permissions(
    *required_permissions: Permission
) -> Callable:

    def permission_checker(
        current_user: dict = Depends(get_current_user)
    ):

        user_role = current_user.get("role")

        try:
            role = Role(user_role)

        except (ValueError, TypeError):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )

        allowed_permissions = ROLE_PERMISSIONS.get(
            role,
            set()
        )

        # All requested permissions must be present
        if not set(required_permissions).issubset(
            allowed_permissions
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return permission_checker