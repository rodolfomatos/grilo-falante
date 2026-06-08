"""
MemPalace Service - Integration with MemPalace memory system

MemPalace provides:
- Verbatim storage (opposite of GF's transformation)
- Semantic search with ChromaDB
- Knowledge graph with temporal entity-relationships
- MCP server for agent access

This service integrates MemPalace as a secondary storage layer:
- GF transforms and governs (primary)
- MemPalace stores verbatim (secondary)

See: docs/shadow_documents/SHADOW_MEMPALACE_INTEGRATION_v1.md
"""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MemPalaceService:
    """
    Service for integrating with MemPalace.

    MemPalace is a CLI tool, so we use subprocess to interact with it.
    """

    def __init__(self, enabled: bool = False, palace_path: Optional[str] = None):
        """
        Initialize MemPalace service.

        Args:
            enabled: Whether MemPalace integration is enabled
            palace_path: Path to MemPalace data directory
        """
        self.enabled = enabled
        self._palace_path = palace_path
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize MemPalace storage.

        Returns:
            True if successful
        """
        if not self.enabled:
            logger.info("MemPalace integration disabled")
            return True

        if self._initialized:
            return True

        try:
            # Check if mempalace CLI is available
            result = subprocess.run(
                ["mcp", "__version__"] if False else ["mempalace", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                logger.warning("MemPalace CLI not found or not functional")
                self.enabled = False
                return False

            # MemPalace CLI is available
            # Note: Initialization should be done manually via `mempalace init <path>`
            # We don't call init via subprocess because it's interactive
            if self._palace_path:
                os.makedirs(self._palace_path, exist_ok=True)
                logger.info(f"MemPalace path set to {self._palace_path}")
                logger.info("Run 'mempalace init <path>' manually if needed")

            self._initialized = True
            return True

        except FileNotFoundError:
            logger.warning("MemPalace CLI not found in PATH")
            self.enabled = False
            return False
        except subprocess.TimeoutExpired:
            logger.warning("MemPalace CLI check timed out")
            self.enabled = False
            return False
        except Exception as e:
            logger.error(f"Failed to initialize MemPalace: {e}")
            self.enabled = False
            return False

    def store_memory(
        self,
        content: str,
        room: str,
        hall: str = "discoveries",
        wing: Optional[str] = None,
    ) -> bool:
        """
        Store a memory in MemPalace.

        Note: MemPalace CLI is primarily interactive. This is a placeholder
        for future integration when MemPalace exposes a proper API.

        Args:
            content: The verbatim content to store
            room: Room name (e.g., "pedra_123", "ilha_456")
            hall: Hall category (facts, events, discoveries, preferences, advice)
            wing: Wing name (defaults to "grilo_falante")

        Returns:
            True if successful (currently always returns False - placeholder)
        """
        if not self.enabled or not self._initialized:
            return False

        # MemPalace CLI is interactive - placeholder for future API integration
        # TODO: Implement when MemPalace exposes non-interactive API
        logger.debug(f"MemPalace store_memory called (placeholder): room={room}, hall={hall}")
        return False

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories in MemPalace.

        Note: MemPalace CLI is primarily interactive. This is a placeholder
        for future integration when MemPalace exposes a proper API.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of matching memories (currently empty - placeholder)
        """
        if not self.enabled or not self._initialized:
            return []

        # MemPalace CLI is interactive - placeholder for future API integration
        # TODO: Implement when MemPalace exposes non-interactive API
        logger.debug(f"MemPalace search called (placeholder): query={query}")
        return []

    def store_ilha(self, ilha: Dict[str, Any]) -> bool:
        """
        Store an ILHA's content in MemPalace.

        Args:
            ilha: ILHA dictionary

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        wing = f"ilha_{ilha['id']}"
        success = True

        # Store topic as room
        self.store_memory(
            content=f"ILHA: {ilha['title']}\nTopic: {ilha['topic']}\nTimestamp: {ilha['timestamp']}",
            room=f"ilha_{ilha['id']}",
            hall="discoveries",
            wing=wing,
        )

        # Store each pedra
        for pedra in ilha.get("pedras", []):
            content = pedra.get("content_summary") or pedra.get("content", "")
            if content:
                room_name = f"pedra_{pedra['id']}"
                success = self.store_memory(
                    content=content,
                    room=room_name,
                    hall=self._get_hall_for_type(pedra.get("type", "claim")),
                    wing=wing,
                ) and success

        return success

    def store_pedra(
        self,
        pedra: Dict[str, Any],
       ilha_id: Optional[str] = None,
    ) -> bool:
        """
        Store a PEDRA's content in MemPalace.

        Args:
            pedra: PEDRA dictionary
            ilha_id: Optional ILHA ID for wing naming

        Returns:
            True if successful
        """
        if not self.enabled:
            return False

        wing = f"ilha_{ilha_id}" if ilha_id else "grilo_falante"
        room = f"pedra_{pedra['id']}"

        content = pedra.get("content_summary") or pedra.get("content", "")
        if not content:
            return True  # Nothing to store

        return self.store_memory(
            content=content,
            room=room,
            hall=self._get_hall_for_type(pedra.get("type", "claim")),
            wing=wing,
        )

    def _get_hall_for_type(self, pedra_type: str) -> str:
        """Map PEDRA type to MemPalace hall."""
        hall_map = {
            "claim": "facts",
            "question": "advice",
            "reaction": "preferences",
            "gap": "discoveries",
            "concept": "discoveries",
            "process": "events",
            "reference": "facts",
        }
        return hall_map.get(pedra_type, "discoveries")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get MemPalace statistics.

        Returns:
            Dictionary with stats
        """
        if not self.enabled:
            return {"enabled": False}

        try:
            result = subprocess.run(
                ["mempalace", "status"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return {
                    "enabled": True,
                    "initialized": self._initialized,
                    "palace_path": self._palace_path,
                    "status": result.stdout.strip(),
                }
            return {"enabled": True, "error": result.stderr}

        except Exception as e:
            return {"enabled": False, "error": str(e)}


# Global instance
_mempalace_service: Optional[MemPalaceService] = None


def get_mempalace_service() -> MemPalaceService:
    """Get or create the global MemPalace service instance."""
    global _mempalace_service
    if _mempalace_service is None:
        _mempalace_service = MemPalaceService(
            enabled=False,  # Disabled by default
        )
    return _mempalace_service


def enable_mempalace(palace_path: Optional[str] = None) -> bool:
    """
    Enable MemPalace integration.

    Args:
        palace_path: Optional path to MemPalace data directory

    Returns:
        True if successful
    """
    service = get_mempalace_service()
    service.enabled = True
    if palace_path:
        service._palace_path = palace_path
    return service.initialize()
