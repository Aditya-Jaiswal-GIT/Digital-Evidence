from fastapi import APIRouter, Depends, Query

from app.core.dependencies import (
    get_current_user,
    require_permissions
)

from app.core.permissions import Permission, Role

from app.schemas.auth_schema import UserResponse

from app.schemas.user_schema import (
    UpdateProfileRequest,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserListResponse
)

from app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["User Management"]
)

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "id": str(current_user["_id"]),
        "full_name": current_user["full_name"],
        "email": current_user["email"],
        "role": current_user["role"],
        "is_active": current_user["is_active"],
        "is_verified": current_user["is_verified"]
    }



@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    return user_service.update_my_profile(
        current_user,
        request.full_name
    )



@router.get("", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    return user_service.get_all_users(
        current_user=current_user,
        page=page,
        page_size=page_size
    )

@router.patch("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    return user_service.change_user_role(
        target_user_id=user_id,
        new_role=request.role,
        current_user=current_user
    )

@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    current_user: dict = Depends(
        require_permissions(Permission.MANAGE_USERS)
    )
):
    return user_service.change_user_status(
        target_user_id=user_id,
        is_active=request.is_active,
        current_user=current_user
    )


