# Plano: Admin Back-office para Grilo Falante Platform

**Versão:** 2.0
**Data:** 2026-04-16
**Autor:** Rodolfo
**Estado:** EM DESENVOLVIMENTO

---

## Histórico de Alterações

| Versão | Data | Alterações |
|--------|------|-----------|
| 1.0 | 2026-04-16 | Versão inicial |
| 1.1 | 2026-04-16 | Adicionado OpenDataLoader PDF e Feynman F1/F2/F3 |
| 1.2 | 2026-04-16 | Implementação completa - todos os módulos API |
| 2.0 | 2026-04-16 | Sistema de Articles com Shadow Documents, Falácias e Wiki |

---

---

## 1. Visão Geral

### 1.1 Contexto

O Grilo Falante evoluiu de um chatbot académico para uma **plataforma genérica de governação epistémica** com arquitectura de plugins. A plataforma suporta actualmente:

- **Platform Core** (`grilo_falante/platform/`): Domain adapter SDK, plugin registry, LLM configurável
- **Plugins**: `grilo_tax` (fiscal), `grilo_student` (suporte estudantil)
- **Unified Chat API** (`grilo_chat_api/`): Routing automático, gestão de sessões

O back-office administrative é necessário para:

1. **Operar a plataforma** em produção
2. **Gerir plugins e repositórios** sem código
3. **Monitorizar o sistema** (SysInfo)
4. **Controlar ciclos** (Acordar/Dormir)
5. **Auto-aprendizagem** - RAG que evolui das interações

### 1.2 Arquitectura Proposta

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ADMIN BACK-OFFICE                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Auth      │  │  Dashboard  │  │   Plugins   │  │Repositories │  │
│  │  (OIDC)    │  │  (SysInfo)  │  │  Manager    │  │  (RAG/FAQ)  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Claims     │  │  Cycles     │  │  Escalation │  │  Sessions   │  │
│  │  Manager    │  │  (Acordar/  │  │   Queue     │  │  Manager    │  │
│  │             │  │   Dormir)   │  │             │  │             │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                         INFRASTRUCTURE LAYER                            │
│  MemPalace (ChromaDB) │ PostgreSQL │ Grilo Falante Platform          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Arquitectura de Repositórios (RAG/FAQ)

### 2.1 Conceito

Um **Repositório** é uma colecção de conteúdo que pode ser transformada em embeddings e usada para RAG (Retrieval-Augmented Generation). Cada plugin pode ter zero ou mais repositórios asociados.

### 2.2 Modelo de Dados

```python
class Repository:
    id: UUID
    name: str
    description: str
    repository_type: RepositoryType  # "faq", "knowledge_base", "documents", "custom"
    plugin_name: Optional[str]  # Plugin associated with this repo
    status: RepositoryStatus  # "active", "indexing", "error"

    # Embeddings config
    embedding_model: str  # e.g., "BAAI/bge-m3"
    chunk_size: int  # default 512
    chunk_overlap: int  # default 50

    # Metadata
    tags: List[str]
    version: int
    created_at: datetime
    updated_at: datetime

    # Stats
    total_chunks: int
    last_indexed_at: Optional[datetime]
```

### 2.3 Tipos de Repositório

| Tipo | Descrição | Exemplos |
|------|-----------|----------|
| `faq` | Perguntas e respostas estruturadas | FAQs de suporte ao estudante |
| `knowledge_base` | Documentação e manuais | Manual de IRC, regulamentos |
| `documents` | Documentos raw (PDF, DOCX) | Legislação, contratos |
| `custom` | Conteúdo personalizado | Base de conhecimento própria |

### 2.4 Fluxo de Ingestão

```
Upload (PDF/DOCX)
       │
       ▼
OpenDataLoader PDF ──▶ Markdown + JSON (com bounding boxes)
       │
       ▼
FeynmanProcessor ──▶ F1 (FAQ simplificado)
       │           ──▶ F2 (Explicação técnica)
       │           ──▶ F3 (Why Loop → Gap detection)
       │
       ▼
Chunking + Embedding
       │
       ▼
MemPalace (fast RAG)
PostgreSQL (authoritative)
```

