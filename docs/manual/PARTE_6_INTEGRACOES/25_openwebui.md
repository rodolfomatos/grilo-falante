# 25. OpenWebUI

## O Que É?

OpenWebUI é uma interface web para LLMs. Pode ser usado como frontend para o Grilo Falante.

---

## Docker Setup

No `docker-compose.yml`:

```yaml
openwebui:
  image: ghcr.io/open-webui/open-webui:latest
  ports:
    - "8080:8080"
  environment:
    OLLAMA_BASE_URL: http://ollama:11434
    WEBUI_AUTH: "true"
```

---

## Configuração

### Variáveis de Ambiente

```env
OPENWEBUI_BASE_URL=http://localhost:8080
OPENWEBUI_API_KEY=your_api_key_here
```

### No OpenWebUI Admin

1. Aceder a `http://localhost:8080/admin`
2. Settings > Connections
3. Adicionar Ollama: `http://ollama:11434`

---

## Integração com Grilo Falante

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  OpenWebUI (8080)  ─────►  Grilo Falante (8001)         │
│       │                              │                       │
│       │   Interface Web             │   MCP/REST API       │
│       │                              │                       │
│       │◄───── Respostas ──────────│                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Configurar como LLM Provider

1. No OpenWebUI: Settings > Connections > Add Ollama
2. URL: `http://ollama:11434`
3. Grilo Falante processa os pedidos

---

## Para Usar

1. Abrir `http://localhost:8080`
2. Criar conta (primeiro utilizador = admin)
3. Chat normalmente
4. Grilo Falante processa em background

---

## API OpenWebUI

```bash
# Chat completion
curl http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer $OPENWEBUI_API_KEY" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "..."}]
  }'
```

---

## Resumo

| Aspeto | Detalhe |
|--------|---------|
| Porta | 8080 |
| Imagem | ghcr.io/open-webui/open-webui |
| Dependência | Ollama |
| Autenticação | Opcional |

---

*Voltar ao [Índice](../00_INDICE.md)*
