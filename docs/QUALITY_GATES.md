# Domain-Specific Quality Gates for Epistemic Governance

These are quality gates specific to the epistemic governance domain of Grilo Falante v3.0. They should be checked in addition to the general quality gates in CHECKLIST.md.

## Epistemic Governance Quality Gates

### 1. Non-Decision Making Gate
**Check:** The system does not produce decisions or validate truths as facts.
**How to verify:**
- Review code and outputs to ensure no claims of truth/validity are made
- Check that outputs explicitly state the system's role is to make costs visible, not to decide
- Verify that any claim outputs include epistemic uncertainty markers (GMIF levels)
**Blocker:** Yes - violates core non-goal

### 2. Visible Human Cost Gate
**Check:** Human judgment cost is made visible in all outputs.
**How to verify:**
- All outputs include references to human involvement requirements
- Legitimacy states (SUSPENDED/ASSERTED) are properly tracked and displayed
- Shadow First methodology is evidenced (documentation created before assumptions)
- Human validation steps are required for progressing claims
**Blocker:** Yes - violates core purpose

### 3. Shadow First Compliance Gate
**Check:** The Shadow First methodology is followed: research before assuming.
**How to verify:**
- For any new concept implemented, check if a shadow document exists
- Review commit history for creation of documentation before implementation
- Verify that FAQs are generated to guide questioning
- Check that shadow debt is acknowledged and addressed
**Blocker:** Yes - core methodology violation

### 4. Graph-Based Governance Gate
**Check:** All reasoning is anchored to materialized graphs.
**How to verify:**
- Claims outputs reference specific graphs used (g7, g8, g9, etc.)
- Current state of reasoning is explicitly declared
- State transitions are validated before progression
- Graphs are versioned and accessible
**Blocker:** Yes - core regime requirement

### 5. GMIF Classification Integrity Gate
**Check:** GMIF classifications are accurate and well-founded.
**How to verify:**
- Classification logic follows documented criteria for each level (M1-M8)
- Evidence supporting classifications is traceable
- Contradictions and assumptions are properly recorded
- Classification history is preserved (does not overwrite, only appends)
**Blocker:** Yes - core to epistemic governance

### 6. Legitimacy State Management Gate
**Check:** Legitimacy states function correctly (SUSPENDED by default, ASSERTED requires human input).
**How to verify:**
- Default state for new claims is LEGITIMACY_SUSPENDED
- Transition to LEGITIMACY_ASSERTED requires explicit human validation
- States are properly persisted and retrieved
- Blocks prevent progression when in SUSPENDED state without validation
**Blocker:** Yes - core regime mechanism

### 7. Artifact Materialization Gate
**Check:** Everything that exists for the regime is a tangible artifact.
**How to verify:**
- All concepts (ILHA, PEDRA, ShadowDocument, etc.) have concrete representations
- Abstract concepts have corresponding data structures or files
- No "in-memory only" concepts that cannot be inspected or audited
- Artifacts are versioned and storable
**Blocker:** Yes - core regime requirement

### 8. Contextual Meaning Gate
**Check:** Context properly modifies meaning of claims.
**How to verify:**
- Same claim in different ILHAs can have different interpretations/GMIF levels
- PEDRA reuse tracking shows in which ILHAs contexts have been applied
- Contextual factors (participants, time, space, topic) are recorded and considered
- ILHA model properly captures moment-space-time-participants
**Blocker:** Medium - important but may not block release if minor

### 9. Autonomous Cycle Compliance Gate
**Check:** Sleep/wake decisions follow defined criteria.
**How to verify:**
- Sleep score calculation uses memory_load, error_rate, gaps_detected, time_since_sleep
- Thresholds are configurable and documented
- System can autonomously decide to sleep/wake based on signals
- Manual override capability exists
**Blocker:** Medium - important feature but may not block initial release

### 10. School Mode Effectiveness Gate
**Check:** Gap resolution process is effective.
**How to verify:**
- Identified gaps are tracked and addressed
- School mode produces documented resolutions
- Resolved gaps are marked as such and don't reappear without cause
- Learning from gap resolution is incorporated into future practice
**Blocker:** Medium - important for learning but may not block release

## Gate Status Indicators

Each gate should be marked as:
- [ ] NOT CHECKED
- [ ] PASSING
- [ ] FAILING (with explanation)
- [ ] NOT APPLICABLE (with justification)

## Verification Process

1. Before declaring work complete, run through each gate
2. For any FAILING gate, document why and determine if it's a blocker
3. Blocker gates MUST be fixed before proceeding
4. Non-blocker gates should be addressed in future work
5. Maintain evidence of gate verification (screenshots, logs, test results)