# SHADOW DOCUMENT — MemPalace Analysis

**GF-ID:** SD-20260416-MP-001
**Source:** https://github.com/MemPalace/mempalace
**Date:** 2026-04-16
**Type:** Shadow Document (não-promotável, para análise)
**GMIF:** M5 (fontes secundárias, descrição de sistema)

---

## 1. O que é o MemPalace

**Definição:** Sistema de memória para IAs com armazenamento verbatim (texto original) e pesquisa semântica plugável.

**Claim principal:** "Local-first AI memory. Verbatim storage, pluggable backend, 96.6% R@5 raw on LongMemEval — zero API calls."

**Nota:** Shadow Document não confere autoridade. Para detalhes canónicos, ver o repositório oficial.

---

## 2. Arquitetura do Sistema

### 2.1 Componentes Principais

```
Palace (Estrutura de memória)
├── Wings (pessoas ou projetos)
├── Rooms (tópicos dentro de wings)
├── Halls (categorias conceptuais)
│   ├── hall_facts — decisões tomadas
│   ├── hall_events — sessões, marcos
│   ├── hall_discoveries — descobertas
│   ├── hall_preferences — hábitos, preferências
│   └── hall_advice — recomendações
├── Tunnels (ligações entre wings)
└── Drawers (texto original armazenado)
```

### 2.2 Camadas Técnicas

| Camada | Função |
|--------|--------|
| **Storage** | ChromaDB (default), plugável |
| **Embedding** | Modelo local (~300MB) |
| **Knowledge Graph** | SQLite local com entity-relationship temporal |
| **MCP Server** | 29 ferramentas para operações |

### 2.3 Fluxo de Dados

```
mine (conteúdo) → Drawers (verbatim) → Index (semântico)
                                       ↓
wake-up (novo contexto) ← search (recuperação)
```

---

## 3. Claim Extraídas (sem validação)

### 3.1 Claims Factuais

| Claim | Fonte | Observações |
|-------|-------|-------------|
| "96.6% R@5 raw" | README.md | Sem LLM, só pesquisa semântica |
| "98.4% held-out" | Benchmarks | Com hybrid v4, 50q dev |
| "≥99% with LLM rerank" | Benchmarks | Qualquer modelo capaz |
| "Zero API calls" | README.md | Para o path de benchmark |
| "Local-first" | README.md | Nada sai sem opt-in |

### 3.2 Claims de Design

| Claim | Análise |
|-------|---------|
| "Wings are top-level organizational unit" | Semelhante a ILHA no GF |
| "Rooms are named ideas" | Semelhante a PEDRA? |
| "Drawers are original text chunks" | Semelhante a content_summary |
| "Hall categories for memory types" | Semelhante a GMIF levels? |

---

## 4. Semelhanças com Grilo Falante

### 4.1 Convergências Observadas

| MemPalace | Grilo Falante | Semelhança |
|-----------|----------------|------------|
| Wing | ILHA | Agregado de contexto |
| Drawer | PEDRA (content) | Conteúdo armazenado |
| Room | PEDRA (topic) | Identificação de tópico |
| Hall | GMIF levels? | Categorização |
| Knowledge Graph | ILHA connections | Relações entre unidades |
| wake-up | ACORDAR | Inicialização de contexto |

### 4.2 Divergências

| MemPalace | Grilo Falante | Diferença |
|-----------|----------------|-----------|
| Verbatim storage | Materialização com transformação | GF transforma, não guarda verbatim |
| Semantic search | Rastreio epistémico + GMIF | GF tem classificação de confiança |
| No LLM for retrieval | LLM com regime de governação | GF usa LLM com regras |
| Auto-detection | Decisão deliberada | GF requer explicitação |

---

## 5. Perguntas de Análise (sem resposta)

### 5.1 Integração GF-MemPalace

1. **MemPalace pode ser o backend de armazenamento de PEDRAs?**
   - Drawers = content_summary?
   - Wings = ILHAs?

2. **Como adicionar GMIF e rastreio epistémico ao MemPalace?**
   - Adicionar metadata de GMIF aos drawers?
   - Criar hall_gmif para classificação?

3. **MemPalace guarda histórico temporal?**
   - PEDRA tem created_at e ended_at
   - MemPalace tem "temporal entity-relationship graph"

4. **Como funciona a deteção de eventos significativos?**
   - MemPalace auto-detecta rooms
   - GF requer decisão explícita de relevância

### 5.2 Questões Abertas

1. MemPalace guarda "conversations verbatim" — o GF guarda materialização com transformação. São complementares ou concorrentes?

2. O Knowledge Graph do MemPalace pode substituir ou integrar com o sistema de ILHAs?

3. O MCP server do MemPalace pode ser usado pelo GF?

4. Como adicionar "saliência" e "consequence_level" ao sistema de memória do MemPalace?

---

## 6. Observações Feynman

### 6.1 F1 (Para uma Criança)

O MemPalace é como uma casa com muitas salas. Cada sala tem uma gaveta com coisas que tu disseste. Quando precisas de lembrar de algo, vais ao corredor, e há portas para diferentes salas. Dentro de cada sala, há gavetas com as conversas todas.

### 6.2 F2 (Para Especialistas)

MemPalace implementa um "memory palace" clássico com:
- Armazenamento verbatim em ChromaDB
- Metadata filtering para scoping
- Knowledge graph temporal em SQLite
- Interface plugável para storage

GF adiciona:
- Regime de governação epistémica
- Classificação GMIF
- Materialização com transformação
- Rastreio de confiança

### 6.3 F3 (Why Loop - Lacunas)

**Porque é que o MemPalace guarda verbatim?**
> Para preservar fidelidade e evitar distorção por sumarização.

**Porque é que o GF transforma?**
> Para manter regime de governação e rastreio de confiança.

**GAP DETECTADO:** São duas abordagens complementares. GF precisa de fidelidade (MemPalace) E transformação governada. Como integrar?

---

## 7. Conclusão Provisória

MemPalace e Grilo Falante têm arquiteturas complementares:

- **MemPalace:** Storage verbatim + retrieval semântico + agents
- **GF:** Regime de governação + classificação epistémica + materialização

**Hipótese:** MemPalace pode ser o backend de armazenamento do GF, com additions de GMIF e regime de governação.

**Necessário:** Investigar integração técnica (MCP server? Knowledge Graph?).

---

## 8. Fontes

- https://github.com/MemPalace/mempalace
- https://mempalaceofficial.com/concepts/the-palace.html
- https://mempalaceofficial.com/concepts/memory-stack.html
- https://mempalaceofficial.com/concepts/knowledge-graph.html

---

**FIM DO DOCUMENTO**
Este documento é um Shadow Document - não confere autoridade.
Para informação canónica, ver fontes listadas acima.
