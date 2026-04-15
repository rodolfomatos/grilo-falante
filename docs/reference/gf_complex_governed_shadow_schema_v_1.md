# GF Complex Governed Shadow Schema v1

## Objetivo

Definir um esquema canónico para shadow documents complexos que não contêm apenas factos simples, mas também:
- claims nucleares da fonte;
- limites do que a fonte não sustenta;
- papel citacional no argumento do paper;
- grau de cobertura relativamente a claims-alvo;
- risco e licença de uso.

O objetivo é impedir colapso categorial entre:
- conteúdo da fonte;
- interpretação editorial;
- governação citacional;
- ligações ao mapa argumentativo.

---

## Princípio central

A unidade mínima deixa de ser apenas uma claim plana.

A unidade correta passa a ser um:

**Epistemic Citation Packet (ECP)**

Um ECP é um objeto composto que representa, de forma separada mas ligada:
1. o que a fonte afirma;
2. o que a fonte não afirma;
3. as limitações internas da fonte;
4. como a fonte pode ser usada no paper;
5. com que força e risco essa utilização é epistemicamente legítima.

---

## Estrutura canónica de alto nível

Cada documento complexo deve ser decomposto em 5 camadas.

### Layer 1 — Bibliographic Layer
Metadados bibliográficos e identificadores estáveis.

### Layer 2 — Source Content Layer
Conteúdo atribuível à fonte.

### Layer 3 — Boundary Layer
Limites, exclusões e não-claims.

### Layer 4 — Citation Governance Layer
Regras de uso da fonte no contexto argumentativo.

### Layer 5 — Argument Linkage Layer
Relação entre a fonte e claims-alvo do paper.

---

## Tipos de objeto

### 1. SourceRecord
Representa a fonte enquanto entidade bibliográfica.

Campos mínimos:
- `source_id`
- `title`
- `authors`
- `year`
- `venue`
- `doi`
- `source_type`
- `ingestion_origin`

Exemplo:

```json
{
  "source_id": "source_moore_healy_2008",
  "title": "The Trouble with Overconfidence",
  "authors": ["Don A. Moore", "Paul J. Healy"],
  "year": 2008,
  "venue": "Psychological Review",
  "doi": "10.1037/0033-295X.115.2.502",
  "source_type": "journal_article",
  "ingestion_origin": "shadow_document"
}
```

### 2. ClaimUnit
Representa uma proposição extraída ou atribuída.

Campos mínimos:
- `claim_id`
- `claim_text`
- `claim_type`
- `attribution`
- `epistemic_role`
- `support_strength`
- `scope`
- `source_id`
- `evidence_basis`
- `claim_status`

Enum sugerido para `claim_type`:
- `core_claim`
- `subsidiary_claim`
- `limitation_claim`
- `boundary_claim`
- `negative_boundary`
- `method_claim`
- `interpretive_claim`
- `citation_governance_claim`
- `paper_alignment_claim`

Enum sugerido para `attribution`:
- `source_explicit`
- `source_implicit`
- `editorial_inference`
- `paper_mapping`

Enum sugerido para `epistemic_role`:
- `descriptive`
- `boundary`
- `limitation`
- `governance`
- `linkage`

Exemplo:

```json
{
  "claim_id": "claim_mh2008_core_01",
  "claim_text": "Overconfidence is not a single psychological phenomenon.",
  "claim_type": "core_claim",
  "attribution": "source_explicit",
  "epistemic_role": "descriptive",
  "support_strength": "strong",
  "scope": "conceptual",
  "source_id": "source_moore_healy_2008",
  "evidence_basis": "literature_synthesis",
  "claim_status": "active"
}
```

### 3. CitationUseRule
Representa a licença normativa de uso da fonte.

Campos mínimos:
- `rule_id`
- `source_id`
- `target_claim_id`
- `coverage_classification`
- `citation_role`
- `risk_level`
- `allowed_use`
- `disallowed_use`
- `rationale`

Enum sugerido para `coverage_classification`:
- `direct_support`
- `partial_support`
- `inferential_support`
- `contextual_background`
- `insufficient_support`

Enum sugerido para `risk_level`:
- `low`
- `medium`
- `high`

Exemplo:

```json
{
  "rule_id": "rule_mh2008_c2",
  "source_id": "source_moore_healy_2008",
  "target_claim_id": "C2",
  "coverage_classification": "direct_support",
  "citation_role": "Provide psychological evidence that humans frequently exhibit excessive confidence in their judgments.",
  "risk_level": "low",
  "allowed_use": "May be cited as support for overprecision as a common form of overconfidence.",
  "disallowed_use": "Must not be cited as proof that people are always overconfident in every context.",
  "rationale": "The source directly supports robust overprecision but explicitly does not claim universality across all contexts."
}
```

