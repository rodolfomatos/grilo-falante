# GRILO FALANTE — KERNEL

## Version

v2.5.0 (Kernel Schema)
v2.5.0 (Regime Version)

## Status

Normative • Authoritative

---

# 0. Purpose

This document defines the **authoritative operational kernel** of the
Grilo Falante regime.

The Kernel resolves **which artefacts possess operational authority**
during the execution of a governed reasoning cycle.

Only artefacts listed in this document may:

* impose normative obligations
* block regime progression
* enforce pipeline transitions
* introduce binding procedural constraints

All other documents in the repository are treated as:

* conceptual foundations
* supporting infrastructure
* experimental extensions
* historical memory

Unless explicitly promoted, they **do not govern execution**.

---

# 1. Authority Resolution Model

The Grilo Falante system resolves authority through the following chain:

INSTALLER
↓
defines the regime

LOADER
↓
activates the regime inside a chat cycle

KERNEL
↓
resolves operational authority

PIPELINE
↓
executes reasoning procedure

EPISTEMIC GRAPHS
↓
enforce state‑machine constraints

This separation ensures that:

* the constitution of the regime
* the activation mechanism
* the operational authority
* the execution engine

remain **distinct and auditable layers**.

---

# 2. Constitutional Layer

The constitutional layer defines the regime itself and the conditions
under which it becomes active.

Authoritative artefacts:

* INSTALLER
* LOADER

Responsibilities:

INSTALLER

* defines the regime
* establishes invariants
* declares epistemic principles

LOADER

* activates the regime in a chat
* enforces materialisation rules
* resolves operational authority via the Kernel

---

# 3. Execution Pipeline

The execution pipeline defines the canonical reasoning procedure
for a governed cycle.

Authoritative artefacts:

* DOCUMENTO_01_Auditoria_Epistemica.md
* DOCUMENTO_02_PIPELINE_CANONICO_v3.md

Responsibilities:

* structure reasoning phases
* enforce procedural discipline
* provide checkpoints for validation

---

# 4. Epistemic Graph Infrastructure

The epistemic graph system defines how reasoning structures must be
represented and validated.

Authoritative artefacts:

* DOCUMENTO_13_Grafo_Epistemico.md
* DOCUMENTO_14_Persistencia_e_Gating_de_Grafos.md
* DOCUMENTO_GRAFO_EPISTEMICO_ESPECIFICACAO.md

Responsibilities:

* represent reasoning as explicit graph structures
* enforce allowed transitions
* prevent unsupported inference

Graphs operate as a **state‑machine constraint layer**.

---

# 5. Validation Mechanisms

Validation artefacts enforce epistemic discipline and procedural
correctness.

Authoritative artefacts:

* DOCUMENTO_12_Validacao_Automatica.md

Responsibilities:

* perform automated checks
* evaluate reasoning compliance
* classify outputs using validation states

Possible validation states include:

ACCEPT
CONDITIONAL
REJECT
REEXECUTE

---

# 6. Relationship with the Normative Index

The document:

DOCUMENTO_03_Indice_Normativo_Artefactos.md

acts as a **catalogue of normative artefacts**.

However:

The Normative Index **does not resolve operational authority**.

Authority is resolved exclusively through the **Kernel**.

This prevents ambiguity between documentation and execution.

---

# 7. Non‑Kernel Artefacts

Documents not listed in the Kernel may exist within the system as:

* theoretical documents
* epistemic protocols
* experimental modules
* documentation
* historical records

Examples include:

* language specifications
* epistemic compiler models
* experimental reasoning frameworks

Such artefacts **do not govern execution** unless promoted.

---

# 8. Promotion Rule

A non‑kernel artefact may become authoritative only through
explicit promotion.

Promotion requires:

1. explicit audit
2. normative decision
3. kernel update

The Kernel must be updated to reflect the promotion.

---

# 9. Kernel Stability Principle

The Kernel must remain:

* small
* explicit
* auditable
* stable across versions

Excessive growth of the Kernel weakens the regime by
introducing diffuse authority.

Kernel changes therefore require **explicit justification
and audit**.

---

# 10. Resulting Architectural Model

With the Kernel in place, the Grilo Falante system
has the following layered architecture:

Constitution
(Installer)

Bootloader
(Loader)

Kernel
(Authority Resolution)

Execution Engine
(Pipeline)

State Machine
(Epistemic Graphs)

Validation Layer
(Lint and validation protocols)

---

# Principle

If an artefact is not present in the Kernel,

it does **not govern the regime**.
