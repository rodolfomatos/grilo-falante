# 3. Instalação Rápida

## Para Totós (Instalação Completa)

Pensa na instalação como **preparar a cozinha** antes de cozinhar:

1. **Docker** = o fogão
2. **PostgreSQL** = o frigorífico
3. **MemPalace** = a despensa rápida
4. **Grilo Falante** = o chef

---

## Opção 1: Docker (Recomendado)

### Passo 1: Verificar Pré-requisitos

```bash
# Verificar Docker
docker --version
# Deves ver: Docker version 20.x.x ou superior

# Verificar Docker Compose
docker-compose --version
# Deves ver: docker-compose version 1.x.x ou superior
```

### Passo 2: Clonar o Repositório

```bash
cd ~/src
git clone https://github.com/rodolfomatos/grilo-falante.git
cd grilo-falante-v3.0
```

Ou se já tens:

```bash
cd ~/src/grilo_falante_v3.0
git pull origin main
```

### Passo 3: Configurar

```bash
# Copiar configuração exemplo
cp .env.example .env

# Editar com as tuas definições
nano .env
```

**Definições importantes:**

```env
# Base de dados (não mudar)
POSTGRES_USER=grilo
POSTGRES_PASSWORD=grilo123
POSTGRES_DB=grilo_falante

# Memória (não mudar)
MEMPALACE_PATH=/home/rodolfo/.mempalace

# LLM Provider (escolhe um)
# Opção A: Ollama local
OLLAMA_BASE_URL=http://localhost:11434

# Opção B: OpenWebUI
OPENWEBUI_BASE_URL=http://localhost:8080
OPENWEBUI_API_KEY= teu_api_key_aqui
```

### Passo 4: Iniciar

```bash
# Construir e iniciar todos os serviços
docker-compose up -d

# Verificar estado
docker-compose ps
```

**Deves ver:**

```
NAME                STATUS
grilo-postgres      Up
grilo-app           Up
grilo-mcp          Up
```

### Passo 5: Verificar

```bash
# Testar API
curl http://localhost:8001/health

# Deves ver:
# {"status": "ok", "version": "3.0.0"}
```

---

## Opção 2: Desenvolvimento (Sem Docker)

### Pré-requisitos

```bash
# Python 3.10+
python3 --version

# PostgreSQL 15+ com pgvector
psql --version

# MemPalace (ChromaDB)
pip install mempalace

# Ollama (opcional, para embeddings)
ollama --version
```

### Instalação Manual

```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -e .

# 3. Inicializar base de dados
# Primeiro, criar a base de dados:
createdb grilo_falante

# 4. Configurar variáveis de ambiente
export DATABASE_URL="postgresql://grilo:grilo123@localhost:5432/grilo_falante"
export MEMPALACE_PATH="/home/rodolfo/.mempalace"

# 5. Iniciar servidor MCP
python3 -m grilo_falante.backend.mcp.server
```

---

## Instalação do MemPalace (opcional)

O MemPalace é usado para pesquisa semântica rápida:

```bash
# Instalar MemPalace
pip install mempalace

# Inicializar
python3 -c "
from mempalace.knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph('/home/rodolfo/.mempalace/knowledge_graph.sqlite3')
print('MemPalace initialized')
"

# Configurar path no .env
echo 'MEMPALACE_PATH=/home/rodolfo/.mempalace' >> .env
```

---

## Instalação do Ollama (para embeddings)

Para pesquisa semântica, precisas de um modelo de embeddings:

```bash
# Instalar Ollama (Linux/Mac)
curl -fsSL https://ollama.com/install.sh | sh

# Ou no Windows: https://ollama.com/download

# Descarregar modelo de embeddings
ollama pull nomic-embed-text

# Verificar
ollama list
```

---

## Configuração do OpenWebUI (opcional)

Se quiseres usar OpenWebUI como interface:

```bash
# No docker-compose.yml, o OpenWebUI já está configurado

# Aceder: http://localhost:8080
# Primeiro utilizador = admin

# Para integrar com Grilo Falante:
# Em OpenWebUI Admin > Settings > Connections > Add Ollama
# URL: http://ollama:11434
```

---

## Testes

Depois de instalar, corre os testes:

```bash
# Ativar ambiente
source venv/bin/activate  # ou source .venv/bin/activate

# Correr testes
python3 -m pytest grilo_falante/tests/ -v

# Deves ver:
# ========== 8 passed in Xs ==========
```

---

## Resolução de Problemas

### Docker: "Port already in use"

```bash
# Verificar que está a usar a porta
lsof -i :8001

# Matar processo
kill -9 <PID>

# Ou usar outra porta no .env
```

### PostgreSQL: "Connection refused"

```bash
# Verificar que PostgreSQL está a correr
docker-compose ps postgres

# Reiniciar
docker-compose restart postgres
```

### MemPalace: "Database not found"

```bash
# Criar directório
mkdir -p ~/.mempalace

# Re-inicializar
python3 -c "
from mempalace.knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()
"
```

---

## Próximo Passo

Agora que instalaste, vamos aprender o [primeiro ciclo](04_primeiro_ciclo.md)!

---

*Voltar ao [Índice](../00_INDICE.md)*
