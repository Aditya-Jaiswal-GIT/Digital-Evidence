from fastapi import APIRouter, HTTPException, status

from app.schemas.auth_schema import (
    SignupRequest,
    UserResponse
)

from app.schemas.auth_schema import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    RefreshRequest
)

from app.core.dependencies import require_permissions

from app.core.permissions import Permission

from app.services.auth_service import logout_user

from app.core.dependencies import get_current_user
from fastapi import Depends

from app.services.auth_service import (
    register_user,
    login_user,
    refresh_user_token
)

from app.services.auth_service import register_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(request: SignupRequest):

    try:

        user = register_user(
            request.model_dump()
        )

        return user

    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error)
        )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(request: LoginRequest):

    return login_user(
        request.email,
        request.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh(request: RefreshRequest):

    return refresh_user_token(
        request.refresh_token
    )


@router.post("/logout")
def logout(request: RefreshRequest):

    return logout_user(request.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_profile(
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


