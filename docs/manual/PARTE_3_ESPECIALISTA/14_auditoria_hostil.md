# 14. Auditoria Hostil

## O Que É?

A **Auditoria Hostil** é um processo de 5 eixos que verifica se o teu raciocínio está bem fundamentado.

---

## Os 5 Eixos

| Eixo | Nome | O Que Verifica |
|------|------|----------------|
| 1 | Modo Automático | Limites do modo automático |
| 2 | Validação Automática | Nível de validação |
| 3 | Grafos Epistémicos | Estrutura do conhecimento |
| 4 | Ledger de Preservação | Registo de eventos |
| 5 | Pipeline Normativo | Tratamento de normas |

---

## Como Usar

### Via MCP

```python
grilo_audit(limit=50)
```

**Resultado:**
```json
{
  "claims_audited": 50,
  "findings": [
    {"axis": "MODO_AUTOMATICO", "severity": "MAJOR", "message": "..."}
  ],
  "audit_result": {
    "axes_results": {...}
  }
}
```

---

### Via CLI

```bash
grilo_run_auditoria_hostil(content="Texto a auditar...")
```

---

## Resultado da Auditoria

### Findings

```json
{
  "axis": "MODO_AUTOMATICO",
  "severity": "CRITICAL|MAJOR|MINOR",
  "claim_id": "CLM-xxx",
  "message": "Descrição do problema",
  "suggestion": "Como corrigir"
}
```

### Severity Levels

| Nível | Significado |
|-------|-------------|
| CRITICAL | Bloqueia operação |
| MAJOR | Deve ser corrigido |
| MINOR | Recomendação |

---

## Exemplos

### Texto Problema

```
"O estudo prova que LLMs são conscientes porque passaram no teste de Turing."
```

**Auditoria encontra:**

| Eixo | Finding | Severidade |
|------|---------|------------|
| 1 | "prova" requer evidência | CRITICAL |
| 2 | Claim sem validação | MAJOR |
| 3 | Sem suporte em grafo | MINOR |

---

## Workflow Completo

```
1. grilo_audit()
   │
   └→ 5 eixos verificados
           │
           ▼
      Findings gerados
           │
           ▼
      Relatório final
           │
           ▼
      Recomendações
```

---

## Integridade Checklist

O sistema pode verificar Claims contra um checklist:

```python
grilo_stamp_capsule(
    capsule_path="/path/to/file.md",
    gmif_level="M5"
)
# Verifica se claims no ficheiro são consistentes
```

---

*Voltar ao [Índice](../00_INDICE.md)*
