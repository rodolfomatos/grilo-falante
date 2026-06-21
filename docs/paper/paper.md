# Grilo Falante: An Epistemic Governance Regime for AI Agents

**Rodolfo Matos**

_Independent Researcher_

---

## Abstract

Grilo Falante (GF) is an epistemic governance regime designed to address a fundamental problem in AI agent reliability: the inability of current language models to distinguish what they know from what they assume. Unlike traditional approaches that treat this as a technical problem (solved by retrieval augmentation, prompt engineering, or fine-tuning), GF treats it as a **protocol design problem**: the creation of formal, agent-agnostic protocols that any agent — human, language model, or software system — can follow to verify its own epistemic state.

GF defines five core protocols — ACORDAR (wake-up ritual with external time anchoring), VAI_DORMIR (cycle closure with handoff persistence), PINA (normative decision gate), Cognitive Lint (output validation), and six Invariants (I1-I6) — that together form a complete epistemic lifecycle. These protocols are specified as templates: abstract, agent-agnostic, and implementable in any substrate.

We present GF v3.0, a concrete implementation of the template for Python/AI agents using the Model Context Protocol (MCP), PostgreSQL with pgvector, and a FastAPI REST layer. We describe the architecture, the implementation decisions, and the relationship with AES (Aggressive Engineering System), a complementary software engineering methodology. A hostile audit identifies where the framework adds genuine value versus where it constitutes over-engineering relative to existing software engineering practices.

**Keywords:** epistemic governance, AI agent reliability, formal protocols, knowledge verification, MCP

---

## 1. Introduction

Large language models (LLMs) have demonstrated remarkable capabilities in generating coherent text, answering questions, and following instructions. However, they suffer from a fundamental epistemic limitation: they cannot natively distinguish between:

- Information they have verified (e.g., retrieved from a database)
- Information they are inferring from training data
- Information they are assuming as conversational convention
- Information they are confabulating (hallucinating)

This limitation manifests in well-documented failure modes: hallucination (Ji et al., 2023), sycophancy (Perez et al., 2022), and inconsistency across sessions (Kuhn et al., 2023). Current mitigation strategies fall into three categories:

1. **Retrieval-Augmented Generation (RAG)** (Lewis et al., 2020): Grounding outputs in retrieved documents
2. **Prompt Engineering**: Instructing the model to cite sources, think step by step, or express uncertainty
3. **Fine-tuning**: Training the model to be more truthful or calibrated

Each approach addresses symptoms rather than the underlying epistemic deficit. RAG does not prevent the model from making unsupported claims beyond the retrieved context. Prompt engineering is brittle and context-dependent. Fine-tuning does not generalize across domains.

Grilo Falante takes a different approach: instead of making the model more reliable at the inference level, it creates a **governance regime** — a set of formal protocols that the agent must execute before, during, and after each cognitive cycle. These protocols externalize the verification process, making it auditable, repeatable, and independent of the model's internal state.

The key insight is that epistemic verification cannot be performed by the same system that produces the claims being verified. Verification requires **external anchoring**: a source of truth outside the model's own reasoning. The simplest example is knowing what time it is: a model cannot infer the current time from its parameters; it must ask an external source (system clock, NTP, human). ACORDAR, the wake-up protocol, generalizes this requirement to all epistemic state: time, context, intention, and integrity.

This paper makes three contributions:

1. **The Template Model**: A formal description of agent-agnostic epistemic protocols
2. **The GF v3.0 Implementation**: A concrete implementation for Python/AI agents
3. **A Hostile Audit**: An honest assessment of where the framework adds value versus where it over-engineers

---

## 2. Background and Related Work

### 2.1 Epistemic Governance

Epistemic governance refers to the rules, practices, and institutions that shape how knowledge is produced, validated, and maintained within a system (Alasuntari & Qadir, 2014). In AI systems, epistemic governance typically manifests as data quality pipelines, model validation frameworks, and human-in-the-loop review processes.

GF draws on Popperian falsification (Popper, 1935): claims are treated as provisional unless they survive explicit attempts at refutation. The Cognitive Lint protocol operationalizes this by defining blocking patterns (assertions that cannot be verified) and rejection states.

### 2.2 AI Agent Reliability Frameworks

Several frameworks address AI agent reliability from different angles:

- **Constitutional AI** (Bai et al., 2022): Defines principles that guide model behavior through RLHF
- **Anthropic's Responsible Scaling** (2023): Organizational governance for model deployment
- **AgentBench** (Liu et al., 2023): Benchmarking agent performance across tasks
- **LangChain/LlamaIndex**: Orchestration frameworks with observability

