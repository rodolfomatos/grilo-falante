# Epistemic Scoring and Decay

## Feynman Explanation

The system needs to decide what matters.

This is done using scores.

Not all knowledge is equal:
- some is frequently used
- some is central
- some is validated

We quantify this.

---

## Importance Score

importance = f(structure, usage, support)

### Components

- Density (claims + relations)
- Connectivity (links to other stones)
- Entity centrality
- Support (validated vs unverified)
- Usage (frequency)

---

## Temporal Decay

We introduce forgetting over time.

Formula:

importance_effective = importance * exp(-λ * Δt)

Where:
- Δt = time since last usage
- λ = decay factor

---

## Thresholds

- KEEP: high importance
- COMPRESS: medium
- FORGET: low

Dynamic thresholds recommended (percentiles)

---

## Retrieval Score

final_score =
    α * semantic_score +
    β * usage_score +
    γ * recency_score

Suggested:
- α = 0.6
- β = 0.25
- γ = 0.15

---

## Principle

What is used survives.
What is unused fades.

