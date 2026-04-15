"""
Ontology States - Enumera os estados de todos os objectos do sistema.
"""

from enum import Enum


class EstadoIlha(str, Enum):
    EMBRIONARIA = "EMBRIONARIA"
    ATIVA = "ATIVA"
    CONSOLIDADA = "CONSOLIDADA"
    ERODENDO = "ERODENDO"
    DORMINTE = "DORMINTE"


class EstadoPedra(str, Enum):
    NOVA = "NOVA"
    EM_ESPERA = "EM_ESPERA"
    AGREGADA = "AGREGADA"
    TRANSFORMADA = "TRANSFORMADA"


class EstadoClaim(str, Enum):
    ESTRUTURAL = "ESTRUTURAL"
    CLASSIFICADA = "CLASSIFICADA"
    EM_ANALISE = "EM_ANALISE"
    VALIDADA = "VALIDADA"
    REJEITADA = "REJEITADA"
    PROMOVIDA = "PROMOVIDA"


class EstadoArtefacto(str, Enum):
    RASCUNHO = "RASCUNHO"
    MATERIALIZADO = "MATERIALIZADO"
    AUDITADO = "AUDITADO"
    VALIDADO = "VALIDADO"
    ARQUIVADO = "ARQUIVADO"


class TipoInteracao(str, Enum):
    MENSAGEM = "MENSAGEM"
    CLAIM = "CLAIM"
    DOCUMENTO = "DOCUMENTO"
    EVENTO = "EVENTO"
    PEDIDO_ESTUDO = "PEDIDO_ESTUDO"


class TipoRelacao(str, Enum):
    RELATED_TO = "RELATED_TO"
    CONTRADIZ = "CONTRADIZ"
    COMPLEMENTA = "COMPLEMENTA"
    DERIVA_DE = "DERIVA_DE"
    AGREGADO_EM = "AGREGADO_EM"
    VERSÃO_DE = "VERSAO_DE"