None of these provide epistemic protocols for individual agents — they focus on training, evaluation, or orchestration. GF operates at a different level: the agent's own cognitive cycle.

### 2.3 The Aggressive Engineering System (AES)

AES (Matos, 2025b) is a software engineering methodology that structures development through kanban, tickets, phases (plan → build → verify → review → learn), and automated quality gates (lint, test, format). AES addresses a similar problem at a different level: it governs the **engineering process**, not the **epistemic state**.

The relationship between GF and AES is complementary:

| Dimension | AES | GF |
|-----------|-----|-----|
| Domain | Software engineering | Epistemic reasoning |
| Object | Code, tickets, CI/CD | Claims, norms, context |
| Verification | Tests, lint, format | Protocols, gates, invariants |
| Persistence | Git, kanban, handoffs | PostgreSQL, ledger, state machine |
| Interface | Makefile, shell hooks | MCP tools, API endpoints |

For software engineering work, AES is sufficient. GF adds value when the agent engages in open-ended epistemic work: research synthesis, document analysis, decision support across multiple sessions.

---

## 3. The Template Model: Protocols Agnostic to Agent Type

The original GF specification (Ambrosio, 2025) describes a set of protocols for an epistemic governance regime. We interpret this corpus as a **template**: each protocol specifies its inputs, steps, gates, and outputs in an abstract, agent-agnostic manner. A "human implementation" of the template would use a physical canvas, notebook, or verbal ritual. A "software implementation" uses MCP tools, function calls, and database writes. An "LLM implementation" uses tool calls and system prompts.

The template defines five protocols and six invariants.

### 3.1 The ACORDAR Protocol (v1.2)

ACORDAR is the wake-up ritual that anchors a cognitive cycle in verified external state. The template specifies five steps:

| Step | Description | Gate |
|------|-------------|------|
| P1 | Temporal identification: obtain date/time from external source | Without confirmation, suspend continuity |
| P2 | Automatic validation: run validation checks (VALID/INVALID) | INVALID → suspend |
| P3 | Integrity verification: confirm MANIFEST.lock, validation success | Failure → DEGRADED state |
| P4 | Context loading: read backlog, changelog, artifacts | — |
| P5 | State declaration: declare OK or DEGRADED, known limits, active issues | — |

The core principle is that temporal anchoring must come from outside the agent's own reasoning. The agent cannot infer what time it is — it must query an external source (NTP, system clock, human). Without this anchoring, the agent has no way to know whether it is resuming a previous cycle or hallucinating continuity.

The DEGRADED state triggers when two or more criteria are met: continuous cycle duration exceeds threshold, repeated identical validation requests, consecutive validation failures, or explicit cognitive fatigue signaling. In DEGRADED state, normative promotion is blocked and VAI_DORMIR is recommended.

### 3.2 The VAI_DORMIR Protocol (v1.7)

VAI_DORMIR closes a cognitive cycle by reviewing activity, updating artifacts, declaring closure, and performing final verification:

| Step | Description |
|------|-------------|
| P1 | Activity review: decisions taken, promotions made, items discarded, open items |
| P2 | Artifact update: backlog, changelog, validated capsules, ledger |
| P3 | Closure declaration: what remains open, what does not carry over, final state |
| P4 | Final verification: no implicit promotion, coherence with manifest, structural integrity |

The protocol prohibits implicit closure ("continuing tomorrow" without the ritual), implicit promotion by silence, and silent promotion of content.

### 3.3 The PINA Protocol (v1.0.0)

PINA (Protocol for Normative Incorporation) governs how normative rules are incorporated into the regime. A Normative Occurrence (NO) is any passage that establishes a rule, defines a prohibition, imposes a constraint, specifies a legitimacy criterion, or restricts interpretation.

For each NO, the agent must:
1. Suspend reasoning that depends on the norm
2. Invoke the PINA decision gate
3. Request explicit authorization with three options:
   - **A — Incorporate**: Accept as binding normative constraint; must be materialized
   - **B — Do not incorporate**: Treat as non-binding text; any use must be marked as external
   - **C — Defer**: Block all dependent actions until resolved

The fundamental rule: no normative rule shall be treated as operative knowledge without explicit human incorporation via PINA.

### 3.4 The Cognitive Lint (LC-FML, v0.1)

Cognitive Lint defines four states for outputs:

- **ACCEPT**: Proceed
- **CONDITIONAL**: Proceed with marking
- **REJECT**: Block
- **REEXECUTE**: Regress to indicated phase

