# Grilo Falante v3.0 - Getting Started

## 1. Quick Start

### 1.1 Start Services

```bash
# Com Docker
docker-compose up -d

# Ou desenvolvimento
make dev
```

### 1.2 Conectar ao MCP Server

O MCP server está disponível em `localhost:8001`.

### 1.3 Iniciar Ciclo de Trabalho

```
1. grilo_load()
2. grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar relatório")
```

### 1.4 Fazer Query

```
gepeto_query(query="Quais são as principais conclusões do relatório?")
```

### 1.5 Terminar Ciclo

```
grilo_vai_dormir()
```

---

## 2. Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    REGIME LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   INACTIVE ──grilo_load()──> LOADED                       │
│                                     │                       │
│                         grilo_acordar()                     │
│                                     │                       │
│                                     v                       │
│   GOVERNING <──── ACTIVE <──────────                        │
│       │                                                     │
│       │         [trabalho]                                  │
│       │                                                     │
│       v                                                     │
│   HIBERNATED                                               │
│       │                                                     │
│   grilo_resume() ou grilo_vai_dormir()                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Exemplos Práticos

### 3.1 Analisar um Texto

```python
# 1. Carregar regime
grilo_load()

# 2. Acordar com intenção clara
grilo_acordar(
    temporal_anchor="2026-04-15",
    intention="Analisar artigo sobre mudanças climáticas"
)

# 3. Criar claims para afirmações importantes
gepeto_create_claim(
    claim_text="A temperatura média global aumentou 1.1°C desde 1880",
    gmif_level="M5",
    source_id=1
)

# 4. Fazer query sobre o conteúdo
gepeto_query(query="Quais são as principais evidências do artigo?")

# 5. Se encontrar normative candidates (normas escondidas)
grilo_pina_propose(
    source_document="artigo_mudancas_climaticas.pdf",
    faithful_statement="Todas as fontes de energia devem ser renováveis",
    location="page 5"
)
# Humano decide: grilo_pina_decide(nca_id="NCA-xxx", decision="A")

# 6. Terminar
grilo_vai_dormir()
```

### 3.2 Auditoria Hostil

```python
# Analisar conteúdo existente
grilo_run_auditoria_hostil(
    content="O estudo prova que os LLMs são conscientes porque passaram no teste de Turing."
)
# Retorna relatório com issues encontrados
```

### 3.3 Resolver Gaps

```python
# Listar gaps identificados
gepeto_list_gaps()

# Executar school mode para um gap
gepeto_school_mode(gap_key="GAP-20260415-001")
```

---

## 4. GMIF Classification Quick Reference

| Level | Quando usar | Exemplo |
|-------|-------------|---------|
| **M1** | Fontes múltiplas independentes confirmam | "3 estudos peer-reviewed mostram X" |
| **M2** | Válido sob suposições específicas | "Se A, então B (com A como premissa)" |
| **M3** | Estrutura limitada, sem suporte completo | "A teoria sugere que X" |
| **M4** | Contradições detetadas | "X segundo A, mas Y segundo B" |
| **M5** | Uma fonte clara | "O relatório do IPCC afirma X" |
| **M6** | Inferência lógica de outros claims | "Portanto, X segue de A e B" |
| **M7** | Agregação de múltiplas fontes | "Com base em 5 estudos, X" |

---

## 5. PINA Protocol

O PINA gere **Normative Candidates (NCA)** - regras extraídas do conteúdo.

### Fluxo PINA

```
1. Propor NCA
   grilo_pina_propose(source_document, faithful_statement, location)

2. Humano decide
   grilo_pina_decide(nca_id, decision)
   - A: Incorporar (regra torna-se INVARIANT)
   - B: Não incorporar
   - C: Adiar

3. Verificar estado
   grilo_pina_status()
```

---

## 6. State Machine

```
                    Pipeline Cognitivo (F0-F8)
                    (implementado mas não automático)

┌──────┐    LOAD    ┌────────┐   ACORDAR   ┌─────────┐
│INACTIVE│ ───────> │ LOADED │ ──────────> │ ACTIVE  │
└──────┘            └────────┘             └────┬────┘
                         │                       │
                         │                       v
                         │                ┌──────────────┐
                         └──────────────> │  GOVERNING   │
                                          └──────┬───────┘
                                                 │
                            grilo_vai_dormir()   │ grilo_resume()
                                                 v
                                          ┌───────────┐
                                          │ HIBERNATED│
                                          └───────────┘
```

---

## 7. Erros Comuns

### ❌ Não fazer grilo_load primeiro
```
Erro: "No active cycle"
Solução: grilo_load() antes de qualquer operação
```

### ❌ Não fazer grilo_acordar
```
Erro: Regime funciona mas não há registo de intenção
Solução: grilo_acordar() para declarar propósito
```

### ❌ Afirmações M1 sem fonte
```
Erro: "Isto é M1 porque é óbvio"
Correção: M1 requer 2+ fontes independentes
```

### ❌ Ignorar M4
```
Erro: "Vou ignorar as contradições"
Correção: M4 significa que algo está errado - investigar
```

---

## 8. API REST vs MCP

| Funcionalidade | REST API | MCP |
|----------------|----------|-----|
| Query | `POST /api/v1/query` | `gepeto_query()` |
| Claims | `POST /api/v1/claims` | `gepeto_create_claim()` |
| Auditoria | `POST /api/v1/audit` | `grilo_audit()` |
| Regime | Não disponível | `grilo_load/acordar/vai_dormir` |

**Regime lifecycle só disponível via MCP.**

---

## 9. Formato de Respostas

### Query Result
```json
{
  "status": "allowed|blocked|review",
  "reason": "explicação",
  "claims": [...],
  "gaps": [...],
  "governance_decision": {...}
}
```

### Claim
```json
{
  "claim_key": "CLM-xxx",
  "claim_text": "...",
  "gmif_level": "M5",
  "gmif_confidence": 0.7,
  "source_id": 1
}
```

---

## 10. Próximos Passos

1. Ler [SKILL.md](./SKILL.md) - Referência completa
2. Ler [regime.md](./grilo_falante/regime/regime.md) - Documentação do regime
3. Ler [ACORDAR.md](./grilo_falante/docs/ACORDAR.md) - Ritual de inicialização
4. Explorar [docs/](./grilo_falante/docs/) - Documentação adicional