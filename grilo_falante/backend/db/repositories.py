"""Repositories — Database access layer for Grilo Falante"""

import hashlib
import json
from datetime import datetime
from typing import Optional
import uuid

import asyncpg

from grilo_falante.backend.db.connection import acquire_connection, acquire_transaction
from grilo_falante.models import (
    GovernedClaim,
    Gap,
    Curator,
    GovernedSource,
    ShadowDocument,
    SessionPreferences,
    StudyPlan,
    StudyPlanStep,
    GovernanceRecord,
    GMIFLevel,
    GapStatus,
    GapType,
    LegitimacyState,
    ValidationState,
)


class ClaimRepository:
    """Repository for governed claims."""

    async def create(self, claim: GovernedClaim) -> GovernedClaim:
        """Create a new claim."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO governed_claims
                (claim_key, claim_text, claim_type, source_id, session_id,
                 gmif_level, gmif_confidence, attribution, epistemic_role,
                 legitimacy_state, validation_status, provenance, gfid)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id, created_at
                """,
                claim.claim_key,
                claim.claim_text,
                claim.claim_type.value if hasattr(claim.claim_type, 'value') else claim.claim_type,
                claim.source_id,
                claim.session_id,
                claim.gmif_level.value if hasattr(claim.gmif_level, 'value') else claim.gmif_level,
                claim.gmif_confidence,
                claim.attribution.value if hasattr(claim.attribution, 'value') else claim.attribution,
                claim.epistemic_role.value if hasattr(claim.epistemic_role, 'value') else claim.epistemic_role,
                claim.legitimacy_state.value if hasattr(claim.legitimacy_state, 'value') else claim.legitimacy_state,
                claim.validation_status.value if hasattr(claim.validation_status, 'value') else claim.validation_status,
                json.dumps(claim.provenance),
                claim.gfid,
            )
            claim.id = row["id"]
            claim.created_at = row["created_at"]
            return claim

    async def get_by_id(self, claim_id: int) -> Optional[GovernedClaim]:
        """Get claim by ID."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM governed_claims WHERE id = $1", claim_id
            )
            return self._row_to_claim(row) if row else None

    async def get_by_key(self, claim_key: str) -> Optional[GovernedClaim]:
        """Get claim by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM governed_claims WHERE claim_key = $1", claim_key
            )
            return self._row_to_claim(row) if row else None

    async def update_validation(
        self,
        claim_id: int,
        new_status: ValidationState,
        new_legitimacy: LegitimacyState,
    ) -> None:
        """Update claim validation status."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                UPDATE governed_claims
                SET validation_status = $2, legitimacy_state = $3, updated_at = NOW()
                WHERE id = $1
                """,
                claim_id,
                new_status.value if hasattr(new_status, 'value') else new_status,
                new_legitimacy.value if hasattr(new_legitimacy, 'value') else new_legitimacy,
            )

    async def search(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[GovernedClaim]:
        """Search claims by text."""
        async with acquire_connection() as conn:
            if session_id:
                rows = await conn.fetch(
                    """
                    SELECT * FROM governed_claims
                    WHERE claim_text ILIKE $1 AND session_id = $2
                    ORDER BY gmif_confidence DESC
                    LIMIT $3
                    """,
                    f"%{query}%",
                    session_id,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM governed_claims
                    WHERE claim_text ILIKE $1
                    ORDER BY gmif_confidence DESC
                    LIMIT $2
                    """,
                    f"%{query}%",
                    limit,
                )
            return [self._row_to_claim(row) for row in rows]

    def _row_to_claim(self, row: asyncpg.Record) -> GovernedClaim:
        """Convert database row to GovernedClaim."""
        return GovernedClaim(
            id=row["id"],
            claim_key=row["claim_key"],
            claim_text=row["claim_text"],
            claim_type=row["claim_type"],
            source_id=row["source_id"],
            session_id=row["session_id"],
            gmif_level=row["gmif_level"],
            gmif_confidence=row["gmif_confidence"],
            attribution=row["attribution"],
            epistemic_role=row["epistemic_role"],
            legitimacy_state=row["legitimacy_state"],
            validation_status=row["validation_status"],
            provenance=row["provenance"] or {},
            usage_count=row["usage_count"],
            last_used=row["last_used"],
            gfid=row["gfid"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class GapRepository:
    """Repository for knowledge gaps."""

    async def create(self, gap: Gap) -> Gap:
        """Create a new gap."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO gaps
                (gap_key, gap_type, query, claim_template, reason, expected_claim, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, created_at
                """,
                gap.gap_key,
                gap.gap_type.value if hasattr(gap.gap_type, 'value') else gap.gap_type,
                gap.query,
                json.dumps(gap.claim_template),
                gap.reason,
                gap.expected_claim,
                gap.status.value if hasattr(gap.status, 'value') else gap.status,
            )
            gap.id = row["id"]
            gap.created_at = row["created_at"]
            return gap

    async def get_by_id(self, gap_id: int) -> Optional[Gap]:
        """Get gap by ID."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM gaps WHERE id = $1", gap_id
            )
            return self._row_to_gap(row) if row else None

    async def get_by_key(self, gap_key: str) -> Optional[Gap]:
        """Get gap by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM gaps WHERE gap_key = $1", gap_key
            )
            return self._row_to_gap(row) if row else None

    async def list_by_status(
        self, status: GapStatus, limit: int = 20
    ) -> list[Gap]:
        """List gaps by status."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM gaps
                WHERE status = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                status.value if hasattr(status, 'value') else status,
                limit,
            )
            return [self._row_to_gap(row) for row in rows]

    async def update_status(self, gap_key: str, new_status: GapStatus) -> Gap:
        """Update gap status."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                UPDATE gaps SET status = $2, updated_at = NOW()
                WHERE gap_key = $1
                RETURNING *
                """,
                gap_key,
                new_status.value if hasattr(new_status, 'value') else new_status,
            )
            return self._row_to_gap(row) if row else None

    async def resolve(
        self, gap_key: str, resolved_claim_id: int, resolved_by: int
    ) -> Gap:
        """Mark gap as resolved."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                UPDATE gaps
                SET status = 'resolved', resolved_claim_id = $2,
                    resolved_by = $3, resolved_at = NOW(), updated_at = NOW()
                WHERE gap_key = $1
                RETURNING *
                """,
                gap_key,
                resolved_claim_id,
                resolved_by,
            )
            return self._row_to_gap(row) if row else None

    def _row_to_gap(self, row: asyncpg.Record) -> Gap:
        """Convert database row to Gap."""
        return Gap(
            id=row["id"],
            gap_key=row["gap_key"],
            gap_type=row["gap_type"],
            query=row["query"],
            claim_template=row["claim_template"] or {},
            reason=row["reason"],
            expected_claim=row["expected_claim"],
            status=row["status"],
            resolved_claim_id=row["resolved_claim_id"],
            resolved_by=row["resolved_by"],
            resolved_at=row["resolved_at"],
            related_claim_ids=row["related_claim_ids"] or [],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class CuratorRepository:
    """Repository for curators."""

    async def create(self, curator: Curator) -> Curator:
        """Create a new curator."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO curators
                (curator_key, name, curator_type, model_name, specializations, accountability_score)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id, created_at
                """,
                curator.curator_key,
                curator.name,
                curator.curator_type.value if hasattr(curator.curator_type, 'value') else curator.curator_type,
                curator.model_name,
                curator.specializations,
                curator.accountability_score,
            )
            curator.id = row["id"]
            curator.created_at = row["created_at"]
            return curator

    async def get_by_id(self, curator_id: int) -> Optional[Curator]:
        """Get curator by ID."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM curators WHERE id = $1", curator_id
            )
            return self._row_to_curator(row) if row else None

    async def get_by_key(self, curator_key: str) -> Optional[Curator]:
        """Get curator by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM curators WHERE curator_key = $1", curator_key
            )
            return self._row_to_curator(row) if row else None

    async def update_score(
        self, curator_id: int, new_score: float, reason: str
    ) -> Curator:
        """Update curator score with history."""
        async with acquire_transaction() as conn:
            # Get old score
            row = await conn.fetchrow(
                "SELECT accountability_score FROM curators WHERE id = $1",
                curator_id,
            )
            old_score = row["accountability_score"] if row else 0.0

            # Insert history
            await conn.execute(
                """
                INSERT INTO curator_score_history (curator_id, old_score, new_score, reason)
                VALUES ($1, $2, $3, $4)
                """,
                curator_id,
                old_score,
                new_score,
                reason,
            )

            # Update curator
            await conn.execute(
                """
                UPDATE curators
                SET accountability_score = $2, last_activity = NOW(), updated_at = NOW()
                WHERE id = $1
                """,
                curator_id,
                new_score,
            )

            row = await conn.fetchrow("SELECT * FROM curators WHERE id = $1", curator_id)
            return self._row_to_curator(row) if row else None

    async def apply_decay(self, days: int = 180) -> int:
        """Apply decay to inactive curators. Returns count of affected curators."""
        async with acquire_connection() as conn:
            result = await conn.execute(
                """
                UPDATE curators
                SET accountability_score = GREATEST(0.0, accountability_score - 0.3),
                    updated_at = NOW()
                WHERE is_active = TRUE
                AND last_activity < NOW() - INTERVAL '1 day' * $1
                AND accountability_score > 0.0
                """,
                days,
            )
            return int(result.split()[-1]) if result else 0

    def _row_to_curator(self, row: asyncpg.Record) -> Curator:
        """Convert database row to Curator."""
        return Curator(
            id=row["id"],
            curator_key=row["curator_key"],
            name=row["name"],
            curator_type=row["curator_type"],
            model_name=row["model_name"],
            specializations=row["specializations"] or [],
            accountability_score=row["accountability_score"],
            is_active=row["is_active"],
            last_activity=row["last_activity"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SourceRepository:
    """Repository for governed sources."""

    async def create(self, source: GovernedSource) -> GovernedSource:
        """Create a new source."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO governed_sources
                (source_key, title, authors, year, doi, url, source_type,
                 source_origin, tier, validation_status, ingestion_origin, raw_metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id, created_at
                """,
                source.source_key,
                source.title,
                source.authors,
                source.year,
                source.doi,
                source.url,
                source.source_type,
                source.source_origin,
                source.tier.value if hasattr(source.tier, 'value') else source.tier,
                source.validation_status.value if hasattr(source.validation_status, 'value') else source.validation_status,
                source.ingestion_origin,
                json.dumps(source.raw_metadata),
            )
            source.id = row["id"]
            source.created_at = row["created_at"]
            return source

    async def get_by_id(self, source_id: int) -> Optional[GovernedSource]:
        """Get source by ID."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM governed_sources WHERE id = $1", source_id
            )
            return self._row_to_source(row) if row else None

    async def get_by_key(self, source_key: str) -> Optional[GovernedSource]:
        """Get source by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM governed_sources WHERE source_key = $1", source_key
            )
            return self._row_to_source(row) if row else None

    async def list_all(self, limit: int = 20) -> list[GovernedSource]:
        """List all sources."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                "SELECT * FROM governed_sources ORDER BY created_at DESC LIMIT $1", limit
            )
            return [self._row_to_source(row) for row in rows]

    def _row_to_source(self, row: asyncpg.Record) -> GovernedSource:
        """Convert database row to GovernedSource."""
        return GovernedSource(
            id=row["id"],
            source_key=row["source_key"],
            title=row["title"],
            authors=row["authors"] or [],
            year=row["year"],
            doi=row["doi"],
            url=row["url"],
            source_type=row["source_type"],
            source_origin=row["source_origin"],
            tier=row["tier"],
            validation_status=row["validation_status"],
            ingestion_origin=row["ingestion_origin"],
            raw_metadata=row["raw_metadata"] or {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


class SessionPreferencesRepository:
    """Repository for session preferences."""

    async def upsert(self, prefs: SessionPreferences) -> SessionPreferences:
        """Create or update session preferences."""
        async with acquire_connection() as conn:
            await conn.execute(
                """
                INSERT INTO session_preferences
                (session_id, topics, domains, recency_weight, preferred_categories,
                 show_metadata, auto_school_mode, confidence_display, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                ON CONFLICT (session_id) DO UPDATE SET
                    topics = EXCLUDED.topics,
                    domains = EXCLUDED.domains,
                    recency_weight = EXCLUDED.recency_weight,
                    preferred_categories = EXCLUDED.preferred_categories,
                    show_metadata = EXCLUDED.show_metadata,
                    auto_school_mode = EXCLUDED.auto_school_mode,
                    confidence_display = EXCLUDED.confidence_display,
                    updated_at = NOW()
                """,
                prefs.session_id,
                prefs.topics,
                prefs.domains,
                prefs.recency_weight,
                prefs.preferred_categories,
                prefs.show_metadata,
                prefs.auto_school_mode,
                prefs.confidence_display,
            )
            return prefs

    async def get_by_session(self, session_id: str) -> Optional[SessionPreferences]:
        """Get preferences by session ID."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM session_preferences WHERE session_id = $1", session_id
            )
            return self._row_to_prefs(row) if row else None

    def _row_to_prefs(self, row: asyncpg.Record) -> SessionPreferences:
        """Convert database row to SessionPreferences."""
        return SessionPreferences(
            session_id=row["session_id"],
            topics=row["topics"] or [],
            domains=row["domains"] or [],
            recency_weight=row["recency_weight"],
            preferred_categories=row["preferred_categories"] or [],
            show_metadata=row["show_metadata"],
            auto_school_mode=row["auto_school_mode"],
            confidence_display=row["confidence_display"],
        )


