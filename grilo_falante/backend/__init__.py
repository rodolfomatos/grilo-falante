"""Backend package — API, MCP, Services, DB"""

from grilo_falante.backend.db.connection import init_pool, close_pool, check_health
from grilo_falante.backend.db.repositories import (
    ClaimRepository,
    GapRepository,
    CuratorRepository,
    SourceRepository,
    SessionPreferencesRepository,
    GovernanceRepository,
)

__all__ = [
    "init_pool",
    "close_pool",
    "check_health",
    "ClaimRepository",
    "GapRepository",
    "CuratorRepository",
    "SourceRepository",
    "SessionPreferencesRepository",
    "GovernanceRepository",
]
