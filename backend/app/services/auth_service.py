from pymongo.errors import DuplicateKeyError

from app.models.user_model import (
    create_user,
    get_user_by_email,
    email_exists
)

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