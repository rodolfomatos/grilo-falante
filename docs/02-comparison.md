# Comparação — Implementação vs Requisitos

## 1. Arquitetura Atual

```
Input (path ou texto)
    │
    ▼
┌──────────────────┐
│ Extract (graphify) │ ← Extrai nós + arestas
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ Classify (GMIF)   │ ← M1-M7 baseado em edge types
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ Generate GF-ID    │ ← SHA256 hash
└──────────────────┘
    │
    ▼
┌──────────────────┐
│ Store (MemPalace/JSON) │
└──────────────────┘
    │
    ▼
Output: JSON + optional HTML
```

---

## 2. O Que system.md Exige

### 2.1 Antes de Executar: ACORDAR Ritual

```
ACORDAR
Data: 2026-04-12
Intenção: <declaração explícita>
```

**Diferença:**
- current: executa imediatamente
- required: exige ritual de entrada primeiro

### 2.2 Durante Execução: Graph-Based Governance

Todo raciocínio deve:
1. Estar ancorado a um grafo materializado
2. Declarar explicitamente o grafo usado
3. Declarar o estado atual
4. Declarar a transição validada

**Diferença:**
- current: extrai grafo, mas não o usa para governar
- required: grafo é governante, não apenas extraído

### 2.3 Após Execução: Lint Cognitivo

Estados: ACCEPT | CONDITIONAL | REJECT | REEXECUTE

**Diferença:**
- current: não há verificação
- required: toda output passa pelo Lint

### 2.4 Estados de Legitimidade

```
LEGITIMACY_SUSPENDED → default
LEGITIMACY_ASSERTED  → exige humana explícita
```

**Diferença:**
- current: todos conceitos tratados igualmente
- required: distinción explícita

---

## 3. Comparação Detalhada

| Aspetto | Agora | Deveria (system.md) | Gap |
|---------|-------|---------------------|-----|
| **Entrada** | Imediata | ACORDAR ritual | CRÍTICO |
| **Extração** | graphify | graphify + ancoragem a grafo | MÉDIO |
| **Classificação** | Heurístico simples (edge types) | GMIF completo (fontes, contradições, temporal) | ALTO |
| **Identificação** | GF-ID (6 char hash) | GF-ID + legitimidade | BAIXO |
| **Persistência** | MemPalace ou JSON | MemPalace + artefacto materializado | BAIXO |
| **Verificação** | Apenas humano (M4) | Lint Cognitivo automático | CRÍTICO |
| **Saída** | JSON + HTML | JSON + artefacto + legitimidade | ALTO |
| **Governação** | Nenhuma | Graph-based + BLOCK | CRÍTICO |

---

## 4. Comparação com epistemic-memory-architecture

### O que o EMA tem

| Componente | Descrição | No Skill? |
|------------|-----------|-----------|
| `evidence_engine.py` | Calcula epistemic score | ❌ |
| `gmif_graph_builder.py` | Classificação real GMIF | ❌ |
| PostgreSQL + pgvector | Base de dados vetorial | ❌ |
| FastAPI completo | API com endpoints | ⚠️ Parcial |
| Claim governance | Estados de claim | ❌ |

### O que falta para ter GMIF completo

1. Integrar `evidence_engine.py` para calcular scores
2. Usar `gmif_graph_builder.py` para classificação
3. Adicionar base de dados PostgreSQL
4. Implementar claim states (PENDING, VERIFIED, REJECTED, etc.)

---

## 5. Matriz de Implementação

| Feature | Status | Prioridade |
|---------|--------|------------|
| graphify extraction | ✅ Feito | - |
| GMIF básica | ⚠️ Feito (simplista) | Melhorar |
| GF-ID | ✅ Feito | - |
| MemPalace | ✅ Feito | - |
| API FastAPI | ⚠️ Feito (básico) | Melhorar |
| ACORDAR | ❌ Falta | ALTA |
| LEGITIMACY states | ❌ Falta | ALTA |
| Graph governance | ❌ Falta | ALTA |
| PINA | ❌ Falta | MÉDIA |
| Lint Cognitivo | ❌ Falta | ALTA |
| BLOCK behavior | ❌ Falta | MÉDIA |
| HTML export | ✅ Feito | - |

---

## 6. Conclusão

O skill atual é uma **ferramenta de análise** funcional mas:

1. **Não executa o regime** — falta o ACORDAR ritual
2. **Não governa** — falta graph-based governance
3. **Não verifica** — falta Lint Cognitivo
4. **Não distingue** — falta estados de legitimidade

Para ser um verdadeira **implementação do regime**, precisa adicionar estes componentes.