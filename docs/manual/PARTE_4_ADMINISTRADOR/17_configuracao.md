# 17. Configuração

## Ficheiro .env

```bash
# Copiar de exemplo
cp .env.example .env
```

---

## Variáveis Obrigatórias

```env
# Base de dados
DATABASE_URL=postgresql://grilo:grilo123@localhost:5432/grilo_falante

# MemPalace
MEMPALACE_PATH=/home/rodolfo/.mempalace
```

---

## LLM Providers

### Ollama (local)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### OpenWebUI

```env
OPENWEBUI_BASE_URL=http://localhost:8080
OPENWEBUI_API_KEY=your_key_here
```

### OpenAI

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

---

## API

```env
API_TOKEN=your_token_here
API_PORT=8001
```

---

## Desenvolvimento

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## Produção

```env
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://example.com
```

---

## Verificar Config

```bash
python3 -c "
from grilo_falante.config import settings
print(f'DB: {settings.database_url}')
print(f'MemPalace: {settings.mempalace_path}')
"
```

---

*Voltar ao [Índice](../00_INDICE.md)*
