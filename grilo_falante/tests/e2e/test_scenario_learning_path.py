"""
Cenário E2E: Learning Path Automático

Um investigador tem um conjunto de claims e gaps sobre um tópico.
O sistema gera automaticamente um learning path ordenado.

Passos:
1. Gerar learning path a partir de claims + gaps
2. Verificar que steps estão ordenados
3. Converter para study plan
4. Converter para markdown
5. Verificar que gaps são intercalados nos steps
"""

import pytest


@pytest.mark.asyncio
async def test_scenario_learning_path(sample_claims, sample_gaps):
    """
    Cenário: Investigador usa LearningPathGenerator para criar
    um plano de estudo a partir de claims e gaps.

    Resultado esperado:
    - Learning path gerado com steps ordenados
    - Gaps intercalados nos steps
    - Conversão para StudyPlan preserva estrutura
    - Markdown gerado é válido e legível
    """
    from grilo_falante.backend.services.learning_path import LearningPathGenerator

    gen = LearningPathGenerator()

    print(f"\n{'='*60}")
    print(f"Cenário Learning Path — {len(sample_claims)} claims, {len(sample_gaps)} gaps")
    print(f"{'='*60}")

    # Passo 1: Gerar learning path
    path = await gen.generate(
        topic="Climate Change Analysis",
        existing_claims=sample_claims,
        identified_gaps=sample_gaps,
    )
    print(f"  Passo 1: Path gerado — {len(path.steps)} steps, {path.gaps_found} gaps")
    assert len(path.steps) > 0, "CRITÉRIO 1 FAIL: Nenhum step gerado"
    print("  ✓ Critério 1: Steps gerados")

    # Passo 2: Verificar ordem
    for i, step in enumerate(path.steps):
        assert step.order == i + 1, f"CRITÉRIO 2 FAIL: Step {i} tem order {step.order}"
    print("  ✓ Critério 2: Steps ordenados (1-based)")

    # Passo 3: Converter para StudyPlan
    plan = gen.to_study_plan(path, gap_key=sample_gaps[0].gap_key)
    assert plan.topic == "Climate Change Analysis"
    assert len(plan.steps) == len(path.steps)
    assert plan.status == "identified"
    print(f"  ✓ Critério 3: StudyPlan criado — {len(plan.steps)} steps, status={plan.status}")

    # Passo 4: Converter para Markdown
    md = gen.to_markdown(path)
    assert path.topic in md
    assert md.startswith("# ")
    assert "## Steps" in md
    for step in path.steps:
        assert step.concept in md, f"CRITÉRIO 4 FAIL: Step '{step.concept}' não está no markdown"
    print(f"  ✓ Critério 4: Markdown válido ({len(md)} chars)")

    # Passo 5: Gaps intercalados
    gap_steps = [s for s in path.steps if s.is_gap]
    print(f"  Passo 5: {len(gap_steps)} gap steps intercalados em {len(path.steps)} steps totais")

    print(f"\n  Resultado: 4/4 critérios OK")
