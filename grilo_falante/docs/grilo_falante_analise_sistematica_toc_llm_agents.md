# Índice Canónico de Artefactos — Grilo Falante (Materialização)

Este documento passa a funcionar como **ÍNDICE** e **âncora**. Cada secção abaixo é um **artefacto lógico independente**, com nome, estatuto e fronteiras claras, pronto para extração para ficheiro separado sem perda semântica.

---

## ARTEFACTO A — INSTALLER v2.5.0 (Canónico)
**Ficheiro-alvo:** `INSTALLER.md`
**Estatuto:** Norma raiz
**Conteúdo:**
- Secções 0–13 do installer v2.5.0 (texto integral aprovado)
- Regras invariantes, pipeline, gates, lint, AFS

---

## ARTEFACTO B — Lint Cognitivo (LC-FML v0.1)
**Ficheiro-alvo:** `lint/LC-FML.md`
**Estatuto:** Especificação formal
**Conteúdo:**
- Blocos Cognitivos (BC)
- Tipos (Claim/Evidence/Assumption)
- Regras R0–R6
- Estados de saída

---

## ARTEFACTO C — Acoplamento Lint × AFS
**Ficheiro-alvo:** `architecture/AFS-LINT-COUPLING.md`
**Estatuto:** Arquitetura executável
**Conteúdo:**
- Pontos P0–P5
- Ordem de interposição
- Regra de inversão

---

## ARTEFACTO D — Avaliação Crítica (Related Work)
**Ficheiro-alvo:** `analysis/RELATED-WORK-CRITIQUE.md`
**Estatuto:** Documento crítico
**Conteúdo:**
- AFS como infraestrutura necessária/insuficiente
- RL e prompt engineering (erro categorial)

---

## ARTEFACTO E — Diagnóstico do system.tgz
**Ficheiro-alvo:** `system/DIAGNOSTIC.md`
**Estatuto:** Decisão técnica
**Conteúdo:**
- Válido mas incompleto
- Extensões mínimas obrigatórias

---

## ARTEFACTO F — Registo de Sessão (Ledger)
**Ficheiro-alvo:** `ledger/SESSION-LOG.md`
**Estatuto:** Fonte de verdade
**Conteúdo:**
- Decisões tomadas
- Estados fixados
- Regras de continuidade

---

## Regra de Extração
Cada artefacto acima é **semanticamente fechado**. A sua extração para ficheiro separado **não requer interpretação adicional**.

---

## Estado
Materialização lógica concluída. Extração física pode ser feita por ordem sem regressões.