Seven rules (R0-R6) map HARD FAIL → REJECT and FLAG → CONDITIONAL. Each rule is tied to a specific pipeline phase (e.g., R2 — premature synthesis in FASE 1 → HARD FAIL).

### 3.5 The Six Invariants (I1-I6)

The invariants are non-negotiable principles that govern all protocol execution:

- **I1 — Auto-contenção**: Nothing is assumed outside explicit documentation
- **I2 — Não-promoção implícita**: Exploratory outputs are not promoted without marking
- **I3 — Rastreabilidade**: Every rule, decision, or document has identifiable origin
- **I4 — Suspensão perante ambiguidade**: Signal and suspend on epistemic ambiguity
- **I5 — Responsabilidade humana final**: Critical normative decisions are not system-made
- **I6 — Integridade sobre fluência**: Structural coherence over style or speed

---

## 4. Implementation: Grilo Falante v3.0

GF v3.0 implements the template for Python/AI agents. The implementation consists of approximately 30,000 lines of Python across 128 files, with a PostgreSQL+pgvector database, a FastAPI REST API, and an MCP server with 52+ tools.

### 4.1 Architecture

```
┌──────────────────────────────────────┐
│         Agent (OpenCode/Claude)       │
│  ┌────────────────────────────────┐   │
│  │   MCP Client (tool calls)      │   │
│  └──────────┬─────────────────────┘   │
└─────────────┼────────────────────────┘
              │ MCP Protocol
              ▼
┌──────────────────────────────────────┐
│         MCP Server (52+ tools)        │
│  ┌────────────────────────────────┐   │
│  │  Regime Layer                   │   │
│  │  ├─ StateMachine (5 states)     │   │
│  │  ├─ Acordar (ACORDAR protocol)  │   │
│  │  ├─ PINAProtocol (A/B/C gate)   │   │
│  │  └─ CognitiveLint (BLOCK/WARN)  │   │
│  └────────────────────────────────┘   │
│  ┌────────────────────────────────┐   │
│  │  Service Layer                 │   │
│  │  ├─ GMIFClassifier (M1-M8)     │   │
│  │  ├─ GapDetectionService        │   │
│  │  ├─ FeynmanService (3 layers)  │   │
│  │  └─ QueryPipeline              │   │
│  └────────────────────────────────┘   │
│  ┌────────────────────────────────┐   │
│  │  Persistence Layer              │   │
│  │  ├─ PostgreSQL + pgvector       │   │
│  │  ├─ Island Memory (legacy)      │   │
│  │  └─ JSON Ledger (audit trail)   │   │
│  └────────────────────────────────┘   │
└──────────────────────────────────────┘
```

### 4.2 State Machine

The regime state machine defines five states with formal transitions:

```
INACTIVE → LOADED → ACTIVE → GOVERNING ↔ HIBERNATED
```

Claims have their own state machine:
```
derived → audited → stabilized → promoted
                    ↕
              contested → deprecated → archived
```

### 4.3 ACORDAR Implementation (Light)

After the hostile audit (Section 6), ACORDAR was simplified to focus on what adds value:

```python
def execute(
    self,
    intention: str,
    temporal_anchor: Optional[str] = None,
    mode: str = "exploratory",
) -> AcordarResult:
```

- **External time**: Uses `datetime.now()` (system clock), not model-internal inference
- **Git context**: Captures `git rev-parse`, `git log -1`, `git status --porcelain`
- **Island restoration**: Loads active islands from PostgreSQL via legacy module
- **Cross-validation**: If a human-supplied anchor is provided, it is compared to system time; mismatches are flagged as warnings

The result includes `verified_timestamp`, `git`, `islands`, and `warnings`.

### 4.4 VAI_DORMIR Implementation

VAI_DORMIR collects cycle state, writes a handoff file to `aes/handoffs/`, processes islands through the batch processor, and hibernates the state machine:

```python
async def vai_dormir_async(
    self,
    session_id: str = "mcp",
    handoff_dir: Optional[str] = None,
) -> dict:
```

The handoff file contains: cycle ID, date, state, intention, temporal anchor, claims count, NCAs pending, mode, git context. This enables session continuity through `resume()`.

### 4.5 PINA Implementation

PINA has full MCP tool support:

- `grilo_pina_propose`: Create a Normative Candidate (NCA) with source document reference
- `grilo_pina_decide`: Record A/B/C decision with consequences
- `grilo_pina_detect`: Scan text for normative occurrences using regex patterns (must, shall, forbidden, require, rule)
- `grilo_pina_configure`: Set mode to `auto | confirm | disabled`

