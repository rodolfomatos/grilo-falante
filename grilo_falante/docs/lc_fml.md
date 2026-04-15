# Lint Cognitivo — LC-FML v0.1

## Objetivo
Especificação formal mínima para verificação de governação cognitiva.

## Unidade
Bloco Cognitivo (BC): fase, claims, evidência, pressupostos, escopo.

## Tipos
- Claim: factual | inferencial | normativa | pedagógica
- Evidence: externa | interna | nenhuma
- Assumption: aceite | recusada | oculta

## Regras
R0 Ancoragem: factual sem evidência → HARD FAIL
R1 Escopo: problema implícito em FASE 0 → HARD FAIL
R2 Ordem: síntese prematura → HARD FAIL
R3 Assunções ocultas → FLAG
R4 TOC: gargalo não único em FASE 3 → HARD FAIL
R5 Pedagogia antes de FASE 4 → FLAG
R6 Auditoria ausente → HARD FAIL

## Estados
ACCEPT | CONDITIONAL | REJECT | REEXECUTE

