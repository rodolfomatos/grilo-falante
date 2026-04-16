"""
Shadow First Skill - Documentation Before Asking

This module implements the Shadow First methodology:

1. RESEARCH - Read docs, web fetch, analyze code
2. DOCUMENT - Create Shadow Document of what you found
3. FAQ - Generate questions you still have
4. ONLY THEN - Ask or implement

Usage:
    from grilo_admin.skills import ShadowFirstSkill

    skill = ShadowFirstSkill()
    result = skill.check("MemPalace")
    if result["status"] == "UNDOCUMENTED":
        skill.shadow("MemPalace")
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from grilo_admin.skills.registry import ConceptRegistry, ConceptStatus

logger = logging.getLogger(__name__)


@dataclass
class ShadowDocument:
    """A shadow document for a concept."""
    concept: str
    content: str
    created_at: str
    file_path: Optional[str] = None


@dataclass
class FAQEntry:
    """An FAQ entry for a concept."""
    question: str
    answer: Optional[str] = None
    status: str = "pending"  # pending, answered, unclear


@dataclass
class ShadowSession:
    """A shadow documentation session."""
    concept: str
    started_at: str
    completed_at: Optional[str] = None
    shadow_doc: Optional[ShadowDocument] = None
    faqs: List[FAQEntry] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)

    def is_complete(self) -> bool:
        """Check if session is complete."""
        return self.shadow_doc is not None


class ShadowFirstSkill:
    """
    Implements the Shadow First methodology.

    The methodology says: before asking, assuming, or implementing,
    you must first:
    1. Research - read docs, web fetch, analyze code
    2. Document - create Shadow Document of what you found
    3. FAQ - generate questions you still have
    4. Only then - ask or implement
    """

    _instance: Optional['ShadowFirstSkill'] = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the skill."""
        if not self._initialized:
            self._registry = ConceptRegistry()
            self._docs_base_path = Path("docs/shadow_documents")
            self._sessions: Dict[str, ShadowSession] = {}
            ShadowFirstSkill._initialized = True

    def check(self, concept: str) -> Dict[str, Any]:
        """
        Check if a concept is documented.

        Args:
            concept: Name of the concept to check

        Returns:
            Dict with:
            - status: documented, partial, undocumented, unknown
            - shadow_score: 0-100
            - recommendation: what to do next
            - missing: list of missing documentation
        """
        result = self._registry.check(concept)

        if not result["registered"]:
            # Register the concept as shadow debt
            self._registry.register_concept(
                name=concept,
                priority="high",
                notes="Auto-registered by shadow_first.check()",
            )
            result = self._registry.check(concept)

        return result

    def shadow(self, concept: str, content: Optional[str] = None) -> ShadowSession:
        """
        Start a shadow documentation session for a concept.

        Args:
            concept: Name of the concept
            content: Optional pre-existing content

        Returns:
            ShadowSession object
        """
        # Check if session already exists
        session_id = concept.lower().replace(" ", "_")
        if session_id in self._sessions:
            return self._sessions[session_id]

        # Create new session
        session = ShadowSession(
            concept=concept,
            started_at=datetime.now().isoformat(),
        )

        if content:
            session.shadow_doc = ShadowDocument(
                concept=concept,
                content=content,
                created_at=datetime.now().isoformat(),
            )

        self._sessions[session_id] = session

        # Update registry
        self._registry.update_concept(
            concept,
            notes=f"Shadow session started at {session.started_at}",
        )

        logger.info(f"Shadow session started for: {concept}")
        return session

    def add_shadow_content(
        self,
        concept: str,
        content: str,
        sources: Optional[List[str]] = None,
    ) -> bool:
        """
        Add shadow document content for a concept.

        Args:
            concept: Name of the concept
            content: The shadow document content
            sources: List of sources used

        Returns:
            True if successful
        """
        session_id = concept.lower().replace(" ", "_")
        session = self._sessions.get(session_id)

        if not session:
            session = self.shadow(concept)

        session.shadow_doc = ShadowDocument(
            concept=concept,
            content=content,
            created_at=datetime.now().isoformat(),
        )

        if sources:
            session.sources_used.extend(sources)

        # Save to file
        self._save_shadow_doc(session)

        # Update registry
        file_path = f"{self._docs_base_path}/SHADOW_{concept.upper().replace(' ', '_')}_v1.md"
        self._registry.update_concept(
            concept,
            shadow_doc_path=file_path,
        )

        logger.info(f"Shadow doc added for: {concept}")
        return True

    def add_faq(
        self,
        concept: str,
        question: str,
        answer: Optional[str] = None,
    ) -> bool:
        """
        Add an FAQ entry for a concept.

        Args:
            concept: Name of the concept
            question: The question
            answer: Optional answer

        Returns:
            True if successful
        """
        session_id = concept.lower().replace(" ", "_")
        session = self._sessions.get(session_id)

        if not session:
            session = self.shadow(concept)

        faq = FAQEntry(
            question=question,
            answer=answer,
            status="answered" if answer else "pending",
        )
        session.faqs.append(faq)

        # Update registry if all FAQs are answered
        if all(faq.status == "answered" for faq in session.faqs):
            file_path = f"{self._docs_base_path}/FAQ_{concept.upper().replace(' ', '_')}_GF_v1.md"
            self._registry.update_concept(
                concept,
                faq_path=file_path,
            )

        return True

    def add_gap(self, concept: str, gap: str) -> bool:
        """
        Add a knowledge gap for a concept.

        Args:
            concept: Name of the concept
            gap: Description of the gap

        Returns:
            True if successful
        """
        session_id = concept.lower().replace(" ", "_")
        session = self._sessions.get(session_id)

        if not session:
            session = self.shadow(concept)

        session.gaps.append(gap)

        # Update registry
        self._registry.update_concept(
            concept,
            notes=f"Gap identified: {gap}",
        )

        return True

    def complete_session(self, concept: str) -> bool:
        """
        Mark a shadow session as complete.

        Args:
            concept: Name of the concept

        Returns:
            True if successful
        """
        session_id = concept.lower().replace(" ", "_")
        session = self._sessions.get(session_id)

        if not session:
            return False

        session.completed_at = datetime.now().isoformat()

        # Final registry update
        self._registry.update_concept(
            concept,
            status=ConceptStatus.COMPLETE if session.shadow_doc else ConceptStatus.PARTIAL,
        )

        logger.info(f"Shadow session completed for: {concept}")
        return True

    def ritual(self) -> Dict[str, Any]:
        """
        Run the pre-session ritual - check shadow debt.

        Returns:
            Dict with shadow debt summary and recommendations
        """
        debt = self._registry.get_shadow_debt()
        score = self._registry.get_shadow_score()

        result = {
            "total_concepts": score["total"],
            "shadow_debt_count": len(debt),
            "avg_shadow_score": score["avg_score"],
            "shadow_debt": [
                {
                    "concept": c.name,
                    "priority": c.priority,
                    "first_mentioned": c.first_mentioned,
                    "shadow_score": c.shadow_score,
                }
                for c in debt
            ],
            "recommendations": [],
        }

        if debt:
            result["recommendations"].append({
                "action": "shadow",
                "concepts": [c.name for c in debt],
                "message": f"⚠️ {len(debt)} concepts in shadow debt. Document them before proceeding.",
            })

        return result

    def status(self) -> Dict[str, Any]:
        """
        Get overall shadow documentation status.

        Returns:
            Dict with status summary
        """
        score = self._registry.get_shadow_score()
        complete = self._registry.get_complete()
        partial = self._registry.get_partial()
        debt = self._registry.get_shadow_debt()

        completeness_pct = 0
        if score["total"] > 0:
            completeness_pct = round((score["complete"] / score["total"]) * 100, 1)

        return {
            "total_concepts": score["total"],
            "complete": score["complete"],
            "partial": score["partial"],
            "undocumented": score["undocumented"],
            "avg_shadow_score": score["avg_score"],
            "completeness_pct": completeness_pct,
            "complete_concepts": [c.name for c in complete],
            "partial_concepts": [c.name for c in partial],
            "shadow_debt_concepts": [c.name for c in debt],
        }

    def generate_report(self, theme: str, concepts: List[str]) -> Dict[str, Any]:
        """
        Generate a session report.

        Args:
            theme: Theme of the session
            concepts: List of concepts documented

        Returns:
            Report dict
        """
        now = datetime.now().isoformat()

        report = {
            "theme": theme,
            "generated_at": now,
            "concepts_documented": concepts,
            "concepts_mentioned": len(concepts),
            "shadow_debt_resolved": 0,
            "gaps_identified": [],
            "next_steps": [],
        }

        for concept in concepts:
            session_id = concept.lower().replace(" ", "_")
            session = self._sessions.get(session_id)
            if session:
                if session.shadow_doc:
                    report["shadow_debt_resolved"] += 1
                report["gaps_identified"].extend(session.gaps)

        # Update registry with report path
        if concepts:
            report_path = f"{self._docs_base_path}/../reports/RELATORIO_SESSAO_{theme.upper().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md"
            for concept in concepts:
                self._registry.update_concept(
                    concept,
                    report_path=report_path,
                )

        return report

    def _save_shadow_doc(self, session: ShadowSession) -> bool:
        """Save shadow document to file."""
        if not session.shadow_doc:
            return False

        file_path = Path(self._docs_base_path) / f"SHADOW_{session.concept.upper().replace(' ', '_')}_v1.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# SHADOW DOCUMENT — {session.concept}

**GF-ID:** SD-{datetime.now().strftime('%Y%m%d')}-{session.concept.upper().replace(' ', '')[:10]}
**Date:** {session.shadow_doc.created_at}
**Type:** Shadow Document (não-promotável)

---

{ session.shadow_doc.content }

---

**Sources used:** {', '.join(session.sources_used) if session.sources_used else 'None'}
**Gaps identified:** {', '.join(session.gaps) if session.gaps else 'None'}

---

**FIM DO DOCUMENTO**
Este documento é um Shadow Document - não confere autoridade.
"""

        with open(file_path, 'w') as f:
            f.write(content)

        session.shadow_doc.file_path = str(file_path)
        logger.info(f"Shadow doc saved to: {file_path}")
        return True

    def get_session(self, concept: str) -> Optional[ShadowSession]:
        """Get a shadow session by concept name."""
        session_id = concept.lower().replace(" ", "_")
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[ShadowSession]:
        """List all active shadow sessions."""
        return list(self._sessions.values())