### 4. ArgumentLink
Representa a ligação entre a fonte e o mapa argumentativo do paper.

Campos mínimos:
- `link_id`
- `source_id`
- `paper_claim_id`
- `relation_type`
- `confidence`
- `basis`

Enum sugerido para `relation_type`:
- `supports`
- `constrains`
- `qualifies`
- `does_not_support`
- `background_for`

Exemplo:

```json
{
  "link_id": "link_mh2008_c3",
  "source_id": "source_moore_healy_2008",
  "paper_claim_id": "C3",
  "relation_type": "supports",
  "confidence": "high",
  "basis": "Coverage classified as direct support in shadow document."
}
```

---

## Separação obrigatória de camadas

### A. Source-descriptive content
Tudo o que é efetivamente atribuível à fonte.

Inclui:
- problema;
- abordagem;
- findings;
- implicações;
- core claims;
- evidence;
- limitations.

### B. Boundary content
Tudo o que fixa fronteiras do uso legítimo.

Inclui:
- what the source does NOT claim;
- exclusões;
- limites de generalização.

### C. Editorial interpretation
Tudo o que já é leitura orientada ao teu projeto.

Inclui:
- expectation vs source comparison;
- explanation da coverage classification;
- suggested citation sentence.

### D. Citation governance
Tudo o que é norma de uso.

Inclui:
- citation role;
- supported claims;
- coverage classification;
- citation risk.

### E. Argument mapping
Tudo o que liga a fonte a nós como `C1`, `C2`, `C3`.

---

## Regras normativas de ingestão

### Regra 1 — Não colapsar claim da fonte com claim editorial
Exemplo proibido:
- tratar `DIRECT SUPPORT` como se fosse uma claim psicológica da fonte.

### Regra 2 — Não colapsar limitação com contradição
Exemplo proibido:
- tratar `does not fully explain why overprecision is prevalent` como refutação da própria tese.

### Regra 3 — Preservar negative boundaries como objetos de primeira classe
Exemplo:
- `The article does not claim that people are always overconfident in every context.`

Isto deve ser armazenado como fronteira explícita, não descartado.

### Regra 4 — Governança citacional não entra no índice sem tipagem
Campos como `LOW`, `DIRECT SUPPORT`, `Supported Claims` não devem ser indexados como conhecimento substantivo sem `claim_type = citation_governance_claim` ou equivalente.

### Regra 5 — Toda ligação ao paper é relação derivada, não conteúdo primário
`C1`, `C2`, `C3` pertencem ao mapa argumentativo do paper, não à ontologia do artigo-fonte.

---

## Relações de grafo canónicas

Entre objetos, o sistema deve suportar pelo menos as seguintes relações:

### Source -> Claim
- `asserts`
- `suggests`
- `reports`
- `limits`
- `does_not_assert`

### Claim -> Claim
- `supports`
- `qualifies`
- `depends_on`
- `constrains`
- `excludes`

### Source -> PaperClaim
- `licensed_for`
- `supports`
- `background_for`
- `does_not_support`
- `constrains`

### Governance relations
- `coverage_for`
- `risk_for`
- `allowed_use_for`
- `disallowed_use_for`

---

## Instanciação do exemplo Moore & Healy (2008)

### SourceRecord
```json
{
  "source_id": "source_moore_healy_2008",
  "title": "The Trouble with Overconfidence",
  "authors": ["Don A. Moore", "Paul J. Healy"],
  "year": 2008,
  "venue": "Psychological Review",
  "doi": "10.1037/0033-295X.115.2.502",
  "source_type": "journal_article",
  "ingestion_origin": "shadow_document"
}
```

