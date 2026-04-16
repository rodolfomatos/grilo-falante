"""
Admin Routers - Collection of all admin API routers.
"""

from grilo_admin.routers.users import router as users_router
from grilo_admin.routers.system import router as system_router
from grilo_admin.routers.plugins import router as plugins_router

__all__ = [
    "users_router",
    "system_router",
    "plugins_router",
]
