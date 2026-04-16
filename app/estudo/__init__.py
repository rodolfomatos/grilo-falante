"""
Estudo Dirigido - Sistema de estudo ativo de lacunas

Este pacote implementa:
- IdentificadorLacunas: Identificação de lacunas de conhecimento
- MotorEstudo: Motor de estudo dirigido
- EstudoDirigido: Estado de um estudo
"""

from app.estudo.lacunas import (
    IdentificadorLacunas,
    LacunaConhecimento,
    SeveridadeLacuna,
    TipoLacuna,
)
from app.estudo.motor import (
    MotorEstudo,
    EstudoDirigido,
    EstadoEstudo,
)

__all__ = [
    # Lacunas
    "IdentificadorLacunas",
    "LacunaConhecimento",
    "SeveridadeLacuna",
    "TipoLacuna",
    # Motor
    "MotorEstudo",
    "EstudoDirigido",
    "EstadoEstudo",
]
