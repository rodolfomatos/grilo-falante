"""
Concept Registry - Tracks all concepts and their shadow documentation status.

The registry maintains:
- All concepts mentioned in the system
- Their shadow documentation status (Shadow Score)
- Shadow Debt (undocumented concepts)
- Links to shadow documents and FAQs
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConceptStatus(str, Enum):
    """Status of a concept in the registry."""
    UNDOCUMENTED = "undocumented"  # Mentioned but never documented
    PARTIAL = "partial"  # Has shadow doc but missing FAQ or report
    COMPLETE = "complete"  # Fully documented (shadow + FAQ + report)
    SHADOW_DEBT = "shadow_debt"  # Needs immediate documentation


@dataclass
class ConceptEntry:
    """An entry in the concept registry."""
    id: str
    name: str
    status: ConceptStatus = ConceptStatus.UNDOCUMENTED
    first_mentioned: Optional[str] = None
    last_updated: Optional[str] = None

    # Documentation links
    shadow_doc_path: Optional[str] = None
    faq_path: Optional[str] = None
    report_path: Optional[str] = None
    registry_path: Optional[str] = None

    # Related concepts
    related_concepts: List[str] = field(default_factory=list)

    # Metadata
    notes: str = ""
    priority: str = "medium"  # high, medium, low

    # Shadow Score (0-100)
    shadow_score: int = 0

    def calculate_shadow_score(self) -> int:
        """Calculate shadow score based on documentation."""
        score = 0
        if self.shadow_doc_path:
            score += 35
        if self.faq_path:
            score += 35
        if self.report_path:
            score += 30
        self.shadow_score = score
        return score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d['status'] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConceptEntry':
        """Create from dictionary."""
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = ConceptStatus(data['status'])
        return cls(**data)


class ConceptRegistry:
    """
    Central registry of all concepts in the Grilo Falante system.

    The registry tracks:
    - Concepts mentioned by users
    - Their documentation status (Shadow Score)
    - Shadow Debt (undocumented concepts)
    - Links to shadow documents and FAQs
    """

    _instance: Optional['ConceptRegistry'] = None
    _initialized: bool = False

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry."""
        if not ConceptRegistry._initialized:
            self._concepts: Dict[str, ConceptEntry] = {}
            self._registry_file: Optional[Path] = None
            ConceptRegistry._initialized = True

    def set_registry_file(self, path: Path) -> None:
        """Set the registry file path."""
        self._registry_file = path
        self.load()

    def register_concept(
        self,
        name: str,
        mentioned_by: Optional[str] = None,
        priority: str = "medium",
        notes: str = "",
    ) -> ConceptEntry:
        """
        Register a new concept or update existing one.

        Args:
            name: Name of the concept
            mentioned_by: Who mentioned it
            priority: high, medium, low
            notes: Additional notes

        Returns:
            The created or updated ConceptEntry
        """
        concept_id = self._normalize_id(name)

        if concept_id in self._concepts:
            concept = self._concepts[concept_id]
            if mentioned_by:
                concept.notes += f"\n[Mentioned by {mentioned_by} on {datetime.now().isoformat()}]"
            self.save()
            return concept

        concept = ConceptEntry(
            id=concept_id,
            name=name,
            status=ConceptStatus.UNDOCUMENTED,
            first_mentioned=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            priority=priority,
            notes=notes,
        )

        if mentioned_by:
            concept.notes = f"Mentioned by {mentioned_by} on {datetime.now().isoformat()}"

        self._concepts[concept_id] = concept
        logger.info(f"Registered concept: {name} (ID: {concept_id})")
        self.save()
        return concept

    def get_concept(self, name_or_id: str) -> Optional[ConceptEntry]:
        """Get a concept by name or ID."""
        concept_id = self._normalize_id(name_or_id)
        return self._concepts.get(concept_id)

    def update_concept(
        self,
        name_or_id: str,
        status: Optional[ConceptStatus] = None,
        shadow_doc_path: Optional[str] = None,
        faq_path: Optional[str] = None,
        report_path: Optional[str] = None,
        related_concepts: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Optional[ConceptEntry]:
        """
        Update a concept's documentation status.

        Args:
            name_or_id: Concept name or ID
            status: New status
            shadow_doc_path: Path to shadow document
            faq_path: Path to FAQ
            report_path: Path to report
            related_concepts: List of related concept IDs
            notes: Additional notes

        Returns:
            Updated ConceptEntry or None if not found
        """
        concept = self.get_concept(name_or_id)
        if not concept:
            return None

        if status:
            concept.status = status
        if shadow_doc_path:
            concept.shadow_doc_path = shadow_doc_path
        if faq_path:
            concept.faq_path = faq_path
        if report_path:
            concept.report_path = report_path
        if related_concepts:
            concept.related_concepts = related_concepts
        if notes:
            concept.notes += f"\n{notes}"

        concept.last_updated = datetime.now().isoformat()
        concept.calculate_shadow_score()

        # Update status based on score
        if concept.shadow_score == 100:
            concept.status = ConceptStatus.COMPLETE
        elif concept.shadow_score > 0:
            concept.status = ConceptStatus.PARTIAL

        self.save()
        return concept

    def list_all(self) -> List[ConceptEntry]:
        """List all concepts."""
        return list(self._concepts.values())

    def list_by_status(self, status: ConceptStatus) -> List[ConceptEntry]:
        """List concepts by status."""
        return [c for c in self._concepts.values() if c.status == status]

    def get_shadow_debt(self) -> List[ConceptEntry]:
        """Get all concepts that are shadow debt (undocumented)."""
        return [c for c in self._concepts.values() if c.status in (
            ConceptStatus.UNDOCUMENTED,
            ConceptStatus.SHADOW_DEBT,
        )]

    def get_complete(self) -> List[ConceptEntry]:
        """Get all fully documented concepts."""
        return [c for c in self._concepts.values() if c.status == ConceptStatus.COMPLETE]

    def get_partial(self) -> List[ConceptEntry]:
        """Get all partially documented concepts."""
        return [c for c in self._concepts.values() if c.status == ConceptStatus.PARTIAL]

    def get_shadow_score(self) -> Dict[str, int]:
        """Get overall shadow documentation statistics."""
        total = len(self._concepts)
        if total == 0:
            return {"total": 0, "complete": 0, "partial": 0, "undocumented": 0, "avg_score": 0}

        complete = len(self.get_complete())
        partial = len(self.get_partial())
        undocumented = len(self.get_shadow_debt())
        avg_score = sum(c.shadow_score for c in self._concepts.values()) / total

        return {
            "total": total,
            "complete": complete,
            "partial": partial,
            "undocumented": undocumented,
            "avg_score": round(avg_score, 1),
            "completeness_pct": round((complete / total) * 100, 1),
        }

    def check(self, name_or_id: str) -> Dict[str, Any]:
        """
        Check a concept's documentation status.

        Returns:
            Dict with status, score, and recommendations
        """
        concept = self.get_concept(name_or_id)

        if not concept:
            return {
                "status": "UNKNOWN",
                "concept": name_or_id,
                "registered": False,
                "recommendation": f"Concept '{name_or_id}' not in registry. Register it first.",
            }

        result = {
            "status": concept.status.value,
            "concept": concept.name,
            "id": concept.id,
            "registered": True,
            "shadow_score": concept.shadow_score,
            "last_updated": concept.last_updated,
            "shadow_doc": concept.shadow_doc_path is not None,
            "faq": concept.faq_path is not None,
            "report": concept.report_path is not None,
        }

        # Add recommendations
        if concept.status == ConceptStatus.COMPLETE:
            result["recommendation"] = "✅ Fully documented."
        elif concept.status == ConceptStatus.PARTIAL:
            missing = []
            if not concept.shadow_doc_path:
                missing.append("shadow doc")
            if not concept.faq_path:
                missing.append("FAQ")
            if not concept.report_path:
                missing.append("report")
            result["recommendation"] = f"⚠️ Partial documentation. Missing: {', '.join(missing)}"
        else:
            result["recommendation"] = f"❌ Shadow debt! Create shadow doc, FAQ, and report."

        return result

    def _normalize_id(self, name: str) -> str:
        """Normalize a concept name to an ID."""
        return name.upper().replace(" ", "_").replace("-", "_")

    def save(self) -> None:
        """Save registry to file."""
        if not self._registry_file:
            return

        data = {
            "last_saved": datetime.now().isoformat(),
            "concepts": {k: v.to_dict() for k, v in self._concepts.items()},
        }

        self._registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._registry_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Registry saved to {self._registry_file}")

    def load(self) -> None:
        """Load registry from file."""
        if not self._registry_file or not self._registry_file.exists():
            return

        with open(self._registry_file, 'r') as f:
            data = json.load(f)

        self._concepts = {}
        for k, v in data.get("concepts", {}).items():
            self._concepts[k] = ConceptEntry.from_dict(v)

        logger.info(f"Registry loaded from {self._registry_file}")

    def export_summary(self) -> str:
        """Export a summary of the registry."""
        score = self.get_shadow_score()

        lines = [
            "=" * 60,
            "SHADOW FIRST - CONCEPT REGISTRY SUMMARY",
            "=" * 60,
            "",
            f"Total concepts: {score['total']}",
            f"Complete: {score['complete']} ({score['completeness_pct']}%)",
            f"Partial: {score['partial']}",
            f"Undocumented (Shadow Debt): {score['undocumented']}",
            f"Average Shadow Score: {score['avg_score']}%",
            "",
        ]

        debt = self.get_shadow_debt()
        if debt:
            lines.append("SHADOW DEBT (needs documentation):")
            for c in debt:
                lines.append(f"  • {c.name} ({c.priority} priority)")
            lines.append("")

        complete = self.get_complete()
        if complete:
            lines.append("COMPLETE (fully documented):")
            for c in complete:
                lines.append(f"  ✅ {c.name} (score: {c.shadow_score}%)")
            lines.append("")

        return "\n".join(lines)


# Global registry instance
registry = ConceptRegistry()
