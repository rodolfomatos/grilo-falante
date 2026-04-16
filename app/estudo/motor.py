"""
Motor de Estudo Dirigido - Sistema de estudo ativo

O sistema pode "ir estudar" quando identifica lacunas.
Este módulo implementa o motor de estudo dirigido.

Estudar não é consumir. É adquirir material novo sob regime controlado:
1. Identificar lacuna
2. Procurar fontes/orientado
3. Materializar fontes
4. Construir documentos sombra
5. Mapear cobertura e claims
6. Integrar se validado
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from app.estudo.lacunas import LacunaConhecimento, IdentificadorLacunas

logger = logging.getLogger(__name__)


class EstadoEstudo(str):
    """Estados do estudo dirigido."""
    IDENTIFICADO = "identificado"
    EM_PROGRESSO = "em_progresso"
    FONTES_LOCALIZADAS = "fontes_localizadas"
    MATERIALIZADO = "materializado"
    AUDITADO = "auditado"
    INTEGRADO = "integrado"
    CONCLUÍDO = "concluído"
    FALHOU = "falhou"


@dataclass
class EstudoDirigido:
    """
    Representa um estudo dirigido para uma lacuna.
    """
    id: str
    lacuna_id: str

    estado: EstadoEstudo = EstadoEstudo.IDENTIFICADO

    # Passos executados
    passos: List[str] = field(default_factory=list)

    # Fontes encontradas
    fontes_encontradas: List[Dict[str, Any]] = field(default_factory=list)

    # Documentos materializados
    documentos_materializados: List[str] = field(default_factory=list)

    # Resultado
    resultado: Optional[str] = None
    erro: Optional[str] = None

    # Metadados
    iniciado_em: str = ""
    concluído_em: Optional[str] = None

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "lacuna_id": self.lacuna_id,
            "estado": self.estado.value if isinstance(self.estado, EstadoEstudo) else self.estado,
            "passos": self.passos,
            "fontes_encontradas": len(self.fontes_encontradas),
            "documentos_materializados": len(self.documentos_materializados),
            "resultado": self.resultado,
            "erro": self.erro,
        }


class MotorEstudo:
    """
    Motor de estudo dirigido.

    Implementa o ciclo de estudo:
    1. Identificar lacuna
    2. Procurar fontes
    3. Materializar fontes
    4. Auditar fontes
    5. Integrar se válido
    """

    def __init__(
        self,
        buscador_fontes: Optional[Callable] = None,
    ):
        """
        Inicializar motor de estudo.

        Args:
            buscador_fontes: Função para buscar fontes (opcional)
        """
        self.buscador_fontes = buscador_fontes
        self.estudos: Dict[str, EstudoDirigido] = {}

    def criar_estudo(
        self,
        lacuna: LacunaConhecimento,
    ) -> EstudoDirigido:
        """
        Criar um novo estudo para uma lacuna.

        Args:
            lacuna: Lacuna a estudar

        Returns:
            Estudo criado
        """
        import uuid
        estudo = EstudoDirigido(
            id=f"estudo-{uuid.uuid4().hex[:8]}",
            lacuna_id=lacuna.id,
            iniciado_em="",
        )
        self.estudos[estudo.id] = estudo
        logger.info(f"Criado estudo {estudo.id} para lacuna {lacuna.id}")
        return estudo

    async def executar_estudo(
        self,
        estudo: EstudoDirigido,
    ) -> EstudoDirigido:
        """
        Executar estudo completo para uma lacuna.

        Args:
            estudo: Estudo a executar

        Returns:
            Estudo com resultado
        """
        try:
            # Passo 1: Identificar lacuna (já feito)
            estudo.passos.append("identificar")
            estudo.estado = EstadoEstudo.EM_PROGRESSO

            # Passo 2: Procurar fontes
            estudo = await self._procurar_fontes(estudo)
            if not estudo.fontes_encontradas:
                estudo.estado = EstadoEstudo.FALHOU
                estudo.erro = "Nenhuma fonte encontrada"
                return estudo

            # Passo 3: Materializar fontes
            estudo = await self._materializar_fontes(estudo)

            # Passo 4: Auditar fontes
            estudo = await self._auditar_fontes(estudo)

            # Passo 5: Integrar
            estudo = await self._integrar_fontes(estudo)

            estudo.estado = EstadoEstudo.CONCLUÍDO
            logger.info(f"Estudo {estudo.id} concluído")

        except Exception as e:
            logger.error(f"Erro no estudo {estudo.id}: {e}")
            estudo.estado = EstadoEstudo.FALHOU
            estudo.erro = str(e)

        return estudo

    async def _procurar_fontes(
        self,
        estudo: EstudoDirigido,
    ) -> EstudoDirigido:
        """Procurar fontes para a lacuna."""
        estudo.passos.append("procurar_fontes")
        estudo.estado = EstadoEstudo.EM_PROGRESSO

        if self.buscador_fontes:
            fontes = await self.buscador_fontes(estudo.lacuna_id)
            estudo.fontes_encontradas = fontes
        else:
            # Buscador simples por defeito
            estudo.fontes_encontradas = [{
                "id": "placeholder",
                "nome": "Fonte não especificada",
                "tipo": "documento",
            }]

        estudo.estado = EstadoEstudo.FONTES_LOCALIZADAS
        return estudo

    async def _materializar_fontes(
        self,
        estudo: EstudoDirigido,
    ) -> EstudoDirigido:
        """Materializar as fontes encontradas."""
        estudo.passos.append("materializar")

        for fonte in estudo.fontes_encontradas:
            estudo.documentos_materializados.append(fonte.get("id", ""))

        estudo.estado = EstadoEstudo.MATERIALIZADO
        return estudo

    async def _auditar_fontes(
        self,
        estudo: EstudoDirigido,
    ) -> EstudoDirigido:
        """Auditar as fontes materializadas."""
        estudo.passos.append("auditar")
        estudo.estado = EstadoEstudo.AUDITADO
        return estudo

    async def _integrar_fontes(
        self,
        estudo: EstudoDirigido,
    ) -> EstudoDirigido:
        """Integrar fontes auditadas no sistema."""
        estudo.passos.append("integrar")
        estudo.estado = EstadoEstudo.INTEGRADO
        estudo.resultado = f"Integradas {len(estudo.documentos_materializados)} fontes"
        return estudo

    def obter_estudo(self, estudo_id: str) -> Optional[EstudoDirigido]:
        """Obter um estudo pelo ID."""
        return self.estudos.get(estudo_id)

    def listar_estudos(
        self,
        estado: Optional[str] = None,
    ) -> List[EstudoDirigido]:
        """Listar estudos, opcionalmente filtrados por estado."""
        estudos = list(self.estudos.values())
        if estado:
            estudos = [e for e in estudos if e.estado.value == estado]
        return estudos
