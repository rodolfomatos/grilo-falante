# Plano: Manual Completo + /grilo chat

**Data:** 2026-04-15
**Estado:** EM EXECUÇÃO
**Versão:** 1.0

## Visão

Sistema Grilo Falante como shell conversacional governada onde `/grilo chat` inicia sessão com extração automática de claims, classificação GMIF, e armazenamento dual (MemPalace + PostgreSQL).

## Arquitetura de Chat

```
User → ChatShell → Extract Claims → GMIF → Governance Gate → LLM Response
                  ↓
           MemPalace (fast cache, wing_conversas)
           PostgreSQL (authoritative, claims table)
```

## Funcionalidades a Implementar

### 1. Bugs Críticos
- [ ] asyncio.run() crash em server.py:630
- [ ] bare except: pass com logging
- [ ] MemPalace gap_detector:90

### 2. /grilo chat Shell
- [ ] ChatShell class
- [ ] send_message() com governance
- [ ] Comando /grilo chat
- [ ] MCP tool grilo_chat
- [ ] Auto-save cada 5 mensagens

### 3. Session Resume
- [ ] grilo_export_session tool
- [ ] Script bash grilo-resume-{id}.sh
- [ ] grilo_import_session tool

### 4. Manual API
- [ ] GET /api/v1/manual/*
- [ ] Pesquisa full-text

### 5. Manual MD
- [ ] 35+ ficheiros MD

## Persistência
- MemPalace: wing_conversas, semantic cache
- PostgreSQL: claims, session_preferences, governance_records

## LLM Provider
- OpenWebUI (via config)

##.auto-save
- A cada 5 mensagens

## Commits Planeados
- fix: asyncio.run bug
- feat: ChatShell class
- feat: grilo chat command
- feat: session resume
- feat: manual API
- docs: manual parts 1-7
