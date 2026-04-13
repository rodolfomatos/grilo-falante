# Visao Unificada

## Objetivo

Consolidar neste projeto quatro linhas de trabalho que hoje estao separadas:

1. `ambrosio_v2.5.0`: regime normativo e maquina de estados cognitiva.
2. `epistemic-memory-architecture`: retrieval, evidencia, governanca epistémica e blocking por insuficiencia de prova.
3. `up-tax-intelligence-layer`: motor de decisao auditavel orientado a dominio, com principio "sem base, sem decisao".
4. `grilo-falante-skill`: interface leve, portavel, usavel em CLI, API e ChatGPT/OpenCode.

O alvo nao e apenas "analisar documentos". O alvo e um **motor de trabalho cognitivo governado**, que recebe uma pergunta ou corpus, materializa claims, recolhe evidencia, passa por gates normativos, e so permite sintese ou promocao quando ha fundamento suficiente e declaracao humana explicita onde necessario.

---

## O Que Cada Projeto Oferece

### `ambrosio_v2.5.0`

Oferece a camada constitucional do sistema:

- ACORDAR
- legitimidade `SUSPENDED` vs `ASSERTED`
- artefactos `Documento Sombra`, `Objeto Digital`, `Capsula Conceptual`
- LOADER/KERNEL para resolucao de autoridade
- grafos normativos como representacao da maquina de estados
- PINA para incorporacao normativa
- regra de BLOCK como comportamento correto

O que pretende: nao produzir respostas melhores por magia, mas obrigar a um processo explicito, auditavel e humano-responsavel.

### `epistemic-memory-architecture`

Oferece a camada epistemica operacional:

- knowledge base baseada em claims
- retrieval e evidencia
- governance layer que decide se a resposta e justificavel
- memoria externa / shadow docs / ingestao
- pipeline experimental para comparar baseline vs sistema governado

O que pretende: responder apenas quando existe evidencia suficiente.

### `up-tax-intelligence-layer`

Oferece o modelo de decisao aplicacional:

- engine de decisao estruturada
- principio "no legal basis -> no decision"
- formato auditavel
- integracao API-first
- incerteza explicita em vez de alucinacao

O que pretende: transformar fontes normativas em decisoes rastreaveis para workflows reais.

### `grilo-falante-skill`

Oferece a camada de produto leve:

- CLI simples
- API FastAPI
- integracao ChatGPT/OpenCode
- graphify extraction
- GMIF basico
- persistencia simples
- state machine runtime leve

O que pretende: tornar o regime utilizavel, portavel e iteravel.

---

## Visao Consolidada

Este projeto deve tornar-se o **runtime unificado do regime Grilo Falante**.

Isso significa juntar:

- a **constituicao** de `ambrosio_v2.5.0`
- a **epistemologia operacional** de `epistemic-memory-architecture`
- o **modelo de decisao auditavel** de `up-tax-intelligence-layer`
- a **ergonomia de produto** do `grilo-falante-skill`

### Formula curta

`grilo-falante-skill` deve evoluir de "skill que extrai e colore claims" para:

> **um motor governado de analise, decisao e sintese epistemicamente bloqueavel**

---

## Arquitetura Alvo

```text
Entrada
  -> ACORDAR
  -> Loader/Kernel resolve autoridade
  -> graph/state machine escolhe pipeline valido
  -> extracao de claims
  -> retrieval de evidencia
  -> classificacao epistemica (GMIF + score)
  -> lint/gates normativos
  -> validacao humana onde exigido
  -> promote OR block
  -> materializacao em artefacto
  -> memoria externa / API / dashboard
```

### Camadas

1. **Constitution Layer**
`ACORDAR`, `LOADER`, `KERNEL`, PINA, artefact types, legitimacy.

2. **Evidence Layer**
Claims, retrieval, embeddings, provenance, confidence, contradiction handling.

3. **Governance Layer**
Graphs, phases, gates, lint, block, promotion rules.

4. **Decision Layer**
Structured outputs: answer, refusal, uncertainty, recommendation, audit trail.

5. **Product Layer**
CLI, API, HTML dashboard, ChatGPT/OpenCode adapters.

---

## Estado Atual

Ja existe base parcial:

- state machine com g7/g8/g9
- ACORDAR parcial
- legitimacy parcial
- F7 promotion gate parcial
- F8 persistence parcial
- integracao leve com CLI/API

Mas ainda falta a parte mais importante para a visao final:

- resolver autoridade via LOADER/KERNEL
- incorporar evidencia real como criterio principal
- bloquear por falta de base, nao apenas por regras locais simples
- materializar artefactos conforme o regime
- transformar outputs em decisoes estruturadas e auditaveis

---

## O Que Tem de Ser Feito

## Fase 1: Fechar o Regime Minimo

Objetivo: sair de "demo funcional" para "runtime minimo coerente".

### 1. Implementar LOADER/KERNEL

Falta:

