"""
System Router - System monitoring and cache management endpoints.
"""

import logging
import os
import platform
import time
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["system"])

_start_time = time.time()


class SystemStats:
    """Collects system statistics."""

    @staticmethod
    def get_uptime() -> float:
        """Get uptime in seconds."""
        return time.time() - _start_time

    @staticmethod
    def get_python_version() -> str:
        """Get Python version."""
        return platform.python_version()

    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """Get platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }

    @staticmethod
    def get_env_vars() -> Dict[str, Any]:
        """Get relevant environment variables (non-sensitive)."""
        sensitive = ["PASSWORD", "SECRET", "KEY", "TOKEN", "API_KEY"]
        env = {}
        for key, value in os.environ.items():
            is_sensitive = any(s.lower() in key.lower() for s in sensitive)
            if is_sensitive:
                env[key] = "***REDACTED***"
            else:
                env[key] = value
        return env

    @staticmethod
    def get_llm_status() -> Dict[str, Any]:
        """Get LLM provider status."""
        from grilo_falante.platform.config import get_llm_config, is_provider_available

        default_provider = get_llm_config().provider
        available = list_available_providers() if 'list_available_providers' in dir() else []

        return {
            "default_provider": default_provider,
            "available_providers": available,
            "bitnet_endpoint": os.getenv("BITNET_BASE_URL", "http://localhost:8002"),
            "ollama_endpoint": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        }

    @staticmethod
    def get_plugins_status() -> Dict[str, Any]:
        """Get installed plugins status."""
        try:
            from grilo_falante.platform import PluginRegistry

            plugins = []
            for name in PluginRegistry.list_plugins():
                try:
                    adapter = PluginRegistry.get(name)
                    meta = adapter.get_metadata()
                    plugins.append({
                        "name": meta.name,
                        "version": meta.version,
                        "status": meta.status.value,
                        "description": meta.description,
                    })
                except Exception as e:
                    plugins.append({
                        "name": name,
                        "status": "error",
                        "error": str(e),
                    })

            return {
                "total": len(plugins),
                "plugins": plugins,
            }
        except ImportError:
            return {"total": 0, "plugins": [], "error": "Platform not available"}

    @staticmethod
    def get_memory_status() -> Dict[str, Any]:
        """Get memory/Cache status."""
        try:
            from grilo_falante.backend.memory.mempalace_cache import MemPalaceCache

            cache = MemPalaceCache()
            stats = cache.get_stats() if hasattr(cache, 'get_stats') else {}

            return {
                "mempalace_available": True,
                "stats": stats,
            }
        except ImportError:
            return {"mempalace_available": False}
        except Exception as e:
            return {"mempalace_available": False, "error": str(e)}

    @staticmethod
    def get_database_status() -> Dict[str, Any]:
        """Get database status."""
        try:
            return {"database_available": "not_checked", "note": "Use /admin/system/health for async check"}
        except ImportError:
            return {"database_available": False, "reason": "Module not available"}
        except Exception as e:
            return {"database_available": False, "error": str(e)}

    @staticmethod
    def get_cycle_status() -> Dict[str, Any]:
        """Get current cycle status."""
        try:
            from grilo_falante.regime.state import StateMachine, CycleState

            sm = StateMachine()
            current_state = sm.current_cycle.state if sm.current_cycle else CycleState.INACTIVE

            return {
                "current_state": current_state.value,
                "has_active_cycle": sm.current_cycle is not None,
            }
        except ImportError:
            return {"error": "Regime module not available"}
        except Exception as e:
            return {"error": str(e)}


class CacheManager:
    """Manages cache operations."""

    _cache_cleared = False
    _last_clear_time: Optional[datetime] = None

    @classmethod
    def clear_all_caches(cls) -> Dict[str, Any]:
        """Clear all caches."""
        cleared = []

        try:
            from grilo_falante.backend.memory.mempalace_cache import MemPalaceCache
            cache = MemPalaceCache()
            if hasattr(cache, 'clear'):
                cache.clear()
                cleared.append("mempalace")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Could not clear mempalece: {e}")

        cls._cache_cleared = True
        cls._last_clear_time = datetime.now()

        return {
            "cleared": cleared,
            "timestamp": cls._last_clear_time.isoformat(),
        }

    @classmethod
    def clear_mempalace(cls) -> Dict[str, Any]:
        """Clear MemPalace cache specifically."""
        try:
            from grilo_falante.backend.memory.mempalace_cache import MemPalaceCache

            cache = MemPalaceCache()
            if hasattr(cache, 'clear'):
                cache.clear()
                cls._last_clear_time = datetime.now()
                return {"success": True, "cache": "mempalace", "timestamp": cls._last_clear_time.isoformat()}
            return {"success": False, "error": "clear() method not available"}
        except ImportError:
            return {"success": False, "error": "MemPalace not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def clear_llm_cache(cls) -> Dict[str, Any]:
        """Clear LLM cache."""
        cls._last_clear_time = datetime.now()
        return {"success": True, "cache": "llm", "timestamp": cls._last_clear_time.isoformat(), "note": "LLM cache clearing not yet implemented"}


@router.get("/status")
async def get_system_status(
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    Get overall system status.

    Returns system information, LLM status, plugins, and cycle state.
    """
    stats = SystemStats()

    return {
        "service": "grilo-falante",
        "version": "3.0.0",
        "uptime_seconds": round(stats.get_uptime(), 2),
        "uptime_human": _format_uptime(stats.get_uptime()),
        "timestamp": datetime.now().isoformat(),
        "platform": stats.get_platform_info(),
        "python_version": stats.get_python_version(),
        "llm": stats.get_llm_status(),
        "plugins": stats.get_plugins_status(),
        "memory": stats.get_memory_status(),
        "database": stats.get_database_status(),
        "cycle": stats.get_cycle_status(),
    }


