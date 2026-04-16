"""
Student Support Domain Adapter for Grilo Falante Platform.

This adapter provides 24×7 support for students and applicants
covering Academic Services, SASUP, and IT support topics.

Usage:
    from grilo_student import StudentSupportAdapter
    from grilo_falante.platform import PluginRegistry

    # Register plugin
    PluginRegistry.register("student_support", StudentSupportAdapter)

    # Use adapter
    adapter = PluginRegistry.get("student_support")
    result = await adapter.process_query(query="...", context={}, llm_config={})

Departments:
- Academic: Enrollments, grades, courses, professors
- SASUP: Scholarships, housing, canteen, health
- IT: WiFi, password, email, software
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
)

logger = logging.getLogger(__name__)


class StudentSupportAdapter(DomainAdapter):
    """
    Domain adapter for student support services.

    Routes queries to appropriate department and provides
    answers from FAQ knowledge base or LLM generation.
    """

    FAQ_KNOWLEDGE_BASE = {
        "academic": {
            "matrícula": "A matrícula pode ser realizada online através do portal académico. O prazo normal é de 15 de setembro a 15 de outubro para o ano letivo regular.",
            "notas": "As notas são publicadas no portal académico até 30 dias após a realização da avaliação. Pode consultar as suas notas em: Portal > Área Pessoal > Histórico Académico.",
            "curso": "Para informações sobre um curso específico, consulte o site da faculdade ou contacte a секретаría académica.",
            "professor": "Os horários de atendimento dos professores estão disponíveis nas respetivas páginas web e no portal académico.",
            "reingresso": "O reingresso é permitido a qualquer momento do ano letivo, mediante análise do processo académico.",
            "transferência": "A transferência entre cursos ou instituições está sujeita a condições específicas. Consulte o regulamento académico.",
        },
        "sasup": {
            "bolsa": "As bolsas de estudo são atribuídas pela Direção-Geral do Ensino Superior (DGES). O prazo de candidatura é geralmente em setembro. Consulte: www.dges.gov.pt",
            "dormitório": "O dormitório estudantil tem capacidade para 200 estudantes. As candidaturas são abertas em julho. Contacte: sasup@universidade.pt",
            "refeitório": "O refeitório funciona das 7h30 às 21h. A refeição completa custa €2.50 para estudantes bolseiros.",
            "saúde": "O SASUP disponibiliza consultas de medicina geral às terças e quintas. Marque através do portal SASUP.",
            "psicologia": "O serviço de psicologia está disponível para estudantes com marcação prévia. Contacte: psicologia@sasup.pt",
            "cartão": "O cartão de estudante é emitido pela Secretaria. Prazo: 5 dias úteis após a inscrição.",
        },
        "it": {
            "wifi": "Rede WiFi: 'Eduroam' para toda a comunidade académica. Credenciais: email institucional e password. Problemas? Contacte: ti@universidade.pt",
            "password": "Para resetar a password, vá ao portal IT com cartão de cidadão ou contacte o helpdesk ext. 1234.",
            "email": "O email institucional é atribuido após a matrícula. Acesso em: webmail.universidade.pt",
            "software": "O Microsoft Office 365 está disponível gratuitamente para estudantes. Downloads em: portal.it/software",
            "vpn": "Para acesso remoto aos recursos da universidade, configure VPN com as instruções em: portal.it/vpn",
            "impressora": "As impressoras estão disponíveis na biblioteca e no edifício de serviços. Custo: €0.05/página.",
        },
    }

    def __init__(self):
        self._metadata = DomainMetadata(
            name="student_support",
            version="1.0.0",
            description=(
                "Student support services adapter for academic services, "
                "SASUP (scholarships, housing, health) and IT support. "
                "Provides 24×7 automated assistance for students."
            ),
            author="University of Porto",
            status=DomainStatus.ACTIVE,
            config_schema={
                "type": "object",
                "properties": {
                    "default_department": {"type": "string", "default": "academic"},
                    "enable_escalation": {"type": "boolean", "default": True},
                    "faq_confidence": {"type": "number", "default": 1.0},
                },
            },
            dependencies=["grilo_falante"],
        )

    def get_metadata(self) -> DomainMetadata:
        return self._metadata

    def get_routing_config(self) -> Dict[str, List[str]]:
        """
        Return routing keywords for student service departments.
        """
        return {
            "academic": [
                "matrícula", "notas", "curso", "professor", "turma",
                "avaliação", "exame", "época", "reingresso", "transferência",
                "university", "faculdade", "licenciatura", "mestrado", "doutoramento",
                "secretaria", "propina", "propinas", "ECTS", "plano curricular",
                "cadeiras", "inscrição", "inscrições", "horário", "aula",
            ],
            "sasup": [
                "bolsa", "bolsas", "dormitório", "residência", "refeitório",
                "cantina", "saúde", "psicologia", "cartão", "identificação",
                "social", "apoio", "subsídio", "comparticipação", "medicina",
                "enfermaria", "seguro", "acidente", "SASUP",
            ],
            "it": [
                "wifi", "wi-fi", "password", "palavra-passe", "email", "correio",
                "software", "computador", "pc", "impressora", "impressão",
                "VPN", "acesso remoto", "conta", "login", "autenticação",
                "TI", "tecnologia", "informática", "helpdesk", "suporte",
                "Teams", "Zoom", "Moodle", "plataforma", "portal",
            ],
        }

    def get_prompts(self) -> Dict[str, str]:
        """
        Return prompt templates for student support.
        """
        return {
            "system": """You are a helpful student support assistant for a university.