**OpenDataLoader PDF** (https://github.com/opendataloader-project/opendataloader-pdf):
- Extrai PDF para Markdown + JSON
- Suporta OCR, tables, formulas, multi-column
- Bounding boxes para citações exactas
- Output: `format="markdown,json"`

### 2.5 Feynman - 3 Níveis de Processamento

O **FeynmanSynthesizer** processa conteúdo em 3 níveis:

| Nível | Nome | Descrição | Output |
|-------|------|-----------|--------|
| **F1** | Explicação da criança | Simples, acessível, linguagem comum | FAQ Q&A simplificado |
| **F2** | Explicação do especialista | Técnica, detalhada, com jargão | Documentação técnica |
| **F3** | Why Loop | "Porque é que X? Porque Y. Porque Z..." | Gaps identificados |

**F3 (Why Loop)** é crucial para auto-aprendizagem:
- Faz perguntas "porquê?" sucessivamente
- Identifica conhecimento profundo
- Deteta gaps (o que não se sabe)
- Trigger "Ir à Escola" quando encontra gap

```
FeynmanSynthesizer.process(content)
    │
    ├──▶ F1: Simplificar ──▶ FAQ simplificado
    ├──▶ F2: Tecnificar ──▶ Explicação técnica
    └──▶ F3: Why Loop ──▶ Gaps ──▶ Ir à Escola
```

### 2.6 Porquê Repositórios?

O Grilo Falante usa **MemPalace + PostgreSQL** como infraestrutura de armazenamento. Em vez de ter um sistema de ficheiros disperso, os repositórios:

1. **Centralizam** todo o conteúdo indexável num modelo consistente
2. **Associam** conteúdo a plugins domains
3. **Versionam** o conteúdo (possibilidade de rollback)
4. **Suportam** múltiplos tipos de conteúdo (FAQ, documentos, etc.)
5. **Permitem** gestão fina de chunking e embedding

---

## 3. Sistema de Auto-Aprendizagem

### 3.1 Visão

O sistema deve ser capaz de **aprender automaticamente** das interações com utilizadores. Quando um utilizador faz uma pergunta e recebe uma resposta (seja do FAQ, seja do LLM), o sistema deve poder:

1. **Extrair claims** da conversa
2. **Classificar** com GMIF
3. **Validar** automaticamente ou propor para validação humana
4. **Indexar** no repositório appropriate
5. **Evoluir** a base de conhecimento

### 3.2 Arquitectura da Auto-Aprendizagem

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AUTO-LEARNING PIPELINE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │ Chat     │──▶│ Claims   │──▶│ Auto-    │──▶│MemPalace │      │
│  │ Session  │   │Extractor │   │ Validate │   │  Index   │      │
│  └──────────┘   └──────────┘   └────┬─────┘   └──────────┘      │
│                                     │                              │
│                              ┌──────▼──────┐                       │
│                              │   PINA      │                       │
│                              │  Protocol   │                       │
│                              │ (Human      │                       │
│                              │  Approval)  │                       │
│                              └─────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 Configurações

| Setting | Descrição | Default |
|---------|-----------|---------|
| `auto_extract_claims` | Extrair claims de conversas | `true` |
| `auto_index_claims` | Indexar claims automaticamente | `true` |
| `require_approval` | Requerer aprovação humana via PINA | `false` |
| `min_confidence` | Confiança mínima para auto-index | `0.7` |
| `dedup_threshold` | Similarity threshold para deduplicação | `0.95` |
| `gmif_auto_promote` | Promover GMIF automaticamente | `false` |

### 3.4 Porquê Auto-Aprendizagem?

O Grilo Falante usa o conceito de **"memória insular"** onde:

- **Pedras** = interacções salientes
- **Ilhas** = agregados de pedras com alta saliência
- **Claims** = conhecimento extraído de interacções

A auto-aprendizagem permite que:

1. **Conversas valiosas** sejam convertidas em knowledge
2. **Respostas frequentes** se tornem FAQs indexadas
3. **Gaps identificados** sejam automaticamente pesquisados
4. **Sistema evolua** sem intervenção constante

---

## 4. Autenticação

### 4.1 Opções

| Opção | Descrição | Complexidade | Quando Usar |
|-------|-----------|--------------|-------------|
| **OpenID Connect** | Integração com provider existente | Alta | Produção com SSO corporativo |
| **Local (JWT)** | Username/password + BCrypt + JWT | Baixa | Desenvolvimento, startups |

### 4.2 Recomendação

**Fase inicial**: JWT local (mais simples de implementar)
**Fase posterior**: OpenID Connect como upgrade

### 4.3 Modelo de Utilizadores

```python
class User:
    id: UUID
    email: str
    password_hash: str
    role: UserRole  # "admin", "operator", "viewer"
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class UserRole(Enum):
    ADMIN = "admin"      # Full access
    OPERATOR = "operator"  # Can handle escalations
    VIEWER = "viewer"    # Read-only access
```

---

## 5. Funcionalidades por Módulo

### 5.1 Dashboard / SysInfo

**Métricas a mostrar:**

| Categoria | Métricas |
|-----------|----------|
| **Sistema** | Uptime, versão, CPU/memória |
| **LLM** | Provider ativo, estado (BitNet/Ollama) |
| **Base de Dados** | PostgreSQL: connected queries, MemPalace: vectors |
| **Plugins** | Número de plugins, estado de cada |
| **RAG** | Total de chunks, últimas indexações |
| **Ciclos** | Último Acordar/Dormir, estado actual |
| **Sessões** | Activas, total, mensagens/min |

**Funcionalidades:**

- Cache management (reset de caches)
- Health checks detalhados
- Logs de sistema

### 5.2 Gestão de Plugins

**Funcionalidades:**

- Listar plugins instalados
- Activar/desactivar plugins
- Editar configuração (routing keywords, escalation triggers)
- Ver detalhes e metadata
- Health check por plugin

### 5.3 Gestão de Ciclos (Acordar/Dormir)

**Estado actual do sistema de ciclos:**

- **Ir Acordar**: Restaura contexto de ilhas activas
- **Ir Dormir**: Processamento batch de saliência
- **Ir à Escola**: Aprendizagem activa quando gap identificado

**Funcionalidades:**

- Trigger manual de ciclos
- Ver estado actual
- Visualizar ilhas e pedras
- Logs de execução

### 5.4 Escalation Queue

**Fluxo de escalação:**

```
User Query → Trigger Detection → Escalation Queue → Operator → Resolution
                                     ↓
                              FAQ/Knowledge Update
```

**Funcionalidades:**

- Lista de conversas pendentes
- Atribuição a operadores
- Chat integrado com utilizador
- Marcar como resolvido
- Estatísticas de escalação

---

## 6. Decisões Técnicas

### 6.1 Stack Tecnológico

| Componente | Escolha | Justificação |
|-----------|---------|--------------|
| **Backend API** | FastAPI | Já usado no projeto, async, type hints |
| **Frontend** | React ou Vue.js | Escolha do developer |
| **UI Components** | shadcn/ui (React) | Acessível, customizável |
| **Database** | PostgreSQL existente | Já faz parte da stack |
| **Embeddings** | MemPalace (ChromaDB) | Já integrado |

### 6.2 API Design

Seguir **RESTful patterns** com:

- `/admin/` como base path
- Paginação em listas
- Filmes por query params
- Responses consistentes

### 6.3 Segurança

- Todas as rotas `/admin/*` requerem autenticação
- JWT com refresh tokens
- Rate limiting
- Input validation
- SQL injection prevention (ORM)

---

## 7. Fases de Implementação

### Fase 5.1: Foundation (Semanas 1-2) ✅

- [x] Auth module (JWT local)
- [x] Base FastAPI structure
- [x] Admin middleware (auth guard)
- [x] User model and CRUD

### Fase 5.2: Dashboard & System Info (Semana 3) ✅

- [x] System status endpoints
- [x] Cache management endpoints
- [x] Dashboard UI page (API only)

### Fase 5.3: Plugin Management (Semana 4) ✅

- [x] Plugin CRUD endpoints
- [x] Plugin config editing
- [x] Plugin management UI (API only)

### Fase 5.4: Repository/RAG Management (Semanas 5-6) ✅

- [x] Repository CRUD endpoints
- [x] Content upload/ingestion
- [x] FAQ editor
- [x] Repository management UI (API only)

### Fase 5.5: Cycles Control (Semana 7) ✅

- [x] Acordar/Dormir endpoints
- [x] Islands/Claims viewing
- [x] Cycles UI page (API only)

### Fase 5.6: Auto-Learning (Semana 8) ✅

- [x] Learning config endpoints
- [x] Claim validation queue
- [x] Learning settings UI (API only)

### Fase 5.7: Escalation & Polish (Semanas 9-10) ✅

- [x] Escalation queue endpoints
- [x] Claims management UI (API only)
- [x] Final integration testing

---

## 8. API Endpoints

### Auth

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/login` | Login (local) |
| POST | `/auth/logout` | Logout |
| POST | `/auth/refresh` | Refresh token |
| GET | `/auth/me` | Current user info |
| POST | `/auth/register` | Register (admin only) |

### Admin System

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/system/status` | Estado geral do sistema |
| GET | `/admin/system/health` | Health checks detalhados |
| GET | `/admin/system/stats` | Métricas e contadores |
| POST | `/admin/system/cache/clear` | Reset de caches |

### Admin Plugins

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/plugins` | List all plugins |
| GET | `/admin/plugins/{name}` | Plugin details |
| PUT | `/admin/plugins/{name}/config` | Update plugin config |
| POST | `/admin/plugins/{name}/enable` | Enable plugin |
| POST | `/admin/plugins/{name}/disable` | Disable plugin |

### Admin Repositories

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/repositories` | List repositories |
| POST | `/admin/repositories` | Create repository |
| GET | `/admin/repositories/{id}` | Repository details |
| PUT | `/admin/repositories/{id}` | Update repository |
| DELETE | `/admin/repositories/{id}` | Delete repository |
| POST | `/admin/repositories/{id}/ingest` | Trigger ingestion |
| POST | `/admin/repositories/{id}/upload` | Upload content |
| GET | `/admin/repositories/{id}/search` | Test search |

### Admin FAQ

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/repositories/{id}/faqs` | List FAQs |
| POST | `/admin/repositories/{id}/faqs` | Create FAQ |
| GET | `/admin/repositories/{id}/faqs/{faq_id}` | Get FAQ |
| PUT | `/admin/repositories/{id}/faqs/{faq_id}` | Update FAQ |
| DELETE | `/admin/repositories/{id}/faqs/{faq_id}` | Delete FAQ |
| POST | `/admin/repositories/{id}/faqs/{faq_id}/approve` | Approve FAQ |
| POST | `/admin/repositories/{id}/faqs/generate` | Generate FAQs (Feynman) |
| POST | `/admin/repositories/{id}/faqs/bulk` | Bulk create FAQs |

### Admin Cycles

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/cycles/status` | Current cycle state |
| GET | `/admin/cycles/history` | Cycle history |
| POST | `/admin/cycles/acordar` | Trigger acordar |
| POST | `/admin/cycles/dormir` | Trigger ir_dormir |
| GET | `/admin/ilhas` | List all islands |
| GET | `/admin/pedras` | List stones |

### Admin Learning/Claims

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/learning/config` | Get auto-learning settings |
| PUT | `/admin/learning/config` | Update settings |
| GET | `/admin/learning/stats` | Learning statistics |
| GET | `/admin/learning/claims` | List all claims |
| GET | `/admin/learning/claims/pending` | Pending validation |
| GET | `/admin/learning/claims/{id}` | Claim details |
| POST | `/admin/learning/claims/{id}/approve` | Approve claim |
| POST | `/admin/learning/claims/{id}/reject` | Reject claim |
| POST | `/admin/learning/claims/{id}/index` | Index validated claim |
| DELETE | `/admin/learning/claims/{id}` | Delete claim |
| POST | `/admin/learning/extract` | Extract claims from content |
| POST | `/admin/learning/process-gap` | Process gap (Feynman) |

### Admin Escalations

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/escalations` | List escalations |
| GET | `/admin/escalations/pending` | Pending escalations |
| GET | `/admin/escalations/stats` | Escalation statistics |
| GET | `/admin/escalations/{id}` | Escalation details |
| GET | `/admin/escalations/{id}/history` | Audit history |
| POST | `/admin/escalations` | Create escalation |
| POST | `/admin/escalations/{id}/assign` | Assign to operator |
| POST | `/admin/escalations/{id}/status` | Update status |
| POST | `/admin/escalations/{id}/resolve` | Mark resolved |
| POST | `/admin/escalations/{id}/close` | Close escalation |
| DELETE | `/admin/escalations/{id}` | Delete escalation |

### Admin Articles

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/admin/articles` | Create article |
| GET | `/admin/articles` | List articles |
| GET | `/admin/articles/{id}` | Get article |
| PUT | `/admin/articles/{id}` | Update article |
| POST | `/admin/articles/{id}/learn` | Trigger learning workflow |
| GET | `/admin/articles/{id}/claims` | Get article claims |
| POST | `/admin/articles/{id}/claims` | Add claim |
| GET | `/admin/articles/{id}/shadow-documents` | Get shadow docs |
| POST | `/admin/articles/{id}/shadow-documents` | Create shadow doc |
| GET | `/admin/articles/{id}/gaps` | Get article gaps |
| GET | `/admin/articles/{id}/faqs` | Get article FAQs |
| GET | `/admin/articles/{id}/wiki` | Get wiki view |
| POST | `/admin/articles/{id}/detect-falacias` | Detect fallacies |
| GET | `/admin/articles/{id}/falacias` | Get detected fallacies |
| POST | `/admin/shadow-documents/{id}/validate` | Validate shadow doc |
| GET | `/admin/articles/validation-queue` | Get validation queue |

### Admin Falacias

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/admin/articles/falacias/{id}/correct` | Get correction suggestion |
| POST | `/admin/articles/falacias/{id}/signal` | Signal to affected items |

---

## 9. UI Frontend

### 9.1 Páginas

```
/admin
├── /login
├── /dashboard          # System overview
├── /plugins           # Plugin management
├── /repositories      # RAG/FAQ repositories
├── /claims            # Claims management
├── /cycles            # Acordar/Dormir control
├── /escalations       # Escalation queue
├── /sessions          # Session monitoring
├── /learning          # Auto-learning config
└── /settings          # System settings
```

---

## 10. Questões em Aberto

| Questão | Opções | Estado |
|---------|--------|--------|
| Frontend framework | React vs Vue | A decidir |
| OpenID Connect vs JWT local | Ambos vs só JWT | A decidir |
| Auto-learning approval | PINA vs automático | A decidir |
| Repositório por plugin | Sim vs não | A decidir |

---

## 11. Histórico de Alterações

| Versão | Data | Alterações |
|--------|------|-----------|
| 1.0 | 2026-04-16 | Versão inicial |
| 1.1 | 2026-04-16 | Adicionado OpenDataLoader PDF e Feynman F1/F2/F3 |
| 1.2 | 2026-04-16 | Implementação completa - API Backoffice v1 |

---

## 12. Referências

- [MEMO ÂNCORA](./references/memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md) - Visão do sistema
- [GMIF Framework](./references/Modelo Gráfico de Meta-Informação.md) - Framework de classificação
- [Grilo Falante Platform](./grilo_falante/platform/) - Platform Core
- [Unified Chat API](./grilo_chat_api/) - Chat API com routing

---

## 13. Admin Services

### 13.1 Services Directory

O back-office inclui serviços em `grilo_admin/services/`:

```
grilo_admin/services/
├── __init__.py
├── opendataloader_service.py  # PDF extraction
├── feynman_processor.py       # F1/F2/F3 processing
└── rag_index_service.py      # Vector indexing
```

### 13.2 OpenDataLoader Service

**File:** `grilo_admin/services/opendataloader_service.py`

Integração com opendataloader-pdf para extração de PDF:
- Extrai PDF para Markdown + JSON
- Suporte para OCR, tabelas, fórmulas
- Fallback para extração básica se não instalado

### 13.3 Feynman Processor

**File:** `grilo_admin/services/feynman_processor.py`

Processador Feynman com 3 níveis:
- **F1**: Explicação para crianças (simplificada)
- **F2**: Explicação técnica para especialistas
- **F3**: Why Loop para detecção de gaps

### 13.4 RAG Index Service

**File:** `grilo_admin/services/rag_index_service.py`

Serviço de indexação RAG:
- ChromaDB (MemPalace) para vector storage
- Fallback para armazenamento em memória
- FAQ management integrado

---

## 14. Arquitetura Final

### 14.1 Stack Completo

```
grilo_admin/
├── __init__.py              # FastAPI app
├── auth/                    # JWT authentication
│   └── jwt_auth.py
├── models/                  # Pydantic models
│   ├── user.py
│   ├── repository.py
│   └── article.py           # Article, ShadowDocument, Gap, Falacia, FAQ
├── routers/                 # API endpoints
│   ├── users.py             # 7 routes (auth)
│   ├── system.py            # 7 routes
│   ├── plugins.py           # 5 routes
│   ├── repositories.py      # 18 routes
│   ├── cycles.py            # 14 routes
│   ├── learning.py          # 12 routes
│   ├── escalations.py       # 11 routes
│   └── articles.py          # 16 routes
└── services/                # Business logic
    ├── opendataloader_service.py
    ├── feynman_processor.py
    └── rag_index_service.py

Total: ~95 routes
```

### 14.2 Dependências

```
fastapi>=0.100
uvicorn>=0.23
python-jose[cryptography]>=3.3
passlib[bcrypt]>=1.7
pydantic>=2.0
chromadb>=0.4 (opcional)
opendataloader-pdf>=1.0 (opcional)
```

---

## 15. Sistema de Articles (v2.0)

### 15.1 Visão Geral

O sistema de Articles permite a **construção de artigos científicos** de forma assistida, usando todo o regime Grilo Falante:

- **Ilhas = Articles** - Um artigo é uma versão estruturada de uma ilha
- **Shadow Documents** - Interpretações Feynman de fontes
- **GMIF para tudo** - Classificação epistémica de todas as claims
- **Wiki view** - Interface de exploração do conhecimento

### 15.2 Modelo de Dados

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ARTICLE                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Article                                                          │
│  ├── id, title, phase, status                                     │
│  ├── gmif_overall (worst claim)                                   │
│  ├── has_pending_validation                                         │
│  └── has_falacias_blocking                                         │
│                                                                      │
│  ArticleClaim ──→ ShadowDocument                                   │
│  ├── claim_text, gmif_level, confidence                           │
│  └── role (MAIN|CONTEXT|REFERENCE)                                │
│                                                                      │
│  ShadowDocument ──→ Feynman F1/F2/F3                              │
│  ├── source (upload|web|internal)                                  │
│  ├── feynman_f1, feynman_f2, feynman_f3_gaps                      │
│  ├── needs_human_validation (sempre true)                         │
│  └── validation_status (PENDING|APPROVED|REJECTED)                │
│                                                                      │
│  Falacia                                                          │
│  ├── type (CONTRADICTION|GENERALIZATION|APPEAL_TO...)             │
│  ├── severity (WARNING|BLOCKING)                                   │
│  ├── propagated (buscar em cascata)                               │
│  └── affected_ilhas                                                │
│                                                                      │
│  Gap ──→ FAQ                                                      │
│  ├── question                                                     │
│  ├── status (OPEN|RESOLVED|PROPAGATED)                           │
│  └── propagated_to_article_id                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 15.3 Fluxo de Trabalho

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARTICLE WORKFLOW                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. EXPLORATÓRIA                                                   │
│     POST /admin/articles/create                                      │
│     → Article criado + Ilha associada                               │
│     → Claims extraídas do input                                     │
│     → Gaps identificadas                                            │
│     → FAQs auto-geradas (visíveis IMEDIATAMENTE)                   │
│                                                                      │
│  2. APRENDIZAGEM                                                   │
│     POST /admin/articles/{id}/learn                                 │
│     → "Ir à Escola" para cada gap                                   │
│     → Shadow Docs criados (upload, web, internal)                  │
│     → Feynman F1/F2/F3 processado                                  │
│     → ⚠️ needs_human_validation = TRUE                              │
│     → validation_status = PENDING                                   │
│                                                                      │
│  3. REVISÃO                                                        │
│     POST /admin/shadow-docs/{id}/validate                          │
│     → Curator valida shadow docs                                    │
│     → Gaps marcados como RESOLVED                                   │
│                                                                      │
│  4. DETEÇÃO DE FALÁCIAS                                            │
│     → Sistema deteta relações problemáticas                         │
│     → PROPAGAÇÃO RECURSIVA: buscar todas ilhas afetadas            │
│     → Sinalizar owners                                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 15.4 Princípios Fundamentais

| Princípio | Descrição |
|-----------|-----------|
| **Curadoria obrigatória** | Todos os shadow docs de fontes web requerem validação humana |
| **FAQ auto-visível** | Dúvidas/perguntas são sempre visíveis ("perguntar não ofende") |
| **GMIF para tudo** | Todas as claims são classificadas M1-M8 |
| **Propagação recursiva** | Falácias afetam todas as ilhas/claims relacionadas |
| **Responsabilização** | Todas as ações de curadoria são auditadas |

### 15.5 Wiki View

O artigo é navegável como uma enciclopédia:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🌐 ARTICLE WIKI VIEW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📚 ALTERAÇÕES CLIMÁTICAS                                           │
│  ├─ 📄 Claims                                                      │
│  │   ├─ [M1] "Temperatura subiu 1.1°C" ✓                         │
│  │   ├─ [M3] "CO2 aumentou 40%" ⚠️ PENDING                       │
│  │   └─ [M4] "80% concordam" ❌ FALÁCIA                           │
│  │                                                                │
│  │   🔗 Ligações lógicas                                          │
│  │   └─ "CO2" ──concorre──► "Temperatura"                        │
│  │                                                                │
│  ├─ 📚 Shadow Documents                                            │
│  │   ├─ [upload] IPCC AR6 ✓ APPROVED                              │
│  │   └─ [web] Wikipedia ⚠️ PENDING                                │
│  │                                                                │
│  ├─ ❓ Dúvidas/Gaps                                               │
│  │   └─ "Como medimos temperatura?" → RESOLVED                    │
│  │                                                                │
│  └─ ❔ FAQs                                                        │
│      ├─ "O que é o efeito estufa?" ✓                             │
│      └─ "Como se mede CO2?" ✓                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 15.6 Teste AI-to-AI

Um script de teste permite observar duas IAs a conversar:

```bash
python3 test_ai_to_ai.py --topic "mudanças climáticas" --rounds 3
```

- **Agent A**: Grilo Falante (com regime, islands, claims, GMIF)
- **Agent B**: AI regular (sem regime)

O teste verifica:
- Como o contexto se mantém entre agentes
- Como as claims são extraídas e classificadas
- Como os gaps são identificados

### 15.7 Deteção de Falácias

O sistema deteta falácias lógicas usando padrões:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FALACIA TYPES                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CONTRADICTION      - Afirmações contraditórias                     │
│  GENERALIZATION     - "todos", "sempre", "nunca"                    │
│  APPEAL_TO_AUTHORITY - Apelo à autoridade não verificado              │
│  APPEAL_TO_MAJORITY - "todos dizem que" sem evidência              │
│  CAUSAL_FALLACY    - Correlação vs causação                        │
│  STRAWMAN          - Deturpação de argumento                       │
│  FALSE_DILEMMA     - Só duas opções quando há mais                   │
│  CIRCULAR_REASONING - Usar a conclusão como premissa                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Serviço:** `grilo_admin/services/falacia_service.py`

| Classe | Função |
|---------|--------|
| `FalaciaDetector` | Deteta falácias em claims |
| `FalaciaPropagator` | Propaga a outras ilhas/articles |
| `FalaciaCorrector` | Sugere correções |

---

## 16. Testes

### 16.1 AI-to-AI Test

**Ficheiro:** `test_ai_to_ai.py`

Testa a conversa entre duas IAs para verificar manutenção de contexto.

```bash
# Executar
python3 test_ai_to_ai.py --topic "Inteligência Artificial" --rounds 3

# Com provider específico
python3 test_ai_to_ai.py --topic "Física Quântica" --provider ollama --rounds 5
```

### 16.2 Modelos

**Ficheiros:**
- `grilo_admin/models/article.py` - Article, ShadowDocument, Gap, Falacia, FAQ
- `grilo_admin/services/falacia_service.py` - Deteção e propagação

Contém todos os modelos para o sistema de articles com Pydantic validation.
