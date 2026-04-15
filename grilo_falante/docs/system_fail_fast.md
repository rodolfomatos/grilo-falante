# Fail-Fast — Condições de Abort

## Princípio
Qualquer violação estrutural do regime deve provocar **aborto imediato do ciclo**. Não há recuperação silenciosa.

## Condições de Abort
1. Lint Cognitivo indisponível ou desativado.
2. Tentativa de promoção em estado exploratório.
3. Persistência de output sem metadata de lint válida.
4. Output com estado REJECT ou REEXECUTE a tentar avançar.
5. Ausência de Objeto Digital quando exigido.

## Efeito
- Ciclo abortado.
- Output marcado como inválido.
- Registo obrigatório no ledger.

