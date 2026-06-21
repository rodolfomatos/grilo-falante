# ADR-001: Invariantes Fundamentais do Grilo Falante

**Status:** Aceite
**Data:** 2026-06-21
**Contexto:** Identificação dos 6 invariantes que definem o regime epistémico.
Nenhum protocolo, ferramenta ou decisão pode violar estes invariantes.

## I1 — Auto-contenção

Nada é assumido fora do que está explicitamente documentado.

**Consequência:** O ACORDAR exige fonte temporal externa (relógio do sistema),
não confiando na perceção interna do modelo.

## I2 — Não-promoção implícita

Nenhum output exploratório é promovido a estrutura reutilizável
sem marcação explícita.

**Consequência:** Ciclos em modo "exploratory" não geram claims promovíveis.
`can_promote()` retorna False até `declare_legitimacy()` ser chamado.

## I3 — Rastreabilidade

Toda a regra, decisão ou documento tem origem identificável.

**Consequência:** O Ledger regista todas as transições, decisões PINA,
e eventos de regime com `cycle_id` e metadados de origem.

## I4 — Suspensão perante ambiguidade relevante

Na presença de ambiguidade epistémica, o sistema sinaliza e suspende.

**Consequência:** Validações que falham (temporal_anchor mismatch, lint REJECT)
bloqueiam progressão no ciclo.

## I5 — Responsabilidade humana final

Decisões normativas críticas não são tomadas pelo sistema.

**Consequência:** PINA modo "confirm" requer decisão humana (A/B/C) para
cada Ocorrência Normativa. O modo "auto" só incorpora trivia.

## I6 — Integridade sobre fluência

Coerência estrutural tem precedência sobre estilo ou rapidez.

**Consequência:** ACORDAR+VAI_DORMIR são passos obrigatórios do ciclo.
Nenhum atalho pode omitir verificação temporal, context restoration, ou handoff.

---

## Regras de Verificação

```python
# Pseudocódigo para verificação programática
def verify_invariants_acordar(result: AcordarResult) -> list[str]:
    violations = []
    if result.source != "system_clock":           # I1
        violations.append("I1: temporal anchor must be external")
    if result.intention_declared is None:          # I2 (implicit)
        violations.append("I2: intention must be declared")
    if result.warnings:                             # I4
        violations.append(f"I4: warnings exist: {result.warnings}")
    return violations

def verify_invariants_vai_dormir(result: dict) -> list[str]:
    violations = []
    if not result.get("handoff_path"):              # I3, I6
        violations.append("I3/I6: handoff file required")
    return violations
```
