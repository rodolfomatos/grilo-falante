"""
Cálculo de Saliência - Componentes e métricas

Este módulo implementa o cálculo de saliência para pedras e ilhas.

A saliência é o que faz uma pedra "bater" no lago - criar ondulação
e marcar um ponto como cognitivamente importante.

Componentes:
- Frequência: quantas vezes surgiu no contexto
- Intensidade: reações/engagement que gerou
- Novidade: quão diferente é do que já existia
- Relevância: conexão com ilhas existentes
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from app.ontology.ilhas import Saliencia, Pedra

logger = logging.getLogger(__name__)


class CalculadorSaliência:
    """
    Calculador de saliência para interações e pedras.

    Usa os componentes definidos na ontologia para calcular
    o valor de saliência (0-1).
    """

    PESOS_PADRÃO = {
        "frequência": 0.3,
        "intensidade": 0.3,
        "novidade": 0.2,
        "relevância": 0.2,
    }

    def __init__(
        self,
        pesos: Optional[Dict[str, float]] = None,
    ):
        """
        Inicializar calculador.

        Args:
            pesos: Dicionário com pesos por componente.
                   Default: {frequência: 0.3, intensidade: 0.3, novidade: 0.2, relevância: 0.2}
        """
        self.pesos = pesos or self.PESOS_PADRÃO.copy()

        total = sum(self.pesos.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Pesos somam {total}, normalizando para 1.0")
            for k in self.pesos:
                self.pesos[k] /= total

    def calcular(
        self,
        frequência: float,
        intensidade: float,
        novidade: float,
        relevância: float,
    ) -> Saliencia:
        """
        Calcular saliência total.

        Args:
            frequência: Valor entre 0-1
            intensidade: Valor entre 0-1
            novidade: Valor entre 0-1
            relevância: Valor entre 0-1

        Returns:
            Objeto Saliencia com valor e componentes
        """
        valor = (
            self.pesos["frequência"] * frequência
            + self.pesos["intensidade"] * intensidade
            + self.pesos["novidade"] * novidade
            + self.pesos["relevância"] * relevância
        )

        valor = min(1.0, max(0.0, valor))

        return Saliencia(
            valor=valor,
            frequência=frequência,
            intensidade=intensidade,
            novidade=novidade,
            relevância=relevância,
        )

    def calcular_de_interação(
        self,
        interação: Dict[str, Any],
    ) -> Saliencia:
        """
        Calcular saliência a partir de uma interação.

        Args:
            interação: Dict com campos da interação

        Returns:
            Saliência calculada
        """
        frequência = min(1.0, interação.get("frequência", 0.5))
        intensidade = min(1.0, interação.get("intensidade", 0.3))
        novidade = min(1.0, interação.get("novidade", 0.5))
        relevância = min(1.0, interação.get("relevância", 0.4))

        return self.calcular(frequência, intensidade, novidade, relevância)

    def calcular_de_pedra(self, pedra: Pedra) -> Saliencia:
        """
        Obter saliência de uma pedra (já calculada).

        Args:
            pedra: Pedra existente

        Returns:
            Saliência da pedra
        """
        return pedra.saliência


class CalculadorFrequência:
    """
    Calcula o componente frequência da saliência.

    Frequência = quantas vezes algo surgiu no contexto
    """

    @staticmethod
    def calcular(
        interações: List[Dict[str, Any]],
        conteúdo: str,
        janela: int = 10,
    ) -> float:
        """
        Calcular frequência de um conteúdo numa janela de interações.

        Args:
            interações: Lista de interações
            conteúdo: Conteúdo a procurar
            janela: Número de interações a considerar

        Returns:
            Valor de frequência (0-1)
        """
        if not interações:
            return 0.5  # Default neutro

        # Últimas N interações
        recentes = interações[-janela:]

        # Contar ocorrências
        count = sum(
            1 for i in recentes
            if conteúdo.lower() in i.get("conteúdo", "").lower()
        )

        # Normalizar para 0-1
        return min(1.0, count / max(1, janela))


class CalculadorIntensidade:
    """
    Calcula o componente intensidade da saliência.

    Intensidade = reactions/engagement que gerou
    """

    @staticmethod
    def calcular(
        interações: List[Dict[str, Any]],
        conteúdo: str,
    ) -> float:
        """
        Calcular intensidade baseada em reações.

        Args:
            interações: Lista de interações
            conteúdo: Conteúdo a avaliar

        Returns:
            Valor de intensidade (0-1)
        """
        # Procurar intensidade declarada
        for i in interações:
            if conteúdo.lower() in i.get("conteúdo", "").lower():
                if "intensidade" in i:
                    return min(1.0, float(i["intensidade"]))

        # Inferir de métricas disponíveis
        sinais_positivos = 0
        sinais_negativos = 0

        for i in interações:
            if conteúdo.lower() in i.get("conteúdo", "").lower():
                # Reações positivas
                if i.get("reacções", 0) > 0:
                    sinais_positivos += 1
                # Claims geradas
                if i.get("claims_geradas", 0) > 2:
                    sinais_positivos += 0.5
                # Bloqueios
                if i.get("bloqueado", False):
                    sinais_negativos += 0.5

        # Score baseado em reações
        total = sinais_positivos + sinais_negativos
        if total == 0:
            return 0.3  # Default

        # Mais positivas = maior intensidade
        ratio = sinais_positivos / total
        return min(1.0, 0.3 + ratio * 0.7)


class CalculadorNovidade:
    """
    Calcula o componente novidade da saliência.

    Novidade = quão diferente é do que já existia
    """

    def __init__(self, threshold_similaridade: float = 0.8):
        self.threshold_similaridade = threshold_similaridade

    def calcular(
        self,
        conteúdo: str,
        mempalace_search: Optional[callable] = None,
        ilhas_existentes: Optional[List[Any]] = None,
    ) -> float:
        """
        Calcular novidade de um conteúdo.

        Args:
            conteúdo: Conteúdo a avaliar
            mempalace_search: Função de busca no MemPalace
            ilhas_existentes: Lista de ilhas existentes

        Returns:
            Valor de novidade (0-1)
            1 = muito novo, 0 = já existe idêntico
        """
        if not conteúdo:
            return 0.5

        # Se não há referências, é novo
        if not mempalace_search and not ilhas_existentes:
            return 0.7  # Default alto para conteúdo novo

        # Buscar similar no MemPalace
        if mempalace_search:
            try:
                similares = mempalace_search(conteúdo, limit=3)
                if similares:
                    # Se encontrou muito similar, baixa novidade
                    melhor_score = similares[0].get("score", 0) if similares else 0
                    if melhor_score > self.threshold_similaridade:
                        return max(0.1, 1.0 - melhor_score)
            except Exception as e:
                logger.warning(f"Erro ao buscar similar no MemPalace: {e}")

        # Verificar contra ilhas existentes
        if ilhas_existentes:
            for ilha in ilhas_existentes:
                desc = ilha.descrição or ""
                nome = ilha.nome or ""
                texto = f"{nome} {desc}".lower()

                if conteúdo.lower() in texto:
                    return 0.2  # Já existe na ilha

                # Similaridade simples
                palavras_conteudo = set(conteúdo.lower().split())
                palavras_ilha = set(texto.split())
                overlap = len(palavras_conteudo & palavras_ilha)

                if overlap > 3:
                    return 0.4  # Alguma sobreposição

        return 0.7  # Default para novo conteúdo


class CalculadorRelevância:
    """
    Calcula o componente relevância da saliência.

    Relevância = conexão com ilhas existentes
    """

    def __init__(self, threshold_conexão: float = 0.6):
        self.threshold_conexão = threshold_conexão

    def calcular(
        self,
        conteúdo: str,
        ilhas: List[Any],
        embedding: Optional[List[float]] = None,
    ) -> float:
        """
        Calcular relevância baseada em conexões com ilhas.

        Args:
            conteúdo: Conteúdo a avaliar
            ilhas: Lista de ilhas existentes
            embedding: Embedding do conteúdo (opcional)

        Returns:
            Valor de relevância (0-1)
        """
        if not ilhas:
            return 0.4  # Default

        conexões = 0
        total_ilhas = len(ilhas)

        for ilha in ilhas:
            # Verificar se conteúdo se relaciona com a ilha
            texto_ilha = f"{ilha.nome or ''} {ilha.descrição or ''}".lower()

            # Palavras em comum
            palavras_conteudo = set(conteúdo.lower().split())
            palavras_ilha = set(texto_ilha.lower().split())
            overlap = len(palavras_conteudo & palavras_ilha)

            if overlap >= 3:
                conexões += 1
            elif overlap >= 1:
                conexões += 0.3

            # Score de ativação da ilha
            if hasattr(ilha, "score_ativação") and ilha.score_ativação > 0.7:
                conexões += 0.2

        # Normalizar
        if total_ilhas == 0:
            return 0.4

        relevance = min(1.0, conexões / total_ilhas)
        return relevance


def calcular_saliência_completa(
    interação: Dict[str, Any],
    ilhas: List[Any],
    mempalace_search: Optional[callable] = None,
) -> Saliencia:
    """
    Função de conveniência para calcular saliência completa.

    Args:
        interação: Dict com dados da interação
        ilhas: Lista de ilhas existentes
        mempalace_search: Função de busca no MemPalace

    Returns:
        Objeto Saliencia calculado
    """
    freq_calc = CalculadorFrequência()
    int_calc = CalculadorIntensidade()
    nov_calc = CalculadorNovidade()
    rel_calc = CalculadorRelevância()

    frequência = freq_calc.calcular(
        interação.get("interações_recentes", []),
        interação.get("conteúdo", ""),
    )

    intensidade = int_calc.calcular(
        interação.get("interações_recentes", []),
        interação.get("conteúdo", ""),
    )

    novidade = nov_calc.calcular(
        conteúdo=interação.get("conteúdo", ""),
        mempalace_search=mempalace_search,
        ilhas_existentes=ilhas,
    )

    relevância = rel_calc.calcular(
        conteúdo=interação.get("conteúdo", ""),
        ilhas=ilhas,
        embedding=interação.get("embedding"),
    )

    return Saliencia.calcular(
        frequência=frequência,
        intensidade=intensidade,
        novidade=novidade,
        relevância=relevância,
    )
