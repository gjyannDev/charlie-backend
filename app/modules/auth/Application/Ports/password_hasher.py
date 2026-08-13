"""
Application port for password hashing.
"""

from typing import Protocol


class PasswordHasherPort(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, plain_password: str, hashed_password: str) -> bool: ...
