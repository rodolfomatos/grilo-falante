"""
Índice Pragmático - Índice operativo orientado a tarefas/perguntas

Além do índice ontológico por assunto, existe um índice operativo
orientado por tarefas, perguntas e procedimentos.

"Como fazer X?" → [tópicos relevantes]
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EntradaPragmática:
    """
    Uma entrada no índice pragmático.

    Representa uma pergunta ou tarefa operativa.
    """
    id: str
    pergunta: str
    tarefa: str
    tópico_id: Optional[str] = None

    # Referências
    ilhas_referenciadas: List[str] = field(default_factory=list)
    claims_referenciadas: List[str] = field(default_factory=list)

    # Metadados
    uso_count: int = 0
    last_used: Optional[str] = None

    def para_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pergunta": self.pergunta,
            "tarefa": self.tarefa,
            "tópico_id": self.tópico_id,
            "ilhas": self.ilhas_referenciadas,
            "claims": self.claims_referenciadas,
            "uso_count": self.uso_count,
        }


class IndicePragmatico:
    """
    Índice Pragmático - camada de perguntas, tarefas e procedimentos.

    Permite buscar por "como fazer X" em vez de só por tópico.
    """

    def __init__(self):
        self.entradas: Dict[str, EntradaPragmática] = {}
        self._pergunta_para_entrada: Dict[str, str] = {}

    def adicionar_entrada(self, entrada: EntradaPragmática) -> None:
        """Adicionar uma entrada ao índice."""
        self.entradas[entrada.id] = entrada

        # Indexar por palavras da pergunta
        palavras = entrada.pergunta.lower().split()
        for palavra in palavras:
            if len(palavra) > 3:
                self._pergunta_para_entrada[f"word:{palavra}"] = entrada.id

        logger.debug(f"Adicionada entrada pragmática: {entrada.id}")

    def indexar_pergunta(
        self,
        pergunta: str,
        tarefa: str,
        ilha_id: Optional[str] = None,
    ) -> str:
        """
        Indexar uma nova pergunta/tarefa.

        Args:
            pergunta: A pergunta (e.g., "Como fazer auditoria?")
            tarefa: Descrição da tarefa
            ilha_id: ID da ilha associada (opcional)

        Returns:
            ID da entrada criada
        """
        import uuid
        entrada_id = f"pragma-{uuid.uuid4().hex[:8]}"

        entrada = EntradaPragmática(
            id=entrada_id,
            pergunta=pergunta,
            tarefa=tarefa,
            ilhas_referenciadas=[ilha_id] if ilha_id else [],
        )

        self.adicionar_entrada(entrada)
        return entrada_id

    def buscar_por_tarefa(self, query: str) -> List[EntradaPragmática]:
        """
        Buscar entradas por tarefa.

        Args:
            query: Query de busca

        Returns:
            Lista de entradas que matcham
        """
        query_lower = query.lower()
        resultados = []

        # Buscar na pergunta
        for entrada in self.entradas.values():
            if query_lower in entrada.pergunta.lower():
                resultados.append(entrada)
                continue

            if query_lower in entrada.tarefa.lower():
                resultados.append(entrada)
                continue

        return resultados

    def buscar_por_ilha(self, ilha_id: str) -> List[EntradaPragmática]:
        """Buscar todas as entradas que referenciam uma ilha."""
        return [
            e for e in self.entradas.values()
            if ilha_id in e.ilhas_referenciadas
        ]

    def incrementar_uso(self, entrada_id: str) -> None:
        """Incrementar contador de uso de uma entrada."""
        if entrada_id in self.entradas:
            self.entradas[entrada_id].uso_count += 1
            from datetime import datetime
            self.entradas[entrada_id].last_used = datetime.now().isoformat()

    def listar_mais_usadas(self, limit: int = 10) -> List[EntradaPragmática]:
        """Listar entradas mais usadas."""
        ordenadas = sorted(
            self.entradas.values(),
            key=lambda e: e.uso_count,
            reverse=True,
        )
        return ordenadas[:limit]

    def adicionar_ilha_a_entrada(
        self,
        entrada_id: str,
        ilha_id: str,
    ) -> bool:
        """Adicionar uma ilha a uma entrada."""
        if entrada_id not in self.entradas:
            return False

        entrada = self.entradas[entrada_id]
        if ilha_id not in entrada.ilhas_referenciadas:
            entrada.ilhas_referenciadas.append(ilha_id)

        return True


# Singleton
_indice_pragmatico: Optional[IndicePragmatico] = None


def get_indice_pragmatico() -> IndicePragmatico:
    """Obter instância global do índice pragmático."""
    global _indice_pragmatico
    if _indice_pragmatico is None:
        _indice_pragmatico = IndicePragmatico()
        _inicializar_padrão(_indice_pragmatico)
    return _indice_pragmatico


def _inicializar_padrão(indice: IndicePragmatico) -> None:
    """Inicializar com entradas pragmáticas padrão."""
    padrão = [
        ("Como fazer auditoria hostil?", "Auditar afirmações de um texto"),
        ("Como extrair claims?", "Extrair claims de um documento"),
        ("Como classificar com GMIF?", "Classificar claims segundo M1-M7"),
        ("Como criar uma ilha?", "Criar uma nova ilha de memória"),
        ("Como fazer sleep cycle?", "Executar ciclo Ir Dormir"),
        ("Como fazer wake cycle?", "Executar ciclo Acordar"),
        ("Como exportar sessão?", "Exportar sessão para resume"),
        ("Como importar sessão?", "Importar sessão de um script"),
        ("Como identificar lacunas?", "Detetar lacunas no conhecimento"),
        ("Como promover uma claim?", "Passar uma claim para validada"),
    ]

    for pergunta, tarefa in padrão:
        indice.indexar_pergunta(pergunta, tarefa)
