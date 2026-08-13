"""
Current-profile use case.
"""

from typing import Any


class GetCurrentProfileUseCase:
    def execute(self, current_user: Any) -> Any:
        return current_user