- comando interno `LOAD GriloFalante FROM system.md`
- resolucao de artefactos governantes via `KERNEL.md`
- distincao entre documento presente e documento com autoridade operacional

Resultado esperado:

- o sistema sabe quais regras estao ativas e por que estao ativas.

### 2. Implementar BLOCK real

Falta:

- bloquear transicao invalida com razao explicita
- distinguir `BLOCK por regra`, `BLOCK por falta de evidencia`, `BLOCK por falta de legitimidade`
- devolver resposta estruturada de bloqueio

Resultado esperado:

- o sistema para corretamente e explica porque nao pode continuar.

### 3. Implementar artefactos do regime

Falta:

- `DocumentoSombra`
- `ObjetoDigital`
- `CapsulaConceptual`
- transicoes permitidas entre estes tipos

Resultado esperado:

- tudo o que o sistema produz existe como artefacto materializado com tipo claro.

---

## Fase 2: Trazer a Camada de Evidencia

Objetivo: substituir heuristica local por governanca baseada em prova.

### 4. Integrar retrieval do `epistemic-memory-architecture`

Falta:

- embeddings
- busca vetorial
- evidence engine
- provenance por claim

Resultado esperado:

- cada claim relevante tem evidencia associada ou ausencia explicita de evidencia.

### 5. Melhorar GMIF

Falta:

- usar evidence score real
- considerar contradicoes, temporalidade, numero e qualidade das fontes
- separar claim grounded, derived e hypothesis com impacto real na promocao

Resultado esperado:

- GMIF deixa de ser apenas cor/rotulo e passa a influenciar governanca.

### 6. Introduzir threshold epistemico configuravel

Falta:

- limiar minimo de evidencia para promover resposta
- thresholds por dominio ou modo
- politica de recusa quando abaixo do limiar

Resultado esperado:

- principio do `up-tax-intelligence-layer`: sem base suficiente, sem decisao.

---

## Fase 3: Transformar em Motor de Decisao Auditavel

Objetivo: passar de analise para decisao estruturada e rastreavel.

### 7. Definir formato canonico de output

Cada output deve poder ser um destes:

- `analysis`
- `decision`
- `refusal`
- `uncertainty`
- `promotion_record`

Campos minimos:

- intencao
- grafo usado
- estado atual
- transicoes percorridas
- claims
- evidencia
- legitimacy
- motivo de promote/block
- artefact type

### 8. Adicionar audit trail forte

Falta:

- lineage por claim
- fontes usadas
- transicoes executadas
- gates aprovados/rejeitados
- quem asserted legitimacy

Resultado esperado:

- qualquer output pode ser auditado retrospectivamente.

### 9. Criar dashboards operacionais

Falta:

- visualizacao de grafos de evidencia
- visualizacao da state machine percorrida
- lista de claims bloqueados/promovidos
- filtros por GMIF e legitimacy

Resultado esperado:

- o sistema deixa de ser caixa preta.

---

## Fase 4: Consolidar o Produto

Objetivo: tornar isto usavel em varios contextos sem duplicar logica.

### 10. Criar core unico e adapters finos

Separar:

- `core/` regime + evidence + governance
- `adapters/cli`
- `adapters/api`
- `adapters/chatgpt`
- `adapters/opencode`

Resultado esperado:

- uma unica logica governante, varias portas de entrada.

### 11. Integrar LLM providers de forma limpa

Usar o que o `iaedu-adapter` mostra:

- isolamento do provider
- streaming quando existir
- sessao/thread mapping
- seguranca por env vars

Resultado esperado:

- o LLM e substituivel e nunca confunde provider com governanca.

### 12. Criar modos de operacao explicitos

Exemplo:

- `explore`
- `analyze`
- `decide`
- `audit`
- `promote`

Cada modo ativa grafos, thresholds e gates diferentes.

---

## Roadmap Recomendado

### Sprint A

- LOADER/KERNEL minimo
- BLOCK estruturado
- output canonico com audit trail minimo

### Sprint B

- evidence retrieval basico
- GMIF melhorado
- threshold epistemico

### Sprint C

- artefact types
- promotion records
- dashboard de estado + evidencia

### Sprint D

- refactor para core + adapters
- provider abstraction
- testes de regressao do regime

---

## Definicao de Sucesso

O projeto tera atingido a visao quando:

1. uma pergunta pode entrar por CLI, API ou ChatGPT;
2. o sistema executa ACORDAR e resolve autoridade normativa;
3. claims sao extraidos e suportados por evidencia rastreavel;
4. a state machine governa realmente as transicoes;
5. respostas sem base suficiente sao bloqueadas;
6. outputs promovidos sao materializados como artefactos auditaveis;
7. um humano consegue inspecionar porque algo foi promovido, bloqueado ou mantido suspenso.

---

## Frase-Guia

Este projeto nao deve tentar parecer inteligente.

Deve tentar ser isto:

> **um sistema que so deixa passar o que consegue justificar, e que torna visivel tudo o que nao consegue justificar.**
