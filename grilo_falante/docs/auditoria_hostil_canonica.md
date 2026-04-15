# Lint Cognitivo — LC‑FML v0.2

## Objetivo
Verificar governação cognitiva e factual, incluindo programação como domínio factual.

## Unidade
Bloco Cognitivo (BC): fase, tipo de claim, evidência, artefacto materializado, escopo.

## Regras Gerais
R0 Factual sem evidência → REJECT
R1 Síntese prematura → REEXECUTE
R2 Escopo implícito → REJECT
R3 Assunções ocultas → FLAG

## Regras Específicas de Programação
R4 Descrição de código ≠ estado factual → REJECT
R5 Correção técnica sem artefacto executável → REJECT
R6 Regressão a solução rejeitada → REEXECUTE

## Estados
ACCEPT | CONDITIONAL | REJECT | REEXECUTE

