"""
Plugins Router - Plugin management endpoints.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plugins", tags=["plugins"])


class PluginManager:
    """Manages plugin operations."""

    _plugin_configs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_plugins(cls) -> List[Dict[str, Any]]:
        """Get all registered plugins."""
        try:
            from grilo_falante.platform import PluginRegistry

            plugins = []
            for name in PluginRegistry.list_plugins():
                try:
                    adapter = PluginRegistry.get(name)
                    meta = adapter.get_metadata()

                    plugin_info = {
                        "name": meta.name,
                        "version": meta.version,
                        "description": meta.description,
                        "author": meta.author,
                        "status": meta.status.value,
                        "dependencies": meta.dependencies,
                        "routing_keywords": adapter.get_routing_config(),
                        "escalation_triggers": adapter.get_escalation_triggers(),
                        "config": cls._plugin_configs.get(name, {}),
                    }
                    plugins.append(plugin_info)
                except Exception as e:
                    plugins.append({
                        "name": name,
                        "status": "error",
                        "error": str(e),
                    })

            return plugins
        except ImportError:
            return []
        except Exception as e:
            logger.error(f"Error getting plugins: {e}")
            return []

    @classmethod
    def get_plugin(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific plugin by name."""
        try:
            from grilo_falante.platform import PluginRegistry

            adapter = PluginRegistry.get(name)
            meta = adapter.get_metadata()

            return {
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "author": meta.author,
                "status": meta.status.value,
                "dependencies": meta.dependencies,
                "routing_keywords": adapter.get_routing_config(),
                "escalation_triggers": adapter.get_escalation_triggers(),
                "config": cls._plugin_configs.get(name, {}),
            }
        except ValueError:
            return None
        except ImportError:
            return None
        except Exception as e:
            logger.error(f"Error getting plugin {name}: {e}")
            return None

    @classmethod
    def update_plugin_config(cls, name: str, config: Dict[str, Any]) -> bool:
        """Update plugin configuration."""
        try:
            from grilo_falante.platform import PluginRegistry

            if name not in PluginRegistry.list_plugins():
                return False

            cls._plugin_configs[name] = config
            logger.info(f"Updated config for plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Error updating plugin config: {e}")
            return False

    @classmethod
    def test_plugin(cls, name: str) -> Dict[str, Any]:
        """Test if a plugin is working."""
        try:
            from grilo_falante.platform import PluginRegistry

            adapter = PluginRegistry.get(name)

            test_query = "test"
            routing_result = adapter.get_department_for_query(test_query)

            return {
                "name": name,
                "status": "working",
                "routing_test": routing_result,
            }
        except ValueError:
            return {"name": name, "status": "not_found"}
        except Exception as e:
            return {"name": name, "status": "error", "error": str(e)}


@router.get("")
async def list_plugins(
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    List all registered plugins.
    """
    plugins = PluginManager.get_plugins()

    return {
        "plugins": plugins,
        "total": len(plugins),
    }


@router.get("/{plugin_name}")
async def get_plugin(
    plugin_name: str,
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    Get details of a specific plugin.
    """
    plugin = PluginManager.get_plugin(plugin_name)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_name}' not found",
        )

    return plugin


@router.put("/{plugin_name}/config")
async def update_plugin_config(
    plugin_name: str,
    config: Dict[str, Any],
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Update plugin configuration. Admin only.
    """
    success = PluginManager.update_plugin_config(plugin_name, config)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_name}' not found or config update failed",
        )

    logger.info(f"User {current_user.email} updated config for plugin: {plugin_name}")

    return {
        "success": True,
        "plugin": plugin_name,
        "config": config,
    }


@router.post("/{plugin_name}/test")
async def test_plugin(
    plugin_name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> Dict[str, Any]:
    """
    Test if a plugin is working. Admin only.
    """
    result = PluginManager.test_plugin(plugin_name)
    return result


@router.get("/{plugin_name}/routing")
async def get_plugin_routing(
    plugin_name: str,
    current_user: User = Depends(require_role(UserRole.VIEWER)),
) -> Dict[str, Any]:
    """
    Get routing configuration for a plugin.
    """
    plugin = PluginManager.get_plugin(plugin_name)

    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin '{plugin_name}' not found",
        )

    return {
        "plugin": plugin_name,
        "routing_keywords": plugin.get("routing_keywords", {}),
        "escalation_triggers": plugin.get("escalation_triggers", []),
    }
