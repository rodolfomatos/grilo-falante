# Documentação — Grilo Falante Skill

## Visão Geral

Esta documentação descreve o grilo-falante-skill em relação ao regime definido em `system.md` do ambrosio_v2.5.0.

---

## Índice

| Documento | Descrição |
|-----------|-----------|
| [01-regime-analysis.md](01-regime-analysis.md) | Análise completa do regime system.md |
| [02-comparison.md](02-comparison.md) | Comparação implementação vs requisitos |
| [03-requirements.md](03-requirements.md) | Requisitos funcionais e não-funcionais |
| [04-future-roadmap.md](04-future-roadmap.md) | Ideias e roadmap futuro |
| [05-state-machine.md](05-state-machine.md) | State machine - arquitetura técnica |
| [06-unified-vision.md](06-unified-vision.md) | Visão consolidada e plano de convergência |
| [07-boole-zeigarnik-analysis.md](07-boole-zeigarnik-analysis.md) | Análise crítica dos dois textos e integração conceptual |
| [08-boole-zeigarnik-implementation-plan.md](08-boole-zeigarnik-implementation-plan.md) | Plano técnico de implementação |
| [09-optimized-request.md](09-optimized-request.md) | Versão otimizada do pedido |
| [10-extras-concepts-integration.md](10-extras-concepts-integration.md) | Integração de conceitos do diretório extras |

---

## Resumo

### O que temos (v1.0)

- ✅ Extracção de conceitos (graphify)
- ✅ Classificação GMIF básica
- ✅ GF-ID generation
- ✅ Persistência (MemPalace/JSON)
- ✅ API FastAPI
- ✅ ChatGPT integration
- ✅ **State Machine (g7/g8/g9)**
- ✅ **ACORDAR ritual**
- ✅ **LEGITIMACY states (SUSPENDED/ASSERTED)**
- ✅ **F7 Promotion Gate (BLOCK/PROMOTE)**
- ✅ **F8 Persistence com metadata**
- ✅ **Cognitive Modes (MEX, AUDIT, etc.)**
- ✅ **LOADER/KERNEL mínimo com rasto materializado**
- ✅ **BLOCK estruturado com payload persistido**

### O que falta (regime completo)

- Classes de artefactos (Sombra/Digital/Cápsula)
- PINA protocol
- BLOCK behavior real em transições inválidas
- GMIF completo (epistemic-architecture)

---

## Pergunta Fundamental

> "Como sabemos que o que pensamos que sabemos é verdade?"

O `system.md` responde:
- Nada implícito
- Validação externa obrigatória
- Materialização de tudo
- Autoridade humana final
- BLOCK quando inválido

O skill agora é uma **implementação parcial do regime**.

---

## Links Externos

- [system.md (ambrosio_v2.5.0)](../../ambrosio_v2.5.0/system.md)
- [LOADER.md (ambrosio_v2.5.0)](../../ambrosio_v2.5.0/loader/LOADER.md)
- [KERNEL.md (ambrosio_v2.5.0)](../../ambrosio_v2.5.0/system/KERNEL.md)
- [epistemic-memory-architecture](../../epistemic-memory-architecture/)

---

## Começar

1. Ver [05-state-machine.md](05-state-machine.md) para usar state machine
2. Ver [04-future-roadmap.md](04-future-roadmap.md) para ideias futuras

Ou ver o [README.md](../README.md) para uso rápido.

---

## Exemplo de Uso

```bash
python3 grilo_pipeline.py ./app \
  --graph g8_grilo_falante_unified_cognitive_model \
  --intention "Verificar claims de autenticacao" \
  --verify-m4 \
  --export-html
```
