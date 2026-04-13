# Índice — Grilo Falante

## Estrutura de Documentos

```
docs/
├── canonicos/     # Definições canónicas
├── prompts/       # Prompts operativos
└── operativos/   # Documentos técnicos
```

## quick start

```bash
python3 -m uvicorn api.server_standalone:app --port 8000
```

## Arquitetura

- **api/** — FastAPI server
- **llm/** — Feedback loop LLM→Grilo
- **reasoning/** — Analisadores
- **governance/** — Validação epistémica

*2026-04-13*