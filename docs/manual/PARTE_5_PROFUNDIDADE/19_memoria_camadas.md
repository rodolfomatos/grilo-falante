# 19. Memória em Camadas

## Arquitetura de 4 Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  CAMADA 1: MemPalace (Cache)                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • Fast semantic search (~10ms)                      │  │
│  │ • ChromaDB                                          │  │
│  │ • Wing: wing_conversas                              │  │
│  │ • First-pass cache                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  CAMADA 2: Vector Index (pgvector)                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • Embedding similarity search                       │  │
│  │ • Ollama (nomic-embed-text)                       │  │
│  │ • 768 dimensions                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  CAMADA 3: Knowledge Graph (PostgreSQL)                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • Typed relationships                              │  │
│  │ • supports / contradicts / depends_on              │  │
│  │ • BFS traversal                                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  CAMADA 4: PostgreSQL (Authoritative)                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • Claims, Sources, Curators                        │  │
│  │ • GF-IDs                                          │  │
│  │ • Governance records                              │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Fluxo de Dados

```
QUERY
  │
  ├─► CAMADA 1: MemPalace (cache)
  │       Se hit → retorna
  │       Se miss → │
  │                  │
  ├─► CAMADA 2: Vector Index
  │       Se hit → retorna + cache em MemPalace
  │       Se miss → │
  │                  │
  ├─► CAMADA 3: Knowledge Graph
  │       Obtém relationships
  │                  │
  └─► CAMADA 4: PostgreSQL
          Retorna authoritative
```

---

## Quando Usar Cada Camada

| Camada | Uso | Latência |
|--------|-----|----------|
| MemPalace | Fast context (~10ms) | ~10ms |
| Vector | Semantic similarity | ~50ms |
| Knowledge Graph | Relationships | ~100ms |
| PostgreSQL | Authoritative | ~100ms |

---

## Código

```python
from grilo_falante.backend.memory import (
    MemPalaceCache,
    VectorIndex,
    KnowledgeGraphStore,
    HybridRetriever
)

# Camada 1: MemPalace
cache = MemPalaceCache()
results = await cache.search("query")  # ~10ms

# Camada 2: Vector
vector = VectorIndex()
embeddings = await vector.embed("query")

# Camada 3: Knowledge Graph
kg = KnowledgeGraphStore()
neighbors = kg.get_neighbors("CLM-xxx")

# Camada 4: PostgreSQL (via repository)
repo = ClaimRepository()
claims = await repo.search("query", limit=20)
```

---

*Voltar ao [Índice](../00_INDICE.md)*
