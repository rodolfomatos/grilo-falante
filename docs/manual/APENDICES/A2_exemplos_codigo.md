# A2. Exemplos de Código

## Python - Query Simples

```python
from grilo_falante.backend.mcp.server import app
from mcp.server.stdio import stdio_server
import asyncio

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

asyncio.run(main())
```

---

## Python - Criar Claim

```python
from grilo_falante.backend.db.repositories import ClaimRepository
from grilo_falante.models import GovernedClaim, GMIFLevel

async def create_claim():
    repo = ClaimRepository()
    claim = GovernedClaim(
        claim_key="CLM-test-001",
        claim_text="Exemplo de claim",
        gmif_level=GMIFLevel.M5,
        gmif_confidence=0.8,
        source_id=None
    )
    created = await repo.create(claim)
    return created
```

---

## Python - Query com RAG

```python
from grilo_falante.backend.memory import HybridRetriever

async def rag_query(question: str):
    retriever = HybridRetriever()
    results = await retriever.retrieve(question, limit=5)

    context = "\n".join([
        f"- {r['claim_text']} (GMIF: {r.get('gmif_level')})"
        for r in results
    ])

    return f"Contexto:\n{context}\n\nPergunta: {question}"
```

---

## Python - ChatShell

```python
from app.skills.chat_shell import ChatShell

async def chat_example():
    shell = ChatShell()

    # Iniciar
    await shell.start(
        intention="Analisar dados",
        mode="exploratory"
    )

    # Enviar mensagens
    response = await shell.send_message(
        "As vendas aumentaram 20%."
    )

    print(response.message)

    # Terminar
    await shell.end()
```

---

## Bash - Script Resume

```bash
#!/bin/bash
# Grilo Falante Session Resume

export GRILO_SESSION_ID="chat_260415_143022"
export GRILO_CYCLE_ID="CYCLE-260415-abc123"
export GRILO_BASE_URL="http://localhost:8001"

echo "A retomar sessão: $GRILO_SESSION_ID"

# Verificar servidor
if ! curl -s "$GRILO_BASE_URL/health" > /dev/null; then
    echo "Erro: Servidor não está a correr"
    exit 1
fi

echo "Servidor OK. Continua a conversa..."
```

---

## Bash - Docker Quick Start

```bash
#!/bin/bash
# Iniciar Grilo Falante

cd ~/src/grilo_falante_v3.0

echo "1. Construir e iniciar..."
docker-compose up -d

echo "2. Aguardar arranque..."
sleep 5

echo "3. Verificar..."
curl -s http://localhost:8001/health | jq .

echo ""
echo "Pronto! Acede a http://localhost:8001/docs"
```

---

## REST - Query Completo

```bash
curl -X POST http://localhost:8001/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quais são as principais conclusões?",
    "session_id": "default",
    "auto_school_mode": true
  }'
```

---

## Python - PINA Workflow

```python
from grilo_falante.regime import PINAProtocol

async def pina_workflow():
    # 1. Propor norma
    propose_result = pina.propose_candidate(
        source_document="relatorio.pdf",
        faithful_statement="Todas as fontes devem ser renováveis",
        location="page 5"
    )

    nca_id = propose_result.nca_id

    # 2. Humano decide...

    # 3. Registar decisão
    decide_result = pina.decide(nca_id, "A")  # A=incorporar

    return decide_result
```

---

*Voltar ao [Índice](../00_INDICE.md)*
