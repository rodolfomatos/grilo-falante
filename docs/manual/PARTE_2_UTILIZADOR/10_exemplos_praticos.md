# 10. Exemplos Práticos

## 1. Analisar um Relatório

```python
# 1. Iniciar
grilo_load()
grilo_acordar(
    temporal_anchor="2026-04-15",
    intention="Analisar relatório Q1",
    mode="exploratory"
)

# 2. Fazer query
gepeto_query(query="Quais são as principais conclusões do relatório?")

# 3. Extrair claims
# Sistema automaticamente extrai claims do relatório

# 4. Criar claim manual
gepeto_create_claim(
    claim_text="As vendas aumentaram 20% no Q1",
    gmif_level="M5",
    source_id=1
)

# 5. Terminar
grilo_vai_dormir()
```

---

## 2. Chat Governado

```bash
$ /grilo chat

> grilo_load()
{"success": true, "state": "LOADED"}

> grilo_acordar(temporal_anchor="2026-04-15", intention="Brainstorming")
{"success": true, "state": "GOVERNING"}

> Precisamos aumentar vendas em 50%.
[M5] OK. 1 claim extraída.

> Podemos fazer isso com novos mercados.
[M3] OK. 1 claim extraída.

> Os novos mercados têm risco elevado.
[M4] 2 claims bloqueadas - requerem verificação.

> :status
{"messages": 4, "claims": 3}

> :quit
Sessão terminada. Claims: 3
```

---

## 3. Verificar Facts

```python
# 1. Query com verificação
gepeto_query(
    query="A temperatura global aumentou quanto desde 1880?"
)

# 2. Ver resultado
# Se claim M5 (uma fonte): Verificar fonte
# Se claim M4 (duvidoso): Investigar contradições

# 3. Validar claim
gepeto_validate_claim(
    claim_id=1,
    curator_id=1,
    decision="approved",
    notes="Confirmado por IPCC 2023"
)
```

---

## 4. Auditoria Hostil

```python
# Analisar texto para problemas
grilo_run_auditoria_hostil(
    content="O estudo prova que LLMs são conscientes porque passaram no teste de Turing."
)

# Resultado:
# - Axis 1: BLOCKED - "prova" requer evidência
# - Axis 2: M4 - Contradição detetada
# - etc.
```

---

## 5. Extrair Normas com PINA

```python
# 1. Identificar norma no texto
# "Todas as fontes de energia devem ser renováveis"

# 2. Propor
grilo_pina_propose(
    source_document="politica_energia.pdf",
    faithful_statement="Todas as fontes de energia devem ser renováveis",
    location="page 5, parágrafo 2"
)
# NCA-abc123 proposto

# 3. Humano decide
# (Ninguém excepto humano pode decidir!)

# 4. Registar
grilo_pina_decide(nca_id="NCA-abc123", decision="A")
# Incorporado como INVARIANT
```

---

## 6. Resolver Gaps

```python
# 1. Detetar gap
gepeto_list_gaps()
# GAP-260415-001: "Temperatura em Marte?"

# 2. School mode
gepeto_school_mode(
    gap_key="GAP-260415-001",
    research_depth="moderate"
)
# Claim criada: "Temperatura média em Marte é -63°C"

# 3. Verificar
gepeto_validate_claim(
    claim_id=2,
    decision="approved"
)
```

---

## 7. Via REST API

```bash
# Criar claim
curl -X POST http://localhost:8001/api/v1/claims \
  -H "Content-Type: application/json" \
  -d '{"claim_key": "CLM-001", "claim_text": "...", "gmif_level": "M5"}'

# Query
curl -X POST http://localhost:8001/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual é a conclusão?"}'

# Ver gaps
curl http://localhost:8001/api/v1/gaps

# Ver PINA pendentes
curl http://localhost:8001/api/v1/pina/pending
```

---

## 8. Integração com Código

```python
from grilo_falante.backend.mcp.server import app
from mcp.server.stdio import stdio_server

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

# Run
asyncio.run(main())
```

---

## 9. Workflow Completo

```
1. LOAD     grilo_load()
2. ACORDAR  grilo_acordar(intention="...")
3. QUERY    gepeto_query(query="...")
4. CLAIMS   gepeto_create_claim(...)
5. AUDIT    grilo_audit()
6. PINA     grilo_pina_propose(...)
7. GAPS     gepeto_school_mode(...)
8. VAI_DORMIR grilo_vai_dormir()
```

---

*Voltar ao [Índice](../00_INDICE.md)*
