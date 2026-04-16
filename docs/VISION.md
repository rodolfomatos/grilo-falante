# VISÃO GERAL — Grilo Falante v3.0

**Versão:** 1.0
**Data:** 2026-04-16
**Última atualização:** Com esta sessão
**Autor:** Rodolfo + OpenCode

---

## 1. O que é o Grilo Falante?

Grilo Falante é um **sistema de governança epistémica** - um sistema que gere conhecimento de forma que:
- Claims são classificadas quanto à sua veracidade (GMIF)
- O contexto é preservado (ILHA)
- Conhecimento pode ser reutilizado entre contextos (PEDRA)
- Sistema pode dormir/acordar autonomamente

> "O Rosebud só faz sentido para quem conhece a história de Charles Foster Kane."

Isto é o的核心 do Grilo Falante - **contexto dá significado ao conhecimento**.

---

## 2. A Metáfora do Rosebud

Do filme Citizen Kane, "Rosebud" é a palavra que Kane murmura antes de morrer. Só quem conhece a história entende o que significa.

No Grilo Falante:
- **Mesma claim** em ILHAs diferentes pode ter significados diferentes
- **Contexto** é o que distingue informação de conhecimento
- Sem contexto, somos como Kane a morrer sem saber o que importava

---

## 3. Arquitetura Conceptual

### 3.1 ILHA — Momento-Espaço-Tempo

```
ILHA = Momento + Espaço + Tempo + Participantes
```

| Campo | Descrição |
|-------|-----------|
| `id` | Identificador único |
| `timestamp` | Momento (ISO format) |
| `ntp_timestamp` | Tempo Unix para sincronização |
| `participants` | Quem estava presente |
| `topic` | Tópico宏观 |
| `interaction_type` | AI-TO-AI, AI-HUMAN, etc. |
| `pedras` | Array de contextos reutilizáveis |

**ILHA é o agregado cognitivo** - o momento completo.

### 3.2 PEDRA — Contexto Reutilizável

PEDRA é um **agregador flexível** de contextos epistémicos:

```
PEDRA pode conter:
├── ShadowDocuments (sombras de fontes)
├── DigitalObjects (PDFs, URLs, imagens)
├── ConceptualCapsules (síntese validada)
└── Ou estar VAZIA (se nada for relevante)
```

| Campo | Descrição |
|-------|-----------|
| `id` | Identificador único |
| `started_at` | Quando o evento começou |
| `ended_at` | Quando terminou (None se ativa) |
| `content_summary` | Resumo do agregado |
| `shadow_documents` | Lista de sombras |
| `digital_objects` | Lista de referências |
| `is_empty` | True se vazia |
| `gmif_events` | Timeline de classificações |
| `gmif_level` | Classificação atual |
| `saliência` | Score de relevância (0-1) |
| `consequence_level` | Nível de consequências |
| `reused_in` | ILHAs onde foi reutilizada |

### 3.3 ShadowDocument — Sombra de uma Fonte

Quando lês um livro, não ficas com o livro - ficas com as **claims** que te marcaram. Isso é uma sombra.

```
ShadowDocument = {
    source_name: str
    source_type: str  # document, url, book
    source_reference: str
    extracted_claims: List[str]
    evidence_level: str  # complete, conditioned, weak
    assumptions: List[str]
    misuse_risks: List[str]
    feynman_f1: str  # Para crianças
    feynman_f2: str  # Para peritos
    feynman_f3_gaps: List[str]  # Why loop
}
```

### 3.4 DigitalObject — Entidade Referenciável

```
DigitalObject = {
    id: str
    type: str  # pdf, url, image, file
    reference: str  # URL ou path
    title: str
    is_capsule: bool  # Se é uma ConceptualCapsule
    capsule_scope: str
    capsule_interpretation: str
    capsule_normative_effect: str
}
```

**ConceptualCapsule** é um DigitalObject com `is_capsule=True`.
CC = <C, A, Σ, Δ> (Content, Scope, Interpretation, Normative Effect)

