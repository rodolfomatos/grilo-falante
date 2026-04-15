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
from grilo_falante.regime import Loader, Acordar, Ledger, LedgerEntryType, StateMachine, PINAProtocol, TransitionValidator

_ledger = Ledger()
_loader = Loader(ledger=_ledger)
_state_machine = _loader.state_machine
_acordar = Acordar(state_machine=_state_machine, ledger=_ledger)
_pina = PINAProtocol(state_machine=_state_machine, ledger=_ledger)
_validator = TransitionValidator(state_machine=_state_machine)

# Create server
app = Server("grilo-falante")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
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
        Tool(
            name="grilo_load",
            description="Load the Grilo Falante regime to start a new cycle",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_unload",
            description="Unload the Grilo Falante regime to end the current cycle",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_acordar",
            description="Execute ACORDAR wake-up ritual with temporal anchoring and intention",
            inputSchema={
                "type": "object",
                "properties": {
                    "temporal_anchor": {"type": "string", "description": "Date/time context (e.g., '2026-04-15')"},
                    "intention": {"type": "string", "description": "What the human intends to accomplish"},
                    "mode": {"type": "string", "enum": ["exploratory", "committed"], "default": "exploratory"},
                },
                "required": ["temporal_anchor", "intention"],
            },
        ),
        Tool(
            name="grilo_vai_dormir",
            description="Hibernate the regime (VAI_DORMIR)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_resume",
            description="Resume the regime from hibernation",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_get_ledger_stats",
            description="Get ledger statistics",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_pina_propose",
            description="Propose a Normative Candidate for PINA decision",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_document": {"type": "string", "description": "Source document reference"},
                    "faithful_statement": {"type": "string", "description": "The normative statement"},
                    "location": {"type": "string", "description": "Location in source"},
                    "graph_scope": {"type": "string"},
                },
                "required": ["source_document", "faithful_statement", "location"],
            },
        ),
        Tool(
            name="grilo_pina_decide",
            description="Record PINA decision for a Normative Candidate",
            inputSchema={
                "type": "object",
                "properties": {
                    "nca_id": {"type": "string", "description": "The NCA-ID"},
                    "decision": {"type": "string", "enum": ["A", "B", "C"], "description": "[A] Incorporate, [B] Do not incorporate, [C] Defer"},
                },
                "required": ["nca_id", "decision"],
            },
        ),
        Tool(
            name="grilo_pina_status",
            description="Get PINA protocol status",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_pina_pending",
            description="List all pending NCA candidates awaiting human decision",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "number", "default": 20, "description": "Maximum results"},
                },
            },
        ),
        Tool(
            name="grilo_validate_transition",
            description="Validate a transition in an epistemic graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_node": {"type": "string", "description": "Current node ID"},
                    "to_node": {"type": "string", "description": "Target node ID"},
                    "graph_id": {"type": "string", "description": "Graph ID"},
                },
                "required": ["from_node", "to_node", "graph_id"],
            },
        ),
        Tool(
            name="grilo_list_graphs",
            description="List all registered epistemic graphs",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="grilo_stamp_capsule",
            description="Add GF-ID and GMIF header to a capsule file",
            inputSchema={
                "type": "object",
                "properties": {
                    "capsule_path": {"type": "string", "description": "Path to capsule file"},
                    "gmif_level": {"type": "string", "description": "GMIF level (M1-M8)"},
                    "force": {"type": "boolean", "default": False},
                },
                "required": ["capsule_path"],
            },
        ),
        Tool(
            name="grilo_run_auditoria_hostil",
            description="Execute AUDITORIA_HOSTIL_CANONICO workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Content to audit"},
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="grilo_run_autopsia_literatura",
            description="Execute AUTOPSIA_LITERATURA workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Literature review content to autopsy"},
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="grilo_run_triagem",
            description="Execute TRIAGEM workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Conversation content to triage"},
                },
                "required": ["content"],
            },
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
        Tool(
            name="grilo_semantic_search",
            description="Fast semantic search using MemPalace cache for context retrieval",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "number", "default": 5, "description": "Maximum results"},
                },
                "required": ["query"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    await init_pool()

    try:
        if name == "grilo_status":
            status = _loader.get_status()
            status["version"] = "3.0.0"
            return [TextContent(type="text", text=json.dumps(status))]

        elif name == "grilo_health":
            health = await check_health()
            return [TextContent(type="text", text=json.dumps(health))]

        elif name == "grilo_load":
            result = _loader.load()
            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "message": result.message,
                "cycle_id": result.cycle_id,
                "state": result.state,
            }))]

        elif name == "grilo_unload":
            result = _loader.unload()
            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "message": result.message,
            }))]

        elif name == "grilo_acordar":
            result = _acordar.execute(
                temporal_anchor=arguments["temporal_anchor"],
                intention=arguments["intention"],
                mode=arguments.get("mode", "exploratory"),
            )
            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "message": result.message,
                "temporal_anchor": result.temporal_anchor,
                "intention_declared": result.intention_declared,
            }))]

        elif name == "grilo_vai_dormir":
            result = _acordar.vai_dormir()
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "grilo_resume":
            result = _acordar.resume()
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "grilo_get_ledger_stats":
            stats = _ledger.get_stats()
            return [TextContent(type="text", text=json.dumps(stats))]

        elif name == "grilo_pina_propose":
            result = _pina.propose_candidate(
                source_document=arguments["source_document"],
                faithful_statement=arguments["faithful_statement"],
                location=arguments["location"],
                graph_scope=arguments.get("graph_scope"),
            )
            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "nca_id": result.nca_id,
                "message": result.message,
            }))]

        elif name == "grilo_pina_decide":
            result = _pina.decide(
                nca_id=arguments["nca_id"],
                decision=arguments["decision"],
            )
            return [TextContent(type="text", text=json.dumps({
                "success": result.success,
                "nca_id": result.nca_id,
                "message": result.message,
                "decision": result.decision,
                "active_invariants": result.active_invariants,
            }))]

        elif name == "grilo_pina_status":
            status = _pina.get_status()
            return [TextContent(type="text", text=json.dumps(status))]

        elif name == "grilo_pina_pending":
            pending = _pina.get_pending()
            return [TextContent(type="text", text=json.dumps({
                "pending_count": len(pending),
                "pending": pending[:arguments.get("limit", 20)],
            }))]

        elif name == "grilo_validate_transition":
            result = _validator.validate_transition(
                from_node=arguments["from_node"],
                to_node=arguments["to_node"],
                graph_id=arguments["graph_id"],
            )
            return [TextContent(type="text", text=json.dumps({
                "valid": result.valid,
                "from_node": result.from_node,
                "to_node": result.to_node,
                "graph_id": result.graph_id,
                "message": result.message,
                "available_transitions": result.available_transitions,
            }))]

        elif name == "grilo_list_graphs":
            graphs = _validator.list_graphs()
            return [TextContent(type="text", text=json.dumps(graphs))]

        elif name == "grilo_stamp_capsule":
            from pathlib import Path
            from grilo_falante.regime import stamp_capsule
            capsule_path = Path(arguments["capsule_path"])
            gmif_level = arguments.get("gmif_level")
            force = arguments.get("force", False)
            stamped = stamp_capsule(capsule_path, gmif_level, force)
            return [TextContent(type="text", text=json.dumps({
                "success": stamped,
                "capsule_path": str(capsule_path),
                "message": "Capsule stamped successfully" if stamped else "Capsule already has metadata or error occurred",
            }))]

        elif name == "grilo_run_auditoria_hostil":
            from grilo_falante.cognitive import AuditoriaHostil
            import asyncio

            content = arguments["content"]
            lines = [l.strip() for l in content.split("\n") if l.strip()]

            claims = []
            for i, line in enumerate(lines):
                if len(line) > 20:
                    claims.append({
                        "id": f"claim_{i}",
                        "claim_text": line,
                        "gmif_level": "M3",
                        "validation_status": "pending",
                    })

            if not claims:
                claims = [{"id": "claim_0", "claim_text": content[:500], "gmif_level": "M3", "validation_status": "pending"}]

            auditoria = AuditoriaHostil()
            report = await auditoria.run_full_audit(claims=claims, governance_records=[])

            return [TextContent(type="text", text=json.dumps(report.to_dict()))]

        elif name == "grilo_run_autopsia_literatura":
            from grilo_falante.cognitive import PromptWorkflows
            workflow = PromptWorkflows()
            result = workflow.autopsia_literatura_workflow(arguments["content"])
            return [TextContent(type="text", text=json.dumps(result))]

        elif name == "grilo_run_triagem":
            from grilo_falante.cognitive import PromptWorkflows
            workflow = PromptWorkflows()
            result = workflow.triagem_workflow(arguments["content"])
            return [TextContent(type="text", text=json.dumps(result))]

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
            from grilo_falante.cognitive import AuditoriaHostil

            claim_repo = ClaimRepository()
            claims = await claim_repo.search("", limit=arguments.get("limit", 50))

            claims_data = [
                {
                    "id": c.claim_key,
                    "claim_text": c.claim_text,
                    "gmif_level": c.gmif_level.value if c.gmif_level else "M4",
                    "validation_status": c.validation_state.value if c.validation_state else "pending",
                }
                for c in claims
            ]

            if not claims_data:
                return [TextContent(type="text", text=json.dumps({
                    "claims_audited": 0,
                    "findings": [],
                    "audit_result": {"status": "no_claims", "message": "No claims to audit"},
                }))]

            auditoria = AuditoriaHostil()
            report = await auditoria.run_full_audit(claims=claims_data, governance_records=[])

            return [TextContent(type="text", text=json.dumps({
                "claims_audited": len(claims),
                "findings": report.findings,
                "audit_result": report.to_dict(),
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

        elif name == "grilo_semantic_search":
            from grilo_falante.backend.memory import MemPalaceCache, MEMPALACE_AVAILABLE
            if not MEMPALACE_AVAILABLE:
                return [TextContent(type="text", text=json.dumps({
                    "error": "MemPalace not available",
                    "results": [],
                }))]
            cache = MemPalaceCache()
            results = await cache.search(
                arguments["query"],
                limit=arguments.get("limit", 5),
            )
            return [TextContent(type="text", text=json.dumps({
                "query": arguments["query"],
                "results": results,
                "count": len(results),
                "source": "mempalace",
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
