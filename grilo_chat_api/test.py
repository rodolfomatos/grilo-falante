"""
Test script for Unified Chat API.

Tests:
1. Plugin registration
2. Query routing
3. Multi-turn conversation
4. Session management
"""

import asyncio
import sys

sys.path.insert(0, "/home/rodolfo/src/grilo_falante_v3.0")


async def test():
    print("=" * 60)
    print("Unified Chat API - Test")
    print("=" * 60)

    from grilo_chat_api import ChatAPIService, GlobalChatAPI
    from grilo_falante.platform import PluginRegistry

    print("\n1. Registering plugins...")
    from grilo_tax import register as register_tax
    from grilo_student import register as register_student

    register_tax()
    register_student()

    print(f"   Registered plugins: {PluginRegistry.list_plugins()}")

    print("\n2. Testing ChatAPIService...")
    api = ChatAPIService()

    print("\n3. Creating session...")
    session = api.create_session(user_id="user123")
    print(f"   Session created: {session.session_id}")

    print("\n4. Testing routing and response...")

    test_queries = [
        ("Como funciona a matrícula?", "student_support", "Academic question"),
        ("Posso deduzir IVA desta fatura?", "tax_intelligence", "Tax question"),
        ("Qual é o prazo para bolsa?", "student_support", "SASUP question"),
        ("Como reseto a password?", "student_support", "IT question"),
        ("Quais são os gastos dedutíveis para IRC?", "tax_intelligence", "IRC question"),
    ]

    for query, expected_domain, description in test_queries:
        result = await api.process_message(
            query=query,
            user_id="user123",
            session_id=session.session_id,
            llm_config={"provider": "bitnet"},
        )

        status = "✅" if result["domain"] == expected_domain else "⚠️"
        print(f"   {status} {description}")
        print(f"      Query: {query[:40]}...")
        print(f"      Domain: {result['domain']} (expected: {expected_domain})")
        print(f"      Confidence: {result['confidence']:.2f}")
        if result.get("escalation_triggered"):
            print(f"      Escalation: YES")
        print()

    print("\n5. Testing escalation trigger...")
    session2 = api.create_session(user_id="user456")

    result = await api.process_message(
        query="Tenho uma reclamação sobre a decisão fiscal",
        user_id="user456",
        session_id=session2.session_id,
        llm_config={"provider": "bitnet"},
    )

    print(f"   Query: Reclamação sobre decisão fiscal")
    print(f"   Escalation triggered: {result.get('escalation_triggered', False)}")

    print("\n6. Testing multi-turn conversation...")
    session3 = api.create_session(user_id="user789")

    queries = [
        "Olá, preciso de ajuda",
        "Como faço matrícula?",
        "Qual é o prazo?",
        "Obrigado!",
    ]

    for q in queries:
        result = await api.process_message(
            query=q,
            user_id="user789",
            session_id=session3.session_id,
            llm_config={"provider": "bitnet"},
        )
        print(f"   User: {q[:30]}...")
        print(f"   Bot:  {result['response'][:50]}...")
        print(f"   Domain: {result['domain']}, Messages: {result['message_count']}")
        print()

    print("\n7. Testing session list...")
    sessions = api.list_sessions()
    print(f"   Total sessions: {len(sessions)}")
    for s in sessions[:3]:
        print(f"   - {s['session_id'][:20]}... (user: {s['user_id']}, msgs: {s['message_count']})")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test())
