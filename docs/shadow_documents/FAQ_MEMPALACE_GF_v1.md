# FAQ — MemPalace & Grilo Falante Integration

**GF-ID:** FAQ-20260416-MPGF-001
**Date:** 2026-04-16
**Type:** FAQ (generated from analysis)

---

## 1. O que é o MemPalace?

MemPalace é um sistema de memória para IAs que:
- Guarda conversas e conteúdos em **texto verbatim** (original, sem transformação)
- Usa pesquisa semântica com ChromaDB como backend padrão
- Organiza em estrutura hierárquica: Wings → Rooms → Halls → Drawers
- Tem Knowledge Graph temporal em SQLite
- Suporta MCP server com 29 ferramentas
- Não requer API key para o path de benchmark (96.6% R@5)

**Fonte:** https://github.com/MemPalace/mempalace

---

## 2. Qual a diferença entre MemPalace e um vector store normal?

| Aspecto | Vector Store | MemPalace |
|---------|-------------|-----------|
| Organização | Flat ou tags simples | Hierárquico (Wings/Rooms/Halls) |
| Conteúdo | Embeddings + texto | Texto verbatim + metadata |
| Pesquisa | Só semântica | Semântica + scoping por wing/room |
| Knowledge Graph | Não tem | Tem (temporal, entity-relationship) |
| Agentes | Não tem | Tem (diários, wings por agente) |

---

## 3. Como se relacionam ILHA e Wing?

**Semelhança:**
- Ambos são agregados de contexto
- ILHA = momento-espaço-tempo no GF
- Wing = projeto/pessoa no MemPalace

**Diferença:**
- ILHA tem timestamp NTP e participantes
- Wing não tem conceito de tiempo como dimensão fundamental
- ILHA é criada por eventos significativos
- Wing é criado por projeto/pessoa

**Pergunta:** Wing pode ser uma ILHA? Ou são conceitos ortogonais?

---

## 4. Como se relacionam PEDRA e Drawer?

**Semelhança:**
- Ambos armazenam conteúdo original
- PEDRA pode ter content_summary
- Drawer guarda texto verbatim

**Diferença:**
- PEDRA é um agregador que pode conter shadow_documents, capsules, digital_objects
- Drawer é só texto
- PEDRA tem saliência, GMIF, consequência
- Drawer não tem classificação epistémica

**Pergunta:** content_summary da PEDRA vai para Drawer? E os shadow_documents?

---

## 5. O que é o Knowledge Graph do MemPalace?

Sistema de entity-relationship com:
- Validity windows (temporal)
- Operações: add, query, invalidate, timeline
- Backed by local SQLite

**Pergunta:** Pode substituir ou integrar com sistema de conexões ILHA-PEDRA?

---

## 6. Como funciona o MCP server?

29 ferramentas cobrindo:
- palace reads/writes
- knowledge-graph operations
- cross-wing navigation
- drawer management
- agent diaries

**Pergunta:** GF pode usar MCP tools do MemPalace como backend?

---

## 7. GF guarda tudo verbatim?

**Não.** GF transforma antes de guardar:
- Materialização: guarda artefactos, não conversas
- Claims extraídas vs texto original
- GMIF classificação

**MemPalace guarda:**
- Texto verbatim
- Conversas originais

**GAP:** GF precisa de ambos - fidelidade E transformação governada.

---

## 8. Como integrar MemPalace com GF?

### Opção A: MemPalace como Backend
- Guardar tudo em MemPalace (verbatim)
- GF faz transformação e classification
- Metadata de GMIF adicionado

### Opção B: Complementares
- MemPalace = memória de longo prazo (verbatim)
- GF = regime de governação (transformação)
- IGUAL ao conceito de ShadowDocument vs Documento original

### Opção C: Unificação
- PEDRA usa estrutura MemPalace
- Adicionar campos: saliência, consequence_level, gmif_events
- Knowledge Graph para conexões

**Pergunta:** Qual é a arquitetura correta?

---

## 9. Como funciona deteção de eventos significativos?

**MemPalace:**
- Auto-detecta rooms do folder structure
- Não tem conceito de "evento"

**GF:**
- Eventos definidos por ti (sair de casa, atropelamento)
- PEDRA criada quando evento significativo ocorre

**GAP:** GF não tem mecanismo de detetar eventos automaticamente. Como implementar?

---

## 10. O que significa "Local-first"?

- Nada sai do dispositivo sem opt-in
- Embedding model local (~300MB)
- ChromaDB local
- SQLite local

**Para GF:** Onde fica o regime de governação? Local ou pode ser remoto?

---

## 11. Claims sobre benchmarks são válidas?

**Claim:** "96.6% R@5 raw"
**Observação:** Sem LLM, só pesquisa semântica. Métrica: R@5 (recall at 5).

**Claim:** "98.4% held-out"
**Observação:** Com hybrid v4, tuned on 50 dev questions.

**Nota:** Shadow Document não valida claims. Precisam de validação独立的.

---

## 12. Como funciona wake-up?

```bash
mempalace wake-up
```

Carrega contexto para nova sessão:
- Busca relevant memories
- Prepara contexto
- Não usa LLM (raw retrieval)

**Semelhança com ACORDAR:**
- GF: ACORDAR carrega estado, ancoragem temporal
- MemPalace: wake-up carrega memories

**Diferença:**
- GF requer declaração explícita de intenção
- MemPalace faz automaticamente

---

## 13. Perguntas em Aberto

1. **Arquitetura:** MemPalace + GF = complementares ou unificados?
2. **Storage:** PostgreSQL + MemPalace + Filesystem - como orquestrar?
3. **Deteção de eventos:** Como automatizar sem perder controlo?
4. **Saliência:** Como calcular e persistir?
5. **GMIF em MemPalace:** Como adicionar sem modificar o core?
6. **MCP integration:** GF pode usar MCP tools do MemPalace?

---

## 14. Próximos Passos

1. [ ] Testar MemPalace localmente
2. [ ] Criar原型 de integração
3. [ ] Definir onde fica PostgreSQL vs MemPalace vs Filesystem
4. [ ] Desenhar arquitetura de storage unificada
5. [ ] Implementar deteção de eventos (se automático)

---

**FIM DA FAQ**
