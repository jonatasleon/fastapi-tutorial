"""Routers for the application."""
from .auth import router as auth_router
from .items import router as items_router
from .users import router as users_router

__all__ = ["auth_router", "items_router", "users_router"]
