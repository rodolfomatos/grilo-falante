"""
Script para criar a ILHA "Shadow First Methodology" na memória.

Este script cria:
- ILHA: "Shadow First Methodology"
- PEDRA 1: "Shadow First" (ConceptualCapsule)
- PEDRA 2: "Shadow Debt" (ShadowDocument)
- PEDRA 3: "Concept Registry" (DigitalObject)
"""

import sys
sys.path.insert(0, '/home/rodolfo/src/grilo_falante_v3.0')

from datetime import datetime, timezone
from grilo_admin.routers.ilhas import ILHAManager
from grilo_admin.models import (
    ILHACreate,
    Participant,
    InteractionType,
    Pedra,
)


def create_shadow_first_ilha():
    """Create the Shadow First Methodology ILHA."""

    print("=" * 70)
    print("CRIANDO ILHA: Shadow First Methodology")
    print("=" * 70)

    ILHAManager.initialize()

    ntp_time = ILHAManager._get_ntp_time()
    now = datetime.now(timezone.utc)
    ilha_id = f"ILHA-{now.strftime('%Y%m%d-%H%M%S')}"

    # Create participants
    participants_data = [
        {"name": "Rodolfo", "role": "human", "type": "human"},
        {"name": "OpenCode", "role": "assistant", "type": "ai"},
    ]
    participants = [
        Participant(name=p["name"], role=p["role"], type=p["type"])
        for p in participants_data
    ]

    # Create pedras directly in the ILHA dict format
    pedras = []
    gmif_counts = {"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0}

    pedra_contents = [
        {
            "content": "Shadow First: Antes de perguntar, assumption, ou implementar, deves primeiro pesquisar documentação, criar Shadow Document do que encontraste, e gerar FAQ com perguntas que ainda tens.",
            "gmif": "M7",
            "type": "claim",
        },
        {
            "content": "Shadow Debt: Conceitos mencionados pelo utilizador mas ainda não documentados. Métrica de documentação: Shadow Score (0-100%). Score 100% = conceito completamente documentado.",
            "gmif": "M5",
            "type": "claim",
        },
        {
            "content": "Concept Registry: Índice central de todos os conceitos documentados. docs/shadow_documents/REGISTRY.md",
            "gmif": "M4",
            "type": "reference",
        },
        {
            "content": "Shadow Score: Métrica de documentação. 100% = completamente documentado (shadow doc + FAQ + relatório). 50% = tem shadow doc mas falta algo. 0% = mencionado mas nunca documentado.",
            "gmif": "M4",
            "type": "claim",
        },
        {
            "content": """7 Regras de Ouro:
1. Nunca perguntes o que podes pesquisar
2. Nunca assumas o que não documentaste
3. Shadow debt não perdoa - cria o doc
4. FAQ não é para ti - é para saberes o que perguntar
5. Relatório é para o teu EU futuro - documenta como se fosses outro
6. Documenta tudo sempre - para tu próprio não te perderes
7. Memória é contextual - o mesmo conceito pode ter significados diferentes""",
            "gmif": "M6",
            "type": "claim",
        },
        {
            "content": """Gaps identificadas no sistema:
G1-G8: ✅ Implementadas
G9: Modelo PEDRA correto (agregador) - A CORRIGIR
G10: Integração MemPalace - A ESTUDAR
G11: Arquitetura storage unificada - A DESENHAR""",
            "gmif": "M5",
            "type": "claim",
        },
        {
            "content": """Shadow First Workflow:
1. MENCÃO → Utilizador menciona conceito
2. CHECK → /shadow_first check <conceito>
3. SE UNDOCUMENTED → SHADOW DEBT
4. SHADOW → /shadow_first shadow <conceito>
5. PESQUISAR → webfetch, grep, glob
6. DOCUMENTAR → Shadow doc + FAQ + Registry
7. PERGUNTAR → Só agora, o que não soube""",
            "gmif": "M6",
            "type": "process",
        },
    ]

    for i, pc in enumerate(pedra_contents, 1):
        pedra_id = f"PEDRA-{now.strftime('%Y%m%d-%H%M%S')}-{i:03d}"
        pedra_dict = {
            "id": pedra_id,
            "ilha_id": ilha_id,
            "author_id": "system",
            "author_name": "OpenCode",
            "content": pc["content"],
            "gmif_level": pc["gmif"],
            "type": pc["type"],
            "is_gap": False,
            "gap_question": None,
            "reused_in": [],
            "created_at": now.isoformat(),
        }
        ILHAManager._pedras[pedra_id] = pedra_dict
        pedras.append(pedra_dict)
        gmif_counts[pc["gmif"]] += 1
        print(f"✅ PEDRA {i} criada: {pedra_id}")
        print(f"   Type: {pc['type']}, GMIF: {pc['gmif']}")

    claims_count = sum(1 for p in pedras if p["type"] == "claim")
    gaps_count = sum(1 for p in pedras if p["type"] == "gap")

    ilha_dict = {
        "id": ilha_id,
        "timestamp": now.isoformat(),
        "ntp_timestamp": ntp_time,
        "participants": [p.model_dump() for p in participants],
        "topic": "Shadow First Methodology - Metodologia de Documentação",
        "topic_summary": "Documentar antes de perguntar, pesquisar antes de assumir, analisar antes de implementar",
        "interaction_type": InteractionType.AI_TO_HUMAN.value,
        "pedras": pedras,
        "claims_count": claims_count,
        "gaps_count": gaps_count,
        "questions_count": 0,
        "gmif_summary": gmif_counts,
        "reused_pedras": [],
        "is_processed": True,
        "processed_at": now.isoformat(),
        "title": "Shadow First: Documentar antes de perguntar",
    }

    ILHAManager._ilhas[ilha_id] = ilha_dict

    print("\n" + "=" * 70)
    print("ILHA Shadow First Methodology criada com sucesso!")
    print("=" * 70)
    print(f"\nID: {ilha_id}")
    print(f"Topic: {ilha_dict['topic']}")
    print(f"Title: {ilha_dict['title']}")
    print(f"Total pedras: {len(pedras)}")
    print(f"Participants: {[p.name for p in participants]}")

    # Verify
    ilha_final = ILHAManager.get_ilha(ilha_id)
    print(f"\nVerificação:")
    print(f"   ILHA exists: {ilha_final is not None}")
    print(f"   pedras count: {len(ilha_final.pedras)}")

    return ilha_final


if __name__ == "__main__":
    create_shadow_first_ilha()
