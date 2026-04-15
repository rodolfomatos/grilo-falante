# Epistemic Architecture

## Feynman Explanation

This document explains where everything happens in the system.

---

## Pipeline Flow

query
→ query_pipeline.py
→ hybrid_retrieval.py
→ epistemic_alignment.py
→ claim_store.py
→ response

---

## Responsibilities

### query_pipeline.py

- orchestrates everything
- ensures evidence is preserved

---

### hybrid_retrieval.py

- retrieves candidate claims
- combines vector + graph

---

### epistemic_alignment.py

- validates LLM output
- compares with evidence

---

### claim_store.py

- persists claims
- tracks status
- (to be extended) tracks usage

---

### sleep_cycle.py

- runs offline
- consolidates memory
- forgets irrelevant claims

---

## Key Insight

System is not linear.

It is a loop:

retrieval → reasoning → usage → sleep → updated retrieval

---

## Principle

The system evolves based on interaction history.

