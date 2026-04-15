# Plano Técnico — Integração Boole + Zeigarnik

## Objetivo

Traduzir a análise conceptual de `07-boole-zeigarnik-analysis.md` para um plano técnico concreto de evolução do `grilo-falante-skill`.

Este plano assume o estado atual do projeto:

- state machine com g7/g8/g9;
- ACORDAR parcial;
- LOADER/KERNEL mínimo;
- legitimacy states;
- BLOCK estruturado;
- persistência JSON/HTML.

---

## Visão de Implementação

O projeto deve ganhar duas camadas novas:

1. **Proposition Engine**
2. **Open Loop Engine**

Estas camadas devem atravessar o ciclo inteiro:

```text
ACORDAR
  -> Loader/Kernel
  -> Proposition Extraction
  -> Claim/Evidence Classification
  -> Dependency + Tension Mapping
  -> Open Loop Registration
  -> Lint / Gate
  -> Human Validation
  -> Promote or Block
  -> Materialized Artefact
```

---

## Módulos Propostos

## 1. `reasoning/propositions.py`

Responsabilidade:

- extrair proposições fundacionais;
- separar assunções de conclusões;
- gerar mapa de dependências;
- identificar tensões;
- registar condições de refutação ou limites.

### Funções propostas

- `extract_foundational_propositions(input_text, nodes, edges)`
- `classify_proposition_role(proposition)`
- `build_dependency_map(propositions)`
- `detect_proposition_tensions(propositions)`
- `extract_falsification_conditions(propositions)`

---

## 2. `reasoning/open_loops.py`

Responsabilidade:

- representar loops cognitivos e epistemológicos em aberto;
- registar fechos, suspensões e bloqueios;
- calcular criticidade dos loops;
- associar loops a claims, proposições e artefactos.

### Funções propostas

- `open_loop_from_claim(claim)`
- `open_loop_from_tension(tension)`
- `close_loop(loop_id, closure_type, evidence=None)`
- `suspend_loop(loop_id, reason)`
- `block_loop(loop_id, reason)`
- `summarize_loop_state(loops)`

---

## 3. `governance/falsifiability_lint.py`

Responsabilidade:

- verificar se proposições relevantes têm condições de refutação, limites de validade ou condições de falha;
- marcar proposições como:
  - `lint_ok`
  - `lint_conditional`
  - `lint_failed`

### Regras mínimas

- proposições fundacionais não podem ser promovidas sem condição de fragilidade declarada ou boundary explicitado;
- conclusões derivadas não podem ser promovidas sem cadeia de suporte.

---

## 4. `governance/loop_closure.py`

Responsabilidade:

- decidir se os loops abertos permitem promoção;
- distinguir loops toleráveis de loops críticos;
- aplicar política de fecho confiável.

### Regras mínimas

- loops críticos abertos -> `BLOCK`
- loops menores podem gerar `CONDITIONAL`
- compromisso confiável materializado pode reduzir criticidade

---

## 5. `models/epistemic_objects.py`

Responsabilidade:

- concentrar tipos de dados novos do projeto.

---

## Tipos de Dados Propostos

## `Proposition`

Campos mínimos:

- `id`
- `statement`
- `role` (`foundational`, `assumption`, `derived`, `constraint`)
- `gmif_type`
- `legitimacy`
- `supporting_claim_ids`
- `falsification_conditions`
- `boundary_conditions`
- `confidence`

## `PropositionDependency`

Campos:

- `from_proposition`
- `to_proposition`
- `relation_type` (`supports`, `depends_on`, `contradicts`, `narrows`, `extends`)

## `TensionRecord`

Campos:

- `id`
- `left_proposition_id`
- `right_proposition_id`
- `tension_type`
- `severity`
- `resolution_status`

## `FalsificationCondition`

Campos:

- `id`
- `proposition_id`
- `condition_text`
- `evidence_needed`
- `status`

## `OpenLoop`

Campos:

- `id`
- `source_type` (`claim`, `proposition`, `tension`, `validation`)
- `source_id`
- `status` (`OPEN`, `SCHEDULED`, `SUSPENDED`, `BLOCKED`, `CLOSED`, `PROMOTED`)
- `criticality` (`low`, `medium`, `high`)
- `closure_policy`
- `trusted_commitment`
- `created_at`
- `updated_at`

---

## Alterações à State Machine

## Modelo g8

### F0 — Intention / Context

Adicionar:

- `domain_question`
- `initial_focus`
- `expected_output_type`

