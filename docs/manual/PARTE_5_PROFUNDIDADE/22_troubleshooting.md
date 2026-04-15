# 22. Troubleshooting

## Problemas Comuns e Soluções

---

## Docker

### "Port already in use"

```bash
# Verificar o que está a usar a porta
lsof -i :8001

# Matar o processo
kill -9 <PID>

# Ou usar outra porta
# Editar .env: MCP_PORT=8002
```

### "Container failed to start"

```bash
# Ver logs
docker-compose logs app

# Verificar configuração
docker-compose config

# Limpar e recomeçar
docker-compose down -v
docker-compose up -d
```

---

## Base de Dados

### "Connection refused"

```bash
# Verificar PostgreSQL
docker-compose ps postgres

# Reiniciar
docker-compose restart postgres

# Testar conexão
docker-compose exec postgres psql -U grilo -d grilo_falante -c "SELECT 1"
```

### "relation does not exist"

```bash
# Verificar schema
docker-compose exec app psql $DATABASE_URL -c "\dt"

# Recriar schema
docker-compose exec app python3 -c "
from grilo_falante.backend.db.connection import init_schema
import asyncio
asyncio.run(init_schema())
"
```

---

## MemPalace

### "Collection does not exist"

```python
# Criar collection manualmente
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='/home/rodolfo/.mempalace/palace')
client.create_collection('mempalace_drawers')
"
```

### "Database locked"

```bash
# Matar processos chroma
pkill -f chroma

# Ou esperar e tentar novamente
sleep 5
```

### "unable to open database file"

```bash
# Verificar path
ls -la /home/rodolfo/.mempalace/

# Criar se não existir
mkdir -p /home/rodolfo/.mempalace/palace
```

---

## MCP Server

### "asyncio.run() cannot be called from a running event loop"

Este erro foi corrigido. Se ainda aparecer:

```bash
# Atualizar código
git pull origin main

# Ou verificar que não há nested async
grep -r "asyncio.run" grilo_falante/
```

### Tool not found

```bash
# Verificar tools disponíveis
curl http://localhost:8001/health

# Reiniciar MCP
docker-compose restart mcp
```

---

## Ollama

### "connection refused"

```bash
# Verificar Ollama
curl http://localhost:11434

# Iniciar se não estiver
ollama serve

# Descarregar modelo
ollama pull nomic-embed-text
```

---

## Chat Governado

### "Cannot send message - regime not active"

```python
# Primeiro iniciar sessão
grilo_chat_start(intention="...")

# Depois enviar mensagem
grilo_chat_send(message="...")
```

### "Session not found"

```bash
# Ver sessões ativas
# No MCP:
grilo_chat_start()  # Cria nova sessão

# Ou usar ID da sessão anterior
grilo_chat_send(message="...", session_id="chat_260415_xxx")
```

---

## Claims

### Claim não criada

```python
# Verificar parâmetros obrigatórios
gepeto_create_claim(
    claim_key="CLM-unique",  # Obrigatório
    claim_text="Texto",       # Obrigatório
    gmif_level="M5",         # Obrigatório
    source_id=1               # Opcional
)
```

### Validação falha

```bash
# Verificar estados válidos
# Estados: pending, submitted, approved, rejected, suspended

curl -X POST http://localhost:8001/api/v1/claims/1/validate \
  -d '{"decision": "approved"}'  # Não "approve"!
```

---

## PINA

### NCA não aparece

```python
# Primeiro criar NCA
grilo_pina_propose(
    source_document="doc.pdf",
    faithful_statement="Regra extraída",
    location="page 5"
)

# Depois verificar
grilo_pina_pending()
```

### Decisão não funciona

```python
# Usar valores corretos
# A = Incorporar
# B = Não incorporar
# C = Adiar

grilo_pina_decide(nca_id="NCA-xxx", decision="A")
```

---

## Performance

### Queries lentas

```bash
# Verificar logs
docker-compose logs app | grep -i slow

# Adicionar índice
docker-compose exec postgres psql -U grilo -d grilo_falante -c "
CREATE INDEX IF NOT EXISTS idx_claims_gmif ON governed_claims(gmif_level);
"
```

### MemPalace lento

```bash
# Ver uso de memória
docker stats

# Limpar cache antigo
rm -rf /home/rodolfo/.mempalace/palace/*.bin
```

---

## Testing

### Testes falham

```bash
# Ver testes
python3 -m pytest grilo_falante/tests/ -v

# Testar módulo específico
python3 -m pytest grilo_falante/tests/test_claims.py -v

# Ver coverage
python3 -m pytest grilo_falante/tests/ --cov
```

---

## Git

### "Please tell me who you are"

```bash
git config --global user.email "tu@email.com"
git config --global user.name "Teu Nome"
```

### "would be overwritten by merge"

```bash
# Guardar alterações
git stash

# Merge
git pull origin main

# Recuperar
git stash pop
```

---

## Reset Completo

Se nada funcionar:

```bash
# 1. Parar tudo
docker-compose down

# 2. Apagar volumes (PERDE DADOS!)
docker-compose down -v

# 3. Limpar cache
rm -rf /home/rodolfo/.mempalace/palace/*.bin

# 4. Recomeçar
docker-compose up -d

# 5. Verificar
docker-compose ps
docker-compose logs app
```

---

## Logs

```bash
# Todos os logs
docker-compose logs -f

# Só app
docker-compose logs -f app

# Só erros
docker-compose logs -f app | grep -i error

# Últimas 100 linhas
docker-compose logs --tail=100 app
```

---

## Obter Ajuda

1. **Ver logs:** `docker-compose logs app`
2. **Ver estado:** `docker-compose ps`
3. **Testar API:** `curl http://localhost:8001/health`
4. **Correr testes:** `python3 -m pytest grilo_falante/tests/ -v`
5. **Abrir issue:** https://github.com/rodolfomatos/grilo-falante/issues

---

*Voltar ao [Índice](../00_INDICE.md)*
