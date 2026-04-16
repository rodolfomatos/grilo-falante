"""
Admin Routers - Collection of all admin API routers.
"""

from grilo_admin.routers.users import router as users_router
from grilo_admin.routers.system import router as system_router
from grilo_admin.routers.plugins import router as plugins_router
from grilo_admin.routers.repositories import router as repositories_router
from grilo_admin.routers.cycles import router as cycles_router
from grilo_admin.routers.learning import router as learning_router
from grilo_admin.routers.escalations import router as escalations_router
from grilo_admin.routers.articles import router as articles_router
from grilo_admin.routers.ilhas import router as ilhas_router
from grilo_admin.routers.skills import router as skills_router

__all__ = [
    "users_router",
    "system_router",
    "plugins_router",
    "repositories_router",
    "cycles_router",
    "learning_router",
    "escalations_router",
    "articles_router",
    "ilhas_router",
    "skills_router",
]