---

## 4. GMIF — Sistema de Classificação

GMIF = **Grilo Falante Meaning Interpretation Framework**

| Level | Description | Example |
|-------|-------------|---------|
| M1 | Proved true | "2+2=4" |
| M2 | Logically derived | Mathematical proof |
| M3 | High confidence | Scientific consensus |
| M4 | Probable | Statistical evidence |
| M5 | Possible | Anecdotal evidence |
| M6 | Speculative | Expert opinion |
| M7 | Unknown | Unvalidated claim |
| M8 | Counterfactual | Known false |

**GMIF History** regista o "quando" - não muda, só rastreia.

---

## 5. Ciclos Autónomos

### 5.1 ACORDAR / IR DORMIR

GF pode decidir autonomamente quando dormir ou acordar baseado em sinais de "cansaço":

**Sinais:**
- `memory_load` - número de ILHAs + PEDRAs
- `error_rate` - rácio de erros
- `gaps_detected` - gaps pendentes
- `time_since_sleep` - minutos desde último sono

**Decisões:**
- `DORMIR` se sleep_score > 50
- `ACORDAR` se wake_score > 50
- `MANTER` caso contrário

### 5.2 ESCOLA

Processo de resolver gaps identificados.

---

## 6. Shadow First — Metodologia

> Antes de perguntar, assumir, ou implementar, deves primeiro:
> 1. Pesquisar documentação
> 2. Criar Shadow Document
> 3. Gerar FAQ

### 6.1 Shadow Debt

Conceitos mencionados mas não documentados.

### 6.2 Shadow Score

| Score | Significado |
|-------|-------------|
| 100% | Completamente documentado |
| 50% | Tem shadow doc mas falta algo |
| 0% | Nunca documentado |

### 6.3 Regras de Ouro

1. Nunca perguntes o que podes pesquisar
2. Nunca assumas o que não documentaste
3. Shadow debt não perdoa - cria o doc
4. FAQ não é para ti - é para saberes o que perguntar
5. Relatório é para o teu EU futuro
6. Documenta tudo sempre
7. Memória é contextual

---

## 7. Visão de Deployment

### 7.1 Arquitetura Sistema Completo

```
┌─────────────────────────────────────────────────────────────┐
│                     Laptop (OpenCode)                        │
├─────────────────────────────────────────────────────────────┤
│  OpenCode                                                    │
│    │                                                         │
│    │ MCP protocol                                           │
│    └──────────────────┐                                   │
└───────────────────────┼────────────────────────────────────┘
                        │ HTTP/REST
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Docker Container                           │
├─────────────────────────────────────────────────────────────┤
│  Grilo Falante Server                                      │
│    ├── FastAPI (port 8001)                                │
│    │                                                           │
│    │ REST API                                               │
│    │   ├── /admin/ilhas/* (ILHA management)              │
│    │   ├── /admin/skills/* (Shadow First)                │
│    │   ├── /admin/cycles/* (Autonomous cycles)            │
│    │   └── /admin/mempalace/* (MemPalace integration)    │
│    │                                                           │
│    ├── ILHAManager                                        │
│    │   ├── Structured ILHAs/PEDRAs                        │
│    │   ├── JSON persistence (data/ilhas.json)              │
│    │   └── Optional MemPalace sync                        │
│    │                                                           │
│    ├── MCP Server                                          │
│    │   └── 40+ tools for OpenCode                         │
│    │                                                           │
│    └── PostgreSQL (future)                                 │
│        └── Articles, Users, etc.                           │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Fluxo de Dados

```
OpenCode Session
    │
    ├── Criar ILHA para a sessão
    │
    ├── Ao encontrar conceito novo:
    │   └── Adicionar ShadowDocument
    │
    ├── Ao criar PEDRA:
    │   └── Adicionar a ILHA atual
    │
    ├── Ao reutilizar PEDRA noutra ILHA:
    │   └── Adicionar a reused_in
    │
    └── Ao fechar sessão:
        └── Sync para MemPalace (opcional)
