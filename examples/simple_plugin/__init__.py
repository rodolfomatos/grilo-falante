"""
Simple Example Domain Adapter - Demonstrates the DomainAdapter interface.

This is a minimal example of how to implement a domain adapter for the
Grilo Falante platform.

Run:
    python -m examples.simple_plugin.test
"""

from grilo_falante.platform import (
    DomainAdapter,
    DomainMetadata,
    DomainStatus,
    QueryResult,
    ValidationResult,
    PluginRegistry,
    get_llm_config,
)


class SimpleQAAdapter(DomainAdapter):
    """
    A simple Q&A domain adapter for testing.

    This adapter responds to questions using basic keyword matching
    and falls back to LLM generation.
    """

    QA_KNOWLEDGE_BASE = {
        "horário": "O horário de funcionamento é das 8h às 20h, de segunda a sexta.",
        "localização": "Estamos localizados no Edifício A, Piso 2, Sala 201.",
        "contacto": "Pode-nos contactar por email para info@exemplo.pt ou por telefone para 22X XXX XXX.",
        "código": "O nosso código fiscal é 123456789.",
    }

    def get_metadata(self) -> DomainMetadata:
        return DomainMetadata(
            name="simple_qa",
            version="0.1.0",
            description="Simple Q&A example adapter for testing",
            author="Grilo Falante",
            status=DomainStatus.ACTIVE,
        )

    def get_routing_config(self) -> dict[str, list[str]]:
        return {
            "general": ["horário", "localização", "contacto", "código", "ajuda"],
            "info": ["informação", "info", "saber"],
        }

    def get_prompts(self) -> dict[str, str]:
        return {
            "system": (
                "You are a helpful assistant for a simple Q&A system. "
                "Answer based on the knowledge base provided. "
                "If you don't know, say you don't know."
            ),
            "query": "Question: {query}\nKnowledge base: {kb}\nAnswer:",
        }

    def get_escalation_triggers(self) -> list[str]:
        return ["urgente", "problema grave", "reclamação", "multa"]

    async def process_query(
        self,
        query: str,
        context: dict,
        llm_config: dict,
    ) -> QueryResult:
        """
        Process a query - try knowledge base first, then LLM.
        """
        query_lower = query.lower()

        for keyword, answer in self.QA_KNOWLEDGE_BASE.items():
            if keyword in query_lower:
                return QueryResult(
                    response=answer,
                    domain=self.get_metadata().name,
                    confidence=1.0,
                    sources=["knowledge_base"],
                )

        if self._has_escalation_trigger(query_lower):
            return QueryResult(
                response=(
                    "Parece que precisa de ajuda urgente. "
                    "Vou escalonar a sua questão para um operador humano."
                ),
                domain=self.get_metadata().name,
                escalation_triggered=True,
                escalation_reason="Escalation trigger found",
                confidence=1.0,
            )

        llm_response = await self._generate_with_llm(query, context, llm_config)
        return QueryResult(
            response=llm_response,
            domain=self.get_metadata().name,
            confidence=0.7,
        )

    async def validate_content(self, content: any) -> ValidationResult:
        """Validate content - always passes for this simple example."""
        return ValidationResult(is_valid=True)

    def _has_escalation_trigger(self, text: str) -> bool:
        for trigger in self.get_escalation_triggers():
            if trigger in text:
                return True
        return False

    async def _generate_with_llm(
        self,
        query: str,
        context: dict,
        llm_config: dict,
    ) -> str:
        """Generate response using LLM."""
        try:
            from grilo_falante.platform.config import LLMClient

            client = LLMClient(provider=llm_config.get("provider", "bitnet"))
            prompts = self.get_prompts()

            response = await client.generate(
                prompt=query,
                system_prompt=prompts["system"],
            )
            return response
        except Exception as e:
            return f"Ocorreu um erro: {str(e)}"


def register_plugin():
    """Register this plugin with the Grilo Falante platform."""
    PluginRegistry.register("simple_qa", SimpleQAAdapter)
    print("Registered plugin: simple_qa")


if __name__ == "__main__":
    import asyncio

    async def test():
        print("=" * 60)
        print("Grilo Falante Platform - Simple Plugin Test")
        print("=" * 60)

        register_plugin()

        print("\n1. Testing PluginRegistry...")
        plugins = PluginRegistry.list_plugins()
        print(f"   Registered plugins: {plugins}")

        print("\n2. Getting plugin instance...")
        adapter = PluginRegistry.get("simple_qa")
        print(f"   Plugin: {adapter.get_metadata().name} v{adapter.get_metadata().version}")

        print("\n3. Testing routing config...")
        routing = adapter.get_routing_config()
        print(f"   Routing keywords: {routing}")

        print("\n4. Testing escalation triggers...")
        triggers = adapter.get_escalation_triggers()
        print(f"   Triggers: {triggers}")

        print("\n5. Testing simple query (should match knowledge base)...")
        result = await adapter.process_query(
            query="Qual é o horário de funcionamento?",
            context={},
            llm_config={"provider": "bitnet"},
        )
        print(f"   Response: {result.response}")
        print(f"   Confidence: {result.confidence}")

        print("\n6. Testing LLM query (should use LLM)...")
        result = await adapter.process_query(
            query="Explique-me o conceito de governação epistémica",
            context={},
            llm_config={"provider": "bitnet"},
        )
        print(f"   Response: {result.response}")
        print(f"   Confidence: {result.confidence}")

        print("\n7. Testing escalation trigger...")
        result = await adapter.process_query(
            query="Tenho uma reclamação urgente!",
            context={},
            llm_config={"provider": "bitnet"},
        )
        print(f"   Response: {result.response}")
        print(f"   Escalated: {result.escalation_triggered}")

        print("\n8. Testing combined keywords...")
        result = await adapter.process_query(
            query="Qual a localização e o contacto?",
            context={},
            llm_config={"provider": "bitnet"},
        )
        print(f"   Response: {result.response}")

        print("\n" + "=" * 60)
        print("Test completed!")
        print("=" * 60)

    asyncio.run(test())
