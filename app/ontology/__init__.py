"""
Ontology Module - Sistema de Memória Insular

Este módulo implementa a ontologia nuclear do sistema de memória insular:
- Ilha: agregado cognitivo consolidado
- Pedra: interação relevante que cria saliência
- Saliencia: componentes da saliência
- Claim: unidade de conhecimento extraída
"""

from app.ontology.estados import (
    EstadoIlha,
    EstadoPedra,
    EstadoClaim,
    EstadoArtefacto,
    TipoInteracao,
    TipoRelacao,
)

from app.ontology.ilhas import (
    Saliencia,
    Pedra,
    MembroIlha,
    RelacaoIlha,
    HistóricoReativacao,
    Ilha,
    Claim,
)

__all__ = [
    # Estados
    "EstadoIlha",
    "EstadoPedra",
    "EstadoClaim",
    "EstadoArtefacto",
    "TipoInteracao",
    "TipoRelacao",
    # Classes
    "Saliencia",
    "Pedra",
    "MembroIlha",
    "RelacaoIlha",
    "HistóricoReativacao",
    "Ilha",
    "Claim",
]
