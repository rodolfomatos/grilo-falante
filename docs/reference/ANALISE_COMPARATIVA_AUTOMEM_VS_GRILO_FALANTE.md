# Análise Comparativa: AutoMem vs Grilo Falante

**Data:** 2026-04-16
**Versão:** 1.0
**Status:** Final
**Preparado para:** Decisão de arquitetura

---

## 1. Sumário Executivo

O Grilo Falante e o AutoMem resolvem **problemas fundamentalmente diferentes** e são orthogonalmente complementares:

| Projeto | Problema Resolvido | Foco |
|---------|------------------|------|
| **AutoMem** | "Como lembrar?" | Memória associativa |
| **Grilo Falante** | "Como não decidir errado?" | Governança epistémica |

**Recomendação:** Adicionar AutoMem como camada superior de recall, mantendo o Grilo Falante como authoritative.

---

## 2. Visão Geral dos Projetos

### 2.1 AutoMem — verygoodplugins/automem

**Repo:** https://github.com/verygoodplugins/automem

#### Filosofia
"MCP server for memory management and information retrieval in AI assistants."

#### Problema Resolvido
LLMs esquecem contexto entre sessões. AutoMem fornece memória persistente associativa.

#### Arquitetura
```
┌─────────────────────────────────────────┐
│         AutoMem Service                  │
│  ┌─────────────┐  ┌────────────┐  │
│  │  FalkorDB   │  │  Qdrant   │  │
│  │  (Graph)   │  │ (Vectors) │  │
│  └─────────────┘  └────────────┘  │
└─────────────────────────────────────────┘
```

#### Componentes Principais

| Componente | Descrição |
|-----------|----------|
| **FalkorDB** | Graph database para relações entre memórias |
| **Qdrant** | Vector database para similarity search |
| **9-component Scoring** | vector×0.25 + keyword×0.15 + relation×0.25 + content×0.25 + temporal×0.15 + tag×0.10 + importance×0.05 + confidence×0.05 + recency×0.10 |

#### Features

1. **Store**: Memórias com metadata, importância, timestamps
2. **Recall**: Scoring híbrido multi-componente
3. **Associate**: 11 tipos de relações (RELATES_TO, PREFERS_OVER, LEADS_TO, etc.)
4. **Enrichment**: Extração automática de entidades, auto-tagging, summaries
5. **Consolidation**: Ciclos inspirados em neurociência (decay diário, creative semanal, cluster mensal)

#### Benchmarks

- LoCoMo (ACL 2024): **89.27%** em locomo-mini, **87.56%** em locomo completo
- Tempo de resposta: ~50ms para recall

---

### 2.2 Grilo Falante — grilo-falante

**Repo:** https://github.com/anomalyco/grilo-falante

#### Filosofia
> *"Este regime não impede erros. Impede que erros sejam cometidos sem que alguém tenha de olhar para eles de frente."*

#### Problema Resolvido
LLMs podem "decidir" sem método explícito. O Grilo Falante exige governança epistémica.

#### Arquitetura
```
┌─────────────────────────────────────────────────────────────────────┐
│                    GRILO FALANTE v3.0                         │
├─────────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI + MCP)                                    │
├─────────────────────────────────────────────────────────────────┤
│  Service Layer                                                 │
│  ├── Core: QueryPipeline, GapDetection, GMIFClassifier       │
│  └── Governance: GovernanceLayer, PINA, GraphLint             │
├─────────────────────────────────────────────────────────────────┤
│  Memory Architecture                                          │
│  ├── MemPalaceCache (ChromaDB) - Fast recall                  │
│  ├── Vector Index (pgvector) - Semantic                       │
│  └── Knowledge Graph - Epistemic                              │
├─────────────────────────────────────────────────────────────────┤
│  Regime Layer: State Machine (INACTIVE→LOADED→ACTIVE→GOVERNING)│
└─────────────────────────────────────────────────────────────────┘
```

#### Componentes Principais

