from fastapi import HTTPException, status
from bson import ObjectId
from app.models.audit_model import create_audit_log
from app.models import user_model
from app.core.permissions import Role
from app.models.token_model import revoke_all_user_refresh_tokens

from app.models.user_model import (
    get_user_by_id,
    list_users,
    update_user_profile,
    update_user_role,
    update_user_status
)



def get_admin_organization_id(current_user: dict) -> str:
    organization_id = current_user.get("organization_id")

    if not organization_id:
        raise HTTPException(
            status_code=403,
            detail="Your account is not assigned to an organization"
        )

    organization_id = str(organization_id)

    if not ObjectId.is_valid(organization_id):
        raise HTTPException(
            status_code=403,
            detail="Invalid organization assignment"
        )

    return organization_id


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


def get_all_users(
    current_user: dict,
    page: int = 1,
    page_size: int = 10
):
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

    organization_id = get_admin_organization_id(current_user)

    return user_model.list_users_by_organization(
        organization_id=organization_id,
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

    organization_id = get_admin_organization_id(current_user)

    target_user = user_model.get_user_by_id_and_organization(
        target_user_id,
        organization_id
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found in your organization"
        )

    old_role = target_user["role"]

    if (
        old_role == Role.ADMIN.value
        and new_role != Role.ADMIN
        and target_user.get("is_active") is True
    ):
        active_admin_count = user_model.users_collection.count_documents({
            "role": Role.ADMIN.value,
            "is_active": True,
            "organization_id": ObjectId(organization_id)
        })

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last active administrator"
            )

    updated_user = user_model.update_user_role_by_organization(
        target_user_id,
        organization_id,
        new_role.value
    )

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found in your organization"
        )

    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="user.role_changed",
        target_user_id=target_user_id,
        changes={
            "role": {
                "old": old_role,
                "new": new_role.value
            }
        },
        organization_id=organization_id
    )

    return updated_user





def change_user_status(
    target_user_id: str,
    is_active: bool,
    current_user: dict
):
    # 1. Validate user ID
    if not ObjectId.is_valid(target_user_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    # 2. Prevent self-deactivation
    if str(current_user["_id"]) == target_user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own account status"
        )

    # 3. Get administrator's organization
    organization_id = get_admin_organization_id(current_user)

    # 4. Find target user in the same organization
    target_user = user_model.get_user_by_id_and_organization(
        target_user_id,
        organization_id
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found in your organization"
        )

    old_status = target_user.get("is_active")

    # 5. Prevent deactivation of the last active administrator
    if (
        target_user.get("role") == Role.ADMIN.value
        and old_status is True
        and is_active is False
    ):
        active_admin_count = (
            user_model.users_collection.count_documents({
                "role": Role.ADMIN.value,
                "is_active": True,
                "organization_id": ObjectId(organization_id)
            })
        )

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate the last active administrator"
            )

    # 6. Update account status
    updated_user = user_model.update_user_status_by_organization(
        target_user_id,
        organization_id,
        is_active
    )

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found in your organization"
        )

    # 7. Revoke refresh tokens after deactivation
    revoked_tokens_count = 0

    if old_status is True and is_active is False:
        revoked_tokens_count = revoke_all_user_refresh_tokens(
            target_user_id
        )

    # 8. Create audit log
    create_audit_log(
        actor_user_id=str(current_user["_id"]),
        action="user.status_changed",
        target_user_id=target_user_id,
        changes={
            "is_active": {
                "old": old_status,
                "new": is_active
            },
            "revoked_refresh_tokens": revoked_tokens_count
        },
        organization_id=organization_id
    )

    # 9. Return updated user
    return updated_user
