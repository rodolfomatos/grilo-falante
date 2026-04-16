"""
Escalation Router - Escalation queue management.

Provides administrative functions for:
- Managing escalation queue
- Assigning escalations to operators
- Tracking resolution status
- Escalation statistics
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user, require_role
from grilo_admin.models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/escalations", tags=["escalations"])


class EscalationStatus(str, Enum):
    """Escalation status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EscalationPriority(str, Enum):
    """Escalation priority."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EscalationManager:
    """Manages escalation queue."""

    _escalations: Dict[str, Dict[str, Any]] = {}
    _history: List[Dict[str, Any]] = []

    @classmethod
    def reset(cls):
        """Reset all escalations (for testing)."""
        cls._escalations = {}
        cls._history = []

    @classmethod
    def create_escalation(
        cls,
        session_id: str,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        priority: EscalationPriority = EscalationPriority.MEDIUM,
        triggered_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new escalation.

        Escalations are created when:
        - User requests human assistance
        - Confidence is below threshold
        - Topic is out of scope
        - Error occurs during processing
        """
        escalation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        escalation = {
            "id": escalation_id,
            "session_id": session_id,
            "user_query": user_query,
            "context": context or {},
            "priority": priority.value,
            "status": EscalationStatus.PENDING.value,
            "assigned_to": None,
            "assigned_at": None,
            "triggered_by": triggered_by,
            "resolution_notes": None,
            "resolved_at": None,
            "created_at": now,
            "updated_at": now,
        }

        cls._escalations[escalation_id] = escalation

        cls._add_history({
            "escalation_id": escalation_id,
            "action": "created",
            "timestamp": now,
        })

        logger.info(f"Created escalation: {escalation_id} (priority: {priority.value})")
        return escalation

    @classmethod
    def get_escalation(cls, escalation_id: str) -> Optional[Dict[str, Any]]:
        """Get an escalation by ID."""
        return cls._escalations.get(escalation_id)

    @classmethod
    def list_escalations(
        cls,
        status: Optional[EscalationStatus] = None,
        priority: Optional[EscalationPriority] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List escalations with optional filters."""
        result = list(cls._escalations.values())

        if status:
            result = [e for e in result if e["status"] == status.value]

        if priority:
            result = [e for e in result if e["priority"] == priority.value]

        if assigned_to:
            result = [e for e in result if e["assigned_to"] == assigned_to]

        return sorted(result, key=lambda x: x["created_at"], reverse=True)[:limit]

    @classmethod
    def get_pending_escalations(cls) -> List[Dict[str, Any]]:
        """Get all pending escalations."""
        return cls.list_escalations(status=EscalationStatus.PENDING)

    @classmethod
    def assign_escalation(
        cls,
        escalation_id: str,
        operator_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Assign an escalation to an operator."""
        escalation = cls._escalations.get(escalation_id)
        if not escalation:
            return None

        now = datetime.now().isoformat()

        escalation["assigned_to"] = operator_id
        escalation["assigned_at"] = now
        escalation["status"] = EscalationStatus.ASSIGNED.value
        escalation["updated_at"] = now

        cls._add_history({
            "escalation_id": escalation_id,
            "action": "assigned",
            "operator_id": operator_id,
            "timestamp": now,
        })

        logger.info(f"Escalation {escalation_id} assigned to {operator_id}")
        return escalation

    @classmethod
    def update_status(
        cls,
        escalation_id: str,
        new_status: EscalationStatus,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update escalation status."""
        escalation = cls._escalations.get(escalation_id)
        if not escalation:
            return None

        now = datetime.now().isoformat()

        old_status = escalation["status"]
        escalation["status"] = new_status.value
        escalation["updated_at"] = now

        if notes:
            escalation["resolution_notes"] = notes

        if new_status == EscalationStatus.RESOLVED:
            escalation["resolved_at"] = now

        cls._add_history({
            "escalation_id": escalation_id,
            "action": "status_changed",
            "from": old_status,
            "to": new_status.value,
            "timestamp": now,
        })

        logger.info(f"Escalation {escalation_id} status: {old_status} -> {new_status.value}")
        return escalation

    @classmethod
    def resolve_escalation(
        cls,
        escalation_id: str,
        resolution_notes: str,
        update_knowledge_base: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Mark an escalation as resolved."""
        escalation = cls._escalations.get(escalation_id)
        if not escalation:
            return None

        now = datetime.now().isoformat()

        escalation["status"] = EscalationStatus.RESOLVED.value
        escalation["resolution_notes"] = resolution_notes
        escalation["resolved_at"] = now
        escalation["updated_at"] = now

        if update_knowledge_base:
            escalation["knowledge_base_updated"] = True

        cls._add_history({
            "escalation_id": escalation_id,
            "action": "resolved",
            "timestamp": now,
        })

        logger.info(f"Escalation {escalation_id} resolved")
        return escalation

    @classmethod
    def close_escalation(
        cls,
        escalation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Close an escalation (after resolution)."""
        return cls.update_status(escalation_id, EscalationStatus.CLOSED)

    @classmethod
    def delete_escalation(cls, escalation_id: str) -> bool:
        """Delete an escalation."""
        if escalation_id in cls._escalations:
            del cls._escalations[escalation_id]
            return True
        return False

    @classmethod
    def get_history(cls, escalation_id: str) -> List[Dict[str, Any]]:
        """Get history for an escalation."""
        return [h for h in cls._history if h["escalation_id"] == escalation_id]

    @classmethod
    def _add_history(cls, entry: Dict[str, Any]):
        """Add a history entry."""
        cls._history.append(entry)

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get escalation statistics."""
        total = len(cls._escalations)
        by_status = {}
        by_priority = {}

        for escalation in cls._escalations.values():
            status = escalation["status"]
            priority = escalation["priority"]
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        pending = len(cls.get_pending_escalations())

        return {
            "total": total,
            "pending": pending,
            "by_status": by_status,
            "by_priority": by_priority,
        }


@router.get("/stats")
async def get_escalation_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Get escalation statistics.

    Returns:
    - Total escalations
    - Pending escalations
    - By status breakdown
    - By priority breakdown
    """
    return EscalationManager.get_stats()


@router.get("")
async def list_escalations(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """
    List all escalations.

    Query params:
    - status: Filter by status (pending, assigned, in_progress, resolved, closed)
    - priority: Filter by priority (low, medium, high, urgent)
    - assigned_to: Filter by operator ID
    - limit: Maximum number to return
    """
    est_status = EscalationStatus(status) if status else None
    est_priority = EscalationPriority(priority) if priority else None

    escalations = EscalationManager.list_escalations(
        status=est_status,
        priority=est_priority,
        assigned_to=assigned_to,
        limit=limit,
    )

    return {
        "total": len(escalations),
        "escalations": escalations,
    }


@router.get("/pending")
async def get_pending_escalations(
    current_user: User = Depends(get_current_user),
):
    """
    Get all pending escalations.

    These are escalations awaiting assignment.
    """
    pending = EscalationManager.get_pending_escalations()
    return {
        "total": len(pending),
        "escalations": pending,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_escalation(
    session_id: str,
    user_query: str,
    priority: str = "medium",
    triggered_by: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Create a new escalation.

    Operator or Admin role required.

    Escalations can be triggered by:
    - User requesting human assistance
    - Low confidence in response
    - Out-of-scope topic
    - Error during processing
    """
    est_priority = EscalationPriority(priority)

    escalation = EscalationManager.create_escalation(
        session_id=session_id,
        user_query=user_query,
        context=context,
        priority=est_priority,
        triggered_by=triggered_by,
    )

    return escalation


@router.get("/{escalation_id}")
async def get_escalation(
    escalation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific escalation by ID."""
    escalation = EscalationManager.get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )
    return escalation


@router.get("/{escalation_id}/history")
async def get_escalation_history(
    escalation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get the history/audit trail for an escalation."""
    escalation = EscalationManager.get_escalation(escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )

    history = EscalationManager.get_history(escalation_id)
    return {
        "escalation_id": escalation_id,
        "history": history,
    }


@router.post("/{escalation_id}/assign")
async def assign_escalation(
    escalation_id: str,
    operator_id: str,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Assign an escalation to an operator.

    Operator or Admin role required.
    """
    escalation = EscalationManager.assign_escalation(escalation_id, operator_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )
    return escalation


@router.post("/{escalation_id}/status")
async def update_escalation_status(
    escalation_id: str,
    new_status: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Update escalation status.

    Valid statuses: pending, assigned, in_progress, resolved, closed

    Operator or Admin role required.
    """
    try:
        status_enum = EscalationStatus(new_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}",
        )

    escalation = EscalationManager.update_status(escalation_id, status_enum, notes)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )
    return escalation


@router.post("/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    resolution_notes: str,
    update_knowledge_base: bool = False,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Mark an escalation as resolved.

    Operator or Admin role required.

    If update_knowledge_base is True, the resolution will be
    used to update the knowledge base to prevent similar escalations.
    """
    escalation = EscalationManager.resolve_escalation(
        escalation_id,
        resolution_notes,
        update_knowledge_base=update_knowledge_base,
    )
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )
    return escalation


@router.post("/{escalation_id}/close")
async def close_escalation(
    escalation_id: str,
    current_user: User = Depends(require_role(UserRole.OPERATOR)),
):
    """
    Close an escalation (after resolution).

    Operator or Admin role required.
    """
    escalation = EscalationManager.close_escalation(escalation_id)
    if not escalation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )
    return escalation


@router.delete("/{escalation_id}")
async def delete_escalation(
    escalation_id: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete an escalation.

    Admin role required.
    """
    deleted = EscalationManager.delete_escalation(escalation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Escalation '{escalation_id}' not found",
        )