### ClaimUnits
```json
[
  {
    "claim_id": "claim_mh2008_core_01",
    "claim_text": "Overconfidence is not a single psychological phenomenon.",
    "claim_type": "core_claim",
    "attribution": "source_explicit",
    "epistemic_role": "descriptive",
    "support_strength": "strong",
    "scope": "conceptual",
    "source_id": "source_moore_healy_2008",
    "evidence_basis": "literature_synthesis",
    "claim_status": "active"
  },
  {
    "claim_id": "claim_mh2008_core_02",
    "claim_text": "The concept includes at least three distinct forms: overestimation, overplacement, and overprecision.",
    "claim_type": "core_claim",
    "attribution": "source_explicit",
    "epistemic_role": "descriptive",
    "support_strength": "strong",
    "scope": "conceptual_taxonomy",
    "source_id": "source_moore_healy_2008",
    "evidence_basis": "literature_synthesis",
    "claim_status": "active"
  },
  {
    "claim_id": "claim_mh2008_core_03",
    "claim_text": "Overprecision is the most robust and widely observed form.",
    "claim_type": "core_claim",
    "attribution": "source_explicit",
    "epistemic_role": "descriptive",
    "support_strength": "moderate_to_strong",
    "scope": "empirical_generalization",
    "source_id": "source_moore_healy_2008",
    "evidence_basis": "synthesis_of_findings",
    "claim_status": "active"
  },
  {
    "claim_id": "claim_mh2008_lim_01",
    "claim_text": "The work is largely conceptual and integrative rather than a single large experimental study.",
    "claim_type": "limitation_claim",
    "attribution": "editorial_inference",
    "epistemic_role": "limitation",
    "support_strength": "strong",
    "scope": "methodological",
    "source_id": "source_moore_healy_2008",
    "evidence_basis": "document_characterization",
    "claim_status": "active"
  },
  {
    "claim_id": "claim_mh2008_bound_01",
    "claim_text": "The article does not claim that people are always overconfident in every context.",
    "claim_type": "negative_boundary",
    "attribution": "editorial_inference",
    "epistemic_role": "boundary",
    "support_strength": "strong",
    "scope": "generalization_limit",
    "source_id": "source_moore_healy_2008",
    "evidence_basis": "source_scope_control",
    "claim_status": "active"
  }
]
```

### CitationUseRule
```json
{
  "rule_id": "rule_mh2008_c2",
  "source_id": "source_moore_healy_2008",
  "target_claim_id": "C2",
  "coverage_classification": "direct_support",
  "citation_role": "Provide psychological evidence that humans frequently exhibit excessive confidence in their judgments.",
  "risk_level": "low",
  "allowed_use": "Use for claims about overprecision and poor calibration of confidence relative to accuracy.",
  "disallowed_use": "Do not use as universal proof that all human judgments are overconfident in every setting.",
  "rationale": "The source directly supports a robust form of overconfidence while preserving contextual limits."
}
```

### ArgumentLinks
```json
[
  {
    "link_id": "link_mh2008_c1",
    "source_id": "source_moore_healy_2008",
    "paper_claim_id": "C1",
    "relation_type": "supports",
    "confidence": "high",
    "basis": "Supported Claims section."
  },
  {
    "link_id": "link_mh2008_c2",
    "source_id": "source_moore_healy_2008",
    "paper_claim_id": "C2",
    "relation_type": "supports",
    "confidence": "high",
    "basis": "Coverage classification: direct support."
  },
  {
    "link_id": "link_mh2008_c3",
    "source_id": "source_moore_healy_2008",
    "paper_claim_id": "C3",
    "relation_type": "supports",
    "confidence": "high",
    "basis": "Suggested citation guidance + supported claims."
  }
]
```

---

## Feynman pedagógico — o que isto é

Isto é uma tentativa de impedir que o sistema trate tudo como a mesma coisa.

Sem este esquema, o pipeline tende a misturar:
- o que o artigo realmente diz;
- o que tu inferes sobre o artigo;
- o que o artigo autoriza citar;
- e o papel desse artigo dentro do teu próprio argumento.

Esse colapso é perigoso porque transforma:
- fronteiras em suporte;
- limitações em contradições;
- notas editoriais em conhecimento do mundo.

O esquema acima separa essas categorias e torna explícitas as relações entre elas.

---

## Requisitos para implementação futura

Antes de alterar o pipeline real, o sistema deve conseguir:
1. detetar secções como `Core Claims`, `Limitations`, `What the Source Does NOT Claim`, `Supported Claims`, `Citation Risk`;
2. classificar cada bloco num tipo epistemicamente distinto;
3. armazenar camadas sem as colapsar;
4. gerar grafo com relações diferenciadas;
5. impedir retrieval cego de objetos normativos como se fossem claims substantivas.

---

## Próximos passos recomendados

### Opção A
Criar uma taxonomia operacional completa de `claim_type`, `relation_type`, `risk_type`, `coverage_type`.

### Opção B
Desenhar o schema SQL/JSON para persistência destes objetos.

### Opção C
Definir um parser de shadow documents complexos baseado neste esquema.

---

[TAG: GF_COMPLEX_GOVERNED_SHADOW_SCHEMA_V1_END]

