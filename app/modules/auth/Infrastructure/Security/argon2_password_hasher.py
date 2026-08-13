"""
Argon2 password hasher implementation.
"""

from passlib.context import CryptContext


class Argon2PasswordHasher:
    def __init__(self) -> None:
        self._pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self._pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)


argon2PasswordHasher = Argon2PasswordHasher()
