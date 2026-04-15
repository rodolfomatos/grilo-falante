# Epistemic Memory Model

## Feynman Explanation

This document defines how the system "remembers" and "forgets".

A human does not remember everything. Instead:
- it selects what matters
- it reinforces what is used
- it forgets what is unused

This system follows the same principles.

---

## Core Concepts

### Stone

A "stone" is a meaningful cognitive unit.

Definition:

- A cluster of claims, entities, and relations
- High epistemic density
- Participates in reasoning

A stone is NOT:
- a message
- a sentence
- raw text

---

### Claim

Atomic epistemic unit.

- Extracted from text
- Stored in DB
- Has status (supported, contested, etc.)

---

### Types of Usage

#### 1. Epistemic Usage (Strong)

Occurs when a claim:
- supports another claim
- contradicts another claim

Location:
- epistemic_alignment.py

---

#### 2. Structural Usage (Medium)

Occurs when a claim:
- participates in graph construction

Location:
- kernel / graph builders

---

#### 3. Latent Usage (Weak)

Occurs when a claim:
- is retrieved but not used

Location:
- hybrid_retrieval.py

---

## Memory Cycle

1. Interaction (query)
2. Retrieval
3. Alignment
4. Usage tracking
5. Time passes
6. Sleep cycle
7. Consolidation / Forgetting

---

## Principle

Memory is not storage.
Memory is selection over time.

