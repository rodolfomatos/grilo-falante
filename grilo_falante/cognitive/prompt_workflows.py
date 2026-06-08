"""
Prompt Workflows — TRIAGEM and RADIOGRAFIA

Based on Grilo Falante canonical prompts from /prompts/
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class PromptPhase(str, Enum):
    FASE_0_STATUTE = "fase_0_statute"
    FASE_A_THEMATIC = "fase_a_thematic"
    FASE_B_IDEA = "fase_b_idea"
    FASE_C_GATE = "fase_c_gate"
    FASE_D_EXCERPT = "fase_d_excerpt"
    FASE_E_SHADOW = "fase_e_shadow"


class PromptType(str, Enum):
    TRIAGEM = "triagem"
    RADIOGRAFIA = "radiografia"
    AUDITORIA_HOSTIL = "auditoria_hostil"
    AUTOPSIA_LITERATURA = "autopsia_literatura"


@dataclass
class TriagemResult:
    """Result of TRIAGEM_E_PRESERVACAO workflow."""

    themes: List[Dict[str, str]]
    ideas: List[Dict[str, str]]
    selected_ideas: List[str]
    excerpts: Dict[str, str]
    shadow_documents: Dict[str, str]


@dataclass
class RadiografiaResult:
    """Result of RADIOGRAFIA workflow."""

    errors: List[Dict[str, str]]
    corrections: List[Dict[str, str]]
    gray_zones: List[str]


@dataclass
class AuditoriaHostilResult:
    """Result of AUDITORIA_HOSTIL_CANONICO workflow."""

    fase_1_materializacao: Dict[str, Any]
    fase_2_auditoria: Dict[str, Any]
    fase_3_feynman: List[Dict[str, str]]
    output_minimo: Dict[str, Any]


@dataclass
class AutopsiaLiteraturaResult:
    """Result of AUTOPSIA_LITERATURA workflow."""

    fase_1_estrutural: Dict[str, Any]
    fase_2_fontes: List[Dict[str, Any]]
    fase_3_teorica: Dict[str, Any]
    fase_4_inferencial: List[Dict[str, str]]
    fase_5_factual: List[Dict[str, str]]
    fase_6_diagnostico: Dict[str, Any]


class PromptWorkflows:
    """
    Prompt workflows based on Grilo Falante canonical definitions.

    TRIAGEM_E_PRESERVACAO: Structured, auditable triage of conversations
    RADIOGRAFIA: Factual diagnostic extraction of errors
    """

    STATUTE_DECLARATION = """ESTATUTO: Ficheiro de arquivo bruto. Nenhum conteúdo tem estatuto por defeito.

Este ficheiro contém uma conversa ou registo de interação. O seu conteúdo:
- NÃO é válido por defeito
- NÃO constitui evidência
- NÃO representa o estado do sistema