You provide information about:
- Academic services (enrollments, grades, courses, professors)
- SASUP services (scholarships, housing, canteen, health)
- IT support (WiFi, password, email, software)

Be friendly, helpful, and concise. Direct students to the right resources.
If you don't know something, say so and suggest who to contact.""",

            "academic": """You are an academic services assistant.

Answer questions about:
- Enrollments and registrations
- Grades and academic records
- Course information
- Professors and schedules

Be precise and refer to official sources when available.""",

            "sasup": """You are a SASUP (Social Services) assistant.

Answer questions about:
- Scholarships and financial aid
- Student housing and dining
- Health and psychological services
- Student cards and ID

Show empathy and provide practical information.""",

            "it": """You are an IT support assistant.

Answer questions about:
- WiFi and network access
- Email and password reset
- Software and licenses
- VPN and remote access

Be technical but accessible.""",

            "escalation": """A student support case requires human attention:

Department: {department}
Question: {query}
Automated response: {response}

Please follow up with the student.""",
        }

    def get_escalation_triggers(self) -> List[str]:
        """
        Return keywords that trigger human escalation.
        """
        return [
            "problema não resolvido",
            "não consegui",
            "urgente",
            "muito importante",
            "reclamação",
            "erro grave",
            "conta bloqueada",
            "pagamento",
            "financeiro",
            "bolsa não recebida",
            "situação social",
            "acompanhamento",
            "psicológico",
            "emergência",
        ]

    def get_department_for_query(self, query: str) -> Optional[str]:
        """
        Determine which department this query belongs to.
        """
        query_lower = query.lower()
        routing_config = self.get_routing_config()

        department_scores: Dict[str, int] = {
            "academic": 0,
            "sasup": 0,
            "it": 0,
        }

        for department, keywords in routing_config.items():
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    department_scores[department] += 1

        max_score = max(department_scores.values())
        if max_score == 0:
            return None

        for dept, score in department_scores.items():
            if score == max_score:
                return dept

        return None

    def should_escalate(
        self,
        query: str,
        response: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if query should trigger escalation.
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
                for phrase in ["não sei", "não tenho a certeza", "informação não disponível"]
            ):
                return True, "Response indicates lack of information"

            if len(response) > 1000 and len(query) < 50:
                return True, "Complex response for simple query (possible confusion)"

        return False, None

    def _find_faq_match(self, query: str) -> Optional[tuple[str, str]]:
        """
        Find a matching FAQ entry for the query.
        """
        query_lower = query.lower()
        best_match = None
        best_score = 0

        for dept, faqs in self.FAQ_KNOWLEDGE_BASE.items():
            for keyword, answer in faqs.items():
                if keyword.lower() in query_lower:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = (dept, answer)

        return best_match

    async def process_query(
        self,
        query: str,
        context: Dict[str, Any],
        llm_config: Dict[str, Any],
    ) -> QueryResult:
        """
        Process a student support query.
        """
        department = self.get_department_for_query(query)

        faq_match = self._find_faq_match(query)

        if faq_match:
            dept, response = faq_match
            return QueryResult(
                response=response,
                domain=self.get_metadata().name,
                sources=["faq_knowledge_base"],
                confidence=1.0,
                metadata={"department": dept, "source": "faq"},
            )

        should_esc, esc_reason = self.should_escalate(query)
        if should_esc:
            return QueryResult(
                response=(
                    "Obrigado pelo seu contacto. Esta questão requer "
                    "atenção personalizada. Vou encaminhá-la para um "
                    "operador que lhe poderá ajudar melhor."
                ),
                domain=self.get_metadata().name,
                escalation_triggered=True,
                escalation_reason=esc_reason,
                confidence=1.0,
            )

        llm_response = await self._generate_response(
            query=query,
            department=department,
            context=context,
            llm_config=llm_config,
        )

        should_esc, esc_reason = self.should_escalate(query, llm_response)
        if should_esc:
            return QueryResult(
                response=llm_response,
                domain=self.get_metadata().name,
                escalation_triggered=True,
                escalation_reason=esc_reason,
                confidence=0.7,
                metadata={"department": department or "general"},
            )

        return QueryResult(
            response=llm_response,
            domain=self.get_metadata().name,
            confidence=0.7,
            metadata={"department": department or "general"},
        )

    async def validate_content(self, content: Any) -> ValidationResult:
        """
        Validate content - basic check for now.
        """
        if isinstance(content, str):
            if len(content) < 5:
                return ValidationResult(
                    is_valid=False,
                    errors=["Content too short"],
                )

        return ValidationResult(is_valid=True)

    async def _generate_response(
        self,
        query: str,
        department: Optional[str],
        context: Dict[str, Any],
        llm_config: Dict[str, Any],
    ) -> str:
        """
        Generate response using LLM.
        """
        try:
            provider = llm_config.get("provider", "bitnet")
            client = LLMClient(provider=provider)
            prompts = self.get_prompts()

            system_prompt = prompts["system"]
            if department and department in ["academic", "sasup", "it"]:
                system_prompt = prompts.get(department, prompts["system"])

            response = await client.generate(
                prompt=query,
                system_prompt=system_prompt,
            )

            return response

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return (
                "Lamentamos, mas não foi possível gerar uma resposta automática. "
                "Por favor, contacte-nos por outros canais ou tente novamente mais tarde."
            )