Default mode is `confirm`: every NCA requires human decision before it becomes operative. Active invariants are tracked in the `PINAProtocol` class and recorded in the ledger.

### 4.6 Persistence

GF v3.0 uses PostgreSQL with pgvector for:
- **Claims** (governed_claims table with 1536-dimensional embeddings)
- **Sources** (governed_sources with tier classification)
- **Gaps** (identified and tracked through school mode)
- **Governance records** (immutable audit log)
- **Sessions** (preferences and state)
- **Islands** (legacy memory system)

The JSON ledger provides a lightweight, file-based audit trail that complements the database.

---

## 5. Hostile Audit: Where It Fails and Where It Adds Value

A precondition for this paper's publication is a hostile audit — an honest assessment of where the framework fails. We present the seven failure modes identified:

### 5.1 Failure Mode 1: ACORDAR Theater

The MCP server is long-running. When 10 queries arrive in 10 seconds, ACORDAR executes 10 times, each time declaring "regime active" and validating the manifest. ACORDAR should guarantee that each cognitive cycle starts with verified state; in practice, it is often a log entry saying "ACORDAR executed." The log is true. The protocol is theater.

**Mitigation**: The lightweight implementation uses system clock and git context as cheap, truthful external anchors. Full validation is only triggered when the cycle state is ambiguous (e.g., after hibernation).

### 5.2 Failure Mode 2: PINA Paralysis

PINA requires a human gate for every Normative Occurrence. A single user prompt can contain multiple implicit norms: "Do this using library X, with tests in Y, and ensure Z is not used." Each implicit norm could trigger PINA, making the system unusable.

**Mitigation**: Default mode is `confirm` with explicit opt-in. `grilo_pina_detect` uses conservative regex patterns. The agent is expected to use judgment about what constitutes a genuinely normative occurrence versus a routine instruction.

### 5.3 Failure Mode 3: Infinite Regress of Verifiers

ACORDAR verifies regime integrity. Who verifies ACORDAR? Who verifies the verifier? The original template resolved this through human friction: the human feels the weight of the ritual. In software, the regress is real unless arbitrarily terminated.

**Resolution**: The bootstrap is accepted as an act of trust. The system trusts that Python runs correctly, that PostgreSQL is connected, that the CPU is not flipping bits. GF does not verify these — they are presuppositions of any software system.

### 5.4 Failure Mode 4: The Completeness Fallacy

Protocols detect errors, they do not prove correctness. A claim can pass ACORDAR, Pipeline, Lint, and PINA and still be wrong. Worse, passing all protocols can create a false sense of epistemic confidence: "it passed the lint" becomes a shortcut for "it is correct."

**Resolution**: GF documentation explicitly states that protocols make the cost of judgment visible, not that they validate truth. The distinction is maintained throughout.

### 5.5 Failure Mode 5: The Category Error

GF states "nothing is assumed outside explicit documentation" (I1), yet the code assumes Python works, PostgreSQL runs, the MCP server has permissions, the file system is reliable, and the CPU produces correct results. GF is not about assumptions in general — it is about **a specific class of epistemic-cognitive assumptions**.

**Resolution**: The invariants are scoped to epistemic governance, not technical infrastructure. Technical assumptions are managed by AES (tests, CI/CD, containerization).

### 5.6 Failure Mode 6: Redundancy with AES

AES already provides: `make check` (integrity verification), `make task` (plan→build→verify→review→learn cycle), kanban (state), hooks (quality gates), AGENTS.md (institutional memory). GF attempts the same at a philosophical level.

**Resolution**: AES governs software engineering; GF governs epistemic reasoning. For software development, AES is sufficient. GF adds value when the work is not coding — conceptual analysis, research synthesis, multi-session decision support.

### 5.7 Failure Mode 7: Real Execution Cost

Each protocol step adds latency, complexity, and token consumption. In an MCP environment where each tool call takes 200ms-2s, a full cycle with ACORDAR (5 steps) + VAI_DORMIR (4 steps) + PINA (3+ steps) = 12+ additional tool calls per cycle.

**Rule of thumb**: If the cost of the protocol exceeds the cost of the error it prevents, the protocol is over-engineering. This rule guided the lightweight implementation.

### 5.8 What Was Kept, What Was Cut

