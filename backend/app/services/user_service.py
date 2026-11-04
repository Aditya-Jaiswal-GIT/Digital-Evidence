from fastapi import HTTPException, status
from bson import ObjectId

from app.models import user_model
from app.core.permissions import Role

from app.models.user_model import (
    get_user_by_id,
    list_users,
    update_user_profile,
    update_user_role,
    update_user_status
)


def update_my_profile(current_user: dict, full_name: str):
    user_id = str(current_user["_id"])

    updated_user = update_user_profile(
        user_id,
        {"full_name": " ".join(full_name.split())}
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user


def get_all_users(page: int = 1, page_size: int = 10):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="Page size must be between 1 and 100"
        )

    return list_users(
        page=page,
        page_size=page_size
    )

def change_user_role(
    target_user_id: str,
    new_role: Role,
    current_user: dict
):
    if not ObjectId.is_valid(target_user_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    if str(current_user["_id"]) == target_user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role"
        )

    target_user = user_model.get_user_by_id(target_user_id)

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent demoting the last active administrator.
    if (
        target_user.get("role") == Role.ADMIN.value
        and new_role != Role.ADMIN
        and target_user.get("is_active") is True
    ):
        active_admin_count = user_model.users_collection.count_documents({
            "role": Role.ADMIN.value,
            "is_active": True
        })

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last active administrator"
            )

    updated_user = user_model.update_user_role(
        target_user_id,
        new_role.value
    )

    return updated_user

def change_user_status(
    target_user_id: str,
    is_active: bool,
    current_user: dict
):
    if not ObjectId.is_valid(target_user_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    if str(current_user["_id"]) == target_user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own account status"
        )

    target_user = user_model.get_user_by_id(target_user_id)

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent deactivation of the last active administrator.
    if (
        target_user.get("role") == Role.ADMIN.value
        and target_user.get("is_active") is True
        and is_active is False
    ):
        active_admin_count = user_model.users_collection.count_documents({
            "role": Role.ADMIN.value,
            "is_active": True
        })

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate the last active administrator"
            )

    updated_user = user_model.update_user_status(
        target_user_id,
        is_active
    )

    return updated_user

