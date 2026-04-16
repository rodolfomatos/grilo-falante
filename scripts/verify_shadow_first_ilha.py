"""
Script para verificar ILHA Shadow First Methodology.
"""

import sys
sys.path.insert(0, '/home/rodolfo/src/grilo_falante_v3.0')

from grilo_admin.routers.ilhas import ILHAManager


def verify_shadow_first_ilha():
    """Verify the Shadow First ILHA exists and show its contents."""
    print("=" * 70)
    print("VERIFICANDO ILHA: Shadow First Methodology")
    print("=" * 70)

    # Find the ILHA
    ilhas = ILHAManager.list_ilhas(limit=100)
    shadow_ilha = None
    for ilha in ilhas:
        if "Shadow First" in ilha.title:
            shadow_ilha = ilha
            break

    if not shadow_ilha:
        print("❌ ILHA 'Shadow First' não encontrada!")
        return

    print(f"\n✅ ILHA encontrada: {shadow_ilha.id}")
    print(f"   Title: {shadow_ilha.title}")
    print(f"   Topic: {shadow_ilha.topic}")
    print(f"   Timestamp: {shadow_ilha.timestamp}")
    print(f"   NTP: {shadow_ilha.ntp_timestamp}")
    print(f"   Participants: {[p.name for p in shadow_ilha.participants]}")
    print(f"   Interaction Type: {shadow_ilha.interaction_type}")
    print(f"   Is Processed: {shadow_ilha.is_processed}")
    print(f"   Processed At: {shadow_ilha.processed_at}")

    print(f"\n📦 PEDRAs ({len(shadow_ilha.pedras)}):")
    for i, pedra in enumerate(shadow_ilha.pedras, 1):
        print(f"\n   {i}. {pedra.id}")
        print(f"      Author: {pedra.author_name}")
        print(f"      Type: {pedra.type}")
        print(f"      GMIF: {pedra.gmif_level}")
        print(f"      Content: {pedra.content[:100]}...")

    print(f"\n📊 GMIF Summary: {shadow_ilha.gmif_summary}")

    print(f"\n📈 Statistics:")
    print(f"   Claims: {shadow_ilha.claims_count}")
    print(f"   Gaps: {shadow_ilha.gaps_count}")
    print(f"   Questions: {shadow_ilha.questions_count}")

    print("\n" + "=" * 70)
    print("VERIFICAÇÃO COMPLETA")
    print("=" * 70)


def list_all_ilhas():
    """List all ILHAs in memory."""
    print("\n" + "=" * 70)
    print("TODAS AS ILHAS EM MEMÓRIA")
    print("=" * 70)

    ilhas = ILHAManager.list_ilhas(limit=100)
    print(f"Total: {len(ilhas)} ILHAs\n")

    for ilha in ilhas:
        print(f"  • {ilha.id}")
        print(f"    Title: {ilha.title}")
        print(f"    Topic: {ilha.topic}")
        print(f"    Pedras: {len(ilha.pedras)}")
        print(f"    Participants: {[p.name for p in ilha.participants]}")
        print()


if __name__ == "__main__":
    verify_shadow_first_ilha()
    list_all_ilhas()
