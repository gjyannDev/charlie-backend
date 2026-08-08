"""
Auth routes exposed by the auth module.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import require_roles
from app.models.user import User
from app.modules.auth.Controllers import authController
from app.modules.auth.Domain.Enums import UserRole
from app.modules.auth.Schemas import (
    MeSchema,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.modules.auth.Services import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    return authController.register(user, db)


@auth_router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return authController.login(user, db)


@auth_router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: RefreshTokenRequest, db: Session = Depends(get_db)):
    return authController.refresh(refresh_token.refresh_token, db)


@auth_router.post("/logout")
def logout(refresh_token: RefreshTokenRequest, db: Session = Depends(get_db)):
    return authController.logout(refresh_token.refresh_token, db)


@auth_router.get("/me", response_model=MeSchema)
def get_me(current_user: User = Depends(get_current_user)):
    return authController.get_me(current_user)


@auth_router.get("/admin-role")
def admin_role_api(current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    return authController.admin_role(current_user)


@auth_router.get("/user-role")
def user_role_api(current_user: User = Depends(require_roles([UserRole.USER]))):
    return authController.user_role(current_user)


@auth_router.get("/multi-role")
def multiple_role_api(
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.USER])),
):
    return authController.multi_role(current_user)
