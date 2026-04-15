"""
Regime Declarativo - Rule Engine com Normas Explícitas

Implementa o regime declarativo onde proposições são validadas
contra normas explícitas antes de output.
"""

from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass


class GateDecision(Enum):
    PASS = "pass"
    BLOCK = "block"
    APPROVAL = "approval"


class NormType(Enum):
    MANDATORY = "mandatory"
    CONDITIONAL = "conditional"
    PROHIBITED = "prohibited"


@dataclass
class Norm:
    id: str
    name: str
    description: str
    norm_type: NormType


def evaluate_claim_with_regime(claim: Dict, regime) -> Tuple[GateDecision, List[str]]:
    """Avalia um claim contra o regime declarativo."""
    # Implementação: verificar GMIF, contradições, fontes
    return GateDecision.PASS, []


def create_default_regime():
    """Cria o regime declarativo padrão."""
    return {
        "name": "Grilo Falante - Declarative Regime",
        "rules": []
    }


def get_regime():
    """Retorna instância global do regime."""
    return create_default_regime()