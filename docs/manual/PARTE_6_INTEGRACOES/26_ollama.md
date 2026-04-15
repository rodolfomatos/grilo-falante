# 26. Ollama

## O Que É?

Ollama permite correr LLMs localmente.

---

## Instalação

```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Verificar
ollama --version
```

---

## Modelos

```bash
# Descarregar modelo
ollama pull llama3

# Listar modelos
ollama list

# Remover modelo
ollama rm llama3
```

---

## Embeddings

Para pesquisa semântica:

```bash
ollama pull nomic-embed-text
```

---

## Configuração

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## API

```bash
# Chat
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [{"role": "user", "content": "Olá"}]
}'

# Embeddings
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "texto a embedar"
}'
```

---

## Com Docker

```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
```

---

## Troubleshooting

```bash
# Ver logs
journalctl -u ollama

# Reiniciar
sudo systemctl restart ollama
```

---

*Voltar ao [Índice](../00_INDICE.md)*
