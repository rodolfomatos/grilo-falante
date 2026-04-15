# 12. Todos os REST Endpoints

Referência completa da REST API.

---

## Base URL

```
http://localhost:8001
```

---

## Autenticação

Se configurado, usa header:

```
Authorization: Bearer <token>
```

---

## Health

### `GET /health`

Verificar saúde do sistema.

```bash
curl http://localhost:8001/health
```

**Resposta:**
```json
{
  "status": "ok",
  "version": "3.0.0",
  "database": "connected",
  "mempalace": "available"
}
```

---

## Claims

### `GET /api/v1/claims/{claim_id}`

Obter claim por ID.

```bash
curl http://localhost:8001/api/v1/claims/1
```

**Resposta:**
```json
{
  "id": 1,
  "claim_key": "CLM-temp-001",
  "claim_text": "A temperatura global aumentou 1.1°C",
  "gmif_level": "M5",
  "gmif_confidence": 0.85,
  "source_id": 1,
  "validation_state": "approved"
}
```

---

### `POST /api/v1/claims`

Criar nova claim.

```bash
curl -X POST http://localhost:8001/api/v1/claims \
  -H "Content-Type: application/json" \
  -d '{
    "claim_key": "CLM-test-001",
    "claim_text": "Exemplo de claim",
    "gmif_level": "M5",
    "gmif_confidence": 0.7,
    "source_id": 1
  }'
```

---

### `POST /api/v1/claims/{claim_id}/validate`

Validar claim.

```bash
curl -X POST http://localhost:8001/api/v1/claims/1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approved",
    "curator_id": 1,
    "notes": "Confirmado",
    "evaluator_confidence": 0.9
  }'
```

---

### `GET /api/v1/claims/cards`

Obter cards de claims para UI.

```bash
curl "http://localhost:8001/api/v1/claims/cards?limit=20"
```

---

### `GET /api/v1/claims/{claim_id}/card`

Obter card específico.

```bash
curl http://localhost:8001/api/v1/claims/1/card
```

---

## Query

### `POST /api/v1/query`

Executar query através do pipeline epistémico.

```bash
curl -X POST http://localhost:8001/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quais são as conclusões do relatório?",
    "session_id": "default",
    "auto_school_mode": true
  }'
```

**Resposta:**
```json
{
  "status": "allowed",
  "reason": "Query processed",
  "claims": [...],
  "gaps": [...],
  "governance_decision": {...}
}
```

---

## Gaps

### `GET /api/v1/gaps`

Listar gaps.

```bash
curl "http://localhost:8001/api/v1/gaps?limit=20"
```

**Parâmetros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| status | string | Filtrar por status |
| limit | int | Número máximo |

---

### `GET /api/v1/gaps/{gap_key}`

Obter gap específico.

```bash
curl http://localhost:8001/api/v1/gaps/GAP-260415-001
```

---

### `POST /api/v1/gaps`

Criar novo gap.

```bash
curl -X POST http://localhost:8001/api/v1/gaps \
  -H "Content-Type: application/json" \
  -d '{
    "gap_type": "factual",
    "query": "Qual é a temperatura em Marte?",
    "reason": "Informação não disponível",
    "session_id": "default"
  }'
```

---

### `POST /api/v1/gaps/{gap_key}/school-mode`

Executar school mode para gap.

```bash
curl -X POST http://localhost:8001/api/v1/gaps/GAP-260415-001/school-mode
```

---

## PINA Protocol

### `GET /api/v1/pina/pending`

Listar NCAs pendentes.

```bash
curl http://localhost:8001/api/v1/pina/pending
```

**Resposta:**
```json
{
  "pending_count": 2,
  "pending": [
    {
      "nca_id": "NCA-abc123",
      "source_document": "relatorio.pdf",
      "faithful_statement": "Todas as fontes devem ser renováveis",
      "location": "page 5",
      "created_at": "2026-04-15T14:00:00"
    }
  ]
}
```

---

### `GET /api/v1/pina/invariants`

Listar invariantes ativos.

```bash
curl http://localhost:8001/api/v1/pina/invariants
```

---

### `GET /api/v1/pina/status`

Estado completo do PINA.

```bash
curl http://localhost:8001/api/v1/pina/status
```

---

## Curators

### `POST /api/v1/curators`

Criar curator.

```bash
curl -X POST http://localhost:8001/api/v1/curators \
  -H "Content-Type: application/json" \
  -d '{
    "curator_key": "CUR-human-001",
    "name": "João Silva",
    "curator_type": "human",
    "specializations": ["climate", "energy"]
  }'
```

