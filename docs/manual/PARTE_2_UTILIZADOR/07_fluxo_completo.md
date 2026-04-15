# 07. Fluxo Completo

## Do Início ao Fim

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. PREPARAR                                               │
│     docker-compose up -d                                    │
│                                                             │
│  2. CARREGAR                                               │
│     grilo_load() → LOADED                                  │
│                                                             │
│  3. ACORDAR                                                │
│     grilo_acordar(intention="...") → GOVERNING            │
│                                                             │
│  4. TRABALHAR                                              │
│     Query → Claims → Gaps → PINA → Audit                   │
│                                                             │
│  5. DORMIR                                                 │
│     grilo_vai_dormir() → HIBERNATED                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# 1. Iniciar
docker-compose up -d

# 2. Chat
python3 -m app.skills.grilo_falante_skill chat

# 3. Dentro do chat
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="...")
> tua mensagem

# 4. Sair
:quit
```

---

## Fluxo Detalhado

### 1. Query → Claims

```
> "As vendas aumentaram 20%"
         │
         ▼
┌─────────────────┐
│  Extract claims │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classify GMIF   │
│ M5 (fonte)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Governance gate │
│ Passed ✓        │
└────────┬────────┘
         │
         ▼
    Store claim
```

### 2. Query → Gaps

```
> "Como aumentar vendas?"
         │
         ▼
┌─────────────────┐
│ Check knowledge │
└────────┬────────┘
         │
         ▼
    Gap detetado
         │
         ▼
┌─────────────────┐
│ Create GAP      │
│ GAP-260415-001 │
└─────────────────┘
```

### 3. PINA Flow

```
> "Todas as decisões devem ter evidência"
         │
         ▼
┌─────────────────┐
│ Propose NCA    │
└────────┬────────┘
         │
         ▼
    NCA pending
         │
         ▼
   Humano decide
   A/B/C
         │
         ▼
┌─────────────────┐
│ Incorporate?   │
│ → INVARIANT     │
└─────────────────┘
```

---

## Estados e Transições

| De | Para | Ação |
|----|------|------|
| INACTIVE | LOADED | grilo_load() |
| LOADED | GOVERNING | grilo_acordar() |
| GOVERNING | HIBERNATED | grilo_vai_dormir() |
| HIBERNATED | GOVERNING | grilo_resume() |
| * | INACTIVE | grilo_unload() |

---

## Guardar e Retomar

```python
# Guardar sessão
grilo_export_session(session_id="chat_xxx")
# → Script bash guardado

# Noutro terminal
source grilo-resume-chat_xxx.sh

# Continuar
grilo_resume()
```

---

## Ferramentas por Fase

| Fase | Ferramentas |
|------|-------------|
| **Regime** | grilo_load, grilo_acordar, grilo_vai_dormir |
| **Query** | gepeto_query, grilo_semantic_search |
| **Claims** | gepeto_create_claim, gepeto_validate_claim |
| **Gaps** | gepeto_list_gaps, gepeto_school_mode |
| **PINA** | grilo_pina_propose, grilo_pina_decide |
| **Audit** | grilo_audit, grilo_run_auditoria_hostil |

---

*Voltar ao [Índice](../00_INDICE.md)*
