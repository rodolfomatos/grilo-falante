# 30. Manual API (RAG)

## O Que É?

A **Manual API** permite aceder ao manual via REST, tornando-o pesquisável para RAG em sistemas como OpenWebUI.

---

## Endpoints

### `GET /api/v1/manual/`

Índice de todos os capítulos.

```bash
curl http://localhost:8001/api/v1/manual/
```

**Resposta:**
```json
{
  "chapters": [
    {"path": "00_INDICE.md", "title": "Índice Geral", "part": "ROOT"},
    {"path": "PARTE_1_FUNDAMENTOS/01_o_que_e_o_grilo.md", "title": "O Que é o Grilo Falante?", "part": "PARTE_1_FUNDAMENTOS"},
    ...
  ],
  "count": 33
}
```

---

### `GET /api/v1/manual/{chapter}`

Obter capítulo específico.

```bash
curl http://localhost:8001/api/v1/manual/PARTE_2_UTILIZADOR/06_chat_gobernado.md
```

**Resposta:**
```json
{
  "path": "PARTE_2_UTILIZADOR/06_chat_gobernado.md",
  "title": "6. Chat Governado",
  "content": "# 6. Chat Governado\n\nO chat governado...",
  "sections": [
    {"level": 1, "title": "6. Chat Governado", "content": ["..."]},
    {"level": 2, "title": "O Que é?", "content": ["..."]}
  ],
  "word_count": 1523
}
```

---

### `GET /api/v1/manual/search`

Pesquisar no manual.

```bash
curl "http://localhost:8001/api/v1/manual/search?q=GMIF"
```

**Resposta:**
```json
{
  "query": "GMIF",
  "results": [
    {
      "file": "PARTE_2_UTILIZADOR/08_claims_gmif.md",
      "line": 1,
      "match": "# 8. Claims e GMIF",
      "context_before": "",
      "context_after": "..."
    },
    ...
  ],
  "count": 34
}
```

---

## Integração com OpenWebUI

### Configurar como Conhecimento

No OpenWebUI, podes adicionar o manual como fonte de RAG:

1. **Admin > Knowledge**
2. **Add Knowledge Source**
3. **API Endpoint:** `http://localhost:8001/api/v1/manual/`

### Exemplo de Uso

```python
# No OpenWebUI, ao fazer uma pergunta:
# O sistema pesquisa automaticamente no manual

> Como usar o chat governado?

# O sistema faz:
# GET /api/v1/manual/search?q=chat+governado
# Retorna contexto relevante do manual
```

---

## Pesquisa Semântica

Para pesquisa semântica (RAG), combina com MemPalace:

```bash
# Primeiro pesquisa no manual
curl "http://localhost:8001/api/v1/manual/search?q=GMIF"

# Depois pesquisa em MemPalace
curl -X POST http://localhost:8001/api/v1/semantic-search \
  -d '{"query": "GMIF levels"}'
```

---

## Estrutura do Conteúdo

Os capítulos são retornados com:

| Campo | Descrição |
|-------|-----------|
| `path` | Caminho do ficheiro |
| `title` | Título extraído do Markdown |
| `content` | Conteúdo completo em Markdown |
| `sections` | Secções estruturadas por heading |
| `word_count` | Número de palavras |

---

## Seccções

Cada capítulo é dividido em secções:

```json
{
  "sections": [
    {
      "level": 1,
      "title": "6. Chat Governado",
      "content": ["linha1", "linha2", ...]
    },
    {
      "level": 2,
      "title": "O Que é?",
      "content": ["O chat governado é..."]
    }
  ]
}
```

---

## Uso Programático

```python
import requests

# Obter índice
index = requests.get("http://localhost:8001/api/v1/manual/").json()

# Pesquisar
results = requests.get(
    "http://localhost:8001/api/v1/manual/search",
    params={"q": "GMIF"}
).json()

# Obter capítulo
chapter = requests.get(
    "http://localhost:8001/api/v1/manual/PARTE_2_UTILIZADOR/06_chat_gobernado.md"
).json()
```

---

## Para Desenvolvedores

O código está em `grilo_falante/backend/api/main.py`:

```python
@app.get("/api/v1/manual/")
async def get_manual_index():
    """Índice de capítulos."""

@app.get("/api/v1/manual/{chapter_path:path}")
async def get_manual_chapter(chapter_path: str):
    """Conteúdo de capítulo."""

@app.get("/api/v1/manual/search")
async def search_manual(q: str = Query(...)):
    """Pesquisa full-text."""
```

---

*Voltar ao [Índice](../00_INDICE.md)*
