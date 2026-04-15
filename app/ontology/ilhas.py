"""
Ontologia de Ilhas - Sistema de Memória Insular

Este módulo implementa o conceito de memória insular conforme descrito
no memo_anchor_feynman_pedagogico_gf_ema_memoria_insular.md:

- Lago: campo de fundo da memória
- Pedra: interação relevante que cria saliência
- Ilha: agregado cognitivo consolidado
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from app.ontology.estados import (
    EstadoIlha,
    EstadoPedra,
    EstadoClaim,
    EstadoArtefacto,
    TipoInteracao,
    TipoRelacao,
)


@dataclass
class Saliencia:
    """
    Componentes da saliência de uma pedra ou interação.

    A saliência é o que faz uma pedra "bater" no lago -
    criar ondulação e marcar um ponto como cognitivamente importante.
    """
    valor: float = 0.0

    frequência: float = 0.0      # Quantas vezes surgiu no contexto
    intensidade: float = 0.0     # Reações que gerou
    novidade: float = 0.0        # Quão diferente é do que já existia
    relevância: float = 0.0       # Conexão com ilhas existentes

    @classmethod
    def calcular(
        cls,
        frequência: float,
        intensidade: float,
        novidade: float,
        relevância: float,
        pesos: Optional[Dict[str, float]] = None,
    ) -> "Saliencia":
        """Calcular saliência total a partir dos componentes."""
        pesos = pesos or {
            "frequência": 0.3,
            "intensidade": 0.3,
            "novidade": 0.2,
            "relevância": 0.2,
        }

        valor = (
            pesos["frequência"] * frequência
            + pesos["intensidade"] * intensidade
            + pesos["novidade"] * novidade
            + pesos["relevância"] * relevância
        )

        return cls(
            valor=min(1.0, max(0.0, valor)),
            frequência=frequência,
            intensidade=intensidade,
            novidade=novidade,
            relevância=relevância,
        )

    def para_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Pedra:
    """
    Uma pedra no lago - interação relevante que cria saliência.

    Uma pedra representa uma interação (mensagem, claim, documento)
    que se destaca o suficiente para ser registada.
    """
    id: str = field(default_factory=lambda: f"PEDRA-{uuid.uuid4().hex[:8]}")
    tipo_interação: TipoInteracao = TipoInteracao.MENSAGEM

    # Saliência
    saliência: Saliencia = field(default_factory=Saliencia)

    # Impacto
    impacto_criou_ilha: bool = False
    ilha_criada: Optional[str] = None
    impacto_ilhas_existentes: List[Dict] = field(default_factory=list)

    # Temporal
    data_criação: datetime = field(default_factory=datetime.now)
    última_reativação: datetime = field(default_factory=datetime.now)
    contagem_reações: int = 0

    # Conteúdo
    conteúdo_original: str = ""
    embedding: Optional[List[float]] = None

    # Estado
    estado: EstadoPedra = EstadoPedra.NOVA

    def reativar(self) -> None:
        """Marcar pedra como reativada."""
        self.última_reativação = datetime.now()
        self.contagem_reações += 1

    def transformar_em_ilha(self) -> "Ilha":
        """Transformar esta pedra numa nova ilha."""
        self.estado = EstadoPedra.TRANSFORMADA
        self.impacto_criou_ilha = True

        return Ilha.criar_de_pedra(self)

    def agregar_a_ilha(self, ilha_id: str) -> None:
        """Marcar pedra como agregada a uma ilha."""
        self.estado = EstadoPedra.AGREGADA

    def está_agregada(self) -> bool:
        return self.estado == EstadoPedra.AGREGADA

    def está_transformada(self) -> bool:
        return self.estado == EstadoPedra.TRANSFORMADA

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tipo_interação": self.tipo_interação.value,
            "saliência": self.saliência.para_dict(),
            "impacto_criou_ilha": self.impacto_criou_ilha,
            "ilha_criada": self.ilha_criada,
            "data_criação": self.data_criação.isoformat(),
            "última_reativação": self.última_reativação.isoformat(),
            "contagem_reações": self.contagem_reações,
            "conteúdo_original": self.conteúdo_original[:100],
            "estado": self.estado.value,
        }


@dataclass
class MembroIlha:
    """Um membro dentro de uma ilha (claim, documento, nota, etc)."""
    member_id: str
    tipo: str  # claim, documento, nota, cápsula...
    saliência: float
    data_inserção: datetime = field(default_factory=datetime.now)
    inserido_por: str = ""  # session_id

    def para_dict(self) -> Dict[str, Any]:
        return {
            "member_id": self.member_id,
            "tipo": self.tipo,
            "saliência": self.saliência,
            "data_inserção": self.data_inserção.isoformat(),
            "inserido_por": self.inserido_por,
        }


@dataclass
class RelacaoIlha:
    """Relação entre duas ilhas."""
    ilha_id: str
    tipo: TipoRelacao
    força: float  # 0-1

    def para_dict(self) -> Dict[str, Any]:
        return {
            "ilha_id": self.ilha_id,
            "tipo": self.tipo.value,
            "força": self.força,
        }


@dataclass
class HistóricoReativacao:
    """Registo de uma reativação da ilha."""
    data: datetime = field(default_factory=datetime.now)
    tipo: str = ""  # reativação, edição, consulta
    session_id: str = ""

    def para_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data.isoformat(),
            "tipo": self.tipo,
            "session_id": self.session_id,
        }


@dataclass
class Ilha:
    """
    Uma ilha no lago - agregado cognitivo consolidado.

    Uma ilha é um território semântico habitável, com ecologia interna,
    que emerge quando uma pedra (ou conjunto de pedras) se consolida.
    """
    id: str = field(default_factory=lambda: f"ILHA-{uuid.uuid4().hex[:8]}")
    nome: str = ""
    descrição: str = ""

    # Fundadores
    artefactos_fundadores: List[str] = field(default_factory=list)  # IDs

    # Membros
    membros: List[MembroIlha] = field(default_factory=list)

    # Relações
    relações: List[RelacaoIlha] = field(default_factory=list)

    # Dinâmica
    grau_consolidação: float = 0.0  # 0-1
    score_ativação: float = 0.0

    # Estado
    estado: EstadoIlha = EstadoIlha.EMBRIONARIA

    # Proveniência
    data_criação: datetime = field(default_factory=datetime.now)
    histórico_reações: List[HistóricoReativacao] = field(default_factory=list)

    # Metadados epistémicos
    claims_validadas: int = 0
    claims_pendentes: int = 0
    lacunas_identificadas: List[str] = field(default_factory=list)

    @classmethod
    def criar_de_pedra(cls, pedra: Pedra) -> "Ilha":
        """Criar uma nova ilha a partir de uma pedra."""
        ilha = cls(
            nome=f"Ilha {pedra.id}",
            descrição=pedra.conteúdo_original[:200] if pedra.conteúdo_original else "",
        )
        ilha.artefactos_fundadores = [pedra.id]
        ilha.score_ativação = pedra.saliência.valor
        return ilha

    def adicionar_membro(self, membro: MembroIlha) -> None:
        """Adicionar um membro à ilha."""
        if not self.tem_membro(membro.member_id):
            self.membros.append(membro)

    def remover_membro(self, member_id: str) -> bool:
        """Remover um membro da ilha."""
        for i, m in enumerate(self.membros):
            if m.member_id == member_id:
                self.membros.pop(i)
                return True
        return False

    def tem_membro(self, member_id: str) -> bool:
        """Verificar se a ilha tem um membro."""
        return any(m.member_id == member_id for m in self.membros)

    def adicionar_reação(self, tipo: str, session_id: str) -> None:
        """Registar uma reativação da ilha."""
        self.histórico_reações.append(
            HistóricoReativacao(tipo=tipo, session_id=session_id)
        )
        self.última_reativação = datetime.now()

    @property
    def última_reativação(self) -> datetime:
        """Obter a data da última reativação."""
        if not self.histórico_reações:
            return self.data_criação
        return max(r.data for r in self.histórico_reações)

    @última_reativação.setter
    def última_reativação(self, value: datetime) -> None:
        """Setter para compatibilidade."""
        pass

    def calcular_score(self, decay_factor: float = 0.95) -> float:
        """
        Calcular score de ativação com decay.

        score = recência × frequência × relevância
        """
        if not self.histórico_reações:
            return 0.0

        agora = datetime.now()
        última = self.última_reativação

        # Recência (mais recente = maior)
        dias_desde = (agora - última).days
        recência = max(0, 1 - (dias_desde * 0.1))

        # Frequência (mais reações = maior)
        frequência = min(1.0, len(self.histórico_reações) / 20)

        # Consolidação
        relevância = self.grau_consolidação

        self.score_ativação = (
            0.4 * recência + 0.3 * frequência + 0.3 * relevância
        )

        return self.score_ativação

    def aplicar_decay(self, factor: float = 0.95) -> None:
        """Aplicar decay ao score."""
        self.score_ativação *= factor

    def adicionar_relação(self, relação: RelacaoIlha) -> None:
        """Adicionar uma relação a outra ilha."""
        if not self.tem_relação(relação.ilha_id):
            self.relações.append(relação)

    def tem_relação(self, ilha_id: str) -> bool:
        """Verificar se tem relação com outra ilha."""
        return any(r.ilha_id == ilha_id for r in self.relações)

    def é_ativa(self, threshold: float = 0.5) -> bool:
        """Verificar se a ilha está ativa."""
        return self.score_ativação >= threshold

    def é_dorminte(self, threshold: float = 0.1) -> bool:
        """Verificar se a ilha está em modo dorminte."""
        return self.score_ativação < threshold

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "descrição": self.descrição,
            "estado": self.estado.value,
            "score_ativação": self.score_ativação,
            "grau_consolidação": self.grau_consolidação,
            "membros_count": len(self.membros),
            "claims_validadas": self.claims_validadas,
            "claims_pendentes": self.claims_pendentes,
            "lacunas": self.lacunas_identificadas,
            "data_criação": self.data_criação.isoformat(),
            "última_reativação": self.última_reativação.isoformat(),
        }


@dataclass
class Claim:
    """Uma claim extraída de uma interação."""
    id: str = field(default_factory=lambda: f"CLM-{uuid.uuid4().hex[:8]}")
    texto: str = ""
    tipo: str = "claim"  # fact, claim, hypothesis, etc.

    # GMIF
    gmif_level: str = "M3"
    gmif_confidence: float = 0.5

    # Estado
    estado: EstadoClaim = EstadoClaim.ESTRUTURAL

    # Proveniência
    session_id: str = ""
    data_criação: datetime = field(default_factory=datetime.now)

    # Embedding
    embedding: Optional[List[float]] = None

    # Sources
    sources: List[str] = field(default_factory=list)

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "texto": self.texto,
            "tipo": self.tipo,
            "gmif_level": self.gmif_level,
            "estado": self.estado.value,
            "session_id": self.session_id,
            "data_criação": self.data_criação.isoformat(),
        }
