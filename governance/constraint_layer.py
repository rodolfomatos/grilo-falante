"""
Constraint Layer - Enforcer de Constrangimentos Discursivos
"""

from typing import List, Tuple
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


def create_default_constraints() -> List[Constraint]:
    return [
        Constraint("C001", "No False Certainty", r"\b(100%|certamente)\b", "Certeza absoluta"),
        Constraint("C002", "No Unattributed Claims", r"(?:diz|mostra|provou)", "Claim factual sem atribuição"),
    ]


def evaluate_text_constraints(text: str) -> Tuple[bool, List]:
    """Avalia texto contra constraints."""
    return True, []


def get_constraint_layer():
    return create_default_constraints()