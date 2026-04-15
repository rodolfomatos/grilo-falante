# 20. RAG e Pesquisa Semântica

## O Que É RAG?

RAG = Retrieval-Augmented Generation

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  LLM                                                        │
│    │                                                        │
│    │ Prompt + Contexto                                      │
│    ▼                                                        │
│  ┌──────────────┐                                          │
│  │  RETRIEVAL   │  ◄── Acede memória                      │
│  └──────┬───────┘                                          │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────┐                                          │
│  │   STORAGE    │  ◄── Guarda conhecimento                 │
│  └──────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## RAG no Grilo Falante

### Retrieval

```python
# Fast search (MemPalace)
grilo_semantic_search(query="mudanças climáticas", limit=5)

# Deep search (PostgreSQL + pgvector)
gepeto_query(query="quais são as evidências?")
```

---

### Storage

```python
# Guardar claim
gepeto_create_claim(
    claim_text="A temperatura aumentou 1.1°C",
    gmif_level="M5"
)
# → PostgreSQL + MemPalace
```

---

## Pesquisa Semântica

### MemPalace (Fast)

```python
results = await cache.search("query")
# ~10ms
# Returns: [{"text": "...", "score": 0.8, "wing": "..."}]
```

---

## Hybrid Retrieval

Combina semantic + epistemic scores:

```python
# Score = 0.65 * semantic + 0.35 * epistemic
results = hybrid_retriever.retrieve(query, limit=10)
```

---

## Embeddings

### Ollama

```python
from grilo_falante.backend.memory.vector_index import VectorIndex

vector = VectorIndex()
embedding = await vector.embed("texto a embedar")
# Dimensão: 768
```

---

## Grafo de Conhecimento

### Relations

```python
# supports, contradicts, depends_on
kg.add_relationship(
    from_claim="CLM-001",
    to_claim="CLM-002",
    relation_type="supports"
)
```

---

## Exemplo Completo

```python
# 1. Fazer query
query = "Quais são os efeitos das mudanças climáticas?"

# 2. Retrieval
context = await hybrid_retriever.retrieve(query, limit=5)

# 3. Generate
prompt = f"""
Contexto: {context}

Pergunta: {query}

Responde baseando-te no contexto.
"""
```

---

## RAG API

```bash
# Semantic search
GET /api/v1/semantic-search?q=mudanças%20climáticas

# Query with RAG
POST /api/v1/query
{
  "query": "Quais são as conclusões?",
  "rag": true
}
```

---

*Voltar ao [Índice](../00_INDICE.md)*
