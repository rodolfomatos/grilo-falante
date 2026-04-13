# Pedido Otimizado

## Objetivo

Este documento reescreve o pedido original do utilizador numa forma mais completa, precisa e eficiente para futuras execuções no projeto.

---

## Fragilidades do Pedido Original

O pedido original era forte na intenção, mas deixava em aberto várias ambiguidades:

1. Não separava análise histórica, epistemológica, cognitiva e arquitetural.
2. Não definia entregáveis explícitos.
3. Não definia o que fazer com exageros narrativos.
4. Não dizia se a resposta devia ser apenas análise ou também proposta operacional.
5. Não explicitava onde integrar os resultados no projeto.

---

## Versão Otimizada

Usar o seguinte pedido:

> Analisa epistemologicamente, historicamente, cognitivamente e arquiteturalmente os dois textos seguintes, tratando-os como propostas de modelos cognitivos potencialmente integráveis no projeto `grilo-falante-skill`.
>
> Objetivos:
> 1. Extrair as ideias centrais de cada texto.
> 2. Distinguir claramente:
>    - insights úteis,
>    - exageros retóricos,
>    - erros factuais ou conceptuais,
>    - omissões importantes.
> 3. Reescrever cada texto numa versão mais rigorosa sem perder o valor heurístico.
> 4. Mapear como as ideias atribuídas a George Boole podem ser integradas como uma camada de análise de proposições, dependências, assunções, conclusões, tensões e condições de refutação.
> 5. Mapear como as ideias associadas ao efeito Zeigarnik podem ser integradas como uma camada de gestão de loops cognitivos, claims pendentes, validações suspensas, bloqueios e fechos confiáveis.
> 6. Relacionar estas duas camadas com os componentes já existentes no projeto:
>    - ACORDAR
>    - LOADER/KERNEL
>    - state machine g7/g8/g9
>    - GMIF
>    - legitimacy states
>    - BLOCK/PROMOTE
>    - artefactos do regime
> 7. Propor uma visão unificada do projeto que consolide:
>    - `ambrosio_v2.5.0`
>    - `epistemic-memory-architecture`
>    - `up-tax-intelligence-layer`
>    - `grilo-falante-skill`
>    - as novas camadas inspiradas por Boole e Zeigarnik
> 8. Produzir um plano concreto de implementação futura com:
>    - módulos novos,
>    - tipos de dados,
>    - mudanças à state machine,
>    - mudanças ao output JSON,
>    - critérios de lint/gating,
>    - roadmap por fases.
>
> Entregáveis esperados:
> - resumo executivo
> - análise crítica dos dois textos
> - lista de erros, exageros e omissões
> - versões corrigidas dos textos
> - proposta de arquitetura integrada
> - requisitos funcionais e não-funcionais novos
> - roadmap priorizado
> - documentação pronta a integrar em `docs/`
>
> Restrições:
> - não assumir que as narrativas históricas estão corretas;
> - separar claramente factos, interpretações e extrapolações;
> - privilegiar integração operacional no projeto, não apenas comentário filosófico;
> - documentar tudo o que for concluído.

---

## Versão Ainda Mais Operacional

Se o objetivo for não só analisar mas já preparar implementação, usar esta variante:

> Analisa os dois textos como fontes para extensão do modelo cognitivo do `grilo-falante-skill`. Documenta tudo em `docs/`, identifica erros, exageros e omissões, propõe correções, e converte o resultado num plano técnico concreto de integração no projeto. O resultado deve incluir novos módulos, novos tipos de dados, alterações à state machine, alterações ao output JSON, novas regras de lint/gating e roadmap por fases.

---

## Entregáveis Recomendados no Projeto

Para este pedido, os entregáveis ideais são:

- `docs/07-boole-zeigarnik-analysis.md`
- `docs/08-boole-zeigarnik-implementation-plan.md`
- `docs/09-optimized-request.md`

---

## Critério de Qualidade

Uma boa resposta a este pedido deve:

1. corrigir o texto sem o esvaziar;
2. preservar o valor conceptual;
3. transformar a análise em arquitetura e roadmap;
4. deixar claro o que é facto, o que é interpretação e o que é proposta.
