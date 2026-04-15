# NORMATIVE REGISTRY (NR)

## Version
v2.5.0

## Status
Canonical • Operational

---

# 0. Function of this document

The **Normative Registry (NR)** is the authoritative record of all **Active Invariants** currently governing the Grilo Falante regime.

While other artefacts manage detection and proposal of norms, the registry lists only **norms that have successfully passed the PINA decision gate and are currently operative**.

The registry therefore represents the **active normative layer of the regime**.

---

# 1. Position in the Normative Pipeline

The Normative Registry is the final stage of the normative pipeline.

Pipeline:

Text
↓
Normative Occurrence (NO)
↓
Normative Catalogue (NC)
↓
Normative Candidate (NCA)
↓
PINA Decision Gate
↓
Active Invariant
↓
Normative Registry (NR)

Only rules that reach **Active Invariant** status may appear in the registry.

---

# 2. Purpose of the Registry

The registry serves four functions:

1. **Authoritative reference** of active norms.
2. **Operational constraint layer** for the regime.
3. **Audit artefact** enabling traceability of normative decisions.
4. **Conflict detection layer** for future normative updates.

---

# 3. Registry Entry Structure

Each registry entry MUST include the following fields.

## Rule ID

Identifier inherited from the Normative Candidate.

Example:

NCA-02

---

## Normative Statement

The operative formulation of the rule.

---

## Graph Binding

Graph(s) and node(s) affected by the rule.

Example:

Graph: G1
Transition: Generation → Acceptance

---

## Norm Type

Category of rule:

- Methodological rule
- Prohibition
- Constraint
- Legitimacy condition
- Interpretative restriction

---

## Origin

Source document where the rule originates.

---

## Activation Event

Reference to the PINA decision that activated the rule.

Example:

PINA decision: Incorporate
Cycle: 2026-03-09

---

## Status

Possible values:

ACTIVE
The rule currently governs the regime.

SUSPENDED
The rule has been temporarily disabled.

RETIRED
The rule has been superseded or removed.

---

# 4. Example Registry Entry

Rule ID:
NCA-02

Normative Statement:
"Exploratory outputs must not be promoted directly to epistemic acceptance."

Graph Binding:
Graph: G1
Transition: Generation → Acceptance (blocked)

Norm Type:
Prohibition

Origin:
DOCUMENTO_10_Falacias_e_Vieses_Cognitivos.md

Activation Event:
PINA decision: Incorporate
Cycle: 2026-03-09

Status:
ACTIVE

---

# 5. Governance Rules

The assistant MUST:

- consult the registry when applying normative constraints;
- treat registry entries as **operative invariants**;
- maintain traceability between registry entries and their originating candidates.

The assistant MUST NOT:

- introduce new operative rules outside the registry;
- modify registry entries without a PINA decision.

---

# 6. Relationship with Other Normative Artefacts

Normative Catalogue (NC)
Stores detected occurrences.

Normative Candidate (NCA)
Stores proposed rules.

PINA Protocol
Determines activation of candidates.

Normative Registry (NR)
Stores only **activated rules**.

---

# 7. Integrity Rule

Any normative rule influencing system behaviour MUST appear in the Normative Registry.

If a rule is not present in the registry, it **does not possess operative authority**.

---

# End of Document

