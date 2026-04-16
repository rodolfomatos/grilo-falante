# Plano: Admin Back-office para Grilo Falante Platform

**Versão:** 1.1
**Data:** 2026-04-16
**Autor:** Rodolfo
**Estado:** Draft

---

## Histórico de Alterações

| Versão | Data | Alterações |
|--------|------|-----------|
| 1.0 | 2026-04-16 | Versão inicial |
| 1.1 | 2026-04-16 | Adicionado OpenDataLoader PDF e Feynman F1/F2/F3 |

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

### Fase 5.1: Foundation (Semanas 1-2)

- [ ] Auth module (JWT local)
- [ ] Base FastAPI structure
- [ ] Admin middleware (auth guard)
- [ ] User model and CRUD

### Fase 5.2: Dashboard & System Info (Semana 3)

- [ ] System status endpoints
- [ ] Cache management endpoints
- [ ] Dashboard UI page

### Fase 5.3: Plugin Management (Semana 4)

- [ ] Plugin CRUD endpoints
- [ ] Plugin config editing
- [ ] Plugin management UI

### Fase 5.4: Repository/RAG Management (Semanas 5-6)

- [ ] Repository CRUD endpoints
- [ ] Content upload/ingestion
- [ ] FAQ editor
- [ ] Repository management UI

### Fase 5.5: Cycles Control (Semana 7)

- [ ] Acordar/Dormir endpoints
- [ ] Islands/Claims viewing
- [ ] Cycles UI page

### Fase 5.6: Auto-Learning (Semana 8)

- [ ] Learning config endpoints
- [ ] Claim validation queue
- [ ] Learning settings UI

### Fase 5.7: Escalation & Polish (Semanas 9-10)

- [ ] Escalation queue endpoints
- [ ] Claims management UI
- [ ] Final integration testing

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

### Admin Cycles

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/cycles/status` | Current cycle state |
| GET | `/admin/cycles/history` | Cycle history |
| POST | `/admin/cycles/acordar` | Trigger acordar |
| POST | `/admin/cycles/dormir` | Trigger ir_dormir |
| GET | `/admin/ilhas` | List all islands |
| GET | `/admin/pedras` | List stones |

### Admin Claims

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/claims` | List claims (paginated) |
| GET | `/admin/claims/{id}` | Claim details |
| POST | `/admin/claims/{id}/validate` | Validate claim |
| POST | `/admin/claims/{id}/reject` | Reject claim |

### Admin Learning

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/learning/config` | Get auto-learning settings |
| PUT | `/admin/learning/config` | Update settings |
| GET | `/admin/learning/pending` | Claims pending approval |
| POST | `/admin/learning/approve/{id}` | Approve claim |

### Admin Escalations

| Method | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/admin/escalations` | List escalations |
| GET | `/admin/escalations/{id}` | Escalation details |
| POST | `/admin/escalations/{id}/assign` | Assign to operator |
| POST | `/admin/escalations/{id}/resolve` | Mark resolved |

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

---

## 12. Referências

- [MEMO ÂNCORA](./references/memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md) - Visão do sistema
- [GMIF Framework](./references/Modelo Gráfico de Meta-Informação.md) - Framework de classificação
- [Grilo Falante Platform](./grilo_falante/platform/) - Platform Core
- [Unified Chat API](./grilo_chat_api/) - Chat API com routing
