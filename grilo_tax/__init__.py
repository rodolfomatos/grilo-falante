"""
Tax Intelligence Domain Adapter for Grilo Falante Platform.

This adapter provides Portuguese tax law (CIVA, CIRC, CIRS) analysis
through the Grilo Falante epistemic governance regime.

Usage:
    from grilo_tax import TaxIntelligenceAdapter
    from grilo_falante.platform import PluginRegistry

    # Register plugin
    PluginRegistry.register("tax_intelligence", TaxIntelligenceAdapter)

    # Use adapter
    adapter = PluginRegistry.get("tax_intelligence")
    result = await adapter.process_query(query="...", context={}, llm_config={})

Tax codes covered:
- CIVA: Código do IVA (VAT)
- CIRC: Código do IRC (Corporate Tax)
- CIRS: Código do IRS (Personal Tax)
"""

import logging
from typing import Any, Dict, List, Optional

from grilo_falante.platform import (
    DomainAdapter,
    DomainMetadata,
    DomainStatus,
    QueryResult,
    ValidationResult,
    LLMClient,
    get_llm_config,
)

logger = logging.getLogger(__name__)


class TaxIntelligenceAdapter(DomainAdapter):
    """
    Domain adapter for Portuguese tax law analysis.

    Provides structured tax decisions with legal basis,
    using the Grilo Falante governance regime.
    """

    TAX_CODES = ["CIVA", "CIRC", "CIRS"]

    DECISION_TYPES = [
        "deductible",
        "non_deductible",
        "partially_deductible",
        "uncertain",
    ]

    RISK_LEVELS = ["low", "medium", "high"]

    def __init__(self):
        self._metadata = DomainMetadata(
            name="tax_intelligence",
            version="1.0.0",
            description=(
                "Portuguese tax law domain adapter for CIVA, CIRC, and CIRS. "
                "Provides auditable tax decisions with legal basis and confidence scores."
            ),
            author="University of Porto",
            status=DomainStatus.ACTIVE,
            config_schema={
                "type": "object",
                "properties": {
                    "default_confidence_threshold": {"type": "number", "default": 0.5},
                    "require_legal_basis": {"type": "boolean", "default": True},
                    "max_legal_citations": {"type": "integer", "default": 5},
                },
            },
            dependencies=["grilo_falante"],
        )

    def get_metadata(self) -> DomainMetadata:
        return self._metadata

    def get_routing_config(self) -> Dict[str, List[str]]:
        """
        Return routing keywords for tax domains.

        Maps user queries to specific tax codes.
        """
        return {
            "iva": [
                "IVA", "VAT", "fatura", "faturas", "dedução", "deduções",
                "发票", "imposto sobre o valor acrescentado",
                "sujeito passivo", "exigibilidade", "taxável",
                "isento", "isenção", "regime", "liquidação",
            ],
            "irc": [
                "IRC", "corporate", "resultados", "lucros", "imposto sobre empresas",
                "rendimentos", "gastos", "dedutibilidade", "base tributável",
                "lucro tributável", "perdas", "mais-valias",
            ],
            "irs": [
                "IRS", "salários", "trabalhador", "trabalhadores", "ordenado",
                "remuneração", "retenção", "fonte", "aportador",
                "pessoal", "trabalho dependente", "trabalho independente",
            ],
            "general": [
                "imposto", "taxa", "tributação", "fiscal",
                "finanças", "autoridade tributária", " AT",
            ],
        }

    def get_prompts(self) -> Dict[str, str]:
        """
        Return prompt templates for tax analysis.
        """
        return {
            "system": """You are a tax analysis assistant specialized in Portuguese tax law.

You analyze tax operations and provide structured decisions with:
- Decision type: deductible | non_deductible | partially_deductible | uncertain
- Confidence score (0.0-1.0)
- Legal basis (code + article + excerpt)
- Risk assessment
- Required follow-up

IMPORTANT RULES:
1. ONLY answer if you can cite specific legal articles
2. If no clear legal basis, return "uncertain" with confidence < 0.5
3. NEVER hallucinate legal articles or provisions
4. Portuguese tax codes: CIVA (IVA/VAT), CIRC (IRC/Corporate Tax), CIRS (IRS/Personal Tax)
5. Always include the disclaimer at the end

Respond in Portuguese.""",

            "query": """Analise a seguinte operação fiscal:

Descrição: {query}

Código(s) fiscal(is) relevante(s): {relevant_codes}

Contexto adicional:
- Entidade: {entity_type}
- Tipo de projeto: {project_type}
- Atividade: {activity_type}
- Localização: {location}

Forneça uma análise estruturada com base legal.""",

            "escalation": """A seguinte questão fiscal requer revisão humana:

{query}

Detalles:
- Confiança: {confidence}
- Decisão: {decision}
- Base legal: {legal_basis}

Por favor, revise e valide ou corrija a análise.""",

            "validation": """Validar a seguinte claim fiscal:

Claim: {claim}
Tipo: {claim_type}
Nível GMIF: {gmif_level}

A claim está correta do ponto de vista fiscal português?
Forneça validação com base legal ou indique erros.""",
        }

    def get_escalation_triggers(self) -> List[str]:
        """
        Return keywords that trigger human escalation in tax context.
        """
        return [
            "reclamação",
            "inspeção",
            "inspeção tributária",
            "multa",
            "oculto",
            "evasão",
            "fraude",
            "fiscalização",
            "verificação",
            "procedimento",
            "autocontrolo",
            "transacção",
            "acordo",
            "litígio",
            "recurso",
            "prudente",
            "incerteza",
            "não sei",
            "não tenho a certeza",
        ]

    def detect_tax_code(self, query: str) -> List[str]:
        """
        Detect which tax codes are relevant to the query.

        Args:
            query: User's query text

        Returns:
            List of detected tax codes (CIVA, CIRC, CIRS)
        """
        query_lower = query.lower()
        detected = []

        iva_keywords = ["iva", "vat", "fatura", "dedução"]
        irc_keywords = ["irc", "corporate", "resultados", "lucros", "empresa"]
        irs_keywords = ["irs", "salário", "trabalhador", "ordenado", "pessoal"]

        if any(kw in query_lower for kw in iva_keywords):
            detected.append("CIVA")
        if any(kw in query_lower for kw in irc_keywords):
            detected.append("CIRC")
        if any(kw in query_lower for kw in irs_keywords):
            detected.append("CIRS")

        if not detected:
            detected.append("general")

        return detected

    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        llm_config: Dict[str, Any],
    ) -> QueryResult:
        """
        Process a tax law query.

        Args:
            query: User's tax question
            context: Session context (entity_type, project_type, etc.)
            llm_config: LLM provider configuration

        Returns:
            QueryResult with tax decision and metadata
        """
        should_escalate, escalation_reason = self.should_escalate(query)

        if should_escalate:
            return QueryResult(
                response=(
                    "Esta questão requer análise por um técnico qualificado. "
                    "Vou escalonar para revisão humana."
                ),
                domain=self.get_metadata().name,
                escalation_triggered=True,
                escalation_reason=escalation_reason,
                confidence=1.0,
            )

        detected_codes = self.detect_tax_code(query)

        llm_response = await self._generate_tax_analysis(
            query=query,
            context=context,
            llm_config=llm_config,
            relevant_codes=detected_codes,
        )

        gmif_level = self._classify_gmif(llm_response)

        claims_extracted = self._extract_claims(llm_response)

        return QueryResult(
            response=llm_response,
            domain=self.get_metadata().name,
            claims_extracted=claims_extracted,
            gmif_classification={"level": gmif_level},
            governance_passed=gmif_level not in ["M4", "M3"],
            sources=[f"tax_code:{code}" for code in detected_codes],
            confidence=self._extract_confidence(llm_response),
        )

    async def validate_content(self, content: Any) -> ValidationResult:
        """
        Validate tax-related content.

        Checks for:
        - Valid JSON structure (if applicable)
        - Legal article citations
        - Consistency with Portuguese tax law
        """
        errors = []
        warnings = []

        if isinstance(content, dict):
            if "legal_basis" in content:
                for basis in content["legal_basis"]:
                    if not self._validate_legal_citation(basis):
                        warnings.append(
                            f"Citação legal potencialmente inválida: {basis}"
                        )

            if "decision" in content:
                if content["decision"] not in self.DECISION_TYPES:
                    errors.append(
                        f"Tipo de decisão inválido: {content['decision']}"
                    )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _classify_gmif(self, response: str) -> str:
        """
        Classify GMIF level based on response characteristics.

        M1: Multiple independent legal sources
        M5: Single clear legal source
        M6: Derived/inferred from legal basis
        M3: Partial, incomplete legal basis
        M4: Contradictory or uncertain
        """
        response_lower = response.lower()

        has_multiple_citations = response.count("artigo") > 1
        has_legal_basis = any(
            code in response_lower for code in ["civa", "circ", "cirs", "artigo"]
        )
        has_uncertain = "incerto" in response_lower or "não sei" in response_lower
        has_contradiction = (
            "mas" in response_lower
            and ("porém" in response_lower or "no entanto" in response_lower)
        )

        if has_multiple_citations and has_legal_basis and not has_uncertain:
            return "M1"
        elif has_legal_basis and not has_uncertain and not has_contradiction:
            return "M5"
        elif has_contradiction:
            return "M4"
        elif has_uncertain:
            return "M3"
        else:
            return "M6"

    def _extract_claims(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract structured claims from tax analysis response.
        """
        claims = []

        decision_patterns = [
            "dedutível",
            "não dedutível",
            "parcialmente dedutível",
            "incerto",
        ]

        for pattern in decision_patterns:
            if pattern in response.lower():
                claims.append({
                    "type": "tax_decision",
                    "claim": pattern,
                    "confidence": self._extract_confidence(response),
                })

        return claims

    def _extract_confidence(self, response: str) -> float:
        """
        Extract confidence score from response.
        """
        import re

        match = re.search(r"confiança[:\s]*(\d+\.?\d*)", response.lower())
        if match:
            return float(match.group(1))

        match = re.search(r"(\d+\.?\d*)", response.lower())
        if match:
            value = float(match.group(1))
            if value <= 1.0:
                return value

        return 0.5

    async def _generate_tax_analysis(
        self,
        query: str,
        context: Dict[str, Any],
        llm_config: Dict[str, Any],
        relevant_codes: List[str],
    ) -> str:
        """
        Generate tax analysis using LLM.
        """
        try:
            provider = llm_config.get("provider", "bitnet")
            client = LLMClient(provider=provider)
            prompts = self.get_prompts()

            query_prompt = prompts["query"].format(
                query=query,
                relevant_codes=", ".join(relevant_codes),
                entity_type=context.get("entity_type", "universidade"),
                project_type=context.get("project_type", "geral"),
                activity_type=context.get("activity_type", "mista"),
                location=context.get("location", "Portugal"),
            )

            response = await client.generate(
                prompt=query_prompt,
                system_prompt=prompts["system"],
            )

            disclaimer = "\n\nEsta é uma avaliação automática preliminar. Valide com os serviços financeiros ou jurídicos."

            if not response.endswith(disclaimer):
                response += disclaimer

            return response

        except Exception as e:
            logger.error(f"Tax analysis error: {e}")
            return (
                "Incapaz de realizar análise fiscal automática. "
                "Por favor, consulte os serviços financeiros."
            )

    def _validate_legal_citation(self, citation: Dict[str, str]) -> bool:
        """
        Validate a legal citation structure.

        Args:
            citation: Dict with 'code' and 'article' keys

        Returns:
            True if citation appears valid
        """
        if not isinstance(citation, dict):
            return False

        code = citation.get("code", "").upper()
        article = citation.get("article", "")

        if code not in self.TAX_CODES and code != "general":
            return False

        if not article or len(article) < 3:
            return False

        return True

    def should_escalate(
        self,
        query: str,
        response: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if tax query should trigger escalation.

        Escalation triggers for tax:
        - Explicit uncertainty markers
        - High-risk keywords
        - Complex multi-code analysis
        """
        query_lower = query.lower()
        triggers = self.get_escalation_triggers()

        for trigger in triggers:
            if trigger in query_lower:
                return True, f"Trigger keyword: '{trigger}'"

        if response:
            response_lower = response.lower()
            if any(
                phrase in response_lower
                for phrase in ["não sei", "incerto", "não tenho a certeza"]
            ):
                return True, "Response indicates uncertainty"

            if "reclamação" in response_lower or "multa" in response_lower:
                return True, "High-risk keywords in response"

        detected_codes = self.detect_tax_code(query)
        if len(detected_codes) > 2:
            return True, "Multi-code analysis (requires human review)"

        return False, None


def register() -> None:
    """
    Register this plugin with the Grilo Falante platform.

    Called automatically when the package is installed via entry_points,
    or can be called manually.
    """
    from grilo_falante.platform import PluginRegistry

    PluginRegistry.register("tax_intelligence", TaxIntelligenceAdapter)
    logger.info("Registered tax_intelligence plugin")


if __name__ == "__main__":
    import asyncio

    async def test():
        print("=" * 60)
        print("Tax Intelligence Plugin - Test")
        print("=" * 60)

        register()

        from grilo_falante.platform import PluginRegistry

        print(f"\nRegistered plugins: {PluginRegistry.list_plugins()}")

        adapter = PluginRegistry.get("tax_intelligence")
        meta = adapter.get_metadata()

        print(f"\nPlugin: {meta.name} v{meta.version}")
        print(f"Description: {meta.description}")

        print(f"\nRouting config: {adapter.get_routing_config()}")
        print(f"Escalation triggers: {adapter.get_escalation_triggers()}")

        print("\n1. Testing tax code detection...")
        test_queries = [
            "Posso deduzir IVA desta fatura?",
            "Quais são os gastos dedutíveis para IRC?",
            "Como funciona a retenção na fonte de IRS?",
            "Qual é a taxa de IVA para serviços de consultoria?",
        ]

        for q in test_queries:
            codes = adapter.detect_tax_code(q)
            print(f"   '{q[:40]}...' → {codes}")

        print("\n2. Testing escalation detection...")
        escalation_queries = [
            "Tenho uma reclamação sobre uma decisão fiscal",
            "Ocorreu uma inspeção tributária",
            "Não sei se esta despesa é dedutível",
        ]

        for q in escalation_queries:
            esc, reason = adapter.should_escalate(q)
            print(f"   '{q[:40]}...' → escalate={esc}, reason={reason}")

        print("\n3. Testing GMIF classification...")
        test_responses = [
            "Com base no Artigo 23º do CIRC, esta despesa é dedutível. Confiança: 0.9",
            "Segundo o Artigo 78º do CIVA, o IVA é recuperável. Confiança: 0.85",
            "Incerto. Preciso de mais informações. Confiança: 0.3",
            "Por um lado o Artigo 20º diz que é dedutível, mas o Artigo 21º indica o contrário. Confiança: 0.4",
        ]

        for r in test_responses:
            gmif = adapter._classify_gmif(r)
            print(f"   GMIF={gmif}: {r[:50]}...")

        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)

    asyncio.run(test())
