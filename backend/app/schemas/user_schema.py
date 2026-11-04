from pydantic import BaseModel, Field, ConfigDict
from app.schemas.auth_schema import UserRole, UserResponse


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(
        min_length=3,
        max_length=100
    )

    model_config = ConfigDict(extra="forbid")


class UpdateUserRoleRequest(BaseModel):
    role: UserRole

    model_config = ConfigDict(extra="forbid")


class UpdateUserStatusRequest(BaseModel):
    is_active: bool

    model_config = ConfigDict(extra="forbid")


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    page_size: int