from enum import Enum
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator
)


class UserRole(str, Enum):

    ADMIN = "admin"
    INVESTIGATOR = "investigator"
    FORENSIC_ANALYST = "forensic_analyst"
    REVIEWER = "reviewer"


class SignupRequest(BaseModel):

    full_name: str = Field(
        min_length=3,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value):

        value = " ".join(value.split())

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):

        return value.lower()


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):

        return value.lower()


class UserResponse(BaseModel):

    id: str

    full_name: str

    email: EmailStr

    role: UserRole

    is_active: bool

    is_verified: bool

    model_config = ConfigDict(
        extra="ignore"
    )
    


class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"


class RefreshRequest(BaseModel):

    refresh_token: str = Field(
        min_length=20,
        max_length=4096
    )