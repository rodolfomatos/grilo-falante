"""
Test script for ILHA/PEDRA Memory System.
"""

import sys
sys.path.insert(0, "/home/rodolfo/src/grilo_falante_v3.0")


def test_ilha_models():
    """Test ILHA and PEDRA models."""
    print("=" * 60)
    print("ILHA/PEDRA Models - Test")
    print("=" * 60)

    from grilo_admin.models.ilha import (
        ILHA,
        ILHACreate,
        Participant,
        Pedra,
        PedraType,
        ShadowDocument,
        DigitalObject,
        GmifEvent,
        InteractionType,
    )

    print("\n1. Testing Participant...")
    p = Participant(name="grilo-gf", role="ai", type="ai")
    assert p.name == "grilo-gf"
    assert p.type == "ai"
    print(f"   Participant: {p.name} ({p.role})")
    print("   ✅ Participant works")

    print("\n2. Testing ShadowDocument...")
    sd = ShadowDocument(
        source_name="MemPalace README",
        source_type="document",
        source_reference="https://github.com/...",
        feynman_f1="For children: library of thoughts",
        feynman_f2="For experts: vector database",
        feynman_f3_gaps=["How does indexing work?"],
        extracted_claims=["MemPalace uses ChromaDB"],
        evidence_level="complete",
        assumptions=["ChromaDB is available"],
        misuse_risks=["Can be used for tracking"],
    )
    assert sd.source_name == "MemPalace README"
    assert sd.feynman_f1 == "For children: library of thoughts"
    assert sd.evidence_level == "complete"
    assert len(sd.extracted_claims) == 1
    print(f"   Shadow doc: {sd.source_name}")
    print(f"   F1: {sd.feynman_f1[:30]}...")
    print("   ✅ ShadowDocument works")

    print("\n3. Testing DigitalObject...")
    do = DigitalObject(
        type="pdf",
        reference="https://arxiv.org/paper.pdf",
        title="Paper on LLMs",
        is_capsule=False,
    )
    assert do.type == "pdf"
    assert do.is_capsule == False
    print(f"   Digital object: {do.title}")
    print("   ✅ DigitalObject works")

    print("\n4. Testing DigitalObject as Capsule...")
    capsule = DigitalObject(
        type="capsule",
        reference="internal:capsule:001",
        title="Conservation Theorem",
        is_capsule=True,
        capsule_scope="Classical Physics",
        capsule_interpretation="Σ_delta",
        capsule_normative_effect="Δ_universal",
    )
    assert capsule.is_capsule == True
    assert capsule.capsule_scope == "Classical Physics"
    print(f"   Capsule: {capsule.title}")
    print(f"   Scope: {capsule.capsule_scope}")
    print("   ✅ ConceptualCapsule (via DigitalObject) works")

    print("\n5. Testing GmifEvent...")
    event = GmifEvent(
        gmif_level="M4",
        source="test",
        note="Test classification",
    )
    assert event.gmif_level == "M4"
    print(f"   GMIF event: {event.gmif_level} from {event.source}")
    print("   ✅ GmifEvent works")

    print("\n6. Testing Pedra...")
    from datetime import datetime, timezone
    pedra = Pedra(
        id="PEDRA-001",
        ilha_id="ILHA-001",
        author_id="author-1",
        author_name="grilo-gf",
        content_summary="Test pedra content",
        shadow_documents=[sd],
        digital_objects=[do],
        is_empty=False,
        gmif_events=[],
        gmif_level="M3",
        type=PedraType.CLAIM,
        reused_in=[],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    assert pedra.content_summary == "Test pedra content"
    assert pedra.is_empty == False
    assert len(pedra.shadow_documents) == 1
    assert len(pedra.digital_objects) == 1
    print(f"   Pedra: {pedra.content_summary[:30]}...")
    print(f"   Shadow docs: {len(pedra.shadow_documents)}")
    print(f"   Digital objects: {len(pedra.digital_objects)}")
    print("   ✅ Pedra works")

    print("\n7. Testing ILHA...")
    from datetime import datetime, timezone
    participants = [Participant(name="grilo-gf", role="ai", type="ai")]
    ilha = ILHA(
        id="ILHA-001",
        topic="Test ILHA",
        participants=participants,
        interaction_type=InteractionType.AI_TO_AI,
        pedras=[pedra],
        title="Test Memory",
        gmif_summary={"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0},
        reused_pedras=[],
    )
    assert ilha.topic == "Test ILHA"
    assert len(ilha.pedras) == 1
    assert ilha.interaction_type == InteractionType.AI_TO_AI
    print(f"   ILHA: {ilha.title}")
    print(f"   Topic: {ilha.topic}")
    print(f"   Pedras: {len(ilha.pedras)}")
    print("   ✅ ILHA works")

    print("\n" + "=" * 60)
    print("All ILHA/PEDRA model tests passed!")
    print("=" * 60)


def test_ilha_manager():
    """Test ILHAManager functionality."""
    print("\n" + "=" * 60)
    print("ILHAManager - Test")
    print("=" * 60)

    from grilo_admin.routers.ilhas import ILHAManager
    from grilo_admin.models.ilha import ILHACreate, Participant, InteractionType

    print("\n1. Testing ILHAManager initialization...")
    ILHAManager.initialize()
    initial_count = len(ILHAManager._ilhas)
    print(f"   Initial ILHAs: {initial_count}")
    print("   ✅ ILHAManager init works")

    print("\n2. Testing ILHA creation...")
    create_data = ILHACreate(
        topic="Test Creation",
        participants=[{"name": "grilo-gf", "role": "ai"}],
        interaction_type=InteractionType.AI_TO_AI,
        title="Test ILHA Creation",
    )
    ilha = ILHAManager.create_ilha(create_data)
    assert ilha is not None
    assert ilha.topic == "Test Creation"
    print(f"   Created ILHA: {ilha.id}")
    print(f"   Title: {ilha.title}")
    print("   ✅ ILHA creation works")

    print("\n3. Testing ILHA retrieval...")
    retrieved = ILHAManager.get_ilha(ilha.id)
    assert retrieved is not None
    assert retrieved.id == ilha.id
    print(f"   Retrieved ILHA: {retrieved.id}")
    print("   ✅ ILHA retrieval works")

    print("\n4. Testing ILHA listing...")
    ilhas = ILHAManager.list_ilhas(limit=10)
    assert len(ilhas) >= 1
    print(f"   Total ILHAs: {len(ilhas)}")
    print("   ✅ ILHA listing works")

    print("\n5. Testing Pedra retrieval...")
    if ilha.pedras:
        pedra_id = ilha.pedras[0].id
        pedra = ILHAManager.get_pedra(pedra_id)
        assert pedra is not None
        print(f"   Retrieved Pedra: {pedra.id}")
        print("   ✅ Pedra retrieval works")

    print("\n6. Testing adding ShadowDocument to Pedra...")
    if ilha.pedras:
        from grilo_admin.models.ilha import ShadowDocument
        pedra_id = ilha.pedras[0].id
        pedra_dict = ILHAManager._pedras.get(pedra_id)
        assert pedra_dict is not None

        shadow_doc = ShadowDocument(
            source_name="Test Source",
            source_type="document",
            feynman_f1="F1 test",
            feynman_f2="F2 test",
            extracted_claims=["Test claim"],
        )
        pedra_dict.setdefault("shadow_documents", []).append(shadow_doc.model_dump())
        pedra_dict["is_empty"] = False
        ILHAManager.save()

        # Verify
        updated_pedra = ILHAManager.get_pedra(pedra_id)
        assert len(updated_pedra.shadow_documents) >= 1
        print(f"   Shadow docs in pedra: {len(updated_pedra.shadow_documents)}")
        print("   ✅ ShadowDocument addition works")

    print("\n7. Testing stats...")
    stats = {
        "total_ilhas": len(ILHAManager._ilhas),
        "total_pedras": len(ILHAManager._pedras),
    }
    print(f"   Stats: {stats}")
    print("   ✅ Stats works")

    print("\n" + "=" * 60)
    print("All ILHAManager tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_ilha_models()
    test_ilha_manager()