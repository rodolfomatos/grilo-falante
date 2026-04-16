"""Test script for the simple plugin example."""

import asyncio
import sys
sys.path.insert(0, "/home/rodolfo/src/grilo_falante_v3.0")

from examples.simple_plugin import SimpleQAAdapter, register_plugin
from grilo_falante.platform import PluginRegistry


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

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
