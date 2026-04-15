"""
Ilhas - Sistema de Memória Insular

Este pacote implementa a gestão de ilhas, saliência e erosão:
- GestorIlhas: criação, gestão de membros, combinação
- CalculadorSaliência: cálculo de saliência
- DinâmicaErosão: decay e transições de estado
- GestorRelações: relações entre ilhas
"""

from app.ilhas.gerenciador import GestorIlhas
from app.ilhas.saliência import (
    CalculadorSaliência,
    CalculadorFrequência,
    CalculadorIntensidade,
    CalculadorNovidade,
    CalculadorRelevância,
    calcular_saliência_completa,
)
from app.ilhas.erosão import DinâmicaErosão, GestorReativações
from app.ilhas.relacoes import GestorRelações, CalculadorSimilaridade, sugerir_agregações_batch

__all__ = [
    # Gestão
    "GestorIlhas",
    # Saliência
    "CalculadorSaliência",
    "CalculadorFrequência",
    "CalculadorIntensidade",
    "CalculadorNovidade",
    "CalculadorRelevância",
    "calcular_saliência_completa",
    # Erosão
    "DinâmicaErosão",
    "GestorReativações",
    # Relações
    "GestorRelações",
    "CalculadorSimilaridade",
    "sugerir_agregações_batch",
]
