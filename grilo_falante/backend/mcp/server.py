"""
MCP Server for Grilo Falante v3.0

Provides tools for epistemic governance via MCP protocol.
"""

import json
import sys
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

from grilo_falante.backend.db.connection import init_pool, close_pool, check_health
from grilo_falante.backend.db.repositories import (
    ClaimRepository,
    GapRepository,
    CuratorRepository,
    SourceRepository,
    SessionPreferencesRepository,
    GovernanceRepository,
    generate_key,
    generate_gfid,
)
from grilo_falante.backend.services import (
    GFIDService,
    GMIFClassifier,
    FeynmanService,
    GapDetectionService,
    CuratorScoringService,
    QueryPipeline,
    SchoolModeService,
)
from grilo_falante.models import (
    GovernedClaim,
    Gap,
    Curator,
    GovernedSource,
    SessionPreferences,
    GMIFLevel,
    GapStatus,
    GapType,
    CuratorType,
    SourceTier,
    ValidationState,
    LegitimacyState,
)

# Create server
app = Server("grilo-falante")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        # Regime tools
        Tool(
            name="grilo_status",
            description="Get current regime status",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_health",
            description="Check system health",
            inputSchema={"type": "object", "properties": {}},
        ),
        # GF-ID tools
        Tool(
            name="grilo_generate_gfid",
            description="Generate a GF-ID for a claim",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Claim content to hash"},
                    "gmif_level": {"type": "string", "description": "GMIF level (M1-M8)"},
                    "suffix": {"type": "string", "description": "Optional suffix"},
                },
                "required": ["content", "gmif_level"],
            },
        ),
        Tool(
            name="grilo_classify_gmif",
            description="Classify claim with GMIF level",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_text": {"type": "string"},
                    "source_count": {"type": "number", "default": 1},
                },
                "required": ["claim_text"],
            },
        ),
        # Claim tools
        Tool(
            name="gepeto_query",
            description="Execute query through epistemic pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "session_id": {"type": "string", "default": "default"},
                    "auto_school_mode": {"type": "boolean", "default": True},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="gepeto_get_claim",
            description="Get claim by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_id": {"type": "number"},
                },
                "required": ["claim_id"],
            },
        ),
        Tool(
            name="gepeto_create_claim",
            description="Create a new claim",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_key": {"type": "string"},
                    "claim_text": {"type": "string"},
                    "source_id": {"type": "number"},
                    "session_id": {"type": "string"},
                    "gmif_level": {"type": "string", "default": "M4"},
                    "gmif_confidence": {"type": "number", "default": 0.5},
                },
                "required": ["claim_key", "claim_text"],
            },
        ),
        Tool(
            name="gepeto_validate_claim",
            description="Submit curator validation for a claim",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_id": {"type": "number"},
                    "curator_id": {"type": "number"},
                    "decision": {"type": "string", "enum": ["approved", "rejected", "corrected"]},
                    "notes": {"type": "string"},
                    "evaluator_confidence": {"type": "number"},
                },
                "required": ["claim_id", "curator_id", "decision"],
            },
        ),
        # Gap tools
        Tool(
            name="gepeto_list_gaps",
            description="List knowledge gaps",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "limit": {"type": "number", "default": 20},
                },
            },
        ),
        Tool(
            name="gepeto_school_mode",
            description="Execute school mode for a gap",
            inputSchema={
                "type": "object",
                "properties": {
                    "gap_key": {"type": "string"},
                },
                "required": ["gap_key"],
            },
        ),
        # Curator tools
        Tool(
            name="gepeto_create_curator",
            description="Create a new curator",
            inputSchema={
                "type": "object",
                "properties": {
                    "curator_key": {"type": "string"},
                    "name": {"type": "string"},
                    "curator_type": {"type": "string", "default": "human"},
                    "model_name": {"type": "string"},
                    "specializations": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["curator_key", "name"],
            },
        ),
        Tool(
            name="gepeto_get_curator",
            description="Get curator by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "curator_id": {"type": "number"},
                },
                "required": ["curator_id"],
            },
        ),
        # Source tools
        Tool(
            name="gepeto_list_sources",
            description="List governed sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "default": 20},
                },
            },
        ),
        Tool(
            name="gepeto_get_source",
            description="Get source by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_id": {"type": "number"},
                },
                "required": ["source_id"],
            },
        ),
        Tool(
            name="gepeto_create_source",
            description="Create a new governed source",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_key": {"type": "string"},
                    "title": {"type": "string"},
                    "authors": {"type": "array", "items": {"type": "string"}},
                    "year": {"type": "number"},
                    "doi": {"type": "string"},
                    "url": {"type": "string"},
                    "source_type": {"type": "string", "default": "paper"},
                    "tier": {"type": "string", "default": "tier_2"},
                },
                "required": ["source_key", "title"],
            },
        ),
        Tool(
            name="gepeto_get_gap",
            description="Get gap by key",
            inputSchema={
                "type": "object",
                "properties": {
                    "gap_key": {"type": "string"},
                },
                "required": ["gap_key"],
            },
        ),
        Tool(
            name="gepeto_resolve_gap",
            description="Resolve a gap with a claim",
            inputSchema={
                "type": "object",
                "properties": {
                    "gap_key": {"type": "string"},
                    "resolved_claim_id": {"type": "number"},
                    "curator_id": {"type": "number"},
                },
                "required": ["gap_key", "resolved_claim_id"],
            },
        ),
        # Session tools
        Tool(
            name="gepeto_session_prefs",
            description="Create or update session preferences",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "topics": {"type": "array", "items": {"type": "string"}},
                    "domains": {"type": "array", "items": {"type": "string"}},
                    "recency_weight": {"type": "number", "default": 0.3},
                    "preferred_categories": {"type": "array", "items": {"type": "string"}},
                    "show_metadata": {"type": "boolean", "default": True},
                    "auto_school_mode": {"type": "boolean", "default": True},
                },
                "required": ["session_id"],
            },
        ),
        # Feynman tools
        Tool(
            name="gepeto_feynman_explain",
            description="Generate Feynman-style explanation",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "level": {"type": "string", "enum": ["fep1", "fep2", "fep3"], "default": "fep1"},
                },
                "required": ["topic"],
            },
        ),
        # Audit tools
        Tool(
            name="grilo_audit",
            description="Run hostile audit on claims",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "limit": {"type": "number", "default": 50},
                },
            },
        ),
        Tool(
            name="grilo_lint",
            description="Lint a text for blocking patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    await init_pool()

    try:
        if name == "grilo_status":
            return [TextContent(type="text", text=json.dumps({"status": "active", "version": "3.0.0"}))]

        elif name == "grilo_health":
            health = await check_health()
            return [TextContent(type="text", text=json.dumps(health))]

        elif name == "grilo_generate_gfid":
            gfid = GFIDService.generate(
                content=arguments["content"],
                gmif_level=arguments["gmif_level"],
                suffix=arguments.get("suffix", ""),
            )
            return [TextContent(type="text", text=json.dumps({"gfid": gfid}))]

        elif name == "grilo_classify_gmif":
            level, confidence = GMIFClassifier.classify(
                arguments["claim_text"],
                arguments.get("source_count", 1),
            )
            return [TextContent(type="text", text=json.dumps({
                "gmif_level": level.value,
                "gmif_confidence": confidence,
            }))]

        elif name == "gepeto_query":
            pipeline = QueryPipeline()
            result = await pipeline.execute(
                query=arguments["query"],
                session_id=arguments.get("session_id", "default"),
                auto_school_mode=arguments.get("auto_school_mode", True),
            )
            return [TextContent(type="text", text=json.dumps({
                "status": result.status,
                "reason": result.reason,
                "claims_count": len(result.claims),
                "gaps_count": len(result.gaps),
                "m4_count": result.m4_count,
                "lint_passed": result.lint_passed,
            }))]

        elif name == "gepeto_get_claim":
            repo = ClaimRepository()
            claim = await repo.get_by_id(arguments["claim_id"])
            if not claim:
                return [TextContent(type="text", text=json.dumps({"error": "Claim not found"}))]
            return [TextContent(type="text", text=json.dumps(claim.to_card()))]

        elif name == "gepeto_create_claim":
            repo = ClaimRepository()
            content_hash = hashlib.md5(arguments["claim_text"].encode()).hexdigest()[:6]
            gfid = generate_gfid(content_hash, arguments.get("gmif_level", "M4"))

            claim = GovernedClaim(
                claim_key=arguments["claim_key"],
                claim_text=arguments["claim_text"],
                source_id=arguments.get("source_id"),
                session_id=arguments.get("session_id", "mcp"),
                gmif_level=GMIFLevel(arguments.get("gmif_level", "M4")),
                gmif_confidence=arguments.get("gmif_confidence", 0.5),
                gfid=gfid,
            )
            created = await repo.create(claim)
            return [TextContent(type="text", text=json.dumps({
                "id": created.id,
                "claim_key": created.claim_key,
                "gfid": created.gfid,
            }))]

        elif name == "gepeto_validate_claim":
            repo = ClaimRepository()
            curator_repo = CuratorRepository()
            gov_repo = GovernanceRepository()

            claim = await repo.get_by_id(arguments["claim_id"])
            if not claim:
                return [TextContent(type="text", text=json.dumps({"error": "Claim not found"}))]

            curator = await curator_repo.get_by_id(arguments["curator_id"])
            if not curator:
                return [TextContent(type="text", text=json.dumps({"error": "Curator not found"}))]

            decision = arguments["decision"]
            new_status = ValidationState.APPROVED if decision == "approved" else ValidationState.REJECTED
            new_legitimacy = LegitimacyState.ASSERTED if decision == "approved" else LegitimacyState.REJECTED

            await repo.update_validation(claim.id, new_status, new_legitimacy)

            # Record governance
            record = GovernanceRecord(
                record_key=generate_key("gov"),
                entity_type="claim",
                entity_id=claim.id,
                entity_key=claim.claim_key,
                action="validate",
                decision=decision,
                previous_state=claim.validation_status,
                new_state=new_status.value,
                curator_id=curator.id,
                curator_key=curator.curator_key,
                curator_confidence=arguments.get("evaluator_confidence"),
                notes=arguments.get("notes"),
            )
            await gov_repo.create(record)

            # Update curator score
            scoring = CuratorScoringService()
            if decision == "corrected":
                await scoring.reward(curator.id, "Valid correction")
            elif decision == "rejected":
                await scoring.penalize(curator.id, "Invalid validation")

            return [TextContent(type="text", text=json.dumps({
                "claim_id": claim.id,
                "decision": decision,
                "new_status": new_status.value,
            }))]

        elif name == "gepeto_list_gaps":
            repo = GapRepository()
            status = arguments.get("status")
            limit = arguments.get("limit", 20)

            if status:
                gaps = await repo.list_by_status(GapStatus(status), limit)
            else:
                gaps = await repo.list_by_status(GapStatus.IDENTIFIED, limit)

            return [TextContent(type="text", text=json.dumps({
                "gaps": [g.to_dict() for g in gaps],
                "count": len(gaps),
            }))]

        elif name == "gepeto_school_mode":
            repo = GapRepository()
            gap = await repo.get_by_key(arguments["gap_key"])
            if not gap:
                return [TextContent(type="text", text=json.dumps({"error": "Gap not found"}))]

            service = SchoolModeService()
            result = await service.execute(gap)

            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "gap_key": result.gap.gap_key,
                "sources_found": result.sources_found,
                "claims_created": result.claims_created,
                "error": result.error,
            }))]

        elif name == "gepeto_create_curator":
            repo = CuratorRepository()
            curator = Curator(
                curator_key=arguments["curator_key"],
                name=arguments["name"],
                curator_type=CuratorType(arguments.get("curator_type", "human")),
                model_name=arguments.get("model_name"),
                specializations=arguments.get("specializations", []),
            )
            created = await repo.create(curator)
            return [TextContent(type="text", text=json.dumps({
                "id": created.id,
                "curator_key": created.curator_key,
                "accountability_score": created.accountability_score,
            }))]

        elif name == "gepeto_get_curator":
            repo = CuratorRepository()
            curator = await repo.get_by_id(arguments["curator_id"])
            if not curator:
                return [TextContent(type="text", text=json.dumps({"error": "Curator not found"}))]
            return [TextContent(type="text", text=json.dumps({
                "id": curator.id,
                "curator_key": curator.curator_key,
                "name": curator.name,
                "curator_type": curator.curator_type.value if hasattr(curator.curator_type, 'value') else curator.curator_type,
                "accountability_score": curator.accountability_score,
                "specializations": curator.specializations,
            }))]

        elif name == "gepeto_list_sources":
            repo = SourceRepository()
            sources = await repo.list_all(arguments.get("limit", 20))
            return [TextContent(type="text", text=json.dumps({
                "sources": [{"id": s.id, "source_key": s.source_key, "title": s.title} for s in sources],
                "count": len(sources),
            }))]

        elif name == "gepeto_get_source":
            repo = SourceRepository()
            source = await repo.get_by_id(arguments["source_id"])
            if not source:
                return [TextContent(type="text", text=json.dumps({"error": "Source not found"}))]
            return [TextContent(type="text", text=json.dumps({
                "id": source.id,
                "source_key": source.source_key,
                "title": source.title,
                "authors": source.authors,
                "year": source.year,
                "doi": source.doi,
                "url": source.url,
                "source_type": source.source_type,
                "tier": source.tier.value if hasattr(source.tier, 'value') else source.tier,
                "validation_status": source.validation_status.value if hasattr(source.validation_status, 'value') else source.validation_status,
            }))]

        elif name == "gepeto_create_source":
            repo = SourceRepository()
            source = GovernedSource(
                source_key=arguments["source_key"],
                title=arguments["title"],
                authors=arguments.get("authors", []),
                year=arguments.get("year"),
                doi=arguments.get("doi"),
                url=arguments.get("url"),
                source_type=arguments.get("source_type", "paper"),
                tier=SourceTier(arguments.get("tier", "tier_2")),
            )
            created = await repo.create(source)
            return [TextContent(type="text", text=json.dumps({
                "id": created.id,
                "source_key": created.source_key,
                "title": created.title,
            }))]

        elif name == "gepeto_get_gap":
            repo = GapRepository()
            gap = await repo.get_by_key(arguments["gap_key"])
            if not gap:
                return [TextContent(type="text", text=json.dumps({"error": "Gap not found"}))]
            return [TextContent(type="text", text=json.dumps(gap.to_dict()))]

        elif name == "gepeto_resolve_gap":
            gap_repo = GapRepository()
            gap = await gap_repo.get_by_key(arguments["gap_key"])
            if not gap:
                return [TextContent(type="text", text=json.dumps({"error": "Gap not found"}))]

            claim_repo = ClaimRepository()
            claim = await claim_repo.get_by_id(arguments["resolved_claim_id"])
            if not claim:
                return [TextContent(type="text", text=json.dumps({"error": "Claim not found"}))]

            await gap_repo.resolve(gap.id, claim.id, arguments.get("curator_id"))

            return [TextContent(type="text", text=json.dumps({
                "gap_key": gap.gap_key,
                "resolved": True,
                "resolved_claim_id": claim.id,
            }))]

        elif name == "gepeto_session_prefs":
            repo = SessionPreferencesRepository()
            prefs = SessionPreferences(
                session_id=arguments["session_id"],
                topics=arguments.get("topics", []),
                domains=arguments.get("domains", []),
                recency_weight=arguments.get("recency_weight", 0.3),
                preferred_categories=arguments.get("preferred_categories", ["M1", "M2", "M5", "M7"]),
                show_metadata=arguments.get("show_metadata", True),
                auto_school_mode=arguments.get("auto_school_mode", True),
            )
            await repo.upsert(prefs)
            return [TextContent(type="text", text=json.dumps({"status": "ok", "session_id": prefs.session_id}))]

        elif name == "gepeto_feynman_explain":
            service = FeynmanService()
            level = FeynmanLevel(arguments.get("level", "fep1"))
            result = service.explain(arguments["topic"], level)
            return [TextContent(type="text", text=json.dumps({
                "level": result.level.value,
                "explanation": result.explanation,
                "concepts": result.concepts_identified,
                "gaps": result.gaps_found,
                "completed": result.completed,
            }))]

        elif name == "grilo_audit":
            claim_repo = ClaimRepository()
            gov_repo = GovernanceRepository()
            claims = await claim_repo.search("", limit=arguments.get("limit", 50))
            findings = []
            for claim in claims:
                if claim.gmif_level == GMIFLevel.M4_DOUBTFUL and claim.gmif_confidence < 0.3:
                    findings.append(f"M4 with low confidence: {claim.claim_key}")
            return [TextContent(type="text", text=json.dumps({
                "claims_audited": len(claims),
                "findings": findings,
                "finding_count": len(findings),
            }))]

        elif name == "grilo_lint":
            from grilo_falante.backend.services.lint import CognitiveLint
            lint = CognitiveLint()
            result = lint.lint(arguments["text"])
            return [TextContent(type="text", text=json.dumps({
                "state": result.state.value,
                "message": result.message,
                "issues": result.issues,
            }))]

        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    finally:
        await close_pool()


import hashlib


if __name__ == "__main__":
    import asyncio

    async def main():
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
