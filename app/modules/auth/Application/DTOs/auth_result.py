"""
Application DTOs for auth use-case results.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

from app.modules.auth.Domain.Events import AuthEvent

T = TypeVar("T")


@dataclass(slots=True)
class AuthUseCaseResult(Generic[T]):
    value: T
    events: tuple[AuthEvent, ...] = ()