class GovernanceRepository:
    """Repository for governance records (immutable audit log)."""

    async def create(self, record: GovernanceRecord) -> GovernanceRecord:
        """Create a new governance record."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO governance_records
                (record_key, entity_type, entity_id, entity_key, action, decision,
                 reason, previous_state, new_state, curator_id, curator_key,
                 curator_confidence, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id, created_at
                """,
                record.record_key,
                record.entity_type,
                record.entity_id,
                record.entity_key,
                record.action,
                record.decision,
                record.reason,
                record.previous_state,
                record.new_state,
                record.curator_id,
                record.curator_key,
                record.curator_confidence,
                json.dumps(record.metadata),
            )
            record.id = row["id"]
            record.created_at = row["created_at"]
            return record

    async def get_by_entity(
        self, entity_type: str, entity_id: int, limit: int = 100
    ) -> list[GovernanceRecord]:
        """Get governance records for an entity."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM governance_records
                WHERE entity_type = $1 AND entity_id = $2
                ORDER BY created_at DESC
                LIMIT $3
                """,
                entity_type,
                entity_id,
                limit,
            )
            return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: asyncpg.Record) -> GovernanceRecord:
        """Convert database row to GovernanceRecord."""
        return GovernanceRecord(
            id=row["id"],
            record_key=row["record_key"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            entity_key=row["entity_key"],
            action=row["action"],
            decision=row["decision"],
            reason=row["reason"],
            previous_state=row["previous_state"],
            new_state=row["new_state"],
            curator_id=row["curator_id"],
            curator_key=row["curator_key"],
            curator_confidence=row["curator_confidence"],
            metadata=row["metadata"] or {},
            created_at=row["created_at"],
        )


class ShadowDocumentRepository:
    """Repository for shadow documents."""

    async def create(self, shadow: ShadowDocument) -> ShadowDocument:
        """Create a new shadow document."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO shadow_documents
                (source_id, factual_summary, projected_claims, citations, limits,
                 misuse_risks, status, validation_notes, f1_count, f2_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id, created_at
                """,
                shadow.source_id,
                shadow.factual_summary,
                shadow.projected_claims,
                json.dumps(shadow.citations),
                shadow.limits,
                shadow.misuse_risks,
                shadow.status.value if hasattr(shadow.status, 'value') else shadow.status,
                shadow.validation_notes,
                shadow.f1_count,
                shadow.f2_count,
            )
            shadow.id = row["id"]
            shadow.created_at = row["created_at"]
            return shadow

    async def get_by_source(self, source_id: int) -> list[ShadowDocument]:
        """Get shadow documents for a source."""
        async with acquire_connection() as conn:
            rows = await conn.fetch(
                "SELECT * FROM shadow_documents WHERE source_id = $1",
                source_id,
            )
            return [self._row_to_shadow(row) for row in rows]

    def _row_to_shadow(self, row: asyncpg.Record) -> ShadowDocument:
        """Convert database row to ShadowDocument."""
        return ShadowDocument(
            id=row["id"],
            source_id=row["source_id"],
            factual_summary=row["factual_summary"],
            projected_claims=row["projected_claims"] or [],
            citations=row["citations"] or [],
            limits=row["limits"] or [],
            misuse_risks=row["misuse_risks"] or [],
            status=row["status"],
            validation_notes=row["validation_notes"],
            f1_count=row["f1_count"],
            f2_count=row["f2_count"],
            created_at=row["created_at"],
        )


