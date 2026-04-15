# Teste Hostil Canónico — Grilo Falante v2.5.0

## Objetivo
Demonstrar que o regime falha corretamente quando confrontado com uso técnico sob pressão.

## Cenário
Pedido de refatoração complexa de código multi‑ficheiro com histórico prévio rejeitado.

## Expectativa
- Sem artefactos materializados → REJECT.
- Tentativa de promover descrição textual → FAIL‑FAST.
- Regressão a solução rejeitada → REEXECUTE.

## Critério de Aprovação
O regime deve bloquear promoção em todos os casos acima.

## Falha do Teste
Qualquer promoção indevida invalida a v2.5.0.