@router.get("/health")
async def get_system_health(
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    Get detailed health checks for all system components.
    """
    stats = SystemStats()

    checks = {
        "api": {"status": "healthy"},
        "llm": {"status": "unknown"},
        "mempalace": {"status": "unknown"},
        "database": {"status": "unknown"},
        "plugins": {"status": "unknown"},
    }

    llm_status = stats.get_llm_status()
    checks["llm"] = {"status": "healthy" if llm_status.get("default_provider") else "degraded"}

    memory_status = stats.get_memory_status()
    checks["mempalace"] = {
        "status": "healthy" if memory_status.get("mempalace_available") else "unavailable"
    }

    db_status = stats.get_database_status()
    checks["database"] = {
        "status": "healthy" if db_status.get("database_available") == True else "unhealthy"
    }

    plugins_status = stats.get_plugins_status()
    checks["plugins"] = {
        "status": "healthy",
        "count": plugins_status.get("total", 0),
    }

    overall_healthy = all(
        c.get("status") in ("healthy", "unknown") for c in checks.values()
    )

    return {
        "healthy": overall_healthy,
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    Get system statistics and metrics.
    """
    stats = SystemStats()

    return {
        "uptime_seconds": round(stats.get_uptime(), 2),
        "platform": stats.get_platform_info(),
        "python_version": stats.get_python_version(),
        "plugins": stats.get_plugins_status(),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/cache/clear")
async def clear_all_caches(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Clear all caches. Admin only.
    """
    logger.info(f"User {current_user.email} triggered cache clear")
    return CacheManager.clear_all_caches()


@router.post("/cache/clear/mempalace")
async def clear_mempalace_cache(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Clear MemPalace cache specifically. Admin only.
    """
    logger.info(f"User {current_user.email} cleared MemPalace cache")
    return CacheManager.clear_mempalace()


@router.post("/cache/clear/llm")
async def clear_llm_cache(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Clear LLM cache specifically. Admin only.
    """
    logger.info(f"User {current_user.email} cleared LLM cache")
    return CacheManager.clear_llm_cache()


@router.get("/env")
async def get_environment(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Get environment variables (filtered). Admin only.
    """
    stats = SystemStats()
    return {
        "environment": stats.get_env_vars(),
        "count": len(stats.get_env_vars()),
    }


def _format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)
