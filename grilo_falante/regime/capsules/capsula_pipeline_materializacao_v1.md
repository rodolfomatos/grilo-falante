# Pipeline Operacional — Materialização e Governação de Projetos de Código
## Metadados Epistémicos

- **GF-ID:** GF-260415-M7-968976
- **GMIF:** M7 — Synthesis - aggregated from multiple derived claims
- **Gerado:** 2026-04-15T14:33:26Z
- **Fonte:** pipeline_materializacao_e_governacao_codigo.md

---


**Base:** PROMPT_PIPELINE_MATERIALIZACAO_PROJETOS_CODIGO.md  
**Modos:** MPG + D (auditoria hostil)  
**Data:** 2026-01-01

---

## Resposta curta (auditoria hostil)

- A abordagem "CODE_*.md com código inteiro" **é necessária, mas insuficiente**.
- Funciona apenas como **snapshot inicial imutável**.
- A profundidade, evolução e não-regressão exigem **working set + diffs + ledger**.

Sem esta separação, o sistema **colapsa por volume e incoerência**.

---

## 1. Papel do humano (passo a passo)

1. Entregar o ficheiro `projeto.tgz`.
2. Declarar o **objetivo inicial** (leitura, refatoração, auditoria, evolução).
3. Confirmar que o `tgz` é o **snapshot canónico inicial**.
4. Autorizar materialização integral no canvas.

O humano **não edita código** no canvas; governa decisões.

---

## 2. Fase A — Ingestão e snapshot (imutável)

### Objetivo
Preservar o projeto **como recebido**, sem interpretação.

### Artefactos criados

- `CODE_SNAPSHOT_MANIFEST.md`
  - lista hierárquica de ficheiros
  - tamanho, tipo, hash (opcional)

- `CODE_SNAPSHOT_<path>.md`
  - **um ficheiro por ficheiro de código**
  - conteúdo integral em bloco de código
  - nunca alterado

**Regra dura:** snapshots **nunca são editados**.

---

## 3. Fase B — Indexação e compreensão

### Objetivo
Tornar o projeto navegável cognitivamente.

### Artefactos

- `CODE_INDEX.md`
  - mapa de diretórios
  - descrição funcional por módulo

- `CODE_MAP.md`
  - relações entre ficheiros
  - fluxos principais (ex.: request → controller → model)

---

## 4. Fase C — Working Set (estado ativo)

### Objetivo
Permitir trabalho sem duplicar snapshots.

### Artefactos

- `WORKING_SET.md`
  - lista de ficheiros ativos
  - objetivos por ficheiro

- `WORK_<id>.md`
  - **apenas excertos relevantes**
  - contexto mínimo necessário

**Regra:** nunca copiar ficheiros inteiros aqui.

---

## 5. Fase D — Evolução e diffs

### Objetivo
Registar mudanças de forma auditável.

### Artefactos

- `DIFF_<id>.md`
  - diff unificado (antes/depois)
  - motivação técnica

- `PATCH_<id>.md` (opcional)
  - patch aplicável

Sem diff explícito, **não há mudança válida**.

---

## 6. Fase E — Decisões técnicas (ledger)

### Objetivo
Evitar regressão e esquecimento.

### Artefactos

- `ADR_<id>.md`
  - decisão
  - contexto
  - alternativas rejeitadas
  - consequências

- `LEDGER_CODIGO.md`
  - índice de decisões

---

## 7. Escalabilidade (auditoria)

### O que escala
- snapshots imutáveis
- diffs incrementais
- working set pequeno

### O que não escala
- duplicar código inteiro
- confiar na conversa

---

## 8. Núcleo mínimo vs desejável

### Núcleo mínimo (obrigatório)
- snapshots imutáveis
- diffs explícitos
- ledger de decisões

### Funcionalidades desejáveis
- hashes de integridade
- visualização automática de diffs
- tags por módulo

---

## Conclusão

> O código não vive na conversa.  
> Vive em snapshots, diffs e decisões.

Este pipeline é **compatível com as limitações do modelo** e suficiente para trabalho profundo e auditável.

