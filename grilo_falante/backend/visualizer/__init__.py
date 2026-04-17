"""
Visualizer - Wikipedia-like explorer for Grilo Falante

Provides interactive visualization of:
- Ilhas (Memory Islands)
- Claims (with GMIF)
- Knowledge Graph
- Sources
- Gaps
"""

from grilo_falante.backend.visualizer.data import (
    VisualizerData,
    IlhaData,
    ClaimData,
    GraphData,
    SourceData,
    GapData,
)

__all__ = [
    "VisualizerData",
    "IlhaData",
    "ClaimData",
    "GraphData",
    "SourceData",
    "GapData",
]