"""
Índices - Sistema de indexes para memória contextualizada

Este paquete implementa os índices para navegação e busca:
- Índice Canónico: tópicos do domínio (mapa de topo)
- Índice Pragmático: perguntas e tarefas (como fazer X)
- Coverage Map: fontes que cobrem cada tópico
- Bundle de Reentrada: pacote para retomar trabalho
"""

from app.indices.canonico import IndiceCanonico, TopicoCanonico, get_indice_canonico
from app.indices.pragmatico import IndicePragmatico, EntradaPragmática, get_indice_pragmatico
from app.indices.coverage import CoverageMap, Cobertura, Lacuna, get_coverage_map
from app.indices.bundle import (
    BundleReentradaCompleto,
    ConstrutorBundle,
    construir_bundle,
)

__all__ = [
    # Canónico
    "IndiceCanonico",
    "TopicoCanonico",
    "get_indice_canonico",
    # Pragmático
    "IndicePragmatico",
    "EntradaPragmática",
    "get_indice_pragmatico",
    # Coverage
    "CoverageMap",
    "Cobertura",
    "Lacuna",
    "get_coverage_map",
    # Bundle
    "BundleReentradaCompleto",
    "ConstrutorBundle",
    "construir_bundle",
]
