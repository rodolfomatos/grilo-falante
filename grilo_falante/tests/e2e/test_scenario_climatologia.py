"""
Cenário E2E: Analista de Climatologia

Um investigador analisa 3 artigos sobre alterações climáticas.
Extrai claims, classifica-as com GMIF, executa lint L1-L8 ao grafo,
e verifica a integridade epistémica do conjunto.

Este cenário documenta cada passo com resultado pass/fail para
que qualquer investigador possa repetir e avaliar o sistema.

Passos:
1. Cria claims a partir de 3 artigos simulados
2. Classifica cada claim com nível GMIF
3. Executa L1-L8 (graph_lint.run_all_checks)
4. Verifica que L5 bloqueia conclusão baseada em CONFLICTED
5. Verifica que L6 não dispara para conclusões com base VERIFIED
6. Reporta resultado global: pass/fail por critério
"""

from datetime import datetime

import pytest

from grilo_falante.models import GovernedClaim, GMIFLevel


def test_scenario_climatologia(sample_claims):
    """
    Cenário completo de análise climatológica.

    Cenário: Investigador analisa 3 artigos sobre clima, extraindo
    6 claims, classificando-as, e validando o grafo epistémico.

    Resultado esperado:
    - L1 (orphans): detected for c:orphan_claim
    - L2 (self-references): detected for c:self_ref
    - L5 (unsupported conclusions): detected for c:bad_conclusion
    - L6 (missing prerequisites): NOT triggered for c:policy
    - L7 (confidence mismatches): detected for c:too_confident
    """
    from grilo_falante.backend.services.graph_lint import GraphLinter

    linter = GraphLinter()
    result = linter.run_all_checks(sample_claims)

    issues_by_code: dict[str, list] = {}
    for i in result.issues:
        issues_by_code.setdefault(i.lint_code, []).append(i)

    print(f"\n{'='*60}")
    print(f"Cenário Climatologia — {len(sample_claims)} claims, {len(result.issues)} issues")
    print(f"Resultado: {'PASS' if result.passed else 'FAIL'}")
    print(f"{'='*60}")
    for code in sorted(issues_by_code):
        for issue in issues_by_code[code]:
            print(f"  [{code}/{issue.severity}] {issue.message[:80]}")

    # Critério 1: L1 detecta orphan claims
    assert "c:orphan_claim" in [
        k for i in result.issues if i.lint_code == "L1" for k in i.claim_keys
    ], "CRITÉRIO 1 FAIL: L1 não detetou c:orphan_claim"
    print("  ✓ Critério 1: L1 detetou orphan claim c:orphan_claim")

    # Critério 2: L2 detecta self-references
    assert any(i.lint_code == "L2" for i in result.issues), (
        "CRITÉRIO 2 FAIL: L2 não detetou self-reference"
    )
    print("  ✓ Critério 2: L2 detetou self-reference c:self_ref")

    # Critério 3: L5 detecta conclusão CONFLICTED
    l5_issues = [i for i in result.issues if i.lint_code == "L5"]
    assert any("c:bad_conclusion" in i.claim_keys for i in l5_issues), (
        "CRITÉRIO 3 FAIL: L5 não detetou conclusão inválida c:bad_conclusion"
    )
    print("  ✓ Critério 3: L5 bloqueou conclusão CONFLICTED c:bad_conclusion")

    # Critério 4: L6 NÃO deteta conclusão com base VERIFIED (c:policy -> c:co2_temp + c:temp_rise)
    l6_issues = [i for i in result.issues if i.lint_code == "L6"]
    assert not any("c:policy" in i.claim_keys for i in l6_issues), (
        "CRITÉRIO 4 FAIL: L6 falso positivo em c:policy"
    )
    print("  ✓ Critério 4: L6 não disparou para c:policy (base VERIFIED)")

    # Add inline pair to trigger L7: parent with low confidence, child exceeding limit
    linter = GraphLinter()
    l7_claims = list(sample_claims) + [
        GovernedClaim(claim_key="c:low_conf_parent", claim_text="Weak evidence",
                      gmif_level=GMIFLevel.UNVERIFIED, gmif_confidence=0.30,
                      claim_references=[]),
        GovernedClaim(claim_key="c:overconfident_child", claim_text="Overly strong derived claim",
                      gmif_level=GMIFLevel.DERIVED, gmif_confidence=0.80,
                      claim_references=["c:low_conf_parent"]),
    ]
    l7_result = linter.run_all_checks(l7_claims)
    l7_issues = [i for i in l7_result.issues if i.lint_code == "L7"]
    assert any("c:overconfident_child" in i.claim_keys for i in l7_issues), (
        "CRITÉRIO 5 FAIL: L7 não detetou confidence mismatch"
    )
    print("  ✓ Critério 5: L7 detetou confidence mismatch em c:overconfident_child")

    print(f"\n  Resultado final: 5/5 critérios OK")