| Componente | Descrição |
|-----------|----------|
| **GMIF (M1-M8)** | Classificação epistémica com blocking rules |
| **Graph Lint (L1-L8)** | Verificações de integridade do grafo |
| **PINA Protocol** | Decisões humanas sobre normas |
| **Auditoria Hostil** | Teste crítico de 5 eixos |
| **Cycle State Machine** | INACTIVE → LOADED → ACTIVE → GOVERNING |
| **Shadow Documents** | Validação de fontes |

---

## 3. Análise Comparativa Dimensional

### 3.1 Foco e Filosofia

| Dimensão | AutoMem | Grilo Falante |
|---------|---------|---------------|
| **Problema** | AI esquece entre sessões | Decisões sem método explícito |
| **Foco** | Memória associativa | Governança cognitiva |
| **Fililosofia** | "Lembrar como humanos" | "Impedir decisões sem custo humano visível" |
| **Resultado** | Recall eficiente | Decisões governadas |

### 3.2 Arquitetura de Memória

| Dimensão | AutoMem | Grilo Falante |
|---------|---------|---------------|
| **Graph** | FalkorDB (native) | PostgreSQL graph |
| **Vector** | Qdrant | pgvector + ChromaDB |
| **Scoring** | 9-componente | 65% semantic + 35% epistemic |
| **Relação mais forte** | Bridge discovery | Graph Lint |

### 3.3 Tipos de Relações

**AutoMem — 11 tipos arbitrários:**
- RELATES_TO, PREFERS_OVER, LEADS_TO, SUPPORTS, OPPOSES, DERIVES_FROM, etc.

**Grilo Falante — 4 tipos estruturados:**
- CONTRADIZ (bloqueante)
- COMPLEMENTA (acrescenta)
- DERIVA_DE (pressupõe)
- AGREGADO_EM (pertence a)

### 3.4 Sistema de Classificação

**AutoMem:**
- Sem sistema de classificação epistémica
- Apenas scoring de relevância

**Grilo Falante — GMIF Levels:**

| Level | Name | Confidence | Blocking |
|-------|------|------------|----------|
| M1 | Primary Evidence | 0.8-1.0 | - |
| M2 | Contextual | 0.6-0.9 | - |
| M3 | Partial | 0.4-0.7 | - |
| M4 | **Doubtful** | 0.1-0.5 | M4 + conf < 0.3 = BLOCK |
| M5 | Interpretation | 0.5-0.8 | - |
| M6 | Derived | 0.4-0.7 | - |
| M7 | Synthesis | 0.5-0.8 | - |
| M8 | Conclusion | 0.3-0.7 | - |

### 3.5 Sistema de Validação

**AutoMem:**
- Sem sistema de validação
- Sem auditoria

**Grilo Falante:**

| Sistema | Descrição |
|---------|----------|
| **Graph Lint (L1-L8)** | L1=orphan, L2=self-ref, L3=contradict, L4=cycle, L5=unsupported, L6=missing M1, L7=confidence mismatch, L8=temporal |
| **Auditoria Hostil** | 5 eixos: automático, validação, grafos, ledger, norma |
| **PINA** | Decision [A/B/C] por humano |

### 3.6 Ciclo de Vida

**AutoMem:**
- Store → Consolidate → Forget (implícito)
- Decay automático baseado em neurociência

**Grilo Falante:**
- INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
- Acordar (temporal anchor + intention)
- Dormir (agregação + relatório)

---

## 4. Comparação de Features

| Feature | AutoMem | Grilo Falante |
|---------|---------|--------------|
| Vector search | ✓ (Qdrant) | ✓ (pgvector) |
| Graph relationships | ✓ (FalkorDB) | ✓ (PostgreSQL) |
| Hybrid recall | ✓ (9-componente) | ✓ (65/35) |
| Bridge discovery | ✓ | ✗ |
| GMIF classification | ✗ | ✓ (M1-M8) |
| Graph Lint | ✗ | ✓ (L1-L8) |
| PINA Protocol | ✗ | ✓ |
| Auditoria Hostil | ✗ | ✓ |
| State lifecycle | ✗ | ✓ (ACORDAR/DORMIR) |
| Shadow Documents | ✗ | ✓ |
| Human-in-the-loop | ✗ (opcional) | ✓ (PINA) |
| Entity enrichment | ✓ | ✗ |
| Consolidation cycles | ✓ | ✗ |

