"""
Sistema de Lacunas - Identificação de lacunas de conhecimento

O sistema pode "ir estudar" quando identifica lacunas nas ilhas.
Este módulo implementa a identificação de lacunas.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from app.ontology.ilhas import Ilha

logger = logging.getLogger(__name__)


class SeveridadeLacuna(str, Enum):
    BAIXA = "baixa"
    MÉDIA = "media"
    ALTA = "alta"
    CRÍTICA = "critica"


class TipoLacuna(str, Enum):
    FONTES = "fontes"
    EVIDÊNCIA = "evidência"
    CLARIFICAÇÃO = "clarificação"
    VALIDAÇÃO = "validação"
    COMPLEXIDADE = "complexidade"


@dataclass
class LacunaConhecimento:
    """
    Representa uma lacuna de conhecimento identificada.
    """
    id: str
    ilha_id: str
    tipo: TipoLacuna
    severidade: SeveridadeLacuna

    descrição: str
    questão: str = ""

    # Estado
    estado: str = "identificada"  # identificada, em_estudo, resolvida
    resolvida_por: Optional[str] = None

    # Metadados
    criada_em: str = ""
    resolvida_em: Optional[str] = None

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "ilha_id": self.ilha_id,
            "tipo": self.tipo.value,
            "severidade": self.severidade.value,
            "descrição": self.descrição,
            "questão": self.questão,
            "estado": self.estado,
            "resolvida_por": self.resolvida_por,
        }


class IdentificadorLacunas:
    """
    Identifica lacunas no conhecimento de uma ilha.

    Usa múltiplos critérios:
    - Claims pendentes vs validadas
    - Topics sem cobertura
    - Questões em aberto
    """

    def __init__(self):
        self.lacunas: Dict[str, LacunaConhecimento] = {}

    def identificar_lacunas_ilha(
        self,
        ilha: Ilha,
    ) -> List[LacunaConhecimento]:
        """
        Identificar lacunas numa ilha.

        Args:
            ilha: Ilha a analisar

        Returns:
            Lista de lacunas identificadas
        """
        lacunas = []

        # 1. Lacuna de validação (claims pendentes)
        if ilha.claims_pendentes > 0 and ilha.claims_validadas == 0:
            lacunas.append(LacunaConhecimento(
                id=f"lac-{ilha.id}-validação",
                ilha_id=ilha.id,
                tipo=TipoLacuna.VALIDAÇÃO,
                severidade=SeveridadeLacuna.ALTA,
                descrição=f"{ilha.claims_pendentes} claims pendentes, 0 validadas",
                questão="Como validar as claims pendentes?",
            ))

        # 2. Lacuna de fontes (ilha sem membros = sem conteúdo)
        if len(ilha.membros) == 0:
            lacunas.append(LacunaConhecimento(
                id=f"lac-{ilha.id}-fontes",
                ilha_id=ilha.id,
                tipo=TipoLacuna.FONTES,
                severidade=SeveridadeLacuna.CRÍTICA,
                descrição="Ilha sem membros - sem conteúdo",
                questão="Que fontes/documentos suportam esta ilha?",
            ))

        # 3. Lacuna mista (muitos pendentes, poucos validados)
        if ilha.claims_pendentes > 5 and ilha.claims_validadas < 2:
            lacunas.append(LacunaConhecimento(
                id=f"lac-{ilha.id}-evidência",
                ilha_id=ilha.id,
                tipo=TipoLacuna.EVIDÊNCIA,
                severidade=SeveridadeLacuna.MÉDIA,
                descrição=f"{ilha.claims_pendentes} pendentes vs {ilha.claims_validadas} validadas",
                questão="Como obter mais evidência para validar claims?",
            ))

        # 4. Lacuna de clarificação (ilha sem descrição)
        if not ilha.descrição or len(ilha.descrição) < 20:
            lacunas.append(LacunaConhecimento(
                id=f"lac-{ilha.id}-clarificação",
                ilha_id=ilha.id,
                tipo=TipoLacuna.CLARIFICAÇÃO,
                severidade=SeveridadeLacuna.BAIXA,
                descrição="Ilha sem descrição clara",
                questão="O que é esta ilha? Qual o seu propósito?",
            ))

        return lacunas

    def identificar_lacunas_sistema(
        self,
        ilhas: List[Ilha],
    ) -> List[LacunaConhecimento]:
        """
        Identificar lacunas em todo o sistema.

        Args:
            ilhas: Lista de ilhas

        Returns:
            Lista de lacunas do sistema
        """
        todas_lacunas = []

        for ilha in ilhas:
            lacunas = self.identificar_lacunas_ilha(ilha)
            for lacuna in lacunas:
                self.lacunas[lacuna.id] = lacuna
                todas_lacunas.append(lacuna)

        logger.info(f"Identificadas {len(todas_lacunas)} lacunas no sistema")
        return todas_lacunas

    def priorizar_lacunas(
        self,
        lacunas: List[LacunaConhecimento],
    ) -> List[LacunaConhecimento]:
        """
        Prioritizar lacunas por severidade.

        Args:
            lacunas: Lista de lacunas

        Returns:
            Lista ordenada por prioridade
        """
        ordem_severidade = {
            SeveridadeLacuna.CRÍTICA: 0,
            SeveridadeLacuna.ALTA: 1,
            SeveridadeLacuna.MÉDIA: 2,
            SeveridadeLacuna.BAIXA: 3,
        }

        return sorted(
            lacunas,
            key=lambda l: ordem_severidade.get(l.severidade, 99)
        )

    def obter_estatísticas_lacunas(
        self,
    ) -> Dict[str, Any]:
        """Obter estatísticas de lacunas do sistema."""
        por_tipo: Dict[str, int] = {}
        por_severidade: Dict[str, int] = {}
        por_estado: Dict[str, int] = {}

        for lacuna in self.lacunas.values():
            por_tipo[lacuna.tipo.value] = por_tipo.get(lacuna.tipo.value, 0) + 1
            por_severidade[lacuna.severidade.value] = por_severidade.get(lacuna.severidade.value, 0) + 1
            por_estado[lacuna.estado] = por_estado.get(lacuna.estado, 0) + 1

        return {
            "total": len(self.lacunas),
            "por_tipo": por_tipo,
            "por_severidade": por_severidade,
            "por_estado": por_estado,
        }
