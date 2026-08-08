"""
Pure auth-domain validation helpers.
"""

from collections.abc import Sequence

from app.modules.auth.Domain.Enums import UserRole


class AuthRules:
    def parse_user_role(self, role: UserRole | str) -> UserRole:
        if isinstance(role, UserRole):
            return role

        try:
            return UserRole(role)
        except ValueError as exc:
            raise ValueError("Invalid role") from exc

    def ensure_allowed_role(
        self, role: UserRole | str, allowed_roles: Sequence[UserRole] | None = None
    ) -> UserRole:
        parsed_role = self.parse_user_role(role)
        if allowed_roles and parsed_role not in allowed_roles:
            raise PermissionError("You do not have permission to access this resource")
        return parsed_role


authRules = AuthRules()
