"""Backend package init"""

from grilo_falante.backend.api.main import app
from grilo_falante.backend.db.connection import init_pool, close_pool

__all__ = ["app", "init_pool", "close_pool"]
