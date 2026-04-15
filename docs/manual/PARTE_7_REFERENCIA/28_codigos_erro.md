# 28. Códigos de Erro

## Erros Comuns

| Código | Mensagem | Solução |
|--------|----------|---------|
| E001 | "No active cycle" | Executar grilo_load() |
| E002 | "Regime not in GOVERNING state" | Executar grilo_acordar() |
| E003 | "Session not found" | Verificar session_id |
| E004 | "Claim not found" | Verificar claim_id |
| E005 | "Invalid GMIF level" | Usar M1-M7 |

---

## Erros de Base de Dados

| Código | Mensagem | Solução |
|--------|----------|---------|
| E101 | "Connection refused" | Verificar PostgreSQL |
| E102 | "relation does not exist" | Correr migrations |
| E103 | "duplicate key" | Usar ID único |

---

## Erros de MemPalace

| Código | Mensagem | Solução |
|--------|----------|---------|
| E201 | "Collection not found" | Criar collection |
| E202 | "Database locked" | Matar processos chroma |
| E203 | "Path not found" | Verificar MEMPALACE_PATH |

---

## Erros de LLM

| Código | Mensagem | Solução |
|--------|----------|---------|
| E301 | "Connection refused" | Verificar Ollama |
| E302 | "Model not found" | Descarregar modelo |
| E303 | "Embedding failed" | Verificar modelo embeddings |

---

## Erros de Governance

| Código | Mensagem | Solução |
|--------|----------|---------|
| E401 | "M4 claims require verification" | Validar claims |
| E402 | "Blocking pattern detected" | Remover palavras bloqueantes |
| E403 | "Invalid PINA decision" | Usar A, B ou C |

---

## Erros de API

| Código | Mensagem | Solução |
|--------|----------|---------|
| E501 | "401 Unauthorized" | Verificar API_TOKEN |
| E502 | "404 Not Found" | Verificar endpoint |
| E503 | "422 Validation Error" | Verificar parâmetros |

---

*Voltar ao [Índice](../00_INDICE.md)*
