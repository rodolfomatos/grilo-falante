"""
ILHAS Router - Context Memory System

Provides endpoints for:
- ILHA CRUD (memory moments)
- Logbook navigation
- Pedra management
- NTP timestamp synchronization
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from grilo_admin.auth import get_current_user
from grilo_admin.models import (
    ILHA,
    ILHACreate,
    ILHAUpdate,
    ILHAFromConversation,
    Participant,
    Pedra,
    PedraType,
    InteractionType,
    LogbookEntry,
    ConversationMessage,
    GmifEvent,
    ShadowDocument,
    DigitalObject,
    User,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ilhas", tags=["ilhas"])
router2 = APIRouter(prefix="/logbook", tags=["logbook"])


class ILHAManager:
    """Manages ILHAS (memory moments)."""

    _ilhas: Dict[str, Dict[str, Any]] = {}
    _pedras: Dict[str, Dict[str, Any]] = {}
    _initialized = False

    @classmethod
    def _get_default_storage_path(cls) -> str:
        """Get default storage path relative to module location."""
        import os
        module_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(module_dir, "data", "ilhas.json")

    _storage_path: str = None  # Lazy initialization

    @classmethod
    def _get_storage_path(cls) -> str:
        """Get storage path, initializing if needed."""
        if cls._storage_path is None:
            cls._storage_path = cls._get_default_storage_path()
        return cls._storage_path

    @classmethod
    def initialize(cls):
        """Initialize storage and load from disk if available."""
        if not cls._initialized:
            cls._initialized = True
            cls._ensure_storage_dir()
            cls.load()

    @classmethod
    def _ensure_storage_dir(cls):
        """Ensure storage directory exists."""
        import os
        storage_dir = os.path.dirname(cls._get_storage_path())
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir, exist_ok=True)

    @classmethod
    def set_storage_path(cls, path: str):
        """Set the storage file path."""
        cls._storage_path = path
        cls._ensure_storage_dir()

    @classmethod
    def save(cls):
        """Save ILHAs and PEDRAs to disk."""
        import json
        cls._ensure_storage_dir()
        storage_path = cls._get_storage_path()
        data = {
            "ilhas": cls._ilhas,
            "pedras": cls._pedras,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Saved {len(cls._ilhas)} ILHAs and {len(cls._pedras)} PEDRAs to {storage_path}")

    @classmethod
    def load(cls):
        """Load ILHAs and PEDRAs from disk."""
        import json
        import os
        storage_path = cls._get_storage_path()
        if not os.path.exists(storage_path):
            logger.info(f"No existing storage at {storage_path}, starting fresh")
            return

        try:
            with open(storage_path, 'r') as f:
                data = json.load(f)
            cls._ilhas = data.get("ilhas", {})
            cls._pedras = data.get("pedras", {})
            logger.info(f"Loaded {len(cls._ilhas)} ILHAs and {len(cls._pedras)} PEDRAs from {storage_path}")
        except Exception as e:
            logger.error(f"Error loading ILHAs: {e}")

    @classmethod
    def _get_ntp_time(cls) -> float:
        """Get current time as Unix timestamp."""
        return time.time()

    @classmethod
    def create_ilha(cls, data: ILHACreate) -> ILHA:
        """Create a new ILHA."""
        cls.initialize()

        ntp_time = cls._get_ntp_time()
        now = datetime.now(timezone.utc)

        participants = [
            Participant(name=p["name"], role=p.get("role", "participant"), type=p.get("type", "ai"))
            for p in data.participants
        ]

        title = data.title or f"{data.interaction_type.value}: {data.topic}"

        ilha_dict = {
            "id": f"ILHA-{now.strftime('%Y%m%d-%H%M%S')}",
            "timestamp": now.isoformat(),
            "ntp_timestamp": ntp_time,
            "participants": [p.model_dump() for p in participants],
            "topic": data.topic,
            "topic_summary": None,
            "interaction_type": data.interaction_type.value,
            "pedras": [],
            "claims_count": 0,
            "gaps_count": 0,
            "questions_count": 0,
            "gmif_summary": {"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0},
            "reused_pedras": [],
            "is_processed": False,
            "processed_at": None,
            "title": title,
        }

        cls._ilhas[ilha_dict["id"]] = ilha_dict
        cls.save()
        logger.info(f"Created ILHA: {ilha_dict['id']} ({title})")
        return cls._dict_to_ilha(ilha_dict)

    @classmethod
    def create_from_conversation(cls, data: ILHAFromConversation) -> ILHA:
        """Create an ILHA from an AI-to-AI conversation."""
        cls.initialize()

        ntp_time = cls._get_ntp_time()
        now = datetime.now(timezone.utc)

        participants = []
        for msg in data.messages:
            name = msg.participant
            if not any(p["name"] == name for p in participants):
                participants.append(Participant(
                    name=name,
                    role="ai" if "MOCK" not in msg.content else "ai",
                    type="ai"
                ))

        title = f"AI-to-AI: {data.topic}"
        ilha_id = f"ILHA-{now.strftime('%Y%m%d-%H%M%S')}"

        pedras = []
        gmif_counts = {"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0}

        for msg in data.messages:
            for claim_text in msg.claims_extracted:
                pedra_id = f"PEDRA-{len(cls._pedras) + 1:05d}"
                gmif = "M3"

                pedra_dict = {
                    "id": pedra_id,
                    "ilha_id": ilha_id,
                    "author_id": "unknown",
                    "author_name": msg.participant,
                    "content": claim_text,
                    "gmif_level": gmif,
                    "type": "claim",
                    "is_gap": False,
                    "gap_question": None,
                    "reused_in": [],
                    "created_at": now.isoformat(),
                }
                cls._pedras[pedra_id] = pedra_dict
                pedras.append(pedra_dict)
                gmif_counts[gmif] += 1

            for gap_text in msg.gaps_extracted:
                pedra_id = f"PEDRA-{len(cls._pedras) + 1:05d}"
                pedra_dict = {
                    "id": pedra_id,
                    "ilha_id": ilha_id,
                    "author_id": "unknown",
                    "author_name": msg.participant,
                    "content": gap_text,
                    "gmif_level": "M3",
                    "type": "gap",
                    "is_gap": True,
                    "gap_question": gap_text,
                    "reused_in": [],
                    "created_at": now.isoformat(),
                }
                cls._pedras[pedra_id] = pedra_dict
                pedras.append(pedra_dict)

        claims_count = sum(1 for p in pedras if p["type"] == "claim")
        gaps_count = sum(1 for p in pedras if p["type"] == "gap")

        ilha_dict = {
            "id": ilha_id,
            "timestamp": now.isoformat(),
            "ntp_timestamp": ntp_time,
            "participants": [p.model_dump() for p in participants],
            "topic": data.topic,
            "topic_summary": None,
            "interaction_type": InteractionType.AI_TO_AI.value,
            "pedras": pedras,
            "claims_count": claims_count,
            "gaps_count": gaps_count,
            "questions_count": gaps_count,
            "gmif_summary": gmif_counts,
            "reused_pedras": [],
            "is_processed": False,
            "processed_at": None,
            "title": title,
        }

        cls._ilhas[ilha_id] = ilha_dict
        cls.save()
        logger.info(f"Created ILHA from conversation: {ilha_id} ({len(pedras)} pedras)")
        return cls._dict_to_ilha(ilha_dict)

    @classmethod
    def get_ilha(cls, ilha_id: str) -> Optional[ILHA]:
        """Get an ILHA by ID."""
        ilha_dict = cls._ilhas.get(ilha_id)
        if ilha_dict:
            return cls._dict_to_ilha(ilha_dict)
        return None

    @classmethod
    def list_ilhas(
        cls,
        limit: int = 50,
        topic: Optional[str] = None,
        interaction_type: Optional[str] = None,
    ) -> List[ILHA]:
        """List all ILHAS."""
        result = []
        for ilha_dict in cls._ilhas.values():
            if topic and topic.lower() not in ilha_dict.get("topic", "").lower():
                continue
            if interaction_type and ilha_dict.get("interaction_type") != interaction_type:
                continue
            result.append(cls._dict_to_ilha(ilha_dict))

        result.sort(key=lambda x: x.timestamp, reverse=True)
        return result[:limit]

    @classmethod
    def get_logbook(cls, limit: int = 50) -> List[LogbookEntry]:
        """Get logbook entries (ILHAS as logbook entries)."""
        entries = []
        for ilha_dict in cls._ilhas.values():
            entry = LogbookEntry(
                id=ilha_dict["id"],
                timestamp=ilha_dict["timestamp"],
                title=ilha_dict.get("title", ""),
                topic=ilha_dict.get("topic", ""),
                interaction_type=ilha_dict.get("interaction_type", ""),
                participants=[p["name"] for p in ilha_dict.get("participants", [])],
                pedras_count=len(ilha_dict.get("pedras", [])),
                claims_count=ilha_dict.get("claims_count", 0),
                gaps_count=ilha_dict.get("gaps_count", 0),
                gmif_summary=ilha_dict.get("gmif_summary", {}),
                is_processed=ilha_dict.get("is_processed", False),
            )
            entries.append(entry)

        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries[:limit]

    @classmethod
    def get_pedra(cls, pedra_id: str) -> Optional[Pedra]:
        """Get a pedra by ID."""
        pedra_dict = cls._pedras.get(pedra_id)
        if pedra_dict:
            return cls._dict_to_pedra(pedra_dict)
        return None

    @classmethod
    def reuse_pedra(cls, pedra_id: str, target_ilha_id: str) -> bool:
        """Reuse a pedra in another ILHA."""
        pedra_dict = cls._pedras.get(pedra_id)
        target_ilha = cls._ilhas.get(target_ilha_id)

        if not pedra_dict or not target_ilha:
            return False

        if target_ilha_id not in pedra_dict["reused_in"]:
            pedra_dict["reused_in"].append(target_ilha_id)

        if pedra_id not in target_ilha.get("reused_pedras", []):
            target_ilha.setdefault("reused_pedras", []).append(pedra_id)

        cls.save()
        logger.info(f"Pedra {pedra_id} reused in ILHA {target_ilha_id}")
        return True

    @classmethod
    def update_ilha(cls, ilha_id: str, updates: ILHAUpdate) -> Optional[ILHA]:
        """Update an ILHA."""
        ilha_dict = cls._ilhas.get(ilha_id)
        if not ilha_dict:
            return None

        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                ilha_dict[key] = value

        if updates.is_processed and not ilha_dict.get("is_processed"):
            ilha_dict["is_processed"] = True
            ilha_dict["processed_at"] = datetime.now(timezone.utc).isoformat()

        cls._ilhas[ilha_id] = ilha_dict
        cls.save()
        return cls._dict_to_ilha(ilha_dict)

    @classmethod
    def _dict_to_ilha(cls, d: Dict[str, Any]) -> ILHA:
        """Convert dict to ILHA."""
        participants = [Participant(**p) for p in d.get("participants", [])]
        pedras = [cls._dict_to_pedra(p) for p in d.get("pedras", [])]

        return ILHA(
            id=d["id"],
            timestamp=d["timestamp"],
            ntp_timestamp=d.get("ntp_timestamp"),
            participants=participants,
            topic=d.get("topic", ""),
            topic_summary=d.get("topic_summary"),
            interaction_type=InteractionType(d.get("interaction_type", "unknown")),
            pedras=pedras,
            claims_count=d.get("claims_count", 0),
            gaps_count=d.get("gaps_count", 0),
            questions_count=d.get("questions_count", 0),
            gmif_summary=d.get("gmif_summary", {}),
            reused_pedras=d.get("reused_pedras", []),
            is_processed=d.get("is_processed", False),
            processed_at=d.get("processed_at"),
            title=d.get("title", ""),
        )

    @classmethod
    def _dict_to_pedra(cls, d: Dict[str, Any]) -> Pedra:
        """Convert dict to Pedra."""
        # Handle new fields with backward compatibility
        content = d.get("content", "")  # Legacy field
        content_summary = d.get("content_summary", content)

        # Handle gmif_events
        gmif_events = []
        for event in d.get("gmif_events", []):
            if isinstance(event, dict):
                gmif_events.append(GmifEvent(**event))
            else:
                gmif_events.append(event)

        # Handle shadow_documents
        shadow_documents = []
        for sd in d.get("shadow_documents", []):
            if isinstance(sd, dict):
                shadow_documents.append(ShadowDocument(**sd))
            else:
                shadow_documents.append(sd)

        # Handle digital_objects
        digital_objects = []
        for do in d.get("digital_objects", []):
            if isinstance(do, dict):
                digital_objects.append(DigitalObject(**do))
            else:
                digital_objects.append(do)

        return Pedra(
            id=d["id"],
            ilha_id=d["ilha_id"],
            started_at=d.get("started_at", d.get("created_at", "")),
            ended_at=d.get("ended_at"),
            author_id=d.get("author_id", ""),
            author_name=d.get("author_name", ""),
            content_summary=content_summary or content,
            shadow_documents=shadow_documents,
            digital_objects=digital_objects,
            is_empty=d.get("is_empty", len(shadow_documents) == 0 and len(digital_objects) == 0 and not content_summary),
            gmif_events=gmif_events,
            gmif_level=d.get("gmif_level", "M3"),
            type=PedraType(d.get("type", "claim")) if d.get("type") else PedraType.CLAIM,
            is_gap=d.get("is_gap", False),
            gap_question=d.get("gap_question"),
            saliencia=d.get("saliencia", 0.5),
            consequence_level=d.get("consequence_level", 0.0),
            decay_enabled=d.get("decay_enabled", True),
            reused_in=d.get("reused_in", []),
            created_at=d.get("created_at", ""),
        )


@router.post("", response_model=ILHA, status_code=status.HTTP_201_CREATED)
async def create_ilha(
    data: ILHACreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new ILHA.

    An ILHA represents a moment-space-time aggregate of context.
    Think of it like a party - the party is a moment (ILHA),
    and each guest has their perspective (pedras).
    """
    return ILHAManager.create_ilha(data)


