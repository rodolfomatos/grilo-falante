# Implementation Plan

## Feynman Explanation

This document defines what changes must be done and where.

---

## Files and Changes

### claim_store.py

Add:
- usage_count
- last_used_at
- mark_claim_used()

Purpose:
- persist usage

---

### epistemic_alignment.py

Add:
- mark usage when claim is matched

Purpose:
- detect epistemic usage

---

### hybrid_retrieval.py

Add:
- usage-aware scoring
- recency-aware ranking

Purpose:
- adaptive retrieval

---

### sleep_cycle.py

Add:
- decay
- classification (keep/compress/forget)
- graph re-evaluation (future step)

Purpose:
- consolidation + forgetting

---

## Order of Implementation

1. claim_store.py
2. epistemic_alignment.py
3. hybrid_retrieval.py
4. sleep_cycle.py

---

## Principle

Do not break existing functionality.
Extend, do not replace.

