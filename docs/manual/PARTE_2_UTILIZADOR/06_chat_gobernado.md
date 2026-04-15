# 6. Chat Governado

## O Que é?

O **chat governado** é uma conversa com o Grilo Falante onde todas as tuas afirmações são:
- Extraídas automaticamente
- Classificadas com GMIF
- Guardadas em memória

É como ter um amigo que anota tudo o que dizes e te ajuda a pensar!

---

## Como Usar

### Opção 1: CLI Interativo

```bash
# No terminal
cd ~/src/grilo_falante_v3.0
python3 -m app.skills.grilo_falante_skill chat
```

**Ou simplesmente:**

```bash
/grilo chat
```

**Resultado:**

```
============================================================
GRILO FALANTE - CHAT GOVERNADO
============================================================

Este chat é governado pelo regime Grilo Falante.
Todas as mensagens são analisadas para claims
e classificadas com GMIF (M1-M7).

Comandos:
  :quit, :exit    Sair
  :save           Guardar sessão
  :export         Exportar script de resume
  :status         Ver estado

============================================================

Sessão iniciada: chat_260415_143022
Cycle ID: CYCLE-260415-6f71a939
Estado: GOVERNING

> _
```

### Opção 2: Via MCP (para LLMs)

```python
# 1. Iniciar sessão
grilo_chat_start(
    intention="Analisar relatório de vendas",
    temporal_anchor="2026-04-15"
)
# Retorna: {"session_id": "mcp_260415_143022", "state": "GOVERNING", ...}

# 2. Enviar mensagem
grilo_chat_send(
    message="As vendas aumentaram 20% no último trimestre.",
    session_id="mcp_260415_143022"
)
# Retorna: {"claims_extracted": 2, "gmif_summary": {"fact": 1, "claim": 1}, ...}

# 3. Terminar sessão
grilo_chat_end(session_id="mcp_260415_143022")
```

---

## Fluxo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. INICIAR                                                 │
│     grilo_chat_start(intention="...")                       │
│              │                                              │
│              ▼                                              │
│  ┌──────────────────┐                                       │
│  │  Regime LOADED   │                                       │
│  └────────┬─────────┘                                       │
│           │ grilo_acordar()                                 │
│           ▼                                                  │
│  ┌──────────────────┐                                       │
│  │ Regime GOVERNING │ ◄─── Estado ativo                     │
│  └────────┬─────────┘                                       │
│           │                                                  │
│           ▼                                                  │
│  2. MENSAGEM                                                │
│     > "As vendas subiram 20%"                              │
│              │                                              │
│           ┌──┴──────────────┐                               │
│           │  EXTRACÇÃO      │                               │
│           │  Claims extraídas│                               │
│           └─┬──────────────┘                               │
│             │                                               │
│           ┌─┴──────────────┐                               │
│           │  CLASSIFICAÇÃO │                               │
│           │  GMIF aplicado  │                               │
│           └─┬──────────────┘                               │
│             │                                               │
│           ┌─┴──────────────┐                               │
│           │  GOVERNANCE    │                               │
│           │  Verificação   │                               │
│           └─┬──────────────┘                               │
│             │                                               │
│             ▼                                               │
│  3. GUARDAR                                                 │
│     MemPalace + PostgreSQL                                 │
│             │                                               │
│             ▼                                               │
│  4. RESPONDER                                                │
│     [M5: fact] OK. 2 claims extraídas.                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Exemplo Prático

```bash
> grilo_load()
{"success": true, "cycle_id": "CYCLE-260415-abc123", "state": "LOADED"}

> grilo_acordar(temporal_anchor="2026-04-15", intention="Analisar relatório Q1")
{"success": true, "state": "GOVERNING", "intention_declared": "Analisar relatório Q1"}

> As vendas da empresa aumentaram 20% no Q1 de 2026.
[{'fact': 1, 'claim': 1}] OK. 2 claims extraídas.

> O relatório indica que o mercado europeu foi o principal impulsionador.
[{'fact': 1}] OK. 1 claims extraídas.

> O crescimento foi impulsionado principalmente por novos clientes.
[{'interpretation': 1}] OK. 1 claims extraídas.

> :status
{"session_id": "chat_260415_143022", "state": "GOVERNING",
 "messages_count": 4, "claims_count": 4, "cycle_id": "CYCLE-260415-abc123"}

> :quit
Sessão terminada. Claims guardadas: 4
```