class StudyPlanRepository:
    """Repository for study plans."""

    async def create(self, plan: StudyPlan) -> StudyPlan:
        """Create a new study plan."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO study_plans
                (plan_key, gap_key, topic, steps, status, current_step, completed_steps)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, created_at
                """,
                plan.plan_key,
                plan.gap_key,
                plan.topic,
                json.dumps([s.model_dump() for s in plan.steps]),
                plan.status.value if hasattr(plan.status, 'value') else plan.status,
                plan.current_step,
                plan.completed_steps,
            )
            plan.id = row["id"]
            plan.created_at = row["created_at"]
            return plan

    async def get_by_key(self, plan_key: str) -> Optional[StudyPlan]:
        """Get study plan by key."""
        async with acquire_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM study_plans WHERE plan_key = $1", plan_key
            )
            return self._row_to_plan(row) if row else None

    def _row_to_plan(self, row: asyncpg.Record) -> StudyPlan:
        """Convert database row to StudyPlan."""
        steps_data = json.loads(row["steps"]) if isinstance(row["steps"], str) else row["steps"]
        steps = [StudyPlanStep(**s) for s in steps_data] if steps_data else []
        return StudyPlan(
            id=row["id"],
            plan_key=row["plan_key"],
            gap_key=row["gap_key"],
            topic=row["topic"],
            steps=steps,
            status=row["status"],
            current_step=row["current_step"],
            completed_steps=row["completed_steps"],
            created_at=row["created_at"],
        )


def generate_key(prefix: str) -> str:
    """Generate a unique key with prefix."""
    uuid_str = str(uuid.uuid4())[:8]
    return f"{prefix}:{uuid_str}"


def generate_gfid(content_hash: str, gmif_level: str, suffix: str = "") -> str:
    """Generate a GF-ID in format GF-{YYMMDD}-{GMIF}-{HASH}."""
    from datetime import datetime
    date_str = datetime.utcnow().strftime("%y%m%d")
    short_hash = content_hash[:6] if len(content_hash) >= 6 else content_hash
    suffix_str = f"-{suffix}" if suffix else ""
    return f"GF-{date_str}-{gmif_level}-{short_hash}{suffix_str}"
