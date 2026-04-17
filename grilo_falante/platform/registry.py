"""
Plugin Registry - Domain adapter discovery and management.

This module provides the PluginRegistry class for registering,
discovering, and managing domain adapters in the Grilo Falante platform.

Usage:
    from grilo_falante.platform.registry import PluginRegistry

    # Register a plugin
    PluginRegistry.register("tax_intelligence", TaxIntelligenceAdapter)

    # List available plugins
    plugins = PluginRegistry.list_plugins()

    # Get a plugin instance
    adapter = PluginRegistry.get("tax_intelligence")

    # Auto-discover from entry_points
    PluginRegistry.load_from_entry_points()
"""

import logging
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for domain adapters.

    Maintains a mapping of domain names to adapter classes.
    Supports manual registration and auto-discovery via entry_points.
    """

    _plugins: Dict[str, Type] = {}
    _instances: Dict[str, Any] = {}
    _entry_point_name = "grilo_falante.domain"

    @classmethod
    def register(
        cls,
        name: str,
        adapter_class: Type,
        overwrite: bool = False,
    ) -> None:
        """
        Register a domain adapter class.

        Args:
            name: Unique identifier for the domain (e.g., "tax_intelligence")
            adapter_class: The adapter class (must inherit from DomainAdapter)
            overwrite: If True, overwrite existing registration

        Raises:
            ValueError: If name already registered and overwrite=False
        """
        if name in cls._plugins and not overwrite:
            raise ValueError(f"Plugin '{name}' already registered. Use overwrite=True to replace.")

        cls._plugins[name] = adapter_class
        if name in cls._instances:
            del cls._instances[name]

        logger.info(f"Registered plugin: {name} ({adapter_class.__name__})")

    @classmethod
    def unregister(cls, name: str) -> bool:
        """
        Unregister a domain adapter.

        Args:
            name: Plugin name to unregister

        Returns:
            True if unregistered, False if not found
        """
        if name in cls._plugins:
            del cls._plugins[name]
            if name in cls._instances:
                del cls._instances[name]
            logger.info(f"Unregistered plugin: {name}")
            return True
        return False

    @classmethod
    def get(cls, name: str) -> Any:
        """
        Get an instance of a registered domain adapter.

        Args:
            name: Plugin name

        Returns:
            Instance of the adapter class

        Raises:
            ValueError: If plugin not found
        """
        if name not in cls._plugins:
            raise ValueError(f"Plugin '{name}' not found. Available: {cls.list_plugins()}")

        if name not in cls._instances:
            cls._instances[name] = cls._plugins[name]()

        return cls._instances[name]

    @classmethod
    def get_class(cls, name: str) -> Type:
        """
        Get the class of a registered domain adapter (without instantiating).

        Args:
            name: Plugin name

        Returns:
            The adapter class

        Raises:
            ValueError: If plugin not found
        """
        if name not in cls._plugins:
            raise ValueError(f"Plugin '{name}' not found")
        return cls._plugins[name]

    @classmethod
    def list_plugins(cls) -> List[str]:
        """
        List all registered plugin names.

        Returns:
            List of plugin names
        """
        return list(cls._plugins.keys())

    @classmethod
    def list_active_plugins(cls) -> List[str]:
        """
        List all plugins with ACTIVE status.

        Returns:
            List of active plugin names
        """
        active = []
        for name in cls._plugins:
            try:
                adapter = cls.get(name)
                if adapter.get_metadata().status.value == "active":
                    active.append(name)
            except Exception as e:
                logger.warning(f"Could not get status for {name}: {e}")
        return active

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if a plugin is registered.

        Args:
            name: Plugin name

        Returns:
            True if registered
        """
        return name in cls._plugins

    @classmethod
    def load_from_entry_points(cls) -> int:
        """
        Auto-discover and register plugins via Python entry_points.

        Looks for packages that define 'grilo_falante.domain' entry_point
        pointing to a DomainAdapter subclass.

        Returns:
            Number of plugins loaded

        Example entry_points in setup.py/pyproject.toml:
            entry_points = {
                "grilo_falante.domain": [
                    "tax_intelligence = grilo_tax:TaxIntelligenceAdapter",
                    "student_support = grilo_student:StudentSupportAdapter",
                ]
            }
        """
        loaded = 0

        try:
            from importlib.metadata import entry_points
        except ImportError:
            from importlib_metadata import entry_points

        try:
            eps = entry_points()
        except TypeError:
            eps = entry_points().get(cls._entry_point_name, [])

        for ep in eps:
            try:
                adapter_class = ep.load()
                cls.register(ep.name, adapter_class)
                loaded += 1
            except Exception as e:
                logger.error(f"Failed to load plugin '{ep.name}': {e}")

        if loaded > 0:
            logger.info(f"Loaded {loaded} plugins from entry_points")

        return loaded

    @classmethod
    def load_from_directory(cls, directory: str) -> int:
        """
        Load plugins from a directory of Python modules.

        Looks for modules that define a DomainAdapter subclass.

        Args:
            directory: Path to directory containing plugin modules

        Returns:
            Number of plugins loaded
        """
        import importlib.util
        import os
        import sys

        loaded = 0
        sys.path.insert(0, directory)

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        module_name,
                        os.path.join(directory, filename),
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, DomainAdapter)
                            and attr is not DomainAdapter
                        ):
                            cls.register(module_name, attr)
                            loaded += 1

                except Exception as e:
                    logger.error(f"Failed to load plugin from {filename}: {e}")

        return loaded

    @classmethod
    def get_all_routing_keywords(cls) -> Dict[str, List[str]]:
        """
        Get combined routing keywords from all active plugins.

        Returns:
            Dict mapping plugin_name to routing keywords
        """
        routing = {}
        for name in cls.list_active_plugins():
            try:
                adapter = cls.get(name)
                routing[name] = adapter.get_routing_config()
            except Exception as e:
                logger.warning(f"Could not get routing for {name}: {e}")
        return routing

    @classmethod
    def get_all_escalation_triggers(cls) -> List[str]:
        """
        Get combined escalation triggers from all active plugins.

        Returns:
            List of unique escalation trigger keywords
        """
        triggers = set()
        for name in cls.list_active_plugins():
            try:
                adapter = cls.get(name)
                triggers.update(adapter.get_escalation_triggers())
            except Exception as e:
                logger.warning(f"Could not get triggers for {name}: {e}")
        return list(triggers)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered plugins (mainly for testing)."""
        cls._plugins.clear()
        cls._instances.clear()


class PluginNotFoundError(ValueError):
    """Raised when a plugin is not found in the registry."""

    pass


class PluginRegistrationError(ValueError):
    """Raised when plugin registration fails."""

    pass