```

### 7.3 Storage Layers

| Layer | Technology | Purpose |
|-------|------------|---------|
| Primary | JSON (data/ilhas.json) | ILHAs/PEDRAs |
| Secondary | MemPalace | Verbatim + Semantic search |
| Tertiary | PostgreSQL | Relational data (future) |
| Quaternary | Filesystem | Documents, reports |

---

## 8. História do Projeto

### 8.1 Origem

O projeto nasceu da necessidade de:
- Gerir conhecimento de forma contextual
- Classificar claims quanto à veracidade
- Preservar o "porquê" das decisões
- Evitar repetir erros

### 8.2 Evolução

1. **v1.0** - Sistema básico de articles
2. **v2.0** - Shadow documents, Feynman layers
3. **v2.5** - Ambrosio, MemPalace integration
4. **v3.0** - ILHA/PEDRA system, autonomous cycles

### 8.3 Esta Sessão (2026-04-16)

Trabalhos realizados:
- Implementação completa do modelo ILHA
- Modelo PEDRA como agregador (G9)
- API endpoints para ILHA/PEDRA
- Persistência JSON
- Shadow First skill
- MemPalace integration (G10)
- Shadow First methodology documentada

---

## 9. Estado Atual

### 9.1 Gaps Implementadas

| Gap | Descrição | Estado |
|-----|-----------|--------|
| G1 | AI-to-AI gera ILHA automaticamente | ✅ |
| G2 | Timestamp NTP | ✅ |
| G3 | IDs únicos participantes | ✅ |
| G4 | Topic extraído | ✅ |
| G5 | Decisão autónoma dormir/acordar | ✅ |
| G6 | Endpoint logbook | ✅ |
| G7 | Campo reused_in | ✅ |
| G9 | Modelo PEDRA como agregador | ✅ |
| G11 | Persistência JSON | ✅ |
| G12 | API conteúdo PEDRA | ✅ |

### 9.2 Gaps Pendentes

| Gap | Descrição | Prioridade |
|-----|-----------|------------|
| G8 | Wiki view conexões | Média |
| G10 | MemPalace integration (completa) | Alta |
| G13 | PostgreSQL backend | Alta |
| G14 | Docker deployment | Alta |
| G15 | MCP server production-ready | Alta |

---

## 10. Próximos Passos

### Fase 1: Docker & Deployment
- [ ] Criar Dockerfile
- [ ] Criar docker-compose.yml
- [ ] Configurar CORS
- [ ] Health endpoint

### Fase 2: MCP Server
- [ ] Atualizar MCP server com novas tools
- [ ] Adicionar ILHA/PEDRA tools
- [ ] Testar com OpenCode

### Fase 3: Production
- [ ] PostgreSQL backend
- [ ] Autenticação
- [ ] Tests
- [ ] CI/CD

---

## 11. Lições Aprendidas

1. **Documentar antes de perguntar** - Shadow First methodology
2. **Contexto > Conteúdo** - O Rosebud metaphor
3. **Agregador > Objeto simples** - PEDRA como agregador flexível
4. **Persistência é essencial** - Sem persistência, perde-se tudo
5. **Graceful degradation** - Sistema deve funcionar sem componentes opcionais

---

## 12. Referências

- `docs/ILHA_VISION_v1.md` - Visão detalhada do sistema ILHA
- `docs/shadow_documents/SHADOW_MEMPALACE_v1.md` - Análise do MemPalace
- `docs/shadow_documents/SHADOW_MEMPALACE_INTEGRATION_v1.md` - Plano de integração
- `docs/skills/SHADOW_FIRST.md` - Metodologia Shadow First
- `grilo_admin/models/ilha.py` - Modelos ILHA/PEDRA
- `grilo_admin/routers/ilhas.py` - API endpoints

---

**FIM DO DOCUMENTO**
