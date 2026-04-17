"""
Data fetchers for Visualizer

Provides structured data objects for each visualization type.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ClaimData:
    """Single claim with GMIF data."""
    id: int
    claim_key: str
    claim_text: str
    gmif_level: str
    gmif_confidence: float
    source_id: Optional[int] = None
    source_title: Optional[str] = None
    epistemic_role: Optional[str] = None
    validation_status: Optional[str] = None
    legitimacy_state: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MembroIlhaData:
    """Member (pedra) of an island."""
    id: int
    name: str
    tipo: str
    saliencia: float


@dataclass
class RelacaoIlhaData:
    """Relationship between islands."""
    target_ilha_key: str
    tipo: str
    target_title: str


@dataclass
class IlhaData:
    """Island (ilha) with members and relationships."""
    id: int
    ilha_key: str
    title: str
    description: str
    estado: str
    membros: List[MembroIlhaData] = field(default_factory=list)
    relacoes: List[RelacaoIlhaData] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class GraphNodeData:
    """Graph node."""
    id: str
    label: str
    node_type: str
    gmif_level: Optional[str] = None


@dataclass
class GraphEdgeData:
    """Graph edge."""
    source: str
    target: str
    edge_type: str


@dataclass
class GraphData:
    """Knowledge graph data."""
    nodes: List[GraphNodeData] = field(default_factory=list)
    edges: List[GraphEdgeData] = field(default_factory=list)


@dataclass
class SourceData:
    """Source document."""
    id: int
    source_key: str
    title: str
    authors: List[str]
    year: Optional[int]
    doi: Optional[str]
    url: Optional[str]
    tier: str


@dataclass
class GapData:
    """Knowledge gap."""
    id: int
    gap_key: str
    query: str
    gap_type: str
    status: str
    reason: Optional[str] = None


@dataclass
class SearchResult:
    """Search result."""
    result_type: str
    key: str
    title: str
    snippet: str
    url: str


class VisualizerData:
    """Main data fetcher for Visualizer."""
    
    async def get_ilhas(self, limit: int = 50) -> List[IlhaData]:
        """Get all islands."""
        from grilo_falante.backend.db.ilhas_repository import IlhaRepository
        
        repo = IlhaRepository()
        ilhas = await repo.listar(limit=limit)
        
        result = []
        for ilha in ilhas:
            membros_data = [
                MembroIlhaData(id=m.member_id, name=m.member_id, tipo=m.tipo, saliencia=m.saliência) 
                for m in ilha.membros
            ]
            relacoes_data = [
                RelacaoIlhaData(target_ilha_key=r.ilha_id, tipo=r.tipo.value if hasattr(r.tipo, 'value') else str(r.tipo), target_title=r.ilha_id) 
                for r in ilha.relações
            ]
            
            result.append(IlhaData(
                id=ilha.id,
                ilha_key=ilha.id,
                title=ilha.nome or ilha.id,
                description=ilha.descrição or "",
                estado=str(ilha.estado.value) if hasattr(ilha.estado, 'value') else str(ilha.estado),
                membros=membros_data,
                relacoes=relacoes_data,
                created_at=ilha.data_criação,
                updated_at=None,
            ))
        return result
    
    async def get_ilha_by_key(self, key: str) -> Optional[IlhaData]:
        """Get island by key."""
        from grilo_falante.backend.db.ilhas_repository import IlhaRepository
        
        repo = IlhaRepository()
        ilha = await repo.buscar_por_key(key)
        
        if notilha:
            return None
        
        membros_data = [
            MembroIlhaData(id=m.member_id, name=m.member_id, tipo=m.tipo, saliencia=m.saliência) 
            for m in ilha.membros
        ]
        relacoes_data = [
            RelacaoIlhaData(target_ilha_key=r.ilha_id, tipo=r.tipo.value if hasattr(r.tipo, 'value') else str(r.tipo), target_title=r.ilha_id) 
            for r in ilha.relações
        ]
        
        return IlhaData(
            id=ilha.id,
            ilha_key=ilha.id,
            title=ilha.nome or ilha.id,
            description=ilha.descrição or "",
            estado=str(ilha.estado.value) if hasattr(ilha.estado, 'value') else str(ilha.estado),
            membros=membros_data,
relacoes=relacoes_data,
            created_at=ilha.data_criação,
            updated_at=None,
        )
    
    async def get_claims(self, limit: int = 100) -> List[ClaimData]:
        """Get all claims."""
        from grilo_falante.backend.db.repositories import ClaimRepository
        
        repo = ClaimRepository()
        claims = await repo.search("%", session_id=None, limit=limit)
        
        result = []
        for c in claims:
            result.append(ClaimData(
                id=c.id,
                claim_key=str(c.claim_key),
                claim_text=str(c.claim_text),
                gmif_level=str(c.gmif_level.value) if hasattr(c.gmif_level, 'value') else str(c.gmif_level),
                gmif_confidence=float(c.gmif_confidence),
                source_id=c.source_id,
                source_title=None,
                epistemic_role=str(c.epistemic_role.value) if hasattr(c.epistemic_role, 'value') else str(c.epistemic_role),
                validation_status=str(c.validation_status.value) if hasattr(c.validation_status, 'value') else str(c.validation_status),
                legitimacy_state=str(c.legitimacy_state.value) if hasattr(c.legitimacy_state, 'value') else str(c.legitimacy_state),
                created_at=c.created_at,
                updated_at=c.updated_at,
            ))
        return result
    
    async def get_graph(self, limit: int = 200) -> GraphData:
        """Get knowledge graph."""
        from grilo_falante.backend.db.repositories import ClaimRepository
        
        repo = ClaimRepository()
        claims = await repo.search("%", session_id=None, limit=limit)
        
        nodes = [
            GraphNodeData(
                id=c.claim_key,
                label=c.claim_text[:50] + "..." if len(c.claim_text) > 50 else c.claim_text,
                node_type="claim",
                gmif_level=str(c.gmif_level.value) if hasattr(c.gmif_level, 'value') else str(c.gmif_level),
            ) for c in claims
        ]
        
        return GraphData(nodes=nodes, edges=[])
    
    async def get_sources(self, limit: int = 50) -> List[SourceData]:
        """Get all sources."""
        from grilo_falante.backend.db.repositories import SourceRepository
        
        repo = SourceRepository()
        sources = await repo.list_all(limit=limit)
        
        return [
            SourceData(
                id=s.id,
                source_key=s.source_key,
                title=s.title,
                authors=s.authors or [],
                year=s.year,
                doi=s.doi,
                url=s.url,
                tier=str(s.tier.value) if hasattr(s.tier, 'value') else str(s.tier),
            ) for s in sources
        ]
    
    async def get_gaps(self, limit: int = 50) -> List[GapData]:
        """Get all gaps."""
        from grilo_falante.backend.db.repositories import GapRepository
        
        repo = GapRepository()
        gaps = await repo.list_all(limit=limit)
        
        return [
            GapData(
                id=g.id,
                gap_key=g.gap_key,
                query=g.query,
                gap_type=str(g.gap_type.value) if hasattr(g.gap_type, 'value') else str(g.gap_type),
                status=str(g.status.value) if hasattr(g.status, 'value') else str(g.status),
                reason=g.reason,
            ) for g in gaps
        ]
    
    async def search(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Search across all entities."""
        results = []
        
        ilhas = await self.get_ilhas(limit=50)
        for i in ilhas:
            if query.lower() in i.title.lower() or query.lower() in i.description.lower():
                results.append(SearchResult(
                    result_type="ilha",
                    key=i.ilha_key,
                    title=i.title,
                    snippet=i.description[:100] + "..." if len(i.description) > 100 else i.description,
                    url=f"/visualizer/ilhas/{i.ilha_key}",
                ))
        
        claims = await self.get_claims(limit=50)
        for c in claims:
            if query.lower() in c.claim_text.lower():
                results.append(SearchResult(
                    result_type="claim",
                    key=c.claim_key,
                    title=c.claim_text[:50] + "..." if len(c.claim_text) > 50 else c.claim_text,
                    snippet=c.claim_text[:100],
                    url=f"/visualizer/claims/{c.claim_key}",
                ))
        
        return results[:limit]