### F1 — Interpretation

Adicionar:

- extraction de proposições fundacionais;
- extraction de candidatos a loops abertos.

### F15 — Claim Classification

Adicionar:

- role da proposição (`assumption`, `derived`, `constraint`);
- relação com GMIF.

### F2 — Inference

Adicionar:

- dependency graph;
- tension map;
- falsification map.

### F3 — Structuring

Adicionar:

- materialização de `Documento Sombra` com:
  - proposições;
  - tensões;
  - loops abertos.

### F4 — Cognitive LINT

Passar a verificar:

- claims sem suporte;
- proposições fundacionais sem boundary/falsifiability;
- tensões severas sem resolução;
- loops críticos abertos;
- legitimacy insuficiente.

### F6 — Human Validation

Permitir:

- assert legitimacy;
- fechar loops;
- suspender loops;
- aceitar compromissos confiáveis.

### F7 — Promotion Gate

Critérios novos:

- sem `LEGITIMACY_ASSERTED` -> `BLOCK`
- loops críticos abertos -> `BLOCK`
- tensões severas não resolvidas -> `BLOCK`
- evidência insuficiente -> `BLOCK`
- condições de falsificação ausentes para proposições fundacionais -> `CONDITIONAL` ou `BLOCK`

### F8 — Persistence

Persistir:

- artefact type;
- propositions;
- tension map;
- open loops;
- closure records;
- rationale de promotion/block.

---

## Alterações ao Output JSON

## Estado atual

Já existem:

- `nodes`
- `edges`
- `metadata`
- `loader_kernel`
- `system_use_records`
- `block` quando aplicável

## Estado alvo

Adicionar:

```json
{
  "status": "promoted | blocked | conditional",
  "artefact": {
    "type": "DocumentoSombra | ObjetoDigital | CapsulaConceptual",
    "id": "..."
  },
  "foundational_propositions": [],
  "dependency_graph": [],
  "tension_map": [],
  "falsification_conditions": [],
  "open_loops": [],
  "closed_loops": [],
  "trusted_commitments": [],
  "evidence_summary": {},
  "promotion_rationale": {},
  "block": {},
  "loader_kernel": {},
  "system_use_records": []
}
```

---

## Novos Requisitos

### RF-20: Proposition Role Classification
- classificar proposições por papel estrutural

### RF-21: Tension Detection
- detetar tensões relevantes entre proposições e claims

### RF-22: Loop Criticality Classification
- distinguir loops menores de loops que impedem promoção

### RF-23: Trusted Commitment Materialization
- permitir fecho parcial por compromisso confiável materializado

### RF-24: Artefact Typing
- cada output materializado deve declarar tipo de artefacto

### RF-25: Proposition-Aware Lint
- lint deve atuar sobre estrutura proposicional e não só sobre claims individuais

---

## Roadmap por Fases

## Fase A — Estrutura mínima

Implementar:

- `Proposition`
- `OpenLoop`
- campos novos no output
- `reasoning/propositions.py` mínimo
- `reasoning/open_loops.py` mínimo

Resultado:

- o sistema já materializa fundamentos e loops.

## Fase B — Governação

Implementar:

- `falsifiability_lint.py`
- `loop_closure.py`
- regras novas em `F4` e `F7`

Resultado:

- promoção passa a depender de estrutura, não só de labels GMIF.

## Fase C — Artefactos do regime

Implementar:

- `DocumentoSombra`
- `ObjetoDigital`
- `CapsulaConceptual`
- transições permitidas

Resultado:

- materialização passa a seguir o regime, não só um dump JSON.

## Fase D — Evidência real

Integrar:

- retrieval do `epistemic-memory-architecture`
- evidence scoring
- provenance por claim/proposição

Resultado:

- proposições e loops passam a ser governados por evidência real.

---

## Critérios de Sucesso

O plano estará bem executado quando o sistema conseguir:

1. extrair proposições fundacionais de um corpus;
2. mapear dependências e tensões;
3. registar loops abertos e fechos confiáveis;
4. bloquear promoção quando a estrutura epistémica está incompleta;
5. materializar tudo isso em artefactos auditáveis.

---

## Recomendação Prática

A melhor ordem de implementação é:

1. modelos de dados;
2. output JSON;
3. proposition engine mínimo;
4. open loop engine mínimo;
5. lint/gating;
6. artefact typing;
7. evidence integration.

Isto minimiza risco e mantém o projeto executável em cada passo.
