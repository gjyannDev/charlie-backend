"""
Reusable FastAPI dependencies.
"""

from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.modules.auth.Domain.Enums import UserRole
from app.modules.auth.Domain.Rules import authRules
from app.modules.auth.Services import get_current_user


def require_roles(allowed_roles: list[UserRole] | None = None):
    """
    Enforce role-based access control for authenticated endpoints.
    """

    def role_checker(current_user: User = Depends(get_current_user)):
        try:
            authRules.ensure_allowed_role(current_user.role, allowed_roles)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User has invalid role: {current_user.role}",
            )
        except PermissionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker
