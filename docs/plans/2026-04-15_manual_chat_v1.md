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
- [x] asyncio.run() crash em server.py:630
- [x] bare except: pass com logging
- [x] MemPalace gap_detector:90

### 2. /grilo chat Shell
- [x] ChatShell class
- [x] send_message() com governance
- [x] Comando /grilo chat
- [x] MCP tool grilo_chat
- [x] Auto-save cada 5 mensagens

### 3. Session Resume
- [x] grilo_export_session tool
- [x] Script bash grilo-resume-{id}.sh
- [ ] grilo_import_session tool

### 4. Manual API
- [ ] GET /api/v1/manual/*
- [ ] Pesquisa full-text

### 5. Manual MD
- [x] 00_INDICE.md
- [x] 01_o_que_e_o_grilo.md
- [x] 03_instalacao.md
- [x] 06_chat_gobernado.md
- [x] 11_todas_mcp_tools.md
- [x] A1_session_resume.md
- [ ] Resto: partes 2,4,5,6,7

## Progresso

### Bugs Corrigidos ✅
- asyncio.run() → await
- bare except → logging

### ChatShell ✅
- app/skills/chat_shell.py criado
- MCP tools: grilo_chat_start, grilo_chat_send, grilo_chat_end, grilo_export_session
- CLI: /grilo chat

### Commits Feitos
- 3d25930 - fix: asyncio.run() bug
- f9f7400 - feat: ChatShell class

### Manual
- docs/manual/00_INDICE.md
- docs/manual/PARTE_1_FUNDAMENTOS/01_o_que_e_o_grilo.md
- docs/manual/PARTE_1_FUNDAMENTOS/03_instalacao.md
- docs/manual/PARTE_2_UTILIZADOR/06_chat_gobernado.md
- docs/manual/PARTE_3_ESPECIALISTA/11_todas_mcp_tools.md
- docs/manual/APENDICES/A1_session_resume.md