---

## Auto-Save

O chat guarda automaticamente a cada **5 mensagens**:

```bash
> (envias mensagem 1)
> (envias mensagem 2)
> (envias mensagem 3)
> (envias mensagem 4)
> (envias mensagem 5)
[AUTO-SAVE] Sessão guardada: {"messages_count": 5, "claims_count": 5}
> (envias mensagem 6)
> (envias mensagem 7)
> ...
> (envias mensagem 10)
[AUTO-SAVE] Sessão guardada: {"messages_count": 10, "claims_count": 10}
```

---

## Exportar Sessão

Para retomar depois:

```bash
> :export
#!/bin/bash
# Grilo Falante Session Resume
# Session: chat_260415_143022
# Cycle: CYCLE-260415-abc123
# Date: 2026-04-15T14:30:22

export GRILO_SESSION_ID="chat_260415_143022"
export GRILO_CYCLE_ID="CYCLE-260415-abc123"

echo "Resuming Grilo Falante session: chat_260415_143022"
echo "Cycle: CYCLE-260415-abc123"
echo ""
echo "To resume, use:"
echo "  grilo chat --session chat_260415_143022"
```

**Para guardar:**

```bash
# Copiar o script para um ficheiro
cat > ~/grilo-resume.sh << 'EOF'
#!/bin/bash
export GRILO_SESSION_ID="chat_260415_143022"
export GRILO_CYCLE_ID="CYCLE-260415-abc123"
source ~/src/grilo_falante_v3.0/shell-utils.sh
grilo_resume --cycle $GRILO_CYCLE_ID
EOF

chmod +x ~/grilo-resume.sh
```

**Para retomar:**

```bash
source ~/grilo-resume.sh
```

---

## Governance Gate

O chat tem um **gate de governança** que bloqueia claims suspeitas:

**Bloqueado se:**
- Contém "obviamente", "claramente", "é óbvio"
- Contradições detetadas
- Sem suporte suficiente

```bash
> A temperatura aumentou porque é óbvio que o clima está a mudar.
[M4: DUVIDOSO] Mensagem contém claims que requerem verificação humana:
Blocking pattern: A temperatura aumentou porque é óbvio...
Estas claims não serão incorporadas até verificação.
```

---

## Guardar em Memória

### MemPalace (Rápido)
- Wing: `wing_conversas`
- Pesquisa semântica instantânea
- ~10ms por query

### PostgreSQL (Definitivo)
- Tabela: `governed_claims`
-GF-ID único por claim
- Histórico completo

---

## Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `:status` | Ver estado da sessão |
| `:save` | Guardar manualmente |
| `:export` | Gerar script de resume |
| `:quit` | Terminar sessão |

---

## Exemplos de Uso

### 1. Análise de Artigo

```bash
> O artigo indica que o café reduz o risco de diabetes em 30%.
[M4] OK. 1 claims extraídas.

> O estudo foi conduzido em 50.000 participantes durante 10 anos.
[M5] OK. 1 claims extraídas.
```

### 2. Brainstorming

```bash
> Precisamos aumentar as vendas em 50% este ano.
[M4] OK. 1 claims extraídas.

> Podemos fazer isso através de expansão para novos mercados.
[M3] OK. 1 claims extraídas.
```

### 3. Revisão de Relatório

```bash
> O relatório menciona uma perda de 2 milhões de euros.
[M5] OK. 1 claims extraídas.

> Esta perda foi devido a investimentos em I&D.
[M4] OK. 1 claims extraídas.
```

---

## Próximo Passo

Agora que sabes usar o chat, vamos ver o [fluxo completo](07_fluxo_completo.md)!

---

*Voltar ao [Índice](../00_INDICE.md)*
