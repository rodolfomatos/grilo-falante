"""
Shadow Document Generator — Generates epistemological shadow documents

S(D) = {x | x é assumido, imposto ou produzido por D, mesmo que não seja afirmar em D}

Based on Grilo Falante canonical definitions.

Canonical question: "O que tens de aceitar para que este documento
seja válido nos seus próprios termos?"
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from grilo_falante.models.shadow import ShadowDocument, EpistemicUnit
from grilo_falante.backend.services.llm import LLMMessage, get_llm_service


@dataclass
class GenerationResult:
    success: bool
    shadow_document: Optional[ShadowDocument] = None
    error: Optional[str] = None


class ShadowDocumentGenerator:
    """
    Generates shadow documents for sources using LLM analysis.

    The shadow document exposes what a document already assumes,
    imposes, or produces, but does not formally declare.
    """

    CANONICAL_QUESTION = (
        "O que tens de aceitar para que este documento "
        "seja válido nos seus próprios termos?"
    )

    WHAT_IT_IS = [
        "Instrumento de auditoria epistemológica",
        "Declaração de custos cognitivos inevitáveis",
        "Mapa de compromissos não negociáveis",
        "Operador de honestidade estrutural",
    ]

    WHAT_IT_IS_NOT = [
        "Crítica externa",
        "Contra-argumento",
        "Interpretação livre",
        "Intenção do autor",
        "Avaliação moral ou política",
    ]

    TRAHO_T1 = (
        "O Documento Sombra governa o uso legítimo do documento principal. "
        "Ao tornar explícitas as condições já pressupostas, altera explicitamente: "
        "o que pode ser promovido, reutilizado, ensinado, ou tratado como neutro."
    )

    TRAHO_T2 = (
        "As consequências referem-se exclusivamente a efeitos internos ao "
        "funcionamento lógico do documento. Estão excluídas: avaliações éticas, "
        "juízos políticos, críticas pragmáticas, intenções atribuídas ao autor."
    )

    GOLDEN_RULE = (
        "Se alguém rejeita o Documento Sombra mas aceita o documento principal, "
        "então não compreendeu o documento principal. "
        "Isto não é retórico — é diagnóstico epistemológico."
    )

    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = get_llm_service(llm_provider)

    async def generate(
        self,
        source_title: str,
        source_content: str,
        source_authors: Optional[List[str]] = None,
        source_type: str = "document",
    ) -> GenerationResult:
        """
        Generate a shadow document for a source.

        Args:
            source_title: Title of the source document
            source_content: Full text content
            source_authors: List of authors
            source_type: Type of source (paper, article, etc.)

        Returns:
            GenerationResult with shadow_document or error
        """
        try:
            analysis_prompt = self._build_analysis_prompt(
                source_title, source_content
            )

            messages = [
                LLMMessage(
                    role="system",
                    content=self._get_system_prompt()
                ),
                LLMMessage(
                    role="user",
                    content=analysis_prompt
                ),
            ]

            response = await self.llm.chat(messages)

            shadow_doc = self._parse_llm_response(
                response.content,
                source_title,
                source_authors or [],
                source_type,
            )

            return GenerationResult(
                success=True,
                shadow_document=shadow_doc,
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e),
            )

    def _get_system_prompt(self) -> str:
        return f"""És um auditor epistemológico do regime Grilo Falante.

A tua tarefa é gerar um Documento Sombra para um documento principal.

O Documento Sombra S(D) define-se como:
S(D) = {{x | x é assumido, imposto ou produzido por D, mesmo que não seja afirmar em D}}

REGRAS FUNDAMENTAIS:

1. NÃO acrescentes novas teses
2. NÃO corrijas o documento principal
3. NÃO o resumas
4. Expões o seu lado estrutural invisível

PERGUNTA CANÓNICA:
{self.CANONICAL_QUESTION}

O QUE É:
{chr(10).join(f"- {w}" for w in self.WHAT_IT_IS)}

