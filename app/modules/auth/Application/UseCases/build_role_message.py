"""
Role-message use case.
"""

from typing import Any


class BuildRoleMessageUseCase:
    def execute(self, message: str, current_user: Any) -> dict[str, str]:
        return {
            "message": message,
            "user": current_user.full_name,
            "role": current_user.role.value,
        }