---

### `GET /api/v1/curators/{curator_id}`

Obter curator.

```bash
curl http://localhost:8001/api/v1/curators/1
```

---

## Sources

### `GET /api/v1/sources`

Listar fontes.

```bash
curl "http://localhost:8001/api/v1/sources?limit=20"
```

---

## Session

### `POST /api/v1/session/preferences`

Criar/atualizar preferências.

```bash
curl -X POST http://localhost:8001/api/v1/session/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "default",
    "topics": ["climate", "energy"],
    "recency_weight": 0.3,
    "preferred_categories": ["M1", "M2", "M5", "M7"],
    "auto_school_mode": true
  }'
```

---

### `GET /api/v1/session/preferences/{session_id}`

Obter preferências.

```bash
curl http://localhost:8001/api/v1/session/preferences/default
```

---

## Learning

### `POST /api/v1/learning-path`

Gerar caminho de aprendizagem.

```bash
curl -X POST http://localhost:8001/api/v1/learning-path \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Aquecimento global",
    "current_level": "beginner"
  }'
```

---

## Kanban

### `GET /api/v1/kanban`

Estado do kanban epistémico.

```bash
curl http://localhost:8001/api/v1/kanban
```

---

### `POST /api/v1/kanban/movements`

Criar movimento no kanban.

```bash
curl -X POST http://localhost:8001/api/v1/kanban/movements \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": 1,
    "from_column": "identified",
    "to_column": "validated"
  }'
```

---

## Audit

### `POST /api/v1/audit`

Executar auditoria.

```bash
curl -X POST http://localhost:8001/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Texto a auditar..."
  }'
```

---

## Prompts

### `POST /api/v1/prompts/triagem`

Workflow de triagem.

```bash
curl -X POST http://localhost:8001/api/v1/prompts/triagem \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Conteúdo a triar..."
  }'
```

---

### `POST /api/v1/prompts/radiografia`

Workflow radiografia.

```bash
curl -X POST http://localhost:8001/api/v1/prompts/radiografia \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Conteúdo a analisar..."
  }'
```

---

## Ingestion

### `POST /api/v1/ingest/pdf`

Upload e processar PDF.

```bash
curl -X POST http://localhost:8001/api/v1/ingest/pdf \
  -F "file=@documento.pdf"
```

---

### `GET /api/v1/shadow/{source_id}`

Obter shadow document.

```bash
curl http://localhost:8001/api/v1/shadow/1
```

---

## Governance

### `GET /api/v1/governance/{entity_type}/{entity_id}`

Obter histórico de governança.

```bash
curl http://localhost:8001/api/v1/governance/claim/1
```

---

## Graph

### `GET /api/v1/graph/dot`

Obter grafo em formato DOT.

```bash
curl "http://localhost:8001/api/v1/graph/dot?graph_id=gf-001"
```

---

## Feynman

### `POST /api/v1/feynman/explain`

Gerar explicação Feynman.

```bash
curl -X POST http://localhost:8001/api/v1/feynman/explain \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Aquecimento global",
    "level": "fep1"
  }'
```

---

## Manual (RAG)

### `GET /api/v1/manual/`

Índice dos capítulos.

```bash
curl http://localhost:8001/api/v1/manual/
```

---

### `GET /api/v1/manual/{chapter}`

Obter capítulo específico.

```bash
curl http://localhost:8001/api/v1/manual/05_regime_lifecycle
```

---

### `GET /api/v1/manual/search`

Pesquisar no manual.

```bash
curl "http://localhost:8001/api/v1/manual/search?q=GMIF"
```

---

## Resumo

| Categoria | Endpoints |
|-----------|-----------|
| **Health** | GET /health |
| **Claims** | GET, POST /api/v1/claims |
| **Query** | POST /api/v1/query |
| **Gaps** | GET, POST /api/v1/gaps |
| **PINA** | GET /api/v1/pina/* |
| **Curators** | GET, POST /api/v1/curators |
| **Sources** | GET /api/v1/sources |
| **Session** | GET, POST /api/v1/session/* |
| **Learning** | POST /api/v1/learning-path |
| **Kanban** | GET, POST /api/v1/kanban |
| **Audit** | POST /api/v1/audit |
| **Prompts** | POST /api/v1/prompts/* |
| **Ingestion** | POST /api/v1/ingest/pdf |
| **Graph** | GET /api/v1/graph/dot |
| **Feynman** | POST /api/v1/feynman/explain |
| **Manual** | GET /api/v1/manual/* |

---

*Voltar ao [Índice](../00_INDICE.md)*