| Component | Verdict | Rationale |
|-----------|---------|-----------|
| ACORDAR (external time) | Keep, simplified | Directly addresses the core epistemic problem |
| ACORDAR (manifest validation) | Cut | Manifests don't change between cycles |
| VAI_DORMIR (review + handoff) | Keep | Essential for session continuity |
| PINA (A/B/C gate) | Keep, default confirm | Prevents auto-normative drift |
| Pipeline v3 (9 phases) | Cut | Redundant with AES CI/CD |
| Cognitive Lint (R0-R6) | Keep | Pre-commit hook implementation |
| Documentos Sombra | Cut | No practical execution model |
| I1-I6 (invariants) | Keep as ADR | Documented, not coded |

---

## 6. Relationship with AES

GF and AES operate at different levels of abstraction:

```
┌─────────────────────────────────────────────┐
│         AES (Engineering Governance)         │
│  ┌─────────┐  ┌────────┐  ┌───────────────┐  │
│  │ Makefile │  │ Kanban │  │ CI/CD Pipeline│  │
│  │ hooks    │  │ tickets│  │ quality gates │  │
│  └─────────┘  └────────┘  └───────────────┘  │
├─────────────────────────────────────────────┤
│       GF (Epistemic Governance)              │
│  ┌─────────┐  ┌────────┐  ┌───────────────┐  │
│  │ ACORDAR │  │ PINA   │  │ Cognitive Lint │  │
│  │ temporal │  │ norms  │  │ output val.   │  │
│  │ anchor   │  │ gate   │  │               │  │
│  └─────────┘  └────────┘  └───────────────┘  │
└─────────────────────────────────────────────┘
```

For software engineering tasks, AES is sufficient and GF adds overhead. For epistemic reasoning tasks (synthesizing research, analyzing documents, maintaining positions across sessions), GF is necessary and AES is insufficient.

The integration point is the `aes/handoffs/` directory: GF writes handoff files that AES agents can read, creating a shared context across sessions and across governance regimes.

---

## 7. Conclusion and Future Work

We have presented Grilo Falante, an epistemic governance regime for AI agents, as both a formal template of agent-agnostic protocols and a concrete implementation for Python/AI agents. The hostile audit identified genuine value (external time anchoring, cycle closure, normative gates) and genuine over-engineering (pipeline formalisms, manifest validation, shadow documents).

The core thesis — that AI agents need formal protocols to distinguish what they know from what they assume — survives the audit. The simplest expression of this thesis is ACORDAR's first step: an agent cannot know what time it is without asking an external source. From this seed, the rest of the regime grows.

### Future Work

1. **NTP Integration**: Replace system clock `datetime.now()` with NTP-sourced time for stronger external anchoring
2. **PINA Auto-Classification**: Train a lightweight classifier to distinguish routine instructions from genuine Normative Occurrences
3. **Cross-Session Epistemic State**: Extend handoff format to include claim state, enabling seamless multi-session reasoning
4. **Integration with Formal Verification**: Connect Cognitive Lint rules to formal verifiers (TLA+, Alloy) for critical claims
5. **Human-in-the-Loop Modes**: Support asynchronous PINA decisions (slack, email) for non-interactive workflows

---

## Acknowledgments

The original Grilo Falante corpus, developed under the working name Ambrosio (2025a), defines the protocol template that this work implements. The AES framework (Matos, 2025b) provides the engineering methodology for structured development.

---

## References

Alasuntari, P., & Qadir, A. (2014). Epistemic governance: An approach to the politics of policy-making. *European Journal of Cultural and Political Sociology*, 1(1), 67-84.

Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. *arXiv preprint arXiv:2212.08073*.

Matos, R. (2025a). Grilo Falante: Sistema de Governança Epistêmica (Ambrosio phase, v1.6.4–v2.3.0). GitHub Repository.

Matos, R. (2025b). AES: Aggressive Engineering System. GitHub Repository.

Ji, Z., et al. (2023). Survey of Hallucination in Natural Language Generation. *ACM Computing Surveys*, 55(12), 1-38.

Kuhn, L., et al. (2023). Self-consistency Improves Chain of Thought Reasoning in Language Models. *ICLR 2023*.

Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS 2020*.

Liu, X., et al. (2023). AgentBench: Evaluating LLMs as Agents. *arXiv preprint arXiv:2308.03688*.

Matos, R. (2025). AES: Aggressive Engineering System. GitHub Repository.

Perez, E., et al. (2022). Discovering Language Model Behaviors with Model-Written Evaluations. *arXiv preprint arXiv:2212.09251*.

Popper, K. (1935). *Logik der Forschung*. Springer.
