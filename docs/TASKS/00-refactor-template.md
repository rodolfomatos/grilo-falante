# Task: Refactor [Component/Module Name]

## Objective
Improve the internal structure of [component/module] without changing its external behavior.

## Pre-Implementation Checklist (Karpathy Principles)
- [ ] **Think Before Coding** — What is the core problem with the current structure? Am I solving a real problem or just polishing?
- [ ] **Simplicity First** — What's the simplest change that achieves the goal? Could this be done in fewer steps?
- [ ] **Surgical Changes** — What is the exact minimum surface area of change? Can I avoid touching tests that still pass?
- [ ] **Goal-Driven Execution** — How will I verify behavior is preserved? What's my rollback if the refactor goes wrong?

## Context
[Describe the current pain points — coupling, duplication, readability, testability issues.]

## Constraints
- External behavior must remain unchanged (no new features, no behavior changes)
- Existing tests must continue to pass without modification
- Public API surface must be preserved or have a documented migration path
- Should improve rather than degrade code quality metrics

## Success Criteria
- All existing tests pass without modification (except where tests tested bad design)
- Code quality metrics improve (complexity, coupling, duplication)
- New structure is demonstrably more maintainable
- No regressions in any existing functionality
