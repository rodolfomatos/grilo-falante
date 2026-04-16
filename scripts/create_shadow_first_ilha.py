"""
Script para criar a ILHA "Shadow First Methodology" com persistência.

Este script cria:
- ILHA: "Shadow First Methodology"
- PEDRA 1: "Shadow First" (ConceptualCapsule)
- PEDRA 2: "Shadow Debt" (ShadowDocument)
- PEDRA 3: "Concept Registry" (DigitalObject)
- E mais 4 pedras com informação relevante

E persiste em data/ilhas.json
"""

import sys
import json
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/home/rodolfo/src/grilo_falante_v3.0')

from grilo_admin.routers.ilhas import ILHAManager
from grilo_admin.models import (
    Participant,
    InteractionType,
)


def create_shadow_first_ilha():
    """Create the Shadow First Methodology ILHA with persistence."""

    print("=" * 70)
    print("CRIANDO ILHA: Shadow First Methodology (com persistência)")
    print("=" * 70)

    # Initialize and load existing data
    ILHAManager.initialize()
    print(f"✅ ILHAManager initialized")
    print(f"   Storage: {ILHAManager._storage_path}")

    # Check if already exists
    existing = [i for i in ILHAManager._ilhas.values() if "Shadow First" in i.get("title", "")]
    if existing:
        print(f"\n⚠️  ILHA 'Shadow First' já existe: {existing[0]['id']}")
        print("   A usar a existente.")
        return ILHAManager._dict_to_ilha(existing[0])

    ntp_time = ILHAManager._get_ntp_time()
    now = datetime.now(timezone.utc)
    ilha_id = f"ILHA-{now.strftime('%Y%m%d-%H%M%S')}"

    # Create participants
    participants = [
        Participant(name="Rodolfo", role="human", type="human"),
        Participant(name="OpenCode", role="assistant", type="ai"),
    ]

    # Define pedras
    pedra_contents = [
        {
            "content": "Shadow First: Antes de perguntar, assumir, ou implementar, deves primeiro pesquisar documentação, criar Shadow Document do que encontraste, e gerar FAQ com perguntas que ainda tens.",
            "gmif": "M7",
            "type": "concept",
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
        {
            "content": """Comandos CLI:
- check <concept> → Verificar documentação
- shadow <concept> → Iniciar sessão
- ritual → Verificar shadow debt
- status → Estado geral
- report <theme> → Gerar relatório

Endpoints API:
- GET /admin/skills/shadow/check/{concept}
- POST /admin/skills/shadow/session/{concept}
- GET /admin/skills/shadow/ritual
- GET /admin/skills/shadow/status""",
            "gmif": "M4",
            "type": "reference",
        },
    ]

    # Create pedras
    pedras = []
    gmif_counts = {"M1": 0, "M2": 0, "M3": 0, "M4": 0, "M5": 0, "M6": 0, "M7": 0, "M8": 0}

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

    # Create ILHA dict
    ilha_dict = {
        "id": ilha_id,
        "timestamp": now.isoformat(),
        "ntp_timestamp": ntp_time,
        "participants": [p.model_dump() for p in participants],
        "topic": "Shadow First Methodology - Metodologia de Documentação",
        "topic_summary": "Documentar antes de perguntar, pesquisar antes de assumir, analisar antes de implementar",
        "interaction_type": InteractionType.AI_TO_HUMAN.value,
        "pedras": pedras,
        "claims_count": sum(1 for p in pedras if p["type"] == "claim"),
        "gaps_count": sum(1 for p in pedras if p["type"] == "gap"),
        "questions_count": 0,
        "gmif_summary": gmif_counts,
        "reused_pedras": [],
        "is_processed": True,
        "processed_at": now.isoformat(),
        "title": "Shadow First: Documentar antes de perguntar",
    }

    # Save to ILHAManager (this also persists)
    ILHAManager._ilhas[ilha_id] = ilha_dict
    ILHAManager.save()

    print("\n" + "=" * 70)
    print("ILHA Shadow First Methodology criada e persistida!")
    print("=" * 70)
    print(f"\nID: {ilha_id}")
    print(f"Topic: {ilha_dict['topic']}")
    print(f"Title: {ilha_dict['title']}")
    print(f"Total pedras: {len(pedras)}")
    print(f"Participants: {[p.name for p in participants]}")
    print(f"Storage: {ILHAManager._storage_path}")

    # Verify
    ILHAManager.load()  # Reload to verify
    ilha_final = ILHAManager.get_ilha(ilha_id)
    print(f"\n✅ Verificação: ILHA existe em storage: {ilha_final is not None}")
    print(f"   Total ILHAs em storage: {len(ILHAManager._ilhas)}")
    print(f"   Total PEDRAs em storage: {len(ILHAManager._pedras)}")

    return ilha_final


if __name__ == "__main__":
    create_shadow_first_ilha()
