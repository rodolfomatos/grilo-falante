# SHADOW DOCUMENT — MemPalace Integration Plan

**GF-ID:** SD-20260416-MEMPALACE-INTEGRATION
**Date:** 2026-04-16
**Type:** Integration Plan
**Status:** Draft

---

## 1. MemPalace Architecture (Summary)

Based on README and docs:

```
MemPalace
├── Storage: ChromaDB (vector store)
├── Knowledge Graph: SQLite (temporal entity-relationship)
├── Structure: Wings → Rooms → Halls → Drawers
├── MCP Server: 29 tools
└── Benchmarks: 96.6% R@5 raw
```

### Key Concepts:
- **Wing**: Person or project (top-level)
- **Room**: Topic within a wing
- **Hall**: Category (facts, events, discoveries, preferences, advice)
- **Drawer**: Original text chunks (verbatim storage)

---

## 2. Integration Options

### Option A: MemPalace as GF Storage Backend

MemPalace stores verbatim, GF transforms and classifies.

```
┌─────────────────────────────────────────────────────────────┐
│                     Grilo Falante                            │
├─────────────────────────────────────────────────────────────┤
│  Transform & Govern                                         │
│  ├── Extract claims                                         │
│  ├── Classify GMIF                                         │
│  ├── Track saliência                                       │
│  └── Create ILHA/PEDRA                                     │
└──────────────────────────┬──────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      MemPalace                               │
├─────────────────────────────────────────────────────────────┤
│  Store Verbatim                                            │
│  ├── Wings = ILHAs (by topic/participant)                  │
│  ├── Rooms = PEDRAs (by type/concept)                      │
│  ├── Drawers = Original content                            │
│  └── Knowledge Graph = PEDRA reuse connections              │
└─────────────────────────────────────────────────────────────┘
```

### Option B: Complementary Systems

MemPalace = long-term memory, GF = epistemic governance.

```
GF creates structured ILHA/PEDRA from interactions
         │
         ▼
MemPalace stores conversation verbatim for retrieval
         │
         ▼
When retrieving, GF can reference both:
- Transformed (governed) view
- Original verbatim context
```

### Option C: Use MemPalace MCP Server

Use MemPalace's 29 MCP tools for GF's memory operations.

```
GF (via MCP) ──────► MemPalace MCP Server
                              │
                              ▼
                      ChromaDB + SQLite
                      (semantic search +
                       knowledge graph)
```

---

## 3. Proposed Architecture

### 3.1 Dual Storage Approach

```
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ILHAManager                                                 │
│  ├── Structured ILHAs/PEDRAs (transformed)                  │
│  ├── In-memory + JSON persistence                           │
│  └── "Shadow First" methodology captured here                │
│                                                              │
│  MemPalace                                                   │
│  ├── Verbatim conversations                                  │
│  ├── Semantic search                                        │
│  └── Knowledge graph (temporal)                             │
│                                                              │
│  PostgreSQL (future)                                        │
│  ├── Articles, Users, Repositories                          │
│  └── Structured relational data                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Mapping

| MemPalace | GF Equivalent |
|-----------|---------------|
| Wing | ILHA or Topic cluster |
| Room | PEDRA or Concept |
| Hall | GMIF level or Content type |
| Drawer | Original text chunk |
| Knowledge Graph | PEDRA reuse connections |

---

## 4. Implementation Steps

### Phase 1: Connect MemPalace as Secondary Storage

```python
# In ILHAManager, after creating ILHA:
def _store_in_mempalace(ilha):
    """Store verbatim content in MemPalace."""
    # Create wing for ILHA
    wing_id = f"ilha_{ilha.id}"

    # Store original conversations in drawer
    for pedra in ilha.pedras:
        mempalace_cli.add_memory(
            content=pedra.content_summary,
            room=f"pedra_{pedra.id}",
            hall="discoveries"
        )
```

### Phase 2: Use MemPalace for Semantic Search

```python
# When searching for related ILHAs:
def search_ilhas(query: str) -> List[ILHA]:
    """Search ILHAs using MemPalace semantic search."""
    results = mempalace_cli.search(query)
    # Map MemPalace results back to ILHAs
    return [map_result_to_ilha(r) for r in results]
```

### Phase 3: Knowledge Graph Integration

```python
# Track PEDRA reuse in knowledge graph:
def track_reuse(pedra_id: str, from_ilha: str, to_ilha: str):
    """Add reuse connection to MemPalace knowledge graph."""
    mempalace_cli.add_entity_relation(
        entity_a=f"pedra_{pedra_id}",
        relation="reused_in",
        entity_b=f"ilha_{to_ilha}",
        timestamp=datetime.now().isoformat()
    )
```

---

## 5. Code Changes Required

### 5.1 New Module

```
grilo_admin/
└── services/
    └── mempalace_service.py  # NEW
```

### 5.2 ILHAManager Changes

```python
class ILHAManager:
    @classmethod
    def create_ilha(cls, data):
        # ... existing code ...

        # NEW: Store in MemPalace
        if cls._mempalace_enabled:
            cls._store_in_mempalace(ilha)

    @classmethod
    def _store_in_mempalace(cls, ilha):
        # ... implementation ...

    # NEW: Configuration
    _mempalace_enabled: bool = False
    _mempalace_path: Optional[str] = None
```

---

## 6. Open Questions

1. **Dual writes**: Should GF always write to both, or optional?
2. **Conflict resolution**: If MemPalace has different data than GF, which wins?
3. **MCP vs CLI**: Use MemPalace MCP server or CLI commands?
4. **Embedding model**: Which model to use for semantic search?
5. **Sync**: How to keep MemPalace and GF in sync?

---

## 7. Risks

- **Complexity**: Adding MemPalace increases system complexity
- **Dependency**: GF now depends on MemPalace
- **Data consistency**: Two sources of truth could diverge
- **Performance**: Semantic search adds latency

---

## 8. Recommendation

**Start with Option B (Complementary)**:

1. GF creates structured ILHA/PEDRA (already done)
2. Optionally store verbatim in MemPalace
3. Use MemPalace only for semantic search, not as primary storage
4. Keep JSON persistence as primary for now

This allows:
- Testing MemPalace integration without breaking existing code
- Learning what works before full integration
- Staying flexible on storage architecture

---

## 9. Next Steps

1. [ ] Create `mempalace_service.py` module
2. [ ] Implement basic MemPalace integration
3. [ ] Add CLI command to sync ILHAs to MemPalace
4. [ ] Test semantic search on ILHAs
5. [ ] Evaluate performance and complexity

---

**FIM DO DOCUMENTO**
Este é um plano de integração - não confere autoridade.