O QUE NÃO É:
{chr(10).join(f"- {w} (NÃO é)" for w in self.WHAT_IT_IS_NOT)}

TRAHO T1 - Efeito Normativo Explícito:
{self.TRAHO_T1}

TRAHO T2 - Limitação das Consequências:
{self.TRAHO_T2}

REGRA DE OURO:
{self.GOLDEN_RULE}

Responde em JSON com a estrutura especificada."""

    def _build_analysis_prompt(
        self,
        title: str,
        content: str,
    ) -> str:
        return f"""Gera o Documento Sombra para o seguinte documento:

TÍTULO: {title}

CONTEÚDO (primeiros 8000 caracteres):
{content[:8000]}

Formato JSON de resposta:
{{
    "title": "Documento Sombra: {title}",
    "evidence_level": "complete|conditioned|weak|doubtful",
    "scope": "O que o documento realmente faz",
    "limits": ["limit1", "limit2", "limit3"],
    "f1_claims": ["claim1 from what author explicitly states", "claim2"],
    "f2_claims": ["inference1 commonly made but not explicitly claimed", "inference2"],
    "assumptions": ["assumption1", "assumption2"],
    "commitments": ["commitment1", "commitment2"],
    "structural_limits": ["limit1", "limit2"],
    "misuse_risks": ["risk1", "risk2"],
    "normative_effect": "O que este documento governa legitimamente",
    "consequence_limitations": ["exclusion1", "exclusion2"],
    "epistemic_synthesis": "demonstrates|suggests|does_not_support",
    "uncertainty_zones": ["zone1", "zone2"],
    "honesty_note": "Nota final de honestidade epistemológica"
}}"""

    def _parse_llm_response(
        self,
        content: str,
        title: str,
        authors: List[str],
        source_type: str,
    ) -> ShadowDocument:
        """Parse LLM response into ShadowDocument."""
        import json
        import re

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                except Exception:
                    data = {}
            else:
                data = {}

        f1_claims = data.get("f1_claims", [])
        f2_claims = data.get("f2_claims", [])

        epistemic_units = []
        for i, claim in enumerate(f1_claims):
            epistemic_units.append(EpistemicUnit(
                id=f"f1_{i}",
                type="explicit",
                content=claim,
                gmif_level="M1" if i == 0 else "M2",
                f1_or_f2="f1",
            ))

        for i, claim in enumerate(f2_claims):
            epistemic_units.append(EpistemicUnit(
                id=f"f2_{i}",
                type="implicit",
                content=claim,
                gmif_level="M4",
                f1_or_f2="f2",
            ))

        shadow = ShadowDocument(
            title=f"Documento Sombra: {title}",
            authors=authors,
            source_type=source_type,
            evidence_level=data.get("evidence_level", "weak"),
            scope=data.get("scope", ""),
            limits=data.get("limits", []),
            epistemic_units=epistemic_units,
            f1_count=len(f1_claims),
            f2_count=len(f2_claims),
            assumptions=data.get("assumptions", []),
            commitments=data.get("commitments", []),
            structural_limits=data.get("structural_limits", []),
            misuse_risks=data.get("misuse_risks", []),
            normative_effect=data.get("normative_effect", ""),
            consequence_limitations=data.get("consequence_limitations", []),
            epistemic_synthesis=data.get("epistemic_synthesis", ""),
            uncertainty_zones=data.get("uncertainty_zones", []),
            honesty_note=data.get("honesty_note", ""),
            status="completed",
        )

        return shadow

    def generate_markdown(self, shadow: ShadowDocument) -> str:
        """
        Generate a human-readable markdown version of the shadow document.
        """
        lines = [
            f"# {shadow.title}",
            "",
            f"**Estatuto:** Documento Sombra (normativo-epistemológico)",
            f"**Evidence Level:** {shadow.evidence_level.upper()}",
            f"**Status:** {shadow.status}",
            "",
            "---",
            "",
        ]

        if shadow.authors:
            lines.append(f"**Autores:** {', '.join(shadow.authors)}")
            lines.append("")

        lines.extend([
            "## 1. Objeto analisado",
            "",
            f"- **Objeto:** {shadow.title}",
            f"- **Domínio:** {shadow.source_type}",
            f"- **Função:** Fixar análise epistemológica canónica",
            "",
            "---",
            "",
            "## 2. Definição base",
            "",
            "Um **Documento Sombra** é um artefacto normativo-analítico cuja função é",
            "tornar explícito aquilo que um documento já assume, impõe ou produz, mas não declara formalmente.",
            "",
            "**Pergunta canónica:**",
            "",
            f"> {self.CANONICAL_QUESTION}",
            "",
            "---",
            "",
            "## 3. Evidência e Scope",
            "",
            f"**Nível de evidência:** {shadow.evidence_level}",
            f"**Scope:** {shadow.scope}",
            "",
        ])

        if shadow.limits:
            lines.extend([
                "### Limites identificados",
                "",
            ])
            for limit in shadow.limits:
                lines.append(f"- {limit}")
            lines.append("")

        if shadow.f1_claims or shadow.f2_claims:
            lines.extend([
                "---",
                "",
                "## 4. Decomposição em Unidades Epistémicas",
                "",
                "### F1 - Afirmações Explícitas (o autor declara)",
                "",
            ])
            for i, claim in enumerate(shadow.f1_claims if hasattr(shadow, 'f1_claims') else []):
                lines.append(f"{i+1}. {claim}")
            lines.append("")

            lines.extend([
                "### F2 - Projeções Implícitas (leitores inferem, autor não declarou)",
                "",
            ])
            for i, claim in enumerate(shadow.f2_claims if hasattr(shadow, 'f2_claims') else []):
                lines.append(f"{i+1}. {claim}")
            lines.append("")

        if shadow.assumptions:
            lines.extend([
                "---",
                "",
                "## 5. Pressupostos",
                "",
            ])
            for assumption in shadow.assumptions:
                lines.append(f"- {assumption}")
            lines.append("")

        if shadow.commitments:
            lines.extend([
                "## 6. Compromissos",
                "",
            ])
            for commitment in shadow.commitments:
                lines.append(f"- {commitment}")
            lines.append("")

        if shadow.normative_effect:
            lines.extend([
                "---",
                "",
                "## 7. Travão T1 - Efeito Normativo Explícito",
                "",
                f"{shadow.normative_effect}",
                "",
            ])

        if shadow.consequence_limitations:
            lines.extend([
                "## 8. Travão T2 - Limitação das Consequências",
                "",
                "Estão explicitamente excluídas:",
                "",
            ])
            for limitation in shadow.consequence_limitations:
                lines.append(f"- {limitation}")
            lines.append("")

        if shadow.misuse_risks:
            lines.extend([
                "---",
                "",
                "## 9. Riscos de Mau Uso",
                "",
            ])
            for risk in shadow.misuse_risks:
                lines.append(f"- {risk}")
            lines.append("")

        if shadow.uncertainty_zones:
            lines.extend([
                "---",
                "",
                "## 10. Zonas de Incerteza",
                "",
            ])
            for zone in shadow.uncertainty_zones:
                lines.append(f"- {zone}")
            lines.append("")

        if shadow.epistemic_synthesis:
            lines.extend([
                "---",
                "",
                "## 11. Síntese Epistémica",
                "",
                f"**Conclusão:** {shadow.epistemic_synthesis.upper()}",
                "",
            ])

        lines.extend([
            "---",
            "",
            "## Regra de Ouro",
            "",
            f"> {self.GOLDEN_RULE}",
            "",
            "---",
            "",
            f"**Nota de honestidade epistemológica:**",
            f"{shadow.honesty_note or 'O presente documento expõe o lado estrutural invisível do documento analisado.'}",
            "",
            "---",
            "",
            "*Documento Sombra gerado pelo regime Grilo Falante v3.0*",
        ])

        return "\n".join(lines)
