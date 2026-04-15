# 23. MemPalace

## O Que é?

MemPalace é um sistema de **memória semântica** baseado em ChromaDB. No Grilo Falante, é usado como:

- **Cache rápido** (~10ms por query)
- **Pesquisa semântica** de contexto
- **Wings** para organizar conhecimentos

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Query                                                     │
│      │                                                     │
│      ▼                                                     │
│   ┌───────────────┐                                        │
│   │  MemPalace    │  ← Cache semântico (~10ms)            │
│   │  (ChromaDB)   │                                        │
│   └───────┬───────┘                                        │
│           │ Hit?                                           │
│      ┌────┴────┐                                           │
│      │         │                                           │
│     YES       NO                                           │
│      │         │                                           │
│      ▼         ▼                                           │
│   Devolver  PostgreSQL + pgvector                         │
│   resultado   (autoritativo)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Dados

### Path

```
/home/rodolfo/.mempalace/
├── chroma.sqlite3          # Base de dados ChromaDB
├── config.json             # Configuração
├── knowledge_graph.sqlite3 # Grafo de conhecimento
└── palace/
    ├── bbc18c3b-.../      # Collection UUID
    │   ├── data_level0.bin
    │   ├── header.bin
    │   └── ...
    └── chroma.sqlite3       # Metadados das collections
```

### Collections

| Collection | Descrição |
|------------|-----------|
| `mempalace_drawers` | Claims e conhecimento |

### Wings

Os wings organizam o conhecimento por domínio:

| Wing | Descrição |
|------|-----------|
| `emotions` | Conteúdo sobre emoções |
| `consciousness` | Temas de consciência |
| `memory` | Processos de memória |
| `technical` | Conteúdo técnico |
| `identity` | Identidade e pessoa |
| `family` | Família e relações |
| `creative` | Criatividade |

---

## API

### Python

```python
from mempalace.searcher import search_memories
from mempalace.knowledge_graph import KnowledgeGraph

# Pesquisa
results = search_memories(
    query="mudanças climáticas",
    n_results=5,
    palace_path="/home/rodolfo/.mempalace/palace"
)
# Returns: {'query': '...', 'results': [{'text': ..., 'wing': ..., 'room': ..., 'similarity': ...}]}

# Knowledge Graph
kg = KnowledgeGraph("/home/rodolfo/.mempalace/knowledge_graph.sqlite3")
kg.add_claim(
    claim_id="CLM-001",
    claim_text="A temperatura aumentou 1.1°C",
    gmif_type="M5",
    metadata={"source": "IPCC"}
)
```

### Via Grilo Falante

```bash
# Pesquisa semântica
/grilo chat
> grilo_semantic_search(query="aquecimento global", limit=5)

# Resultado:
{
  "query": "aquecimento global",
  "results": [
    {"text": "...", "wing": "technical", "score": -0.129},
    ...
  ],
  "count": 5,
  "source": "mempalace"
}
```

---

## No Grilo Falante

### MemPalaceCache

Ficheiro: `grilo_falante/backend/memory/mempalace_cache.py`

```python
class MemPalaceCache:
    """Cache semântico usando MemPalace."""

    def __init__(self):
        self.palace_path = "/home/rodolfo/.mempalace/palace"
        self.collection_name = "mempalace_drawers"

    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Pesquisa semântica."""
        results = search_memories(
            query=query,
            n_results=limit,
            palace_path=self.palace_path,
        )
        return [
            {
                "claim_id": r.get("source_file", ""),
                "claim_text": r.get("text", ""),
                "gmif_level": "M4",
                "score": r.get("similarity", 0.5),
                "wing": r.get("wing", ""),
                "room": r.get("room", ""),
            }
            for r in results.get("results", [])
        ]

    async def store(self, claim_id: str, claim_text: str, gmif_level: str) -> bool:
        """Guardar claim."""
        self._kg.add_claim(
            claim_id=claim_id,
            claim_text=claim_text,
            gmif_type=gmif_level,
        )
```

---

## Integração com Chat

No chat governado, o MemPalace é usado automaticamente:

```
User: "A temperatura global aumentou 1.1°C desde 1880"
         │
         ▼
ChatShell._store_claims()
         │
         ├──► MemPalace (cache rápido)
         │      wing=wing_conversas
         │
         └──► PostgreSQL (autoritativo)
                Tabela: governed_claims
```

---

## Wing `wing_conversas`

O chat governado usa o wing `wing_conversas` para guardar:

- Mensagens analisadas
- Claims extraídas
- Contexto conversacional

```python
# Em ChatShell
cache = MemPalaceCache()
await cache.store(
    claim_id=claim["id"],
    claim_text=claim["text"],
    gmif_level="M5",
    metadata={"wing": "wing_conversas", "session": self.session_id}
)
```

---

## Troubleshooting

### "Collection does not exist"

```bash
# Verificar collections
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/home/rodolfo/.mempalace/palace')
print('Collections:', client.list_collections())
"
```

### "Database locked"

```bash
# Matar processos chroma
pkill -f chroma
# Ou esperar e tentar novamente
```

### Performance

Se MemPalace estiver lento:

```bash
# Ver uso de recursos
top -p $(pgrep -f chroma)

# Limpar dados antigos (opcional)
# CUIDADO: isto apaga conhecimento
rm -rf /home/rodolfo/.mempalace/palace/*.bin
```

---

## Alternatives

Se MemPalace não estiver disponível, o sistema degrada graciosamente:

```python
try:
    cache = MemPalaceCache()
    results = await cache.search(query)
except Exception as e:
    logger.warning(f"MemPalace unavailable: {e}")
    results = []  # Fallback para PostgreSQL
```

---

## Referência

- **ChromaDB:** https://docs.trychroma.com/
- **MemPalace:** https://github.com/rodolfomatos/mempalace

---

*Voltar ao [Índice](../00_INDICE.md)*
