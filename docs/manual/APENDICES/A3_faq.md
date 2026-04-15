# A3. FAQ

## Perguntas Frequentes

---

## O Que É o Grilo Falante?

É um sistema de **governança epistémica** que ajuda a verificar afirmações, classificar conhecimento com GMIF (M1-M7), e manter um ledger de auditoria.

---

## Preciso de Docker?

Não. Podes instalar localmente:
```bash
pip install grilo-falante
python3 -m grilo_falante.backend.mcp.server
```

---

## Qual a Diferença Entre MemPalace e PostgreSQL?

| | MemPalace | PostgreSQL |
|--|-----------|------------|
| **Tipo** | Cache (ChromaDB) | Base de dados |
| **Velocidade** | ~10ms | ~100ms |
| **Conteúdo** | Semântico | Autoritativo |
| **Persistência** | Não (pode perder) | Sim |

---

## Como Começar?

```bash
docker-compose up -d
python3 -m app.skills.grilo_falante_skill chat
grilo_load()
grilo_acordar(temporal_anchor="2026-04-15", intention="Aprender")
```

---

## O Que É GMIF?

Governance Markup Interpretation Framework - sistema de classificação M1-M7:

- **M1**: Provas múltiplas
- **M4**: Duvidoso (contradições)
- **M7**: Síntese agregada

---

## Posso Usar Sem Regime Lifecycle?

Sim, mas não é recomendado. Sem `load()` + `acordar()`, o sistema está em INACTIVE e não guarda conhecimento.

---

## Como Faço Resume de Sessão?

```bash
# Exportar
grilo_export_session(session_id="chat_xxx")
# → Gera script bash

# Guardar
cat > ~/.grilo-resume.sh << 'EOF'
#!/bin/bash
export GRILO_SESSION_ID="chat_xxx"
...
EOF

# Retomar
source ~/.grilo-resume.sh
```

---

## Como Integro com OpenWebUI?

1. No docker-compose, OpenWebUI já está configurado
2. Acede http://localhost:8080
3. Configura Ollama em Admin > Connections

---

## Posso Criar os Meus Próprios Levels GMIF?

Por agora, os níveis são fixos (M1-M7). Podes subclassificar no metadata.

---

## Como Reporto Bugs?

1. Abre issue em https://github.com/rodolfomatos/grilo-falante
2. Inclui logs: `docker-compose logs app`
3. Inclui versão: `curl http://localhost:8001/health`

---

## Onde Está a Documentação?

- Este manual: `docs/manual/`
- README: `README.md`
- SKILL.md: `/home/rodolfo/.config/opencode/skills/grilo_falante/SKILL.md`

---

## Como Posso Contribuir?

1. Fork o repo
2. Cria branch: `git checkout -b feature/nova-feature`
3. Faz changes
4. Tests: `python3 -m pytest`
5. Commit e push
6. Pull Request

---

## Qual a Licença?

MIT License - livre para usar, modificar, distribuir.

---

*Voltar ao [Índice](../00_INDICE.md)*
