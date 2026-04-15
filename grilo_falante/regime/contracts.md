# Contracts

## Promotion Contract

**Rule:** Nenhum resultado é promovido sem aprovação do Lint Cognitivo.

**Allowed states:** ACCEPT, CONDITIONAL

**Prohibited states:** REJECT, REEXECUTE

Promoção indevida aborta o ciclo.

## Validation Contract

- Claims require GF-ID and GMIF classification
- M4 claims with confidence < 0.3 are blocking
- All validations recorded in governance ledger

## Curator Contract

- Curators start at score 0.5
- Penalties for incongruence: -0.1
- Rewards for valid corrections: +0.05
- Auto-decay after 6 months inactivity: -0.3