---

## 5. O Que AutoMem Traz de Novo

| Componente | Valor para Grilo Falante |
|-----------|------------------------|
| **FalkorDB** | Graph mais otimizado que PostgreSQL |
| **Qdrant** | Vectors mais rápidos que pgvector |
| **Bridge Discovery** | Conexões multi-hop entre ilhas |
| **9-componente scoring** | Complementar ao 65/35 |
| **Enrichment** | Auto-extração de entidades |
| **Consolidation cycles** | Decay/cluster automáticos |

---

## 6. O Que É Único no Grilo Falante

| Componente | Descrição |
|-----------|----------|
| **GMIF (M1-M8)** | Classificação epistémica com blocking rules — não existe em nenhum outro projeto |
| **PINA** | Decisões Normative Candidate por humano |
| **Graph Lint (L1-L8)** | Verificações de integridade automatizadas |
| **Auditoria Hostil** | Teste crítico sistemático |
| **Acordar/Dormir** | Ciclo com ancoragem temporal |
| **Shadow Documents** | Validação de fontes |

---

## 7. Sistema de Memória Insular: Pedras e Ilhas

### 7.1 Metáfora Original

> **Lago:** Campo de fundo da memória
> **Pedra:** Interação relevante que cria saliência
> **Ilha:** Agregado cognitivo consolidado

### 7.2 Comparação com AutoMem

| Conceito Grilo Falante | Equivalente AutoMem | Diferença |
|------------------------|---------------------|-----------|
| Lago | FalkorDB + Qdrant | Mais sofisticado |
| Pedra | Memory item | + saliência calculada |
| Ilha | Cluster | + ecologia interna |
| Wing | Tag/Category | + estado (ativa/dorminte) |

### 7.3 Dinâmica Temporal

| Sistema | AutoMem | Grilo Falante |
|---------|---------|---------------|
| Decay | Automático (neurociência) | Manual (dormir cycle) |
| Reativação | Implícita |Explícita (acordar) |
| Transformação | Cluster automático | Decisão humana |

---

## 8. Conclusão

### 8.1 Orthogonalidade

Os sistemas resolvem **problemas diferentes**:
- AutoMem: "como recordar eficientemente?"
- Grilo Falante: "como decidir corretamente?"

Não competem — completam-se.

### 8.2 Decisão Recomendada

**RECOMENDAÇÃO FINAL:**

1. **Manter** MemPalace atual + PostgreSQL + GMIF/PINA
2. **Adicionar** AutoMem como camada opcional de cache
3. **Não substituir** — não remover nada

### 8.3 Arquitetura Híbrida Proposta

```
┌─────────────────────────────────────────────┐
│            CONSULTA                         │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │ (optional)
        ▼
┌─────────────────────────────────────────────┐
│  CAMADA 1: AutoMem (opcional)               │
│  • FalkorDB + Qdrant                       │
│  • Bridge discovery                       │
└──────���─���────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  CAMADA 2: MemPalace (MANTER)               │
│  • Wings: ilhas, pedras, claims            │
│  • Ciclo dormir/acordar                   │
└─────────────────┬───────────────────────┘
                  │ (cache miss)
                  ▼
┌─────────────────────────────────────────────┐
│  CAMADA 3: PostgreSQL (MANTER - AUTHORITY) │
│  • Claims + GMIF                          │
│  • Graph Lint                            │
│  • PINA + Auditoria                      │
└─────────────────────────────────────────────┘
```

---

## Referências

- AutoMem: https://github.com/verygoodplugins/automem
- MCP-AutoMem: https://github.com/verygoodplugins/mcp-automem
- Grilo Falante: https://github.com/anomalyco/grilo-falante
- Memo Anchor (Ilhas): `docs/reference/memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md`