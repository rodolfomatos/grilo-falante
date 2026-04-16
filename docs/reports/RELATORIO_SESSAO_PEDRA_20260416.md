# RELATÓRIO — Sessão de Correção Conceptual do Modelo PEDRA

**GF-ID:** REPORT-20260416-PEDRA-v1
**Data:** 2026-04-16
**Participantes:** Rodolfo + OpenCode
**Tipo:** Relatório de sessão (para reentrada futura)

---

## 1. Resumo Executivo

Esta sessão纠正ou o modelo de PEDRA no Grilo Falante v3.0. O modelo atual em `grilo_admin/models/ilha.py` não refletia a visão correta de PEDRA como:
- Agregador flexível de conteúdos (ShadowDocuments, ConceptualCapsules, DigitalObjects)
- Delimitada por eventos significativos (não por tempo fixo)
- Com saliência que pode crescer/decair

**Resultado:** Modelo纠正ado e criado shadow documents para análise.

---

## 2. O que estava errado

### 2.1 Modelo Original de PEDRA

```python
# ANTES (incorreto)
class Pedra:
    id: str
    ilha_id: str
    content: str  # só texto simples
    gmif_level: str  # só classificação atual
    type: str  # claim/gap
    is_gap: bool
    gap_question: Optional[str]
    reused_in: List[str]
    created_at: str
```

**Problemas identificados:**
1. `content: str` - texto simples não representa o agregado
2. Não há campos para ShadowDocuments, ConceptualCapsules, DigitalObjects
3. GMIF só tem nível atual, não histórico
4. Não há saliência com crescimento/decaimento
5. Não há `started_at`/`ended_at` para delimitar eventos
6. Não há `consequence_level`

---

## 3. O que foi clarificado

### 3.1 Definição Correcta de PEDRA

**PEDRA = Agregador flexível** que pode conter:
- **ShadowDocuments** - sombras de fontes (o que fica quando te lembras de um livro)
- **ConceptualCapsules** - síntese validada e reutilizável (é um DigitalObject)
- **DigitalObjects** - PDFs, URLs, imagens (entidades referenciáveis)
- **Ou estar VAZIA** - se não houver nada relevante

**Herança:**
- ConceptualCapsule **é um** DigitalObject (por definição)
- ConceptualCapsule **pode conter** outros DigitalObjects (por composição)

### 3.2 Dimensão Temporal

**PEDRA começa quando:**
- ACORDAR (início de ciclo) - nova pedra começa
- Evento significativo ocorre

**PEDRA termina quando:**
- Outra PEDRA começa (evento seguinte)
- DORMIR (fecho de ciclo)

**Exemplo do trajeto:**
```
TRAJETO: Sair de casa → Café → Encontrar amigo → Livro → Casa

PEDRA 1: Sair de casa → Café (evento: ir ao café)
PEDRA 2: Encontrar amigo → Livro (evento: encontro + empréstimo)
PEDRA 3: Atropelamento → Hospital (evento: atropelamento)
```

### 3.3 Saliência e Consequências

| Evento | Relevância | Memória |
|--------|------------|---------|
| Comida no café | Baixa | 2-3 dias |
| Encontrar amigo + livro | Média | Alguns dias |
| Atropelamento | **Alta** | Duradoura |

**Saliência** = crescimento baseado em consequências × reuse

**GMIF History** = só regista o "quando", não muda. É uma timeline.

### 3.4 MemPalace

**Descoberta:** Não havia Shadow Document do MemPalace. Fizemos análise.

**Resumo:**
- Sistema de memória para IAs
- Guarda texto verbatim (não transforma)
- Estrutura: Wings → Rooms → Halls → Drawers
- Knowledge Graph temporal
- MCP server com 29 ferramentas
- 96.6% R@5 raw retrieval

**Relação com GF:**
- Complementares: MemPalace = fidelidade, GF = governação
- Wing ≈ ILHA (ambos agregam contexto)
- Drawer ≈ PEDRA content (ambos armazenam)

---

## 4. Modelo Corrigido de PEDRA

```python
# DEPOIS (corrigido)
class Pedra:
    id: str
    ilha_id: str

    # Dimensão temporal - delimitada por eventos
    started_at: datetime      # quando o evento começou
    ended_at: Optional[datetime]  # quando terminou (None se ativa)

    # Agregado flexível
    content_summary: str      # resumo do agregado (para display)

    # Composição: pode ter qualquer combinação
    shadow_documents: List[ShadowDocument]   # sombras de fontes
    digital_objects: List[DigitalObject]     # objetos digitais
    # ConceptualCapsule é um DigitalObject com is_capsule=True
    # Não precisa de lista separada

    is_empty: bool = True    # True se não tem conteúdos

    # Rastreio GMIF (só regista o quando, não muda)
    gmif_events: List[GmifEvent]  # timeline de classificações

    # Saliência
    saliencia: float              # pode crescer ou decair
    consequence_level: float       # nível de consequências
    decay_enabled: bool = True

    # Reutilização
    reused_in: List[str]          # ILHAs onde foi reutilizada
```

