# 8. Claims e GMIF

## O Que é uma Claim?

Uma **claim** (afirmação) é uma declaração que pode ser verificada.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  "A temperatura global aumentou 1.1°C desde 1880."          │
│                                                             │
│  ✓ É uma claim porque:                                     │
│    - Pode ser verificada (sim/não)                         │
│    - Tem fontes (IPCC)                                     │
│    - Tem evidências                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### vs. Facto

| | Claim | Facto |
|--|-------|-------|
| **Definição** | Afirmação que requer verificação | Verdade comprovada |
| **Exemplo** | "X causou Y" | "O céu é azul" |
| **Status** | Pendente de verificação | Verificado |

---

## GMIF - Governance Markup Interpretation Framework

GMIF classifica claims por **força epistémica**:

### Os 7 Níveis

| Level | Nome | Descrição | Quando Usar |
|-------|------|-----------|-------------|
| **M1** | Primário | Provas múltiplas independentes | 3+ fontes confirmam |
| **M2** | Contextual | Verdadeiro sob suposições | "Se A, então B" |
| **M3** | Parcial | Estrutura incompleta | Sem suporte completo |
| **M4** | Duvidoso | Contradições detetadas | Fontes discordam |
| **M5** | Interpretação | Uma fonte clara | Uma fonte verifica |
| **M6** | Derivado | Inferência lógica | Segue de outras claims |
| **M7** | Síntese | Agregado de fontes | Com base em N fontes |

---

## Exemplos por Nível

### M1 - Primário
```python
# MULTIPLAS FONTES INDEPENDENTES CONFIRMAM
claim_text = (
    "O aquecimento global está a ocorrer porque: "
    "1) NASA confirma +1.1°C desde 1880, "
    "2) NOAA confirma, "
    "3) IPCC confirma com 95% confiança"
)
gmif_level = "M1"
# Requer: 2+ fontes independentes
```

### M2 - Contextual
```python
# VERDADEIRO SE ASSUMIRES CERTAS COISAS
claim_text = (
    "Se reduzirmos emissões em 50% até 2030, "
    "a temperatura estabiliza em +1.5°C"
)
gmif_level = "M2"
# Requer: Pressupostos declarados
```

### M3 - Parcial
```python
# ESTRUTURA LIMITADA, SEM SUPORTE COMPLETO
claim_text = "A teoria sugere que X causa Y"
gmif_level = "M3"
# Requer: Mais evidências
```

### M4 - Duvidoso
```python
# CONTRADIÇÕES DETETADAS
claim_text = "X causa Y (segundo estudo A), mas não Y (segundo estudo B)"
gmif_level = "M4"
# Requer: Investigação adicional
```

### M5 - Interpretação
```python
# UMA FONTE CLARA
claim_text = "O relatório IPCC afirma: +1.1°C desde 1880"
gmif_level = "M5"
# Requer: Fonte citada
```

### M6 - Derivado
```python
# INFERÊNCIA LÓGICA
claim_text = "X é verdade, Y segue de X, logo Y é verdade"
gmif_level = "M6"
# Requer: Cadeia lógica válida
```

### M7 - Síntese
```python
# AGREGAÇÃO DE MÚLTIPLAS FONTES
claim_text = (
    "Com base em 50 estudos analisados, "
    "conclui-se que X é a causa mais provável de Y"
)
gmif_level = "M7"
# Requer: N fontes, metodologia declarada
```

---

## Criar Claims

### Via MCP

```python
gepeto_create_claim(
    claim_key="CLM-temp-001",
    claim_text="A temperatura global aumentou 1.1°C desde 1880",
    gmif_level="M5",
    gmif_confidence=0.85,
    source_id=1,
    session_id="chat_260415"
)
```

**Resposta:**
```json
{
  "claim_key": "CLM-temp-001",
  "gmif_level": "M5",
  "created_at": "2026-04-15T14:30:00"
}
```

