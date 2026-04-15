# 5. Regime Lifecycle

## O Que é?

O **Regime Lifecycle** é o ciclo de vida do Grilo Falante. Tal como um dia tem manhã, trabalho, e noite, o Grilo Falante tem estados.

---

## Diagrama de Estados

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                    REGIME LIFECYCLE                          │
│                                                             │
│  ┌──────────┐    grilo_load()    ┌──────────┐             │
│  │ INACTIVE │ ─────────────────> │  LOADED  │             │
│  └──────────┘                    └────┬─────┘             │
│                                        │                   │
│                                        │ grilo_acordar()   │
│                                        ▼                   │
│  ┌───────────┐    grilo_vai_dormir() ┌──────────┐        │
│  │ HIBERNATED│ <──────────────────── │ GOVERNING│        │
│  └─────┬─────┘                       └────┬─────┘        │
│        │         grilo_resume()           │               │
│        │                                  │               │
│        └──────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Estados

### INACTIVE
**O sistema está parado.**

- Nenhum ciclo ativo
- Não guarda conhecimento
- Não responde a queries

```python
grilo_status()
# {"state": "INACTIVE", "cycle_id": null}
```

---

### LOADED
**O regime está carregado mas ainda não acordou.**

- Ciclo criado
- Claims podem ser criadas
- Mas ainda não está em "modo governado"

```python
grilo_load()
# {"success": true, "state": "LOADED", "cycle_id": "CYCLE-260415-abc123"}

grilo_status()
# {"state": "LOADED", "cycle_id": "CYCLE-260415-abc123"}
```

---

### GOVERNING
**O regime está ativo e a governar.**

- Regime fully operational
- Queries são processadas com governance
- Claims são classificadas
- Ledger regista tudo

```python
grilo_acordar(
    temporal_anchor="2026-04-15",
    intention="Analisar relatório de vendas"
)
# {"success": true, "state": "GOVERNING"}

grilo_status()
# {"state": "GOVERNING", "cycle_id": "CYCLE-260415-abc123", "claims_count": 15}
```

---

### HIBERNATED
**O regime está suspenso mas pode retomar.**

- Session preserved
- Claims guardadas
- Pode retomar com `grilo_resume()`

```python
grilo_vai_dormir()
# {"success": true, "state": "HIBERNATED"}

grilo_status()
# {"state": "HIBERNATED", "cycle_id": "CYCLE-260415-abc123"}
```

---

## Ciclo Completo

```
┌─────────────────────────────────────────────────────────────┐
│  1. INICIAR                                               │
│     $ grilo_load()                                        │
│         │                                                 │
│         ▼                                                 │
│     INACTIVE ───> LOADED                                 │
│                                                             │
│  2. ACORDAR                                               │
│     $ grilo_acordar(temporal_anchor="2026-04-15",        │
│                      intention="Analisar relatório")        │
│         │                                                 │
│         ▼                                                 │
│     LOADED ───> GOVERNING                                │
│                                                             │
│  3. TRABALHAR                                             │
│     $ gepeto_query(query="...")                           │
│     $ grilo_pina_propose(...)                            │
│     $ grilo_run_auditoria_hostil(...)                    │
│         │                                                 │
│         ▼                                                 │
│     [ Claims extraídas, classificadas, guardadas ]       │
│                                                             │
│  4. DORMIR                                                │
│     $ grilo_vai_dormir()                                 │
│         │                                                 │
│         ▼                                                 │
│     GOVERNING ───> HIBERNATED                            │
│                                                             │
│  5. RETOMAR (opcional)                                    │
│     $ grilo_resume()                                      │
│         │                                                 │
│         ▼                                                 │
│     HIBERNATED ───> GOVERNING                            │
│                                                             │
│  6. TERMINAR (quando pronto)                             │
│     $ grilo_unload()                                      │
│         │                                                 │
│         ▼                                                 │
│     Qualquer estado ───> INACTIVE                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Exemplos Práticos

### Exemplo 1: Análise Rápida

```python
# Começar
grilo_load()  # → LOADED

# Configurar
grilo_acordar(
    temporal_anchor="2026-04-15",
    intention="Verificar facts",
    mode="exploratory"
)  # → GOVERNING

# Trabalhar
gepeto_query(query="Quais são as fontes?")

# Terminar
grilo_vai_dormir()  # → HIBERNATED
```

### Exemplo 2: Sessão Longa

```python
# Começar de manhã
grilo_load()
grilo_acordar(intention="Análise de mercado")

# Trabalhar...
gepeto_query(query="...")
gepeto_create_claim(...)

# Pausa para almoço
grilo_vai_dormir()  # → HIBERNATED

# Retomar depois
grilo_resume()  # → GOVERNING

# Continuar trabalho...

# Terminar quando acabar
grilo_unload()  # → INACTIVE
```

### Exemplo 3: Com Chat Governado

```python
# Via chat CLI
$ /grilo chat

# O chat internamente faz:
grilo_load()        # → LOADED
grilo_acordar()    # → GOVERNING

# Fase interactiva
> mensagem 1
> mensagem 2

# Sair
> :quit
grilo_vai_dormir()  # → HIBERNATED
```

---

## Parâmetros do ACORDAR

### temporal_anchor
A âncora temporal indica o contexto de tempo.

```python
grilo_acordar(
    temporal_anchor="2026-04-15",  # Data específica
    intention="..."
)
# ou
grilo_acordar(
    temporal_anchor="2026-04-15T14:30:00",  # Com hora
    intention="..."
)
```

**Dica:** Usa a data real para que o sistema saiba em que momento estás a pensar.

### intention
A intenção indica o objetivo da sessão.

```python
grilo_acordar(
    intention="Analisar relatório de vendas Q1"
)
# ou
grilo_acordar(
    intention="Verificar factos do artigo sobre IA"
)
# ou
grilo_acordar(
    intention="Brainstorming para projeto X"
)
```

### mode
O modo indica o tipo de trabalho.

| Modo | Descrição |
|------|-----------|
| `exploratory` | Exploratório, sem compromisso |
| `committed` | Comprometido, decisões têm peso |

```python
grilo_acordar(
    intention="Planeamento estratégico",
    mode="committed"  # Decisions will be binding
)
```

---

## O que Acontece em Cada Estado

| Estado | grilo_load | grilo_acordar | Queries | Claims | Ledger |
|--------|------------|---------------|---------|--------|--------|
| INACTIVE | ✅ | ❌ | ❌ | ❌ | ❌ |
| LOADED | ✅ | ✅ | ✅ | ✅ | ❌ |
| GOVERNING | ❌ | ❌ | ✅ | ✅ | ✅ |
| HIBERNATED | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Ledger

O **Ledger** é o diário do ciclo. Regista tudo o que acontece.

```python
grilo_get_ledger_stats()
# {
#     "entries": 45,
#     "cycles": 3,
#     "last_entry": "2026-04-15T14:30:00"
# }
```

**O ledger guarda:**
- Claims criadas
- Transições de estado
- Decisões PINA
- Auditorias executadas

---

## Session vs Cycle

| Conceito | Descrição |
|----------|-----------|
| **session_id** | Conversa com o utilizador (ex: "chat_260415") |
| **cycle_id** | Ciclo do regime (ex: "CYCLE-260415-abc123") |

```
session_id: "chat_260415_143022"  ← A tua conversa
    │
    └── cycle_id: "CYCLE-260415-abc123"  ← O ciclo do regime
```

---

##Próximo Passo

Agora que conheces o lifecycle, vamos aprender o [fluxo completo](07_fluxo_completo.md)!

---

*Voltar ao [Índice](../00_INDICE.md)*
