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
- [x] 00_INDICE.md ✅
- [x] PARTE_1_FUNDAMENTOS (01-04) ✅
- [x] PARTE_2_UTILIZADOR (05-10) ✅
- [x] PARTE_3_ESPECIALISTA (11-14) ✅
- [x] PARTE_4_ADMINISTRADOR (15-18) ✅
- [x] PARTE_5_PROFUNDIDADE (19-22) ✅
- [x] PARTE_6_INTEGRACOES (23-26) ✅
- [x] PARTE_7_REFERENCIA (27-29) ✅
- [x] APENDICES (A1-A3) ✅
- [x] **TOTAL: 32 ficheiros**

## Progresso

### Bugs Corrigidos ✅
- asyncio.run() → await
- bare except → logging

### ChatShell ✅
- app/skills/chat_shell.py criado
- MCP tools: grilo_chat_start, grilo_chat_send, grilo_chat_end, grilo_export_session
- CLI: /grilo chat

### Manual MD (20+ ficheiros)
- PARTE_1: 01-04 ✅
- PARTE_2: 05,07-10 ✅
- PARTE_3: 11-14 ✅
- PARTE_4: 15 ✅
- PARTE_5: 22 ✅
- PARTE_6: 23-25, 27 ✅
- APENDICES: A1 ✅

### Commits Feitos
- 3d25930 - fix: asyncio.run() bug
- f9f7400 - feat: ChatShell class
- 2b717c5 - docs: manual start
- e3e731b - docs: MemPalace, Graphify, Cheatsheet
- 2d17966 - docs: Regime, Claims, REST, Troubleshooting
- c8f7652 - docs: Gaps/PINA, Exemplos, Fluxo, Primeiro Ciclo
