"""
GF-ID Service — Grilo Falante ID generation

Generates unique identifiers for claims in format:
GF-{YYMMDD}-{GMIF}-{HASH}
"""

import hashlib
from datetime import datetime


class GFIDService:
    """
    Service for generating GF-IDs.

    Format: GF-{YYMMDD}-{GMIF}-{HASH}
    - YYMMDD: Date of creation
    - GMIF: GMIF level (M1-M8)
    - HASH: First 6 chars of MD5 hash of content
    """

    @staticmethod
    def generate(
        content: str,
        gmif_level: str,
        suffix: str = "",
    ) -> str:
        """
        Generate a GF-ID.

        Args:
            content: The claim text or content to hash
            gmif_level: The GMIF level (M1-M8)
            suffix: Optional suffix for disambiguation

        Returns:
            GF-ID string in format GF-{YYMMDD}-{GMIF}-{HASH}
        """
        date_str = datetime.utcnow().strftime("%y%m%d")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:6]
        suffix_str = f"-{suffix}" if suffix else ""
        return f"GF-{date_str}-{gmif_level}-{content_hash}{suffix_str}"

    @staticmethod
    def parse(gfid: str) -> dict:
        """
        Parse a GF-ID into components.

        Args:
            gfid: GF-ID string

        Returns:
            Dict with date, gmif_level, hash, and suffix
        """
        parts = gfid.split("-")
        if len(parts) != 4 or parts[0] != "GF":
            raise ValueError(f"Invalid GF-ID format: {gfid}")

        return {
            "prefix": "GF",
            "date": parts[1],
            "gmif_level": parts[2],
            "hash": parts[3],
        }

    @staticmethod
    def is_valid(gfid: str) -> bool:
        """
        Check if a GF-ID is valid.

        Args:
            gfid: GF-ID string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = GFIDService.parse(gfid)
            if len(parsed["date"]) != 6:
                return False
            if not parsed["gmif_level"].startswith("M"):
                return False
            if len(parsed["hash"]) < 4:
                return False
            return True
        except (ValueError, IndexError):
            return False
