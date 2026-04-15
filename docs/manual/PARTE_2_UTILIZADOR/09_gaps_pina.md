# 9. Gaps e PINA

## O Que São Gaps?

Um **gap** (lacuna) é algo que o sistema **não sabe** mas precisa.

```
QUERY: "Qual é a temperatura em Marte?"
  → Sistema não sabe
  → Gap identificado: temperatura_marte
  → School Mode recomendado
```

---

## Tipos de Gaps

| Tipo | Descrição |
|------|-----------|
| `factual` | Facto específico |
| `conceptual` | Conceito não entendido |
| `relational` | Relação entre conceitos |
| `methodological` | Método de verificação |

---

## School Mode (Ir à Escola)

Resolve gaps buscando informação:

```
Gap identificado → Research → Claim criada → Guardada
```

```python
gepeto_school_mode(gap_key="GAP-xxx", research_depth="moderate")
```

---

## PINA Protocol

PINA = Protocol for Normative Incorporation

Extrai **regras normativas** do conteúdo.

---

## Fluxo PINA

```
1. PROPOSE  → grilo_pina_propose()
2. DECIDE   → grilo_pina_decide(nca_id, decision)
3. STATUS   → grilo_pina_status()
```

**Decisões:**
- A = Incorporar (torna-se INVARIANT)
- B = Não incorporar
- C = Adiar

---

## API Gaps

```python
gepeto_list_gaps()           # Listar
gepeto_get_gap(gap_key)      # Obter
gepeto_school_mode(gap_key)   # Resolver
```

---

## API PINA

```python
grilo_pina_propose(
    source_document="doc.pdf",
    faithful_statement="Regra extraída",
    location="page 5"
)

grilo_pina_decide(nca_id="NCA-xxx", decision="A")

grilo_pina_status()

grilo_pina_pending()
```

---

*Voltar ao [Índice](../00_INDICE.md)*
