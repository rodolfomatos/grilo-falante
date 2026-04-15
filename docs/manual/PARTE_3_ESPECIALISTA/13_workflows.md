# 13. Workflows

## O Que São?

Workflows são processos automatizados que executam tarefas complexas.

---

## Workflows Disponíveis

| Workflow | Descrição |
|----------|-----------|
| `auditoria_hostil` | Análise de 5 eixos |
| `autopsia_literatura` | Análise profunda de artigos |
| `triagem` | Triagem inicial de conteúdo |
| `radiografia` | Análise detalhada de erros |

---

## Auditoria Hostil

Análise completa de texto.

```python
grilo_run_auditoria_hostil(content="Texto a analisar...")
```

---

## Autopsia Literatura

Análise profunda de artigos científicos.

```python
grilo_run_autopsia_literatura(content="Artigo completo...")
```

**Faz:**
1. Extrai claims
2. Verifica fontes
3. Deteta contradições
4. Gera relatório

---

## Triagem

Triagem inicial de conteúdo.

```python
grilo_run_triagem(content="Conteúdo a trier...")
```

**Faz:**
1. Identifica tipo de conteúdo
2. Extrai claims básicas
3. Classifica GMIF preliminar
4. Identifica gaps

---

## Radiografia

Análise detalhada de erros.

```python
# Via REST
curl -X POST http://localhost:8001/api/v1/prompts/radiografia \
  -d '{"content": "Texto com erros..."}'
```

**Faz:**
1. Deteta erros factuais
2. Identifica fontes
3. Sugere correções
4. Documenta no ledger

---

## Via REST API

```bash
# Triagem
curl -X POST http://localhost:8001/api/v1/prompts/triagem \
  -H "Content-Type: application/json" \
  -d '{"content": "..."}'

# Radiografia
curl -X POST http://localhost:8001/api/v1/prompts/radiografia \
  -H "Content-Type: application/json" \
  -d '{"content": "..."}'
```

---

*Voltar ao [Índice](../00_INDICE.md)*