### Via Chat

```bash
> A temperatura global aumentou 1.1°C desde 1880.
[M5] OK. Claim criada: CLM-260415-abc123
```

### Através de Query

```python
gepeto_query(query="Qual é a temperatura global?")
# Automaticamente extrai claims e classifica
```

---

## Validar Claims

### Fluxo de Validação

```
┌──────────┐   criar    ┌───────────┐  validar  ┌──────────┐
│ PENDING  │ ─────────> │ SUBMITTED │ ───────> │ APPROVED │
└──────────┘            └───────────┘          └──────────┘
                              │
                              │ rejeitar
                              ▼
                        ┌──────────┐
                        │ REJECTED │
                        └──────────┘
```

### Exemplo

```python
gepeto_validate_claim(
    claim_id=1,
    curator_id=1,  # Quem valida
    decision="approved",  # approved, rejected, corrected
    notes="Confirmado por IPCC e NOAA",
    evaluator_confidence=0.9
)
```

---

## Claims e Governance

### Governance Gate

```
Claim entrada
     │
     ▼
┌──────────┐
│   M1?    │───Sim───► APPROVED
└────┬─────┘
     │ Não
     ▼
┌──────────┐
│   M4?    │───Sim───► BLOCKED (requer verificação)
└────┬─────┘
     │ Não
     ▼
┌──────────┐
│  outras? │──────────► SUBMITTED (para validação)
└──────────┘
```

### Regras

1. **M1 + fontes verificadas** → Aprovado automaticamente
2. **M4 (duvidoso)** → Bloqueado até verificação humana
3. **Sem fontes** → Requer validação

---

## GF-ID

Cada claim tem um **GF-ID** único:

```
GF-{YYMMDD}-{GMIF}-{HASH}

Exemplo: GF-260415-M5-temp11
```

**Formato:**
- `YYMMDD` = Data de criação
- `GMIF` = Nível GMIF
- `HASH` = Hash único do conteúdo

---

## Extrair Claims Automaticamente

O Grilo Falante pode extrair claims de texto:

### Via Chat

```bash
> O relatório indica que as vendas aumentaram 20% e os custos diminuíram 5%.
[M4] 2 claims extraídas:
  - CLM-001: "As vendas aumentaram 20%" (M5)
  - CLM-002: "Os custos diminuíram 5%" (M5)
```

### Via MCP

```python
# claims são automaticamente extraídas de queries
gepeto_query(query="O que diz o relatório sobre vendas?")
# Retorna claims extraídas + classificações
```

---

## Claims vs. Gaps

| Conceito | Descrição |
|----------|-----------|
| **Claim** | Uma afirmação que o sistema conhece |
| **Gap** | Uma questão que o sistema não sabe responder |

```
┌─────────────────────────────────────────┐
│                                           │
│  QUERY: "Qual é a temperatura em Marte?"  │
│                                           │
│  ┌─────────────┐                          │
│  │ Claim:      │                          │
│  │ "A Terra    │──────► Sei isto          │
│  │  aqueceu   │                          │
│  │  1.1°C"    │                          │
│  └─────────────┘                          │
│                                           │
│  ┌─────────────┐                          │
│  │ Gap:       │──────► NÃO sei isto      │
│  │ "Temp.     │                          │
│  │  Marte?"   │                          │
│  └─────────────┘                          │
│                                           │
└─────────────────────────────────────────┘
```

---

## Estado da Claim

| Estado | Significado |
|--------|-------------|
| `pending` | Criada, não validada |
| `submitted` | Submetida para validação |
| `approved` | Aprovada por curator |
| `rejected` | Rejeitada |
| `suspended` | Suspensa (requer investigação) |

---

## Próximo Passo

Agora que conheces claims e GMIF, vamos aprender sobre [Gaps e PINA](09_gaps_pina.md)!

---

*Voltar ao [Índice](../00_INDICE.md)*
