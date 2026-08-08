"""
Compatibility shim for the moved auth router.
"""

from app.modules.auth.Routes import auth_router as user_router

__all__ = ["user_router"]
