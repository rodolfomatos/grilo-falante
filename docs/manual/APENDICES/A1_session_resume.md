# A1. Código de Sessão e Resume

## O Problema

Quando estás a trabalhar com o Grilo Falante e o sistema crasha ou fechas o terminal, perdes o estado da sessão.

**Solução:** Sistema de resume estilo OpenCode.

---

## Como Funciona

### Ciclo de Vida da Sessão

```
1. INICIAR          grilo_chat_start()
   │
   ├─→ session_id   "chat_260415_143022"
   │
   ├─→ cycle_id     "CYCLE-260415-abc123"
   │
   └─→ Estado guardado em memória

2. TRABALHAR        (mensagens, claims, etc.)

3. EXPORTAR         grilo_export_session()
   │
   └─→ Script bash guardado

4. CRASH/FECHAR

5. RETOMAR          source grilo-resume-XXX.sh
   │
   └─→ Sessão restaurada
```

---

## Exportar Sessão

### Via CLI

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
```

### Via MCP

```python
grilo_export_session(session_id="chat_260415_143022")
```

**Output:**
```json
{
  "script": "#!/bin/bash\nexport GRILO_SESSION_ID=\"chat_260415_143022\"...",
  "session_id": "chat_260415_143022",
  "cycle_id": "CYCLE-260415-abc123",
  "messages_count": 15,
  "claims_count": 42
}
```

---

## Guardar Script de Resume

```bash
# Criar directório para scripts
mkdir -p ~/.grilo

# Exportar script
cat > ~/.grilo/grilo-resume-chat_260415_143022.sh << 'EOF'
#!/bin/bash
# Grilo Falante Session Resume
# Session: chat_260415_143022
# Cycle: CYCLE-260415-abc123
# Date: 2026-04-15T14:30:22

export GRILO_SESSION_ID="chat_260415_143022"
export GRILO_CYCLE_ID="CYCLE-260415-abc123"
export GRILO_BASE_URL="http://localhost:8001"

# Verificar se o servidor está a correr
if ! curl -s "$GRILO_BASE_URL/health" > /dev/null; then
    echo "Erro: Grilo Falante não está a correr!"
    echo "Inicia com: docker-compose up -d"
    exit 1
fi

echo "A retomar sessão: $GRILO_SESSION_ID"
echo "Cycle: $GRILO_CYCLE_ID"
echo ""

# Aqui podes adicionar lógica para retomar o chat
EOF

chmod +x ~/.grilo/grilo-resume-chat_260415_143022.sh
```

---

## Script de Auto-Resume

Cria um script que permite selecionar a sessão:

```bash
cat > ~/.grilo/grilo-resume.sh << 'EOF'
#!/bin/bash
# Grilo Falante Session Selector

SCRIPT_DIR="$HOME/.grilo"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  Grilo Falante - Selecionar Sessão"
echo "=========================================="
echo ""

# Listar sessões disponíveis
sessions=$(ls -t grilo-resume-*.sh 2>/dev/null | head -5)

if [ -z "$sessions" ]; then
    echo "Nenhuma sessão guardada."
    echo "Executa 'grilo chat' para criar uma nova."
    exit 1
fi

echo "Sessões disponíveis:"
echo ""
select session in $sessions "Nova sessão"; do
    if [ "$session" = "Nova sessão" ]; then
        echo "A iniciar nova sessão..."
        /usr/bin/python3 -m app.skills.grilo_falante_skill chat
        break
    else
        echo "A retomar: $session"
        source "$session"
        break
    fi
done
EOF

chmod +x ~/.grilo/grilo-resume.sh
```

**Adicionar ao `.bashrc` ou `.zshrc`:**

```bash
echo 'export PATH="$HOME/.grilo:$PATH"' >> ~/.bashrc
```

---

## Utilização

### Listar sessões
```bash
ls -la ~/.grilo/
```

### Retomar sessão específica
```bash
source ~/.grilo/grilo-resume-chat_260415_143022.sh
```

### Menu interativo
```bash
grilo-resume
# ou
~/.grilo/grilo-resume.sh
```

---

## Estado Guardado

O que é guardado quando exportas:

| Campo | Descrição |
|-------|-----------|
| `session_id` | ID único da sessão de chat |
| `cycle_id` | ID do ciclo do regime |
| `messages_count` | Número de mensagens |
| `claims_count` | Número de claims extraídas |
| `state` | Estado atual (GOVERNING, HIBERNATED, etc.) |

### O que NÃO é guardado automaticamente

- Histórico completo de mensagens
- Claims detalhadas (precisam de query à DB)

### Para guardar tudo

```bash
> :save
{
  "session_id": "chat_260415_143022",
  "cycle_id": "CYCLE-260415-abc123",
  "state": "GOVERNING",
  "messages_count": 15,
  "claims_count": 42,
  "saved_at": "2026-04-15T14:45:00"
}
```

---

## Via API REST

```bash
# Exportar sessão
curl http://localhost:8001/api/v1/session/export/chat_260415_143022

# Guardar sessão
curl -X POST http://localhost:8001/api/v1/session/save \
  -H "Content-Type: application/json" \
  -d '{"session_id": "chat_260415_143022"}'
```

---

## Integração com OpenCode

O utilizador mencionou o padrão OpenCode:

```
opencode -s xxxxxxxxxxxx
```

Para integrar com OpenCode, cria um alias:

```bash
# No .bashrc ou .zshrc
alias grilo='python3 -m app.skills.grilo_falante_skill'

# Para iniciar chat governado
grilo chat

# Para retomar
source ~/.grilo/grilo-resume-ULTIMA_SESSAO.sh
```

---

## Fluxo Completo de Resume

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. TRABALHAR                                               │
│     $ grilo chat                                            │
│     > mensagen 1                                            │
│     > mensagem 2                                            │
│     > :export  →  ~/.grilo/sessao.sh                        │
│                                                             │
│  2. CRASH / FECHAR                                          │
│                                                             │
│  3. RETOMAR                                                 │
│     $ source ~/.grilo/sessao.sh                            │
│                                                             │
│     OU                                                       │
│                                                             │
│     $ grilo-resume                                         │
│     > Selecionar sessão...                                  │
│     > 1. chat_260415_143022                                │
│     > 2. chat_260414_091523                                │
│     > #? 1                                                  │
│                                                             │
│  4. CONTINUAR                                               │
│     Estado restaurado! Podes continuar.                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Notas Importantes

1. **O ciclo_id é a chave** - permite ao regime saber exatamente onde parou
2. **Claims ficam na DB** - podes recuperar com queries
3. **MemPalace é cache** - não é backup, apenas velocidade

---

*Voltar ao [Índice](../00_INDICE.md)*
