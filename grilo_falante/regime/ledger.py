"""
Grilo Falante Ledger — Persistent History

The ledger maintains a complete audit trail of:
- Claims made
- GF-IDs assigned
- Normative decisions (PINA)
- State transitions
- Audit results
- Regime events
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class LedgerEntryType(Enum):
    CLAIM = "CLAIM"
    NORMATIVE_CANDIDATE = "NORMATIVE_CANDIDATE"
    DIGITAL_OBJECT = "DIGITAL_OBJECT"
    AUDIT = "AUDIT"
    TRANSITION = "TRANSITION"
    PINA_DECISION = "PINA_DECISION"
    LINT_RESULT = "LINT_RESULT"
    REGIME_EVENT = "REGIME_EVENT"


@dataclass
class LedgerEntry:
    entry_id: str
    entry_type: str
    gf_id: Optional[str] = None
    content: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cycle_id: Optional[str] = None


class Ledger:
    """
    Persistent ledger for tracking all regime operations.
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or Path("ledger.json")
        if self.ledger_path.parent != Path("."):
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: list[LedgerEntry] = []
        self._load()

    def _load(self):
        """Load existing ledger from disk"""
        if self.ledger_path.exists():
            try:
                data = json.loads(self.ledger_path.read_text())
                self._entries = [LedgerEntry(**e) for e in data]
            except (json.JSONDecodeError, TypeError):
                self._entries = []

    def _save(self):
        """Save ledger to disk"""
        data = [asdict(e) for e in self._entries]
        self.ledger_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def add_entry(
        self,
        entry_type: LedgerEntryType,
        content: str = "",
        gf_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        entry_id: Optional[str] = None,
        cycle_id: Optional[str] = None
    ) -> LedgerEntry:
        """Add a new entry to the ledger"""
        if entry_id is None:
            entry_id = self._generate_entry_id(entry_type)

        entry = LedgerEntry(
            entry_id=entry_id,
            entry_type=entry_type.value,
            gf_id=gf_id,
            content=content,
            metadata=metadata or {},
            cycle_id=cycle_id
        )

        self._entries.append(entry)
        self._save()
        return entry

    def _generate_entry_id(self, entry_type: LedgerEntryType) -> str:
        """Generate a unique entry ID"""
        timestamp = datetime.now().strftime("%y%m%d%H%M%S%f")
        prefix = entry_type.value[:3].upper()
        return f"{prefix}-{timestamp}"

    def get_claims(self, cycle_id: Optional[str] = None) -> list[LedgerEntry]:
        """Get all claim entries, optionally filtered by cycle"""
        entries = [e for e in self._entries if e.entry_type == LedgerEntryType.CLAIM.value]
        if cycle_id:
            entries = [e for e in entries if e.cycle_id == cycle_id]
        return entries

    def get_nca(self) -> list[LedgerEntry]:
        """Get all normative candidate entries"""
        return [e for e in self._entries if e.entry_type == LedgerEntryType.NORMATIVE_CANDIDATE.value]

    def get_audits(self) -> list[LedgerEntry]:
        """Get all audit entries"""
        return [e for e in self._entries if e.entry_type == LedgerEntryType.AUDIT.value]

    def get_regime_events(self) -> list[LedgerEntry]:
        """Get all regime event entries"""
        return [e for e in self._entries if e.entry_type == LedgerEntryType.REGIME_EVENT.value]

    def get_transitions(self) -> list[LedgerEntry]:
        """Get all transition entries"""
        return [e for e in self._entries if e.entry_type == LedgerEntryType.TRANSITION.value]

    def search(self, query: str) -> list[LedgerEntry]:
        """Search ledger entries by content"""
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.content.lower() or query_lower in str(e.metadata).lower()
        ]

    def get_cycle_entries(self, cycle_id: str) -> list[LedgerEntry]:
        """Get all entries for a specific cycle"""
        return [e for e in self._entries if e.cycle_id == cycle_id]

    def get_stats(self) -> dict:
        """Get ledger statistics"""
        by_type = {}
        for entry_type in LedgerEntryType:
            count = sum(1 for e in self._entries if e.entry_type == entry_type.value)
            by_type[entry_type.value] = count

        return {
            "total_entries": len(self._entries),
            "by_type": by_type,
            "cycles": len(set(e.cycle_id for e in self._entries if e.cycle_id)),
            "first_entry": self._entries[0].timestamp if self._entries else None,
            "last_entry": self._entries[-1].timestamp if self._entries else None,
        }

    def clear(self):
        """Clear all entries (use with caution)"""
        self._entries = []
        self._save()