---

## 5. Questões em Aberto

### 5.1 Integração de Storage

**Pergunta:** Onde ficam os dados?
- PostgreSQL (SQLAlchemy) - já existe
- MemPalace (vector store) - descobrir como integrar
- Filesystem (docs/) - já existe

**Decisão:** Todas as anteriores, mas precisa de arquitetura.

### 5.2 Deteção de Eventos

**Pergunta:** Como automatizar sem perder controlo?

GF não tem mecanismo de detetar eventos significativos automaticamente.

### 5.3 Arquitectura de Storage Unificada

```
┌─────────────────────────────────────────┐
│            Grilo Falante                │
├─────────────────────────────────────────┤
│                                          │
│  ILHAManager (in-memory)                │
│  └── _ilhas, _pedras (agora corrigidos) │
│                                          │
│  PostgreSQL                              │
│  └── Articles, Users, Repositories...   │
│                                          │
│  MemPalace (?)                          │
│  └── Wings, Rooms, Drawers...          │
│  └── Knowledge Graph                    │
│                                          │
│  Filesystem                              │
│  └── docs/, shadow_documents/           │
│                                          │
└─────────────────────────────────────────┘
```

---

## 6. Documentos Criados

| Documento | Tipo | Descrição |
|-----------|------|-----------|
| `docs/shadow_documents/SHADOW_MEMPALACE_v1.md` | Shadow | Análise do MemPalace |
| `docs/shadow_documents/FAQ_MEMPALACE_GF_v1.md` | FAQ | Perguntas sobre integração |
| `docs/reports/RELATORIO_SESSAO_PEDRA_20260416.md` | Report | Este documento |

---

## 7. Estado das Gaps (atualizado)

| Gap | Descrição | Estado |
|-----|-----------|--------|
| G1 | AI-to-AI gera ILHA automaticamente | ✅ Implementado |
| G2 | Timestamp NTP nos dados | ✅ Implementado |
| G3 | IDs únicos participantes | ✅ Implementado |
| G4 | Topic extraído | ✅ Implementado |
| G5 | Decisão autónoma dormir/acordar | ✅ Implementado |
| G6 | Endpoint logbook | ✅ Implementado |
| G7 | Campo reused_in | ✅ Implementado |
| G8 | Wiki view conexões | ⏳ Pendente |
| **G9** | **Modelo PEDRA correto** | **⏳ A corrigir** |
| **G10** | **Integração MemPalace** | **⏳ A estudar** |
| **G11** | **Arquitetura storage unificada** | **⏳ A desenhar** |

---

## 8. Próximos Passos

1. [ ] Corrigir modelo de PEDRA em `grilo_admin/models/ilha.py`
2. [ ] Criar modelos para ShadowDocument, DigitalObject, ConceptualCapsule
3. [ ] Estudar integração MemPalace (testar localmente)
4. [ ] Desenhar arquitetura de storage unificada
5. [ ] Implementar deteção de eventos significativos (ou decisão deliberada)
6. [ ] Atualizar visão (ILHA_VISION) com novo modelo

---

## 9. Lições Aprendidas

1. **Devemos fazer Shadow Documents ANTES de perguntar** - O utilizador mencionou que já tínhamos falado várias vezes do MemPalace, mas eu não tinha forma de saber sem documentar.

2. **PEDRA não é só texto** - É um agregador rico com múltiplos tipos de conteúdo.

3. **Tempo = dimensão fundamental** - PEDRA começa e termina com eventos, não com ciclos temporais fixos.

4. **GMIF History = timeline, não estado** - Não muda, só regista o "quando".

5. **MemPalace e GF são complementares** - Um dá fidelidade, outro dá governação.

---

## 10. Reentrada Futura

Para retomar este trabalho:

1. Ler `docs/shadow_documents/SHADOW_MEMPALACE_v1.md` para contexto do MemPalace
2. Ler `docs/shadow_documents/FAQ_MEMPALACE_GF_v1.md` para perguntas em aberto
3. Ler este relatório para estado atual
4. Começar por corrigir o modelo de PEDRA em `grilo_admin/models/ilha.py`
5. Definir arquitetura de storage antes de implementar

---

**FIM DO RELATÓRIO**
