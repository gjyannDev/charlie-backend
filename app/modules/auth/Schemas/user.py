"""
Pydantic schemas for auth requests and responses.
"""

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.auth.Domain.Enums import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.USER

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None
    token_type: str = "bearer"


class MeSchema(UserResponse):
    """
    Schema returned by /auth/me endpoint.
    """
