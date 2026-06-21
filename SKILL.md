---
summary: Grilo Falante v3.0 — Epistemic Governance Regime via MCP. Apply GMIF classification, premise propagation, and hostile audit to any input. Persists claims to PostgreSQL with pgvector similarity search.
version: 3.0.0
last_updated: 2026-06-21
name: grilo_falante
description: análise epistemológica de conteúdo - GMIF classification, PostgreSQL persistence, GF-IDs
trigger: /grilo
---

# /grilo

Analisa qualquer input (chat, artigo, decisão) aplicando os princípios do regime Grilo Falante:
- **GMIF** para classificar claims por força epistémica
- **PostgreSQL + pgvector** para persistir e indexar entre sessões
- **GF-IDs** como identificadores persistentes (como DOIs para claims)

## Pré-requisitos

Antes de usar, inicializa o regime:

```
1. grilo_load()
2. grilo_acordar(temporal_anchor="2026-04-15", intention="...")
```

Sem este ritual, o sistema está em estado INACTIVE.

## MCP Tools Disponíveis

### Regime Lifecycle
```
grilo_load()                              # Carregar regime
grilo_acordar(temporal_anchor, intention) # Ritual de acordar
grilo_vai_dormir()                       # Hibernar
grilo_resume()                            # Retomar
grilo_status()                            # Ver estado
```

### Query e Análise
```
gepeto_query(query="...")                 # Executar query com governança
gepeto_create_claim(claim_text="...")     # Criar claim
gepeto_get_claim(claim_id="...")         # Obter claim
grilo_classify_gmif(claim_text="...")   # Classificar GMIF
```

### Auditoria
```
grilo_run_auditoria_hostil(content="...") # Auditoria 5 eixos
grilo_audit()                            # Auditoria básica
```

### PINA Protocol
```
grilo_pina_propose(source_document, faithful_statement, location)
grilo_pina_decide(nca_id, decision)      # decision: "A", "B", ou "C"
grilo_pina_status()
```

### Gaps
```
gepeto_list_gaps()
gepeto_school_mode(gap_key="...")
```

## O Que Este Skill Faz

O Grilo Falante resolve três problemas:

1. **O LLM não guarda memória entre sessões** - PostgreSQL persiste tudo
2. **O LLM não sabe a força epistémica do que diz** - GMIF classifica
3. **Não há rastreabilidade** - GF-IDs permitem tracking

Este skill:
- Aplica GMIF para classificar cada claim
- Guarda tudo no PostgreSQL (persistente)
- Gera GF-IDs únicos e persistentes

## GMIF Classification

| Code | Name | Description |
|------|------|-------------|
| M1 | Primary Evidence | Múltiplas fontes independentes |
| M2 | Contextual | Válido sob suposições específicas |
| M3 | Partial | Suporte estrutural limitado |
| M4 | Doubtful | Contradições detetadas |
| M5 | Interpretation | Fonte clara única |
| M6 | Derived | Logicamente inferido |
| M7 | Synthesis | Agregado de múltiplas fontes |

## Fluxo de Trabalho

### Iniciar Sessão
```
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar relatório")
```

### Analisar
```
gepeto_query(query="Quais são as conclusões principais?")
```

### Criar Claim
```
gepeto_create_claim(claim_text="O mercado cresceu 5%", gmif_level="M5")
```

### Propor Normativa (PINA)
```
grilo_pina_propose(
    source_document="Relatório Q1",
    faithful_statement="O mercado cresceu 5%",
    location="page 3, paragraph 2"
)
```

### Terminar Sessão
```
grilo_vai_dormir()
```

## Regras

- Se não sabes, diz "não sei" - não inventes
- Hipóteses = M6 ou M3
- M1/M5 requer fonte verificável
- O skill NUNCA produz decisão - apenas análise

## Quando Falhar é Correto

Se não consegues verificar, BLOCK como **M3** ou **M4**.
Falhar é legítimo - não inventes.