Antes de qualquer uso, requer triagem explícita."""

    TRIAGEM_PROHIBITIONS = [
        "Nunca criar documentos sem excerpt literal colado",
        "Nunca resumir ou reinterpretar o excerpt",
        "Nunca promover ideias a capsules, normas ou decisões",
        "Nunca assumir continuidade entre ficheiros/chats",
    ]

    RADIOGRAFIA_PROHIBITIONS = [
        "Não criar documentos normativos",
        "Não aplicar correções",
        "Não sugerir soluções",
        "Não decidir ações",
        "Não assumir continuidade entre chats",
    ]

    def triagem_workflow(self, conversation_content: str) -> Dict[str, Any]:
        """
        Execute TRIAGEM_E_PRESERVACAO workflow.

        Phases:
        FASE 0: Statute declaration
        FASE A: Thematic index
        FASE B: Idea survey
        FASE C: Human decision gate (STOP)
        FASE D: Literal excerpt reception
        FASE E: Shadow document (optional)
        """
        return {
            "statute": self.STATUTE_DECLARATION,
            "fase_a_thematic_index": self._triagem_fase_a(conversation_content),
            "fase_b_idea_survey": self._triagem_fase_b(conversation_content),
            "fase_c_gate": {
                "action": "STOP",
                "instruction": "Parar aqui. Perguntar ao utilizador quais as ideias a preservar.",
                "prohibitions": self.TRIAGEM_PROHIBITIONS,
            },
            "fase_d_excerpt": {
                "instruction": "Apenas se utilizador selecionar ideia(s), solicitar excerpt literal",
            },
        }

    def _triagem_fase_a(self, content: str) -> List[Dict[str, str]]:
        """FASE A: Thematic index - map distinct themes."""
        themes = []
        lines = content.split("\n")

        current_theme = None
        theme_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                if current_theme:
                    themes.append(current_theme)
                theme_count += 1
                current_theme = {
                    "id": f"theme_{theme_count}",
                    "title": line.lstrip("#").strip(),
                    "description": "",
                    "status": "exploratory",
                }
            elif current_theme:
                if current_theme["description"]:
                    current_theme["description"] += " " + line[:100]
                else:
                    current_theme["description"] = line[:100]

        if current_theme:
            themes.append(current_theme)

        return themes

    def _triagem_fase_b(self, content: str) -> List[Dict[str, str]]:
        """FASE B: Idea survey - identify conceptual ideas."""
        ideas = []
        lines = content.split("\n")

        idea_count = 0
        current_idea = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if any(indicator in line.lower() for indicator in ["idea:", "conceito:", "proposta:"]):
                if current_idea:
                    ideas.append(current_idea)
                idea_count += 1
                current_idea = {
                    "id": f"idea_{idea_count}",
                    "label": line,
                    "description": "",
                    "implicit_status": "exploratory",
                }
            elif current_idea:
                if current_idea["description"]:
                    current_idea["description"] += " " + line[:100]
                else:
                    current_idea["description"] = line[:100]

        if current_idea:
            ideas.append(current_idea)

        return ideas

    def radiografia_workflow(self, conversation_content: str) -> Dict[str, Any]:
        """
        Execute RADIOGRAFIA_ERROS workflow.

        FASE 0: Statute declaration
        FASE A: Error/incident identification
        FASE B: Correction request identification
        FASE C: Explicit separation (three sections)
        """
        return {
            "statute": "ESTATUTO: Registo factual de interação. Sem valor normativo.",
            "fase_a_errors": self._radiografia_fase_a(conversation_content),
            "fase_b_corrections": self._radiografia_fase_b(conversation_content),
            "fase_c_separation": {
                "instruction": "Produzir TRÊS secções claramente separadas:",
                "section_1": "Erros/Incidentes identificados",
                "section_2": "Pedidos de correção identificados",
                "section_3": "Zonas cinzentas/ambíguas",
            },
            "prohibitions": self.RADIOGRAFIA_PROHIBITIONS,
        }

    def _radiografia_fase_a(self, content: str) -> List[Dict[str, str]]:
        """FASE A: Identify errors and incidents."""
        errors = []
        lines = content.split("\n")

        error_markers = ["erro", "error", "fail", "falha", "incidente", "violação"]
        error_count = 0

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(marker in line_lower for marker in error_markers):
                error_count += 1
                context_before = lines[max(0, i - 2) : i]
                context_after = lines[i + 1 : min(len(lines), i + 3)]

                errors.append(
                    {
                        "id": f"error_{error_count}",
                        "description": line[:200],
                        "type": self._classify_error_type(line_lower),
                        "context": " | ".join(context_before + [f">>> {line}"] + context_after)[
                            :500
                        ],
                    }
                )

        return errors

    def _radiografia_fase_b(self, content: str) -> List[Dict[str, str]]:
        """FASE B: Identify correction requests."""
        corrections = []
        lines = content.split("\n")

        correction_markers = ["corrigir", "correct", "alterar", "change", "modificar", "please"]
        correction_count = 0

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(marker in line_lower for marker in correction_markers):
                correction_count += 1
                context_before = lines[max(0, i - 1) : i]

                corrections.append(
                    {
                        "id": f"correction_{correction_count}",
                        "formulation": line,
                        "target": self._classify_correction_target(line_lower),
                        "nature": self._classify_correction_nature(line_lower),
                        "context": " | ".join(context_before + [f">>> {line}"]),
                    }
                )

        return corrections

    def _classify_error_type(self, text: str) -> str:
        """Classify error type."""
        if any(w in text for w in ["técnico", "technical", "bug", "crash"]):
            return "technical_error"
        elif any(w in text for w in ["procedimental", "procedural", "violação", "violation"]):
            return "procedural_error"
        elif any(w in text for w in ["cognitivo", "cognitive", "falha", "omission"]):
            return "cognitive_failure"
        elif any(w in text for w in ["documento", "documentary", "inconsistency"]):
            return "documentary_inconsistency"
        elif any(w in text for w in ["comportamento", "behavior", "undesired"]):
            return "undesired_behavior"
        return "unknown"

    def _classify_correction_target(self, text: str) -> str:
        """Classify correction target."""
        if "prompt" in text:
            return "prompt"
        elif "installer" in text:
            return "installer"
        elif "validation" in text:
            return "validation"
        elif "comportamento" in text or "behavior" in text:
            return "behavior"
        return "unknown"

    def _classify_correction_nature(self, text: str) -> str:
        """Classify correction nature."""
        if "corrigir" in text or "correct" in text:
            return "correction"
        elif "reforçar" in text or "reinforce" in text:
            return "reinforcement"
        elif "bloquear" in text or "block" in text:
            return "blocking"
        elif "clarificar" in text or "clarify" in text:
            return "clarification"
        return "unknown"

    def auditoria_hostil_workflow(self, content: str) -> Dict[str, Any]:
        """
        Execute AUDITORIA_HOSTIL_CANONICO workflow.

        FASE 1: Integration and materialization
        FASE 2: Hostile audit (5 axes)
        FASE 3: Feynman audit
        """
        return {
            "statute": "Template operativo fixo. Reutilizável.",
            "modos_cognitivos": ["MPG", "D"],
            "hierarquia": "D > MPG",
            "fase_1_materializacao": {
                "instruction": "Identificar todos os documentos, pipelines, esquemas ou propostas",
                "action": "Materializar no canvas versões integradas, documentos novos, patches",
                "prohibitions": ["Não assumir continuidade implícita"],
                "resultado_esperado": "Conjunto fechado e rastreável de artefactos",
            },
            "fase_2_auditoria": {
                "instruction": "Auditoria hostil completa sem suavização retórica",
                "axes": {
                    "A_completude_estrutural": [
                        "Existem fases em falta?",
                        "Existem pré-condições não explicitadas?",
                        "Existe fecho de ciclo?",
                    ],
                    "B_correcao_categorial": [
                        "Exploração vs decisão vs promoção estão separadas?",
                        "Existe autoridade implícita indevida?",
                    ],
                    "C_coerencia_temporal": [
                        "O sistema degrada com o tempo?",
                        "Existem pontos de esquecimento estrutural?",
                    ],
                    "D_escalabilidade_cognitiva": [
                        "O volume cresce de forma controlada?",
                        "O modelo depende da conversa?",
                    ],
                },
            },
            "fase_3_feynman": {
                "instruction": "Reexplicar cada fase como se ensinado a terceiro externo",
                "action": "Usar reexplicação para identificar lacunas, ambiguidades ou saltos lógicos",
            },
            "regras_duras": [
                "Não suavizar críticas",
                "Não omitir falhas por cortesia",
                "Cada falha identificada deve ter proposta concreta de correção",
                "Todas as conclusões relevantes devem ser materializadas no canvas",
            ],
            "output_minimo": [
                "O que está correto e sólido",
                "O que está incompleto, errado ou perigoso",
                "Patch mínimo necessário para tornar o sistema robusto",
            ],
        }

    def autopsia_literatura_workflow(self, content: str) -> Dict[str, Any]:
        """
        Execute AUTOPSIA_LITERATURA workflow.

        FASE 1: Structural mapping
        FASE 2: Source and fidelity audit
        FASE 3: Theoretical robustness
        FASE 4: Inferential audit
        FASE 5: Factual accuracy
        FASE 6: Global diagnosis
        """
        return {
            "statute": "Análise factual de revisão de literatura. Sem valor normativo.",
            "fase_1_estrutural": {
                "instruction": "Extrair teses centrais (explícitas e implícitas), sub-teses, encadeamento lógico",
                "prohibitions": ["Não avaliativo nesta fase"],
            },
            "fase_2_fontes": {
                "instruction": "Para cada afirmação que invoque literatura",
                "source_classification": ["descritivo", "inferencial", "normativo", "retórico"],
                "checks": [
                    "Afirmação explicitamente suportada pela fonte citada?",
                    "Overclaiming (conclusões além do que a fonte permite)?",
                    "Under-specification (fonte citada mas papel ambíguo)?",
                ],
                "markers": [
                    "citações frágeis",
                    "citações decorativas",
                    "dependência excessiva de autoridade",
                ],
            },
            "fase_3_teorica": {
                "instruction": "Avaliar compatibilidade entre quadros teóricos",
                "frameworks": [
                    "educação inclusiva",
                    "sociocultural theory",
                    "SLA",
                    "psicologia cognitiva",
                    "UDL",
                ],
                "identifications": [
                    "Tensões não resolvidas",
                    "Compatibilizações implícitas não justificadas",
                    "Zonas de ecletismo teórico não controlado",
                ],
                "distinctions": [
                    "Convergência legítima",
                    "Justaposição pragmática",
                    "Incoerência conceptual",
                ],
            },
            "fase_4_inferencial": {
                "instruction": "Identificar saltos inferenciais, pressupostos não declarados, circularidades",
                "checks": [
                    "Conclusões intermédias decorrem das premissas?",
                    "Capítulo faz trabalho teórico real ou apenas acumulação de referências?",
                ],
            },
            "fase_5_factual": {
                "instruction": "Verificar precisão conceptual e factual",
                "checks": [
                    "Conceitos usados de forma imprecisa?",
                    "Termos polissémicos não estabilizados?",
                    "Usos anacrónicos ou diluídos de conceitos técnicos?",
                ],
            },
            "fase_6_diagnostico": {
                "instruction": "Produzir veredicto epistémico global",
                "output": [
                    "Pontos de elevada solidez",
                    "Zonas estruturalmente frágeis",
                    "Riscos sérios para defesa académica",
                    "Afirmações que resistem a escrutínio",
                    "Afirmações que exigem defesa oral cuidadosa",
                    "Afirmações que deveriam ser reformuladas ou recuadas",
                ],
            },
            "regras_duras": [
                "Não reescrever o texto",
                "Não melhorar estilo",
                "Não suavizar críticas",
                "Não introduzir novas fontes",
                "Não assumir intenções do autor",
                "Distiguir sempre descrição, avaliação e inferência",
            ],
        }
