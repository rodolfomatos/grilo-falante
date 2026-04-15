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
                context_before = lines[max(0, i-2):i]
                context_after = lines[i+1:min(len(lines), i+3)]

                errors.append({
                    "id": f"error_{error_count}",
                    "description": line[:200],
                    "type": self._classify_error_type(line_lower),
                    "context": " | ".join(context_before + [f">>> {line}"] + context_after)[:500],
                })

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
                context_before = lines[max(0, i-1):i]

                corrections.append({
                    "id": f"correction_{correction_count}",
                    "formulation": line,
                    "target": self._classify_correction_target(line_lower),
                    "nature": self._classify_correction_nature(line_lower),
                    "context": " | ".join(context_before + [f">>> {line}"]),
                })

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
