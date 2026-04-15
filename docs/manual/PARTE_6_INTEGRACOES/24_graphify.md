# 24. Graphify

## O Que é?

Graphify é um sistema de **extração de conhecimento** que analiza código e documentos para criar grafos de entidades e relações.

**No Grilo Falante:** É usado como primeiro passo do pipeline de análise.

---

## Pipeline Completo

```
Graphify (extracção)
        │
        ▼
Grilo Falante (governance)
        │
        ▼
MemPalace (cache)
        │
        ▼
PostgreSQL (autoritativo)
```

---

## Graphify vs Grilo Falante

| Aspeto | Graphify | Grilo Falante |
|--------|----------|----------------|
| **Objetivo** | Extrair entidades e relações | Governar afirmações |
| **Output** | Grafo de conhecimento | Claims classificadas |
| **Focus** | Estrutura do conhecimento | Verdade/Provas |
| **GMIF** | Não | Sim (M1-M7) |

---

## Uso via Skill

```bash
/graphify <path>              # Full pipeline
/graphify <path> --mode deep  # Thorough extraction
/graphify <path> --update    # Incremental
/graphify <path> --no-viz    # Skip visualization
/graphify query "<question>" # Query
```

---

## Exemplos

### Extrair de diretório

```bash
/graphify ./src/myproject
```

**Output:**

```json
{
  "nodes": [
    {"id": "func_1", "label": "calculate_total", "type": "function"},
    {"id": "cls_1", "label": "OrderProcessor", "type": "class"},
    ...
  ],
  "edges": [
    {"source": "func_1", "target": "cls_1", "relation": "method_of"},
    ...
  ]
}
```

### Query ao grafo

```bash
/graphify query "How is the user authenticated?"
```

---

## Via Python

```python
from graphify.extract import extract
from graphify.build import build_from_json

# Extrair
files = list(Path('src/').glob('**/*.py'))
result = extract(files)

# Construir grafo
G = build_from_json(result)

# Aceder a nós e arestas
nodes = G.nodes(data=True)
edges = G.edges(data=True)
```

---

## Integração com Grilo Falante

Ficheiro: `app/integrations/graphify_integration.py`

### GraphifyGMIFPipeline

```python
class GraphifyGMIFPipeline:
    """Pipeline: Graphify → GMIF → MemPalace."""

    def __init__(self):
        self.graphify = GraphifyExtractor()
        self.gmif = GMIFClassifier()
        self.memory = SemanticMemory()

    def run(self, path: str) -> Dict:
        # 1. Graphify extraction
        graph_data = self.graphify.extract(path)

        # 2. Classificar com GMIF
        for node in graph_data["nodes"]:
            gmif_level = self.gmif.classify(
                node["label"],
                confidence=node.get("confidence", "EXTRACTED")
            )
            node["gmif"] = gmif_level

        # 3. Guardar em MemPalace
        self.memory.store(graph_data)

        return graph_data
```

---

## Confidence Tags

O Graphify usa tags de confiança:

| Tag | Significado |
|-----|-------------|
| `EXTRACTED` | Extraído diretamente do código/fonte |
| `INFERRED` | Inferido de contexto |
| `AMBIGUOUS` | Incerto, requer verificação |

**Mapeamento para GMIF:**

| Graphify | Grilo Falante GMIF |
|----------|-------------------|
| EXTRACTED | M1 (com múltiplas fontes) |
| INFERRED | M5 ou M6 |
| AMBIGUOUS | M4 (duvidoso) |

---

## Via Grilo Pipeline CLI

```bash
python3 grilo_pipeline.py <path> [opções]

Opções:
  --no-store     Não guardar
  --cache        Usar cache
  --export-html  Exportar dashboard HTML
  --verify-m4    Verificar claims M4
  --llm iaedu    Usar LLM iaedu
  --graph NAME   Graph name
```

---

## Output

```
grilo_output/
├── graph.json           # Grafo completo
├── gmif_annotated.json  # Nós com GMIF
├── claims.json         # Claims extraídas
└── html/
    └── dashboard.html  # Visualização
```

---

## Troubleshooting

### "graphify: command not found"

```bash
pip install graphify
# ou
python3 -m graphify --version
```

### Graphify lento

```bash
# Usar cache
/graphify ./src --update

# Apenas re-clustering
/graphify ./src --cluster-only
```

---

## Referência

- **Graphify Skill:** `/home/rodolfo/.claude/skills/graphify/SKILL.md`
- **GitHub:** https://github.com/rodolfomatos/graphify

---

*Voltar ao [Índice](../00_INDICE.md)*
