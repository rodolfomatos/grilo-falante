# ANÁLISE HOSTIL — gf_scientific_compiler_v_2_spec.md

## Resumo (Feynman)

O **Scientific Compiler** é como um professor que lê um artigo científico e pergunta:

> "O que é que realmente provas? Tens a evidência?"

O documento descreve um sistema que:
1. Lê artigos académicos
2. Extrai as afirmações (claims)
3. Verifica as fontes (shadow documents)
4. Constrói um grafo de raciocínio
5. Deteta argumentos frágeis

---

## ProbleMAS ENCONTRADOS (Análise Hostil)

### 1. **Pipeline não executa** — O pipeline está descrito mas não implementado
O documento mostra diagramas como:

```
Load GriloFalante Kernel
↓
Load Scientific Compiler
↓
...
```

Mas não há código real. Apenas markdown.

### 2. **Shadow Documents não existem** — O sistema pede "shadow corpus" mas não há
O documento diz:
> "Shadow documents form the evidence corpus used by the compiler"

Mas em todo o ambrosio_v2.5.0 não há pasta de shadow documents.

### 3. **GMIF parcialmente implementado** — Já temos classification, mas não graph DOT
O sistema atual (`grilo_pipeline.py`) já faz:
- GMIF classification (M1-M7)
- Claim extraction

Mas não gera grafos GraphViz.

### 4. **12 Stages, 0 Implementação**
O documento define 12 stages detallhados,mas nenhuma função Python existe.

### 5. **Claim Registry formato indefinido**
O documento mostra:

| C1 | ... |
| C2 | ... |

Mas não diz se é JSON, YAML, ou markdown table.

---

## OQUE FAZ SENTIDO

### Coisas boas no documento:
1. **Separação de responsabilidades** — GF (governance), SC (compiler), GMIF (graph)
2. **M4 como "Doubtful"** — Bom uso de vermelho para incerteza
3. **"Missing references do not block"** — Evita loops infinitos
4. **Linter Rules** — L1-L8 bien estruturados
5. **Critical Path** — Identifica fraquezas

---

## O QUE FALTA

1. ⛔ Implementação de cada Stage
2. ⛔ Parser de artigos académicos (PDF/DOI)
3. ⛔ Shadow document generator
4. ⛔ GraphViz DOT generator
5. ⛔ Fragility analyzer real
6. ⛔ Integração com MemPalace (para guardar shadow corpus)

---

## COMO INTEGRAR COM "IR À ESCOLA"

O "Ir à Escola" loop que implementei complementa o Scientific Compiler:

| Scientific Compiler | Ir à Escola (implementado) |
|-----------------|---------------------|
| Reference Verification | Active Search (mempalace → docs → web) |
| Claim Extraction | Gap Detector |
| GMIF Classification | Feynman Synthesize |
| Graph Construction | *falta* |
| Fragility Analysis | Why Loop |

**Falta**: Integrar graph generation.

---

## RECOMENDAÇÕES

### PRIORIDADE 1: Gerar Grafo DOT
```python
def build_gmif_graph(claims, evidence, gmif_types):
    dot_code = """
digraph EpistemicGraph {
node [style=filled];
"""
    for e in evidence:
        dot_code += f'{e.id} [label="{e.type}", fillcolor="{e.color}"];'
    return dot_code + "}"
```

### PRIORIDADE 2: Parser de Artigos
Usar `requests` + `BeautifulSoup` para buscar DOIs.

### PRIORIDADE 3: Shadow Document Generator
```python
def create_shadow_doc(reference):
    return {
        "metadata": {...},
        "claims": [...],
        "reliability": "M4"  # se não verificado
    }
```

### PRIORIDADE 4: Fragility Analyzer
Calcular critical path real.

---

## MÉTRICAS

| Métrica | Valor |
|--------|-------|
| Stages definidos | 12 |
| Linter rules | 8 |
| GMIF types | 7 |
| Implementado | ~20% |
| Em falta | ~80% |

---

*AUDITOR: Hostil*
*DATE: 2026-04-13*