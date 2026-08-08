"""
Domain enum definitions for the auth module.
"""

from enum import Enum


class UserRole(str, Enum):
    """
    Canonical auth role enum shared by schemas, rules, and models.
    """

    ADMIN = "admin"
    USER = "user"