@router.post("/from-conversation", response_model=ILHA, status_code=status.HTTP_201_CREATED)
async def create_from_conversation(
    data: ILHAFromConversation,
    current_user: User = Depends(get_current_user),
):
    """
    Create an ILHA from an AI-to-AI conversation.

    This is called automatically after an AI-to-AI conversation
    to persist the memory moment with all pedras.
    """
    return ILHAManager.create_from_conversation(data)


@router.get("", response_model=List[ILHA])
async def list_ilhas(
    limit: int = 50,
    topic: Optional[str] = None,
    interaction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    List all ILHAS.

    Filters:
    - topic: Filter by topic (partial match)
    - interaction_type: ai_to_ai, ai_to_human, human_to_human
    """
    return ILHAManager.list_ilhas(limit=limit, topic=topic, interaction_type=interaction_type)


@router.get("/logbook", response_model=List[LogbookEntry])
async def get_logbook(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """
    Get logbook entries.

    The logbook is a chronological view of all ILHAS,
    like a diary or journal.
    """
    return ILHAManager.get_logbook(limit=limit)


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
):
    """Get ILHA system statistics."""
    total_ilhas = len(ILHAManager._ilhas)
    total_pedras = len(ILHAManager._pedras)
    total_reused = sum(len(p.get("reused_in", [])) for p in ILHAManager._pedras.values())

    by_type = {}
    for ilha_dict in ILHAManager._ilhas.values():
        itype = ilha_dict.get("interaction_type", "unknown")
        by_type[itype] = by_type.get(itype, 0) + 1

    return {
        "total_ilhas": total_ilhas,
        "total_pedras": total_pedras,
        "total_reused_pedras": total_reused,
        "by_interaction_type": by_type,
    }


@router.get("/{ilha_id}", response_model=ILHA)
async def get_ilha(
    ilha_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get an ILHA by ID."""
    ilha = ILHAManager.get_ilha(ilha_id)
    if not ilha:
        raise HTTPException(status_code=404, detail=f"ILHA '{ilha_id}' not found")
    return ilha


@router.put("/{ilha_id}", response_model=ILHA)
async def update_ilha(
    ilha_id: str,
    updates: ILHAUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update an ILHA."""
    ilha = ILHAManager.update_ilha(ilha_id, updates)
    if not ilha:
        raise HTTPException(status_code=404, detail=f"ILHA '{ilha_id}' not found")
    return ilha


@router.get("/{ilha_id}/pedras")
async def get_ilha_pedras(
    ilha_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all pedras in an ILHA."""
    ilha = ILHAManager.get_ilha(ilha_id)
    if not ilha:
        raise HTTPException(status_code=404, detail=f"ILHA '{ilha_id}' not found")
    return {
        "ilha_id": ilha_id,
        "pedras": ilha.pedras,
        "pedras_count": len(ilha.pedras),
    }


@router.post("/{ilha_id}/pedras/{pedra_id}/reuse")
async def reuse_pedra(
    ilha_id: str,
    pedra_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Reuse a pedra in another ILHA.

    This simulates the "travel" of a context to another moment.
    """
    success = ILHAManager.reuse_pedra(pedra_id, ilha_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"ILHA '{ilha_id}' or Pedra '{pedra_id}' not found"
        )
    return {"success": True, "message": f"Pedra {pedra_id} reused in {ilha_id}"}


@router.get("/pedras/{pedra_id}", response_model=Pedra)
async def get_pedra(
    pedra_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a pedra by ID."""
    pedra = ILHAManager.get_pedra(pedra_id)
    if not pedra:
        raise HTTPException(status_code=404, detail=f"Pedra '{pedra_id}' not found")
    return pedra