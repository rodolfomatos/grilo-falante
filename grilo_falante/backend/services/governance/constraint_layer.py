"""
Constraint Layer - Discursive constraint enforcer

From prototype: enforces discursive constraints on claims
(prohibitions, mandatory elements, qualifications).
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ConstraintType(Enum):
    PROHIBITION = "prohibition"
    MANDATORY = "mandatory"
    QUALIFICATION = "qualification"


class ConstraintLevel(Enum):
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"


@dataclass
class Constraint:
    id: str
    name: str
    pattern: str
    message: str
    constraint_type: ConstraintType = ConstraintType.PROHIBITION
    level: ConstraintLevel = ConstraintLevel.WARNING


@dataclass
class ConstraintViolation:
    constraint_id: str
    constraint_name: str
    matched_text: str
    position: int
    level: ConstraintLevel
    message: str


DEFAULT_CONSTRAINTS = [
    Constraint(
        id="C001",
        name="No False Certainty",
        pattern=r"\b(100%|certamente|com certeza|absolutamente|definitivamente)\b",
        message="Absolute certainty claim detected - requires evidence",
        constraint_type=ConstraintType.PROHIBITION,
        level=ConstraintLevel.BLOCK,
    ),
    Constraint(
        id="C002",
        name="No Unattributed Claims",
        pattern=r"\b(diz|mostra|provou|demonstrou|evidencia)\s+(?:que|que\s+o|como)\b",
        message="Factual claim without attribution detected",
        constraint_type=ConstraintType.PROHIBITION,
        level=ConstraintLevel.ERROR,
    ),
    Constraint(
        id="C003",
        name="Requires Qualification",
        pattern=r"\b(todos|siempre|sempre|todo|always)\b",
        message="Universal quantifier requires careful qualification",
        constraint_type=ConstraintType.QUALIFICATION,
        level=ConstraintLevel.WARNING,
    ),
    Constraint(
        id="C004",
        name="No Implicit Authority",
        pattern=r"\b(confia em mim|acredita em mim|trust me|believe me)\b",
        message="Self-referential authority claim detected",
        constraint_type=ConstraintType.PROHIBITION,
        level=ConstraintLevel.BLOCK,
    ),
    Constraint(
        id="C005",
        name="Causal Language Warning",
        pattern=r"\b(por isso|portanto|therefore|thus|consequently|logo)\b",
        message="Causal inference detected - verify premise/conclusion relationship",
        constraint_type=ConstraintType.QUALIFICATION,
        level=ConstraintLevel.WARNING,
    ),
]


def create_default_constraints() -> List[Constraint]:
    """Create the default constraint set."""
    return DEFAULT_CONSTRAINTS.copy()


def evaluate_text_constraints(
    text: str,
    constraints: Optional[List[Constraint]] = None
) -> Tuple[bool, List[ConstraintViolation]]:
    """
    Evaluate text against constraints.

    Args:
        text: The text to evaluate
        constraints: Optional list of constraints (uses defaults if not provided)

    Returns:
        Tuple of (passed, violations) where passed is True if no violations
    """
    if constraints is None:
        constraints = create_default_constraints()

    violations = []

    for constraint in constraints:
        pattern = re.compile(constraint.pattern, re.IGNORECASE)
        for match in pattern.finditer(text):
            violation = ConstraintViolation(
                constraint_id=constraint.id,
                constraint_name=constraint.name,
                matched_text=match.group(),
                position=match.start(),
                level=constraint.level,
                message=constraint.message,
            )
            violations.append(violation)

    has_blocking = any(v.level == ConstraintLevel.BLOCK for v in violations)
    passed = not has_blocking

    return passed, violations


def evaluate_for_promotion(
    text: str,
    constraints: Optional[List[Constraint]] = None
) -> Tuple[str, List[ConstraintViolation]]:
    """
    Evaluate text against constraints for promotion readiness.

    Returns:
        Tuple of (status, violations) where status is "PASS", "CONDITIONAL", or "BLOCK"
    """
    passed, violations = evaluate_text_constraints(text, constraints)

    if not passed:
        return "BLOCK", violations

    warnings = [v for v in violations if v.level == ConstraintLevel.WARNING]
    errors = [v for v in violations if v.level == ConstraintLevel.ERROR]

    if errors:
        return "CONDITIONAL", violations

    if warnings:
        return "CONDITIONAL", violations

    return "PASS", violations


def get_constraint_summary(violations: List[ConstraintViolation]) -> dict:
    """Get summary of constraint violations."""
    return {
        "total": len(violations),
        "blocking": len([v for v in violations if v.level == ConstraintLevel.BLOCK]),
        "errors": len([v for v in violations if v.level == ConstraintLevel.ERROR]),
        "warnings": len([v for v in violations if v.level == ConstraintLevel.WARNING]),
        "by_constraint": {
            v.constraint_id: {
                "name": v.constraint_name,
                "count": sum(1 for x in violations if x.constraint_id == v.constraint_id)
            }
            for v in violations
        }
    }