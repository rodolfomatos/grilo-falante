# Plano: Manual Completo + /grilo chat

**Data:** 2026-04-15
**Estado:** COMPLETO
**Versão:** 1.0

## Visão

Sistema Grilo Falante como shell conversacional governada onde /grilo chat inicia sessao com extracao automatica de claims, classificacao GMIF, e armazenamento dual (MemPalace + PostgreSQL).

## Funcionalidades Implementadas

### 1. Bugs Criticos
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

### 4. Manual MD
- [x] 32 ficheiros MD completos
- [x] PARTE_1 a PARTE_7 + APENDICES

## Ficheiros Criados

```
docs/manual/
├── 00_INDICE.md
├── PARTE_1_FUNDAMENTOS/ (01-04)
├── PARTE_2_UTILIZADOR/ (05-10)
├── PARTE_3_ESPECIALISTA/ (11-14)
├── PARTE_4_ADMINISTRADOR/ (15-18)
├── PARTE_5_PROFUNDIDADE/ (19-22)
├── PARTE_6_INTEGRACOES/ (23-26)
├── PARTE_7_REFERENCIA/ (27-29)
└── APENDICES/ (A1-A3)
```

## Pendente

- REST API para manual (/api/v1/manual/*)
- Integracao OpenWebUI/plugin

## Commits

- 3d25930 - fix: asyncio.run() bug
- f9f7400 - feat: ChatShell class
- 4550f9e - docs: Complete manual
