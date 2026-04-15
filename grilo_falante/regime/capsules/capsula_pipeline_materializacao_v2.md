# Pipeline Operacional — Materialização e Governação de Projetos de Código (v2)
## Metadados Epistémicos

- **GF-ID:** GF-260415-M7-6519ee
- **GMIF:** M7 — Synthesis - aggregated from multiple derived claims
- **Gerado:** 2026-04-15T14:33:26Z
- **Fonte:** pipeline_materializacao_e_governacao_codigo_v_2.md

---


## Estatuto
Documento operativo integrado. Substitui versões anteriores informais.

## Modos cognitivos
MPG + D (hierarquia: D > MPG)

---

## FASE 0 — Enquadramento e validade epistémica (NOVA)

### Objetivo
Fixar o referencial contra o qual todas as decisões serão avaliadas.

### Artefacto obrigatório

**CODE_CONTEXT.md**
- origem do projeto;
- estado (produção, legado, protótipo, experimental);
- restrições explícitas (tempo, risco, compatibilidade);
- critério(s) de sucesso verificáveis.

Sem este documento, **nenhum ciclo é válido**.

---

## FASE A — Ingestão e snapshot (imutável)

### Objetivo
Preservar o projeto exatamente como recebido.

### Artefactos

- **CODE_SNAPSHOT_MANIFEST.md**
  - árvore de ficheiros;
  - metadados básicos (tipo, tamanho, hash opcional).

- **CODE_SNAPSHOT_<path>.md**
  - um ficheiro por ficheiro de código;
  - conteúdo integral;
  - nunca editado.

Regra dura: snapshots são **imutáveis**.

---

## FASE B — Indexação e compreensão

### Objetivo
Tornar o projeto navegável cognitivamente.

### Artefactos

- **CODE_INDEX.md** — mapa funcional por módulo.
- **CODE_MAP.md** — relações e fluxos principais.

---

## FASE C — Working Set (estado ativo)

### Objetivo
Permitir trabalho focado sem duplicar código.

### Artefactos

- **WORKING_SET.md** — lista de ficheiros ativos e objetivos.
- **WORK_<id>.md** — excertos mínimos relevantes.

Regra: nunca copiar ficheiros inteiros nesta fase.

---

## FASE D — Evolução e diffs

### Objetivo
Permitir mudança auditável.

### Artefactos

- **DIFF_<id>.md** — diff unificado + motivação.
- **PATCH_<id>.md** (opcional) — patch aplicável.

Sem diff explícito, **não existe mudança válida**.

---

## FASE E — Gate de promoção (NOVA)

### Objetivo
Separar exploração de decisão.

### Artefacto obrigatório

**PROMOTION_GATE.md**
- lista de mudanças propostas;
- checklist:
  - diff existente;
  - ADR existente;
  - impacto identificado;
- decisão explícita: ACEITE / REJEITADA / ADIADA.

Sem gate, não há promoção.

---

## FASE F — Decisões técnicas e ledger

### Objetivo
Preservar racionalidade e evitar regressão.

### Artefactos

- **ADR_<id>.md** — decisão, contexto, alternativas, consequências.
- **LEDGER_CODIGO.md** — índice cronológico.
- **DECISIONS_INDEX.md** (NOVA) — índice temático transversal.

---

## FASE G — Fecho de ciclo (NOVA)

### Objetivo
Encerrar explicitamente cada ciclo de trabalho.

### Artefacto obrigatório

**CYCLE_CLOSE_<id>.md**
- objetivo inicial cumprido?;
- scope não tratado;
- dívida técnica introduzida;
- riscos remanescentes.

Sem fecho, o ciclo permanece **incompleto**.

---

## Princípios estruturais

- O código não vive na conversa.
- Exploração não cria autoridade.
- Decisão exige gate explícito.
- Nada é aceite sem diff e sem contexto.

---

## Fim do documento

