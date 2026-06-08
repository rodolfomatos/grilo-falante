"""
Kanban Epistemico — Epistemic movement tracking

Manages epistemically relevant movements across columns:
- Identified → Explored → Audited → Blocked Consciously → Consolidated → Archived

Based on Grilo Falante canonical definition.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class KanbanColumn(str, Enum):
    IDENTIFIED = "identified"
    EXPLORED = "explored"
    AUDITED = "audited"
    BLOCKED = "blocked"
    CONSOLIDATED = "consolidated"
    ARCHIVED = "archived"


class MovementType(str, Enum):
    IDEA = "idea"
    AUDIT = "audit"
    DECISION = "decision"
    PROPOSAL = "proposal"
    REJECTION = "rejection"


@dataclass
class EpistemicMovement:
    """An epistemically relevant movement tracked in the kanban."""

    id: Optional[int] = None
    movement_key: str = ""
    title: str = ""
    description: str = ""
    column: KanbanColumn = KanbanColumn.IDENTIFIED
    movement_type: MovementType = MovementType.IDEA
    author: str = "system"
    rationale: str = ""
    blockers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    result: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None


@dataclass
class KanbanState:
    """State of the Kanban board."""

    identified: List[EpistemicMovement] = field(default_factory=list)
    explored: List[EpistemicMovement] = field(default_factory=list)
    audited: List[EpistemicMovement] = field(default_factory=list)
    blocked: List[EpistemicMovement] = field(default_factory=list)
    consolidated: List[EpistemicMovement] = field(default_factory=list)
    archived: List[EpistemicMovement] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "identified": [self._movement_to_dict(m) for m in self.identified],
            "explored": [self._movement_to_dict(m) for m in self.explored],
            "audited": [self._movement_to_dict(m) for m in self.audited],
            "blocked": [self._movement_to_dict(m) for m in self.blocked],
            "consolidated": [self._movement_to_dict(m) for m in self.consolidated],
            "archived": [self._movement_to_dict(m) for m in self.archived],
        }

    def _movement_to_dict(self, m: EpistemicMovement) -> Dict[str, Any]:
        return {
            "id": m.id,
            "movement_key": m.movement_key,
            "title": m.title,
            "description": m.description,
            "type": m.movement_type.value,
            "author": m.author,
            "rationale": m.rationale,
            "blockers": m.blockers,
            "dependencies": m.dependencies,
            "result": m.result,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }


class KanbanEpistemico:
    """
    Manages epistemically relevant movements across the kanban board.

    Notes:
    - A movement can return to any column
    - "Blocked consciously" is not a failure, it's a decision
    - Nothing progresses implicitly
    """

    COLUMNS = [
        KanbanColumn.IDENTIFIED,
        KanbanColumn.EXPLORED,
        KanbanColumn.AUDITED,
        KanbanColumn.BLOCKED,
        KanbanColumn.CONSOLIDATED,
        KanbanColumn.ARCHIVED,
    ]

    def __init__(self):
        self._movements: Dict[str, EpistemicMovement] = {}
        self._counter: int = 0

    def create_movement(
        self,
        title: str,
        description: str = "",
        movement_type: MovementType = MovementType.IDEA,
        author: str = "system",
    ) -> EpistemicMovement:
        """Create a new epistemic movement."""
        self._counter += 1
        movement_key = f"move_{self._counter:04d}"

        movement = EpistemicMovement(
            movement_key=movement_key,
            title=title,
            description=description,
            movement_type=movement_type,
            author=author,
        )

        self._movements[movement_key] = movement
        return movement

    def move(
        self,
        movement_key: str,
        to_column: KanbanColumn,
        rationale: str = "",
    ) -> Optional[EpistemicMovement]:
        """
        Move an epistemic movement to a new column.

        A movement can move to any column (including backwards).
        """
        if movement_key not in self._movements:
            return None

        movement = self._movements[movement_key]
        movement.column = to_column
        movement.updated_at = datetime.utcnow()

        if rationale:
            movement.rationale = rationale

        if to_column == KanbanColumn.ARCHIVED:
            movement.archived_at = datetime.utcnow()

        return movement

    def block(
        self,
        movement_key: str,
        blockers: List[str],
        rationale: str = "",
    ) -> Optional[EpistemicMovement]:
        """Block a movement with explicit blockers."""
        if movement_key not in self._movements:
            return None

        movement = self._movements[movement_key]
        movement.column = KanbanColumn.BLOCKED
        movement.blockers = blockers
        movement.updated_at = datetime.utcnow()

        if rationale:
            movement.rationale = rationale

        return movement

    def consolidate(
        self,
        movement_key: str,
        result: str,
        rationale: str = "",
    ) -> Optional[EpistemicMovement]:
        """Consolidate a movement with a result artifact."""
        if movement_key not in self._movements:
            return None

        movement = self._movements[movement_key]
        movement.column = KanbanColumn.CONSOLIDATED
        movement.result = result
        movement.updated_at = datetime.utcnow()

        if rationale:
            movement.rationale = rationale

        return movement

    def get_state(self) -> KanbanState:
        """Get current kanban state."""
        state = KanbanState()

        for movement in self._movements.values():
            if movement.column == KanbanColumn.IDENTIFIED:
                state.identified.append(movement)
            elif movement.column == KanbanColumn.EXPLORED:
                state.explored.append(movement)
            elif movement.column == KanbanColumn.AUDITED:
                state.audited.append(movement)
            elif movement.column == KanbanColumn.BLOCKED:
                state.blocked.append(movement)
            elif movement.column == KanbanColumn.CONSOLIDATED:
                state.consolidated.append(movement)
            elif movement.column == KanbanColumn.ARCHIVED:
                state.archived.append(movement)

        return state

    def get_movement(self, movement_key: str) -> Optional[EpistemicMovement]:
        """Get a specific movement."""
        return self._movements.get(movement_key)

    def list_by_column(self, column: KanbanColumn) -> List[EpistemicMovement]:
        """List all movements in a column."""
        return [m for m in self._movements.values() if m.column == column]

    def count_by_column(self) -> Dict[str, int]:
        """Get counts per column."""
        counts = {col.value: 0 for col in KanbanColumn}
        for movement in self._movements.values():
            counts[movement.column.value] += 1
        return counts