def register() -> None:
    """
    Register this plugin with the Grilo Falante platform.
    """
    from grilo_falante.platform import PluginRegistry

    PluginRegistry.register("student_support", StudentSupportAdapter)
    logger.info("Registered student_support plugin")


if __name__ == "__main__":
    import asyncio

    async def test():
        print("=" * 60)
        print("Student Support Plugin - Test")
        print("=" * 60)

        register()

        from grilo_falante.platform import PluginRegistry

        print(f"\nRegistered plugins: {PluginRegistry.list_plugins()}")

        adapter = PluginRegistry.get("student_support")
        meta = adapter.get_metadata()

        print(f"\nPlugin: {meta.name} v{meta.version}")

        print("\n1. Testing department routing...")
        test_queries = [
            ("Como faço a matrícula?", "academic"),
            ("Quando são publicadas as notas?", "academic"),
            ("Como candidato a bolsa de estudo?", "sasup"),
            ("O refeitório está aberto ao domingo?", "sasup"),
            ("Como reseto a password do email?", "it"),
            ("O WiFi não funciona no meu quarto", "it"),
            ("Olá, preciso de ajuda", None),
        ]

        for query, expected_dept in test_queries:
            detected = adapter.get_department_for_query(query)
            status = "✅" if detected == expected_dept else "⚠️"
            print(f"   {status} '{query[:35]}...' → {detected or 'general'}")

        print("\n2. Testing FAQ matching...")
        faq_queries = [
            "Como funciona a rede WiFi?",
            "Quando posso candidatar-me a bolsa?",
            "Qual é o prazo para matrícula?",
            "Como acesso ao email institucional?",
        ]

        for query in faq_queries:
            match = adapter._find_faq_match(query)
            if match:
                dept, answer = match
                print(f"   ✅ '{query[:30]}...' → {dept}")
            else:
                print(f"   ⚠️ '{query[:30]}...' → no match")

        print("\n3. Testing escalation triggers...")
        esc_queries = [
            ("Tenho uma reclamação a fazer", True),
            ("É urgente, não consigo login", True),
            ("Quanto custa a refeição?", False),
            ("Quando são as aulas?", False),
        ]

        for query, expected_esc in esc_queries:
            esc, reason = adapter.should_escalate(query)
            status = "✅" if esc == expected_esc else "⚠️"
            print(f"   {status} '{query[:30]}...' → escalate={esc}")

        print("\n4. Testing process_query (FAQ)...")
        result = await adapter.process_query(
            query="Qual é o horário do refeitório?",
            context={},
            llm_config={"provider": "bitnet"},
        )
        print(f"   Response: {result.response}")
        print(f"   Confidence: {result.confidence}")
        print(f"   Source: {result.metadata.get('source')}")

        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)

    asyncio.run